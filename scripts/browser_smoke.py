"""Optional Playwright smoke check; generated interactions are NOT human data."""
import json
import os
from pathlib import Path
import sys
import threading
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Handler
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
checks=[]
try:
    with sync_playwright() as p:
        options={'headless':True}
        if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
        browser=p.chromium.launch(**options)
        page=browser.new_page(viewport={'width':1280,'height':1000})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}')
        page.wait_for_function("document.getElementById('spec').value.length>0")
        page.click('#solve');page.wait_for_function("document.getElementById('decision').textContent.includes('counterbalanced_layout_test')")
        checks.append('decision_endpoint_rendered')
        page.click('#start');assert page.evaluate('window.probabilityMachineSnapshot()') is None
        checks.append('no_recording_without_opt_in')
        page.check('#consent');page.click('#start');page.wait_for_function("document.getElementById('trialStatus').textContent.includes('Trial 1/')")
        page.click('#decoy');page.click('#target')
        snapshot=page.evaluate('window.probabilityMachineSnapshot()')
        assert len(snapshot['trials'])==1 and snapshot['trials'][0]['errors']==1 and snapshot['trials'][0]['success']
        checks.append('target_and_error_recording')
        variant=snapshot['variant']
        page.click('#start');page.wait_for_function("document.getElementById('trialStatus').textContent.includes('Trial 2/')")
        page.keyboard.press('Escape');snapshot=page.evaluate('window.probabilityMachineSnapshot()')
        assert snapshot['variant']==variant and snapshot['trials'][1]['reason']=='escape' and not snapshot['trials'][1]['success']
        checks.append('stable_session_assignment_and_stop')
        with page.expect_download() as d:page.click('#export')
        assert d.value.suggested_filename.endswith('.json');checks.append('json_download')
        page.click('#reset');assert page.evaluate('window.probabilityMachineSnapshot()') is None
        checks.append('discard_clears_memory')
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        checks.append('mobile_no_horizontal_overflow')
        page.check('#consent');page.click('#start');page.wait_for_function("document.getElementById('trialStatus').textContent.includes('Trial 1/')")
        page.click('#target');assert page.evaluate('window.probabilityMachineSnapshot().trials.length')==1
        checks.append('mobile_interaction')
        page.screenshot(path=str(root/'results/workbench-smoke.png'),full_page=True)
        assert not errors,errors;checks.append('no_browser_javascript_errors')
        report={'status':'passed','checks':checks,'browser':browser.version,'data_origin':'automated_smoke_test_NOT_human_evidence','limitations':['Not a security audit','Not an accessibility audit','No user research or enjoyment validation']}
        (root/'results/browser-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2));browser.close()
finally:
    server.shutdown();server.server_close();thread.join()
