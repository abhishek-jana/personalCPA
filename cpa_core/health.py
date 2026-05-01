import httpx
import sqlite3
import sqlite_vss
import os
from typing import Dict, List, Any

class SystemHealth:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url

    def check_ollama(self) -> Dict[str, Any]:
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    models = [m["name"] for m in response.json().get("models", [])]
                    return {"status": "ok", "models": models}
                return {"status": "error", "message": "Ollama returned an unexpected status code."}
        except Exception:
            return {"status": "error", "message": "Could not connect to Ollama. Is it running?"}

    def check_sqlite_vss(self) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(":memory:")
            conn.enable_load_extension(True)
            sqlite_vss.load(conn)
            cursor = conn.cursor()
            cursor.execute("select vss_version()")
            version = cursor.fetchone()[0]
            conn.close()
            return {"status": "ok", "version": version}
        except Exception as e:
            return {"status": "error", "message": f"Failed to load sqlite-vss extension. This is required for 'Memory' (Vector Search)."}

    def run_all(self, critical_models: List[str], optional_models: List[str] = None) -> Dict[str, Any]:
        ollama = self.check_ollama()
        vss = self.check_sqlite_vss()

        if optional_models is None:
            optional_models = []

        installed_models = ollama.get("models", [])

        def is_model_installed(req):
            for installed in installed_models:
                if installed == req or installed.split(':')[0] == req:
                    return True
            return False

        missing_critical = [m for m in critical_models if not is_model_installed(m)]
        missing_optional = [m for m in optional_models if m not in critical_models and not is_model_installed(m)]

        overall_status = "ok"
        if ollama["status"] == "error" or vss["status"] == "error" or missing_critical:
            overall_status = "error"

        return {
            "status": overall_status,
            "ollama": ollama,
            "vss": vss,
            "missing_critical": missing_critical,
            "missing_optional": missing_optional
        }
