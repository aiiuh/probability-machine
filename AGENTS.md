# Project instructions

Read README.md and STATUS.md first. Follow explicit current user instructions over historical assumptions.

- Research primary sources for material technical claims. Separate observed, assumed, simulated, and model-generated evidence.
- Do not assume the incentive hypothesis or current architecture is correct. Compare with simpler baselines and log negative results.
- This is a public repository. No credentials, participant records, private project notes, personal profiles, or local-machine paths.
- The core must remain runnable without provider credentials. Keep optional adapters separate and spending bounded.
- Preserve one side-effect authority; probabilities do not grant permissions.
- Unit tests, synthetic experiments, API/HTTP checks, browser tests, and human validation are different evidence classes. Never substitute one for another in a claim.
- Keep duplicate and dependent evidence from becoming artificial corroboration. Track origins, sources, and model/input versions.
- Run `python3 -m unittest discover -s tests -v` and `python3 experiments.py` after changes. Explain unrun tests or unavailable capabilities exactly.
