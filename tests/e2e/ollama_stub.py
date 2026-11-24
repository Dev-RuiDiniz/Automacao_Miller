import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class OllamaFixture(BaseHTTPRequestHandler):
    def reply(self, status, body):
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        self.reply(200, {"ok": True})

    def do_POST(self):
        if self.path != "/api/generate":
            self.reply(404, {})
            return

        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if request.get("format") == "json":
            if "FALHA SINTETICA" in request["prompt"]:
                self.reply(200, {"response": "Resposta sintética fora do formato esperado."})
                return
            deadline = time.monotonic() + 30
            while not Path("/tmp/liberar-analise").exists():
                if time.monotonic() > deadline:
                    self.reply(503, {"error": "O teste não liberou a análise."})
                    return
                time.sleep(0.1)
            response = json.dumps({"achados": [{
                "titulo": "Ato sintético",
                "fato": "Trecho do documento de teste.",
                "pagina": 1,
                "evidencia": "ATO REGULATORIO SINTETICO",
            }]})
        else:
            response = "# Relatório Técnico de Inteligência Regulatória\n\n## 1. Resumo executivo\n\n"
            response += "O documento de teste contém um ato sintético na página 1."
        self.reply(200, {"response": response})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 11434), OllamaFixture).serve_forever()
