"""
Cliente HTTP para Ollama API
"""
import time
import base64
import io
import requests
from PIL import Image
from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_RETRIES,
    OLLAMA_HEALTH_TIMEOUT,
    OLLAMA_HEALTH_CACHE_TTL,
    OLLAMA_MODELS,
    TIMEOUTS,
)
from utils.logging_setup import LOGGER


class OllamaClient:
    """
    Cliente HTTP para comunicação com Ollama.
    Suporta geração de texto e análise de imagens.
    """

    def __init__(self, active_models=None):
        self.base_url = OLLAMA_BASE_URL
        self.retries = OLLAMA_RETRIES
        self.health_timeout = OLLAMA_HEALTH_TIMEOUT
        self.logger = LOGGER

        # Modelos ativos (podem ser customizados)
        self.active_models = dict(active_models) if active_models else dict(OLLAMA_MODELS)

        # Session HTTP reutilizável
        self.session = requests.Session()

        # Cache de health check
        self._health_cache = {"ts": 0.0, "ok": None}

        # Flag de stop para interromper operações
        self.stop_flag = False

    # ------------------------------------------------------------------
    # NOVO: atualiza modelos em runtime (usado pelo modal de configuração)
    # ------------------------------------------------------------------
    def update_models(self, new_models: dict):
        """
        Atualiza os modelos activos sem reiniciar o cliente.
        Faz merge com os defaults para não perder roles não configurados.
        """
        merged = dict(OLLAMA_MODELS)   # começa com defaults
        merged.update(new_models)       # sobrescreve com os novos
        self.active_models = merged
        # Invalida cache de health para forçar re-check
        self._health_cache = {"ts": 0.0, "ok": None}
        self.logger.info("✅ Modelos Ollama actualizados: %s", merged)

    def is_available(self):
        """
        Verifica disponibilidade do Ollama com cache de 5s.
        Retorna True se disponível, False caso contrário.
        """
        try:
            now = time.time()
            cached = self._health_cache

            if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < OLLAMA_HEALTH_CACHE_TTL:
                return bool(cached["ok"])

            resp = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=self.health_timeout,
            )
            ok = resp.status_code == 200
            self._health_cache = {"ts": now, "ok": ok}
            return ok

        except Exception:
            self._health_cache = {"ts": time.time(), "ok": False}
            return False

    def _get_model(self, role):
        return self.active_models.get(role, OLLAMA_MODELS.get(role, ""))

    def _get_timeout(self, role):
        return TIMEOUTS.get(role, (5, 30))

    def generate_text(
        self,
        prompt,
        role="text_quality",
        temperature=0.7,
        num_predict=350,
    ):
        """
        Gera texto usando modelo Ollama via /api/chat.
        """
        if self.stop_flag:
            return ""

        if not self.is_available():
            self.logger.warning("⚠️ Ollama indisponível. Usando fallback.")
            return ""

        model = self._get_model(role)
        timeout = self._get_timeout(role)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente especialista em produtos de corte laser, "
                        "decoração artesanal e objetos afetivos personalizados. "
                        "Responda SEMPRE em português brasileiro. "
                        "Siga as instruções de formato com precisão."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": num_predict,
                "repeat_penalty": 1.1,
            },
        }

        last_err = None
        for attempt in range(1, self.retries + 1):
            if self.stop_flag:
                return ""
            try:
                resp = self.session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=timeout,
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                text = (data.get("message") or {}).get("content") or data.get("response") or ""
                self.logger.info("✅ [%s] gerou resposta (%d chars)", model, len(text))
                return text.strip()
            except Exception as e:
                last_err = e
                self.logger.warning(
                    "Ollama falhou (tentativa %d/%d) [%s]: %s",
                    attempt, self.retries, model, e
                )
                if attempt < self.retries:
                    time.sleep(2.0)

        if last_err:
            self.logger.error(
                "Ollama falhou definitivamente [%s]: %s",
                model, last_err, exc_info=True
            )
        return ""

    def describe_image(self, image_path):
        """
        Analisa imagem usando moondream via /api/generate.
        """
        if self.stop_flag:
            return ""

        if not self.is_available():
            return ""

        model = self._get_model("vision")
        timeout = self._get_timeout("vision")

        try:
            with Image.open(image_path) as img:
                img.thumbnail((512, 512), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            payload = {
                "model": model,
                "prompt": (
                    "Look only at the main laser-cut wooden object in the center of this image. "
                    "Ignore the background, walls, stuffed animals, toys, watermarks and any text overlays. "
                    "Describe ONLY the central object: its shape, theme and style. "
                    "One short sentence. Be specific and factual."
                ),
                "images": [img_b64],
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 60},
            }

            resp = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout,
            )

            if resp.status_code == 200:
                vision_text = (resp.json().get("response") or "").strip()
                self.logger.info("👁️ [moondream] %s", vision_text[:80])
                return vision_text

        except Exception as e:
            self.logger.warning("Falha ao descrever imagem com moondream: %s", e)

        return ""
