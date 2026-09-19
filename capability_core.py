"""Small trusted-host capability contract reference. NOT a sandbox or durable runtime.

Owns contracts and checks, not scheduling, providers, retry, or distributed effects.
Only register reviewed, trusted callables. Production adapters must enforce scopes,
time/memory/egress limits and persistent effect reconciliation outside this module.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import json
import math
import re
from typing import Any, Callable


class ContractError(ValueError):
    pass


def encode(value: Any, max_bytes: int = 1_000_000) -> bytes:
    """Canonical finite JSON only; byte limit is NOT an allocation/time sandbox."""
    def check(v, depth=0):
        if depth > 40:
            raise ContractError("JSON depth limit exceeded")
        if v is None or type(v) in (str, bool, int):
            return
        if type(v) is float and math.isfinite(v):
            return
        if type(v) is list:
            for x in v: check(x, depth + 1)
            return
        if type(v) is dict and all(type(k) is str for k in v):
            for x in v.values(): check(x, depth + 1)
            return
        raise ContractError("finite JSON with string keys required")
    check(value)
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                     allow_nan=False).encode("utf-8")
    if len(raw) > max_bytes:
        raise ContractError("serialized artifact limit exceeded")
    return raw


def digest(value: Any) -> str:
    return hashlib.sha256(encode(value)).hexdigest()


def clone(value: Any) -> Any:
    return json.loads(encode(value))


class Artifacts:
    """In-memory content-addressed values; private to this kernel instance."""
    def __init__(self): self._values: dict[str, bytes] = {}
    def put(self, value: Any) -> str:
        raw = encode(value)
        key = hashlib.sha256(raw).hexdigest()
        self._values[key] = raw
        return key
    def get(self, key: str) -> Any:
        raw = self._values[key]
        if hashlib.sha256(raw).hexdigest() != key:
            raise ContractError("artifact hash mismatch")
        return json.loads(raw)


@dataclass(frozen=True)
class Capability:
    name: str
    version: str
    description: str
    kind: str  # pure, read, effect -- classifications asserted by trusted host
    units: int  # synthetic work reservation, NOT dollars/tokens or real billing
    input_contract: str
    output_contract: str
    validate_input: Callable[[Any], bool]
    validate_output: Callable[[Any], bool]
    execute: Callable[[Any, "Context"], Any]
    verifier_id: str = "unverified"
    verify: Callable[[Any, Any], bool] | None = None
    dependencies: tuple[str, ...] = ()
    # Must change if any executable behavior, closure, prompt or validator changes.
    release: str = "1"

    def manifest(self) -> dict:
        return {k: getattr(self, k) for k in (
            "name", "version", "description", "kind", "units", "input_contract",
            "output_contract", "verifier_id", "release")} | {"dependencies": list(self.dependencies)}


@dataclass(frozen=True)
class Policy:
    allowed: frozenset[str]
    effect_grants: frozenset[str] = frozenset()
    def __post_init__(self):
        if not isinstance(self.allowed, frozenset) or not isinstance(self.effect_grants, frozenset):
            raise ContractError("policy sets must be immutable frozensets")
        if any(type(x) is not str or not x for x in self.allowed | self.effect_grants):
            raise ContractError("policy identifiers must be nonempty strings")
        if not self.effect_grants <= self.allowed:
            raise ContractError("effect grant must be within allowed capabilities")
    def narrow(self, names) -> "Policy":
        names = frozenset(names)
        if not names <= self.allowed:
            raise ContractError("cannot widen parent authority")
        return Policy(names, self.effect_grants & names)


@dataclass
class Run:
    policy: Policy
    budget: int = 100
    max_calls: int = 100
    max_depth: int = 12
    used: int = field(default=0, init=False)
    calls: int = field(default=0, init=False)
    cancelled: bool = field(default=False, init=False)
    trace: list = field(default_factory=list, init=False)
    # Per-process/per-run duplicate suppression ONLY. Never presented as exactly-once.
    effects: dict = field(default_factory=dict, init=False)
    def __post_init__(self):
        if any(type(x) is not int or x < 0 for x in (self.budget, self.max_calls, self.max_depth)):
            raise ContractError("budgets and limits must be nonnegative integers")
    def cancel(self): self.cancelled = True


@dataclass(frozen=True)
class Receipt:
    capability: str
    status: str
    reason: str
    input_hash: str | None = None
    output_hash: str | None = None
    release_hash: str | None = None
    units: int = 0
    reused: bool = False
    effect_state: str = "not_attempted"

    def require_verified(self, artifacts: Artifacts) -> Any:
        if self.status != "verified" or not self.output_hash:
            raise ContractError(f"unaccepted dependency: {self.capability}: {self.status}")
        return artifacts.get(self.output_hash)


class Context:
    def __init__(self, kernel, run, policy, dependencies, depth):
        self._kernel, self._run, self._policy = kernel, run, policy
        self._dependencies, self._depth = dependencies, depth
    def call(self, name: str, value: Any, *, effect_key: str | None = None) -> Receipt:
        if name not in self._dependencies:
            raise ContractError("undeclared dependency")
        return self._kernel._call(name, value, self._run, self._policy, self._depth + 1, effect_key)
    def value(self, receipt: Receipt) -> Any:
        return receipt.require_verified(self._kernel.artifacts)


class Kernel:
    """Synchronous conformance runner over trusted adapters, no automatic retries.

    A production Weft/other runtime should implement this boundary, not run as a
    competing authority. Single-threaded; not safe for concurrent Run mutation.
    """
    def __init__(self, capabilities):
        self._registry = {}
        self.artifacts = Artifacts()
        self._cache: dict[tuple[str, str], Receipt] = {}
        for cap in capabilities:
            if not isinstance(cap, Capability) or not re.fullmatch(r"[a-z][a-z0-9_.-]*", cap.name):
                raise ContractError("invalid capability")
            if cap.name in self._registry:
                raise ContractError("duplicate capability name")
            if cap.kind not in ("pure", "read", "effect") or type(cap.units) is not int or cap.units < 0:
                raise ContractError("invalid kind or work reservation")
            if not all(type(x) is str and x for x in (cap.version, cap.release, cap.input_contract,
                                                     cap.output_contract, cap.verifier_id)):
                raise ContractError("versioned contracts required")
            if not isinstance(cap.dependencies, tuple) or len(set(cap.dependencies)) != len(cap.dependencies):
                raise ContractError("dependencies must be a unique tuple")
            if any(not callable(x) for x in (cap.execute, cap.validate_input, cap.validate_output)):
                raise ContractError("trusted adapter functions required")
            if cap.verify is not None and not callable(cap.verify):
                raise ContractError("invalid verifier")
            self._registry[cap.name] = cap
        self._fingerprints = {}
        self._closure = {}
        def visit(name, path):
            if name not in self._registry or name in path:
                raise ContractError("missing or cyclic dependency")
            if name in self._fingerprints: return
            cap = self._registry[name]
            for child in cap.dependencies: visit(child, path | {name})
            closure = {name}
            for child in cap.dependencies: closure |= self._closure[child]
            if cap.kind == "pure" and any(self._registry[x].kind != "pure" for x in closure):
                raise ContractError("a pure recipe cannot hide a read or effect")
            if cap.kind == "read" and any(self._registry[x].kind == "effect" for x in closure):
                raise ContractError("a read recipe cannot hide an effect")
            self._closure[name] = closure
            self._fingerprints[name] = digest({"manifest": cap.manifest(),
                "children": {c: self._fingerprints[c] for c in cap.dependencies}})
        for name in self._registry: visit(name, set())

    def describe(self, name: str, policy: Policy) -> dict:
        if name not in policy.allowed or name not in self._registry:
            raise ContractError("unknown or unauthorized capability")
        return self._registry[name].manifest() | {"release_hash": self._fingerprints[name]}

    def discover(self, query: str, policy: Policy, limit: int = 5) -> list[dict]:
        """Bounded lexical baseline, not semantic relevance or complete recall."""
        if type(limit) is not int or not 1 <= limit <= 20 or type(query) is not str:
            raise ContractError("invalid discovery request")
        tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
        matches = []
        for name in policy.allowed & self._registry.keys():
            cap = self._registry[name]
            score = len(tokens & set(re.findall(r"[a-z0-9]+", (name + " " + cap.description).lower())))
            if score: matches.append((score, name, cap))
        return [{"name": c.name, "version": c.version, "description": c.description, "kind": c.kind}
                for _, _, c in sorted(matches, key=lambda row: (-row[0], row[1]))[:limit]]

    def call(self, name: str, value: Any, run: Run, *, effect_key: str | None = None) -> Receipt:
        return self._call(name, value, run, run.policy, 0, effect_key)

    def _call(self, name, value, run, policy, depth, effect_key):
        def done(status, reason, **kw):
            receipt = Receipt(name, status, reason, **kw)
            run.trace.append(receipt)
            return receipt
        if type(name) is not str or not name: return done("denied", "invalid capability identifier")
        if run.cancelled: return done("denied", "run cancelled")
        if depth > run.max_depth: return done("denied", "call depth exceeded")
        if run.calls >= run.max_calls: return done("denied", "call count exceeded")
        run.calls += 1
        if name not in policy.allowed or name not in self._registry:
            return done("denied", "unknown or unauthorized capability")
        cap = self._registry[name]
        if not self._closure[name] <= policy.allowed:
            return done("denied", "required dependencies are outside authority")
        if cap.kind == "effect" and (name not in policy.effect_grants or not isinstance(effect_key, str) or not effect_key.strip()):
            return done("denied", "effect requires explicit host grant and operation key")
        try:
            original = clone(value)
            if cap.validate_input(clone(original)) is not True:
                raise ContractError("input rejected")
            ih, rh = self.artifacts.put(original), self._fingerprints[name]
        except Exception:
            return done("denied", "input contract rejected")
        common = {"input_hash": ih, "release_hash": rh}
        fingerprint = (rh, ih)
        if cap.kind == "effect" and effect_key in run.effects:
            old_fp, old = run.effects[effect_key]
            if old_fp != fingerprint:
                return done("denied", "operation key already bound to different input/release", **common)
            return done(old.status, "recorded operation; not re-executed", **common,
                        output_hash=old.output_hash, reused=True, effect_state=old.effect_state)
        # Check full authority before reuse. Only declared pure verified values may cache.
        if cap.kind == "pure" and fingerprint in self._cache:
            old = self._cache[fingerprint]
            self.artifacts.get(old.output_hash)  # integrity check, not silent recomputation
            return done("verified", "verified pure result reused", **common,
                        output_hash=old.output_hash, reused=True, effect_state="none")
        if run.used + cap.units > run.budget:
            return done("denied", "work budget exhausted", **common)
        run.used += cap.units  # reserve BEFORE entering adapter; retained on failure
        effect = cap.kind == "effect"
        if effect:
            run.effects[effect_key] = (fingerprint, Receipt(name, "uncertain", "operation started",
                **common, units=cap.units, effect_state="uncertain"))
        ctx = Context(self, run, policy.narrow(self._closure[name] - {name}), cap.dependencies, depth)
        try:
            result = cap.execute(clone(original), ctx)
            if cap.validate_output(clone(result)) is not True:
                raise ContractError("output rejected")
            output_hash = self.artifacts.put(result)
            passed = cap.verify(clone(original), clone(result)) if cap.verify else None
            if passed is not None and type(passed) is not bool:
                raise ContractError("verifier must return bool or unknown")
            status = "verified" if passed is True else "failed" if passed is False else "unverified"
            effect_state = ("verified" if passed is True else "uncertain") if effect else "none"
            receipt = done(status, "verifier " + str(passed), **common, output_hash=output_hash,
                           units=cap.units, effect_state=effect_state)
        except Exception:
            # Exceptions can contain secrets. Do not expose arbitrary adapter error text.
            receipt = done("uncertain" if effect else "failed", "adapter or verifier failed",
                           **common, units=cap.units, effect_state="uncertain" if effect else "none")
        if effect: run.effects[effect_key] = (fingerprint, receipt)
        if cap.kind == "pure" and receipt.status == "verified": self._cache[fingerprint] = receipt
        return receipt
