"""
LASERFLIX — Vision Analyzer
Moondream + filtro de qualidade de imagem
"""

import os
import base64
import io
import logging
from PIL import Image, ImageStat

LOGGER = logging.getLogger("Laserflix")


class VisionAnalyzer:
    """Análise visual com Moondream + filtro de qualidade"""

    def __init__(self, client):
        self.client = client

    def quality_score(self, image_path: str) -> dict:
        """Avalia qualidade da imagem para visão"""
        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                w, h = img_rgb.size
                box = (int(w * 0.05), int(h * 0.10), int(w * 0.75), int(h * 0.90))
                center = img_rgb.crop(box)
                gray = center.convert("L")
                stat_g = ImageStat.Stat(gray)
                brightness = stat_g.mean[0]
                hsv = center.convert("HSV")
                stat_s = ImageStat.Stat(hsv)
                saturation = stat_s.mean[1]
                white_pct = (brightness / 255.0) * max(0, 1.0 - (stat_g.stddev[0] / 80.0)) * 100
                use_vision = not (brightness > 210 or saturation < 25 or white_pct > 50)
                LOGGER.info(f"📊 brilho={brightness:.1f} sat={saturation:.1f} branco~{white_pct:.1f}% → vision={use_vision}")
                return {"brightness": brightness, "saturation": saturation, "white_pct": white_pct, "use_vision": use_vision}
        except Exception as e:
            LOGGER.warning(f"Falha em quality_score: {e}")
            return {"brightness": 0, "saturation": 100, "white_pct": 0, "use_vision": True}

    def describe_image(self, image_path: str, model: str) -> str:
        """Descreve objeto central com Moondream"""
        if not image_path or not os.path.exists(image_path):
            return ""
        if not self.client.check_health():
            return ""
        try:
            with Image.open(image_path) as img:
                img.thumbnail((512, 512), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            payload = {
                "model": model,
                "prompt": "Look only at the main laser-cut wooden object in the center. Ignore background, toys, watermarks. Describe ONLY the central object: shape, theme, style. One short sentence.",
                "images": [img_b64],
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 60},
            }
            resp = self.client.session.post(f"{self.client.base_url}/api/generate", json=payload, timeout=(5, 60))
            if resp.status_code == 200:
                vision_text = (resp.json().get("response") or "").strip()
                LOGGER.info(f"👁️ [moondream] {vision_text[:80]}")
                return vision_text
        except Exception as e:
            LOGGER.warning(f"Falha ao descrever imagem: {e}")
        return ""
