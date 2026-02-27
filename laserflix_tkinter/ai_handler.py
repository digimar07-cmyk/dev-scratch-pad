"""LASERFLIX v7.4.0 — AI Handler
Gerencia interações com Ollama e análise de projetos
"""

import time
import requests
import base64
import io
from PIL import Image, ImageStat
import logging

LOGGER = logging.getLogger("Laserflix")

# Configuração central dos modelos
OLLAMA_MODELS = {
    "text_quality": "qwen2.5:7b-instruct-q4_K_M",
    "text_fast": "qwen2.5:3b-instruct-q4_K_M",
    "vision": "moondream:latest",
    "embed": "nomic-embed-text:latest",
}

FAST_MODEL_THRESHOLD = 50

TIMEOUTS = {
    "text_quality": (5, 120),
    "text_fast": (5, 75),
    "vision": (5, 60),
    "embed": (5, 15),
}


class AIHandler:
    """Gerencia todas as operações de IA com Ollama"""
    
    def __init__(self, base_url="http://localhost:11434", retries=3):
        self.base_url = base_url
        self.retries = retries
        self.health_timeout = 4
        self.session = requests.Session()
        self._health_cache = {"ts": 0.0, "ok": None}
        self.active_models = dict(OLLAMA_MODELS)
        self.stop_analysis = False
    
    def is_available(self) -> bool:
        """Checa disponibilidade do Ollama com cache de 5s"""
        try:
            now = time.time()
            cached = self._health_cache
            if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < 5.0:
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
    
    def _model_name(self, role: str) -> str:
        """Retorna o nome do modelo configurado para o papel dado"""
        return self.active_models.get(role, OLLAMA_MODELS.get(role, ""))
    
    def _timeout(self, role: str):
        return TIMEOUTS.get(role, (5, 30))
    
    def generate_text(
        self,
        prompt: str,
        role: str = "text_quality",
        temperature: float = 0.7,
        num_predict: int = 350,
    ) -> str:
        """Gera texto com o modelo definido por role"""
        if self.stop_analysis:
            return ""
        
        if not self.is_available():
            LOGGER.warning("Ollama indisponível. Usando fallback.")
            return ""
        
        model = self._model_name(role)
        timeout = self._timeout(role)
        
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
            if self.stop_analysis:
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
                LOGGER.info("✅ [%s] gerou resposta (%d chars)", model, len(text))
                return text.strip()
            except Exception as e:
                last_err = e
                LOGGER.warning("Ollama falhou (tentativa %d/%d) [%s]: %s", attempt, self.retries, model, e)
                if attempt < self.retries:
                    time.sleep(2.0)
        
        if last_err:
            LOGGER.error("Ollama falhou definitivamente [%s]: %s", model, last_err, exc_info=True)
        return ""
    
    def image_quality_score(self, image_path: str) -> dict:
        """Avalia se a imagem tem qualidade suficiente para análise"""
        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                w, h = img_rgb.size
                box = (int(w*0.05), int(h*0.10), int(w*0.75), int(h*0.90))
                center = img_rgb.crop(box)
                
                gray = center.convert("L")
                stat_g = ImageStat.Stat(gray)
                brightness = stat_g.mean[0]
                
                hsv = center.convert("HSV")
                stat_s = ImageStat.Stat(hsv)
                saturation = stat_s.mean[1]
                
                white_pct = (brightness / 255.0) * max(0, 1.0 - (stat_g.stddev[0] / 80.0))
                white_pct_normalized = white_pct * 100
                
                use_vision = not (
                    brightness > 210 or
                    saturation < 25 or
                    white_pct_normalized > 50
                )
                
                LOGGER.info(
                    "📊 [quality] brilho=%.1f sat=%.1f fundo_branco~%.1f%% → vision=%s",
                    brightness, saturation, white_pct_normalized, use_vision
                )
                return {
                    "brightness": brightness,
                    "saturation": saturation,
                    "white_pct": white_pct_normalized,
                    "use_vision": use_vision,
                }
        except Exception as e:
            LOGGER.warning("Falha em image_quality_score: %s", e)
            return {"brightness": 0, "saturation": 100, "white_pct": 0, "use_vision": True}
    
    def describe_image(self, image_path: str) -> str:
        """Usa moondream para descrever o objeto central da imagem"""
        if not image_path or not self.is_available():
            return ""
        
        model = self._model_name("vision")
        timeout = self._timeout("vision")
        
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
                LOGGER.info("👁️ [moondream] %s", vision_text[:80])
                return vision_text
        except Exception as e:
            LOGGER.warning("Falha ao descrever imagem com moondream: %s", e)
        
        return ""
    
    def choose_text_role(self, batch_size: int = 1) -> str:
        """Escolhe modelo rápido para lotes grandes"""
        if batch_size > FAST_MODEL_THRESHOLD:
            return "text_fast"
        return "text_quality"
