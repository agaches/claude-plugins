import http.server
import os
import tempfile
import threading
import unittest

from verifier_liens import extraire_urls, main, verifier


class _Handler(http.server.BaseHTTPRequestHandler):
    def _reponse(self, code):
        self.send_response(code)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_HEAD(self):
        routes = {"/ok": 200, "/head-interdit": 405, "/robot": 403}
        self._reponse(routes.get(self.path, 404))

    def do_GET(self):
        routes = {"/ok": 200, "/head-interdit": 200, "/robot": 403}
        self._reponse(routes.get(self.path, 404))

    def log_message(self, *args):
        pass


class TestVerifierLiens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.serveur = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        cls.base = f"http://127.0.0.1:{cls.serveur.server_port}"
        threading.Thread(target=cls.serveur.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.serveur.shutdown()

    def test_extraire_urls_dedoublonne_et_nettoie(self):
        t = "voir [doc](https://a.com/x). et <https://b.com/y>, https://a.com/x"
        self.assertEqual(extraire_urls(t), ["https://a.com/x", "https://b.com/y"])

    def test_200_est_ok(self):
        self.assertEqual(verifier(self.base + "/ok")[0], "ok")

    def test_404_est_ko(self):
        self.assertEqual(verifier(self.base + "/absent")[0], "ko")

    def test_head_405_puis_get_200_est_ok(self):
        self.assertEqual(verifier(self.base + "/head-interdit")[0], "ok")

    def test_403_est_avertissement(self):
        self.assertEqual(verifier(self.base + "/robot")[0], "a-verifier")

    def test_injoignable_est_ko(self):
        self.assertEqual(verifier("http://127.0.0.1:9/", timeout=2)[0], "ko")

    def _fichier(self, contenu):
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        f.write(contenu)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_main_code_retour(self):
        ko = self._fichier(f"{self.base}/ok et {self.base}/absent")
        ok = self._fichier(f"{self.base}/ok")
        self.assertEqual(main([ko]), 1)
        self.assertEqual(main([ok]), 0)


if __name__ == "__main__":
    unittest.main()
