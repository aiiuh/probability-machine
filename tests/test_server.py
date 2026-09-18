import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from server import Handler
from probability_machine import information_value, plan, softmax

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0), Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True); cls.thread.start()
        cls.spec=json.loads((Path(__file__).parents[1]/'examples/layout.json').read_text())
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def req(self,method,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        c.request(method,path,body,headers or {}); r=c.getresponse(); out=(r.status,dict(r.getheaders()),r.read());c.close();return out
    def test_page(self):
        status,h,b=self.req('GET','/');self.assertEqual(status,200);self.assertIn(b'Probability Machine',b);self.assertIn('Content-Security-Policy',h)
    def test_no_arbitrary_file_access(self):self.assertEqual(self.req('GET','/../probability_machine.py')[0],404)
    def test_bad_host(self):self.assertEqual(self.req('GET','/',headers={'Host':'attacker.invalid'})[0],403)
    def test_cross_origin(self):self.assertEqual(self.req('POST','/api/plan','{}',{'Origin':'https://attacker.invalid','Content-Type':'application/json'})[0],403)
    def test_json_only(self):self.assertEqual(self.req('POST','/api/plan','{}')[0],415)
    def test_empty_request(self):self.assertEqual(self.req('POST','/api/plan','',{'Content-Type':'application/json'})[0],413)
    def test_bad_json(self):self.assertEqual(self.req('POST','/api/plan','bad',{'Content-Type':'application/json'})[0],400)
    def test_array_rejected(self):self.assertEqual(self.req('POST','/api/plan','[]',{'Content-Type':'application/json'})[0],400)
    def test_nonfinite_rejected(self):self.assertEqual(self.req('POST','/api/plan','{"x":NaN}',{'Content-Type':'application/json'})[0],400)
    def test_plan_endpoint(self):
        status,h,b=self.req('POST','/api/plan',json.dumps(self.spec),{'Content-Type':'application/json'})
        self.assertEqual(status,200);self.assertFalse(json.loads(b)['executed']);self.assertEqual(h['Cache-Control'],'no-store')
    def test_sources_required_for_measured(self):
        s=dict(self.spec,model_origin='measured')
        with self.assertRaises(ValueError):plan(s)
    def test_sources_preserved(self):
        s=dict(self.spec,model_origin='measured',model_sources=['example:unverified-user-supplied'])
        self.assertEqual(plan(s)['model_sources'],s['model_sources'])
    def test_malformed_answer_coverage(self):
        with self.assertRaises(ValueError):information_value({'m':1},{'a':{'m':1}},{'yes':{'wrong':1}},0)
    def test_zero_temperature_extremes(self):self.assertEqual(softmax({'a':1e308,'b':-1e308},0),{'a':.5,'b':.5})

if __name__=='__main__':unittest.main()
