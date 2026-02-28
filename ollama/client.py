"""
LASERFLIX — Ollama Client
HTTP client + health checks com cache
"""

import time
import requests
import logging

LOGGER = logging.getLogger("Laserflix")

# Timeouts por tipo de modelo
TIMEOUTS = {
    "text_quality": (5, 120),
    "text_fast": (5, 75),
    "vision": (5, 60),
    "embed": (5, 15),
}


class OllamaClient:
    """Cliente HTTP para Ollama com cache de health"""

    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        self.retries = 3
        self.health_timeout = 4
        self._health_cache = {"ts": 0.0, "ok": None}

    def check_health(self) -> bool:
        """Verifica disponibilidade (cache 5s)"""
        try:
            now = time.time()
            cached = self._health_cache
            if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < 5.0:
                return bool(cached["ok"])
            resp = self.session.get(f"{self.base_url}/api/tags", timeout=self.health_timeout)
            ok = resp.status_code == 200
            self._health_cache = {"ts": now, "ok": ok}
            return ok
        except Exception:
            self._health_cache = {"ts": time.time(), "ok": False}
            return False

    def generate_text(self, prompt: str, model: str, role: str = "text_quality", temperature: float = 0.7, num_predict: int = 350) -> str:
        """Gera texto com chat API (Qwen2.5-Instruct)"""
        if not self.check_health():
            LOGGER.warning("Ollama indisponível")
            return ""
        timeout = TIMEOUTS.get(role, (5, 30))
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Você é um assistente especialista em produtos de corte laser. Responda em português brasileiro."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature, "top_p": 0.9, "top_k": 40, "num_predict": num_predict, "repeat_penalty": 1.1},
        }
        last_err = None
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=timeout)
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama HTTP {resp.status_code}")
                data = resp.json()
                text = (data.get("message") or {}).get("content") or data.get("response") or ""
                LOGGER.info(f"✅ [{model}] gerou resposta ({len(text)} chars)")
                return text.strip()
            except Exception as e:
                last_err = e
                LOGGER.warning(f"Ollama falhou (tentativa {attempt}/{self.retries}): {e}")
                if attempt < self.retries:
                    time.sleep(2.0)
        LOGGER.error(f"Ollama falhou definitivamente: {last_err}")
        return ""
