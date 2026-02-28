"""Análise de imagem com Moondream."""
import os
import base64
import io
from PIL import Image, ImageStat
from ollama.ollama_client import _ollama_is_available, _model_name, _timeout


def _image_quality_score(app, image_path: str) -> dict:
    """Avalia se a imagem tem qualidade suficiente para o Moondream analisar sem alucinar."""
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
                saturation < 25  or
                white_pct_normalized > 50
            )

            app.logger.info(
                "📊 [quality] brilho=%.1f sat=%.1f fundo_branco~%.1f%% → vision=%s",
                brightness, saturation, white_pct_normalized, use_vision
            )
            return {
                "brightness": brightness,
                "saturation": saturation,
                "white_pct":  white_pct_normalized,
                "use_vision": use_vision,
            }
    except Exception as e:
        app.logger.warning("Falha em _image_quality_score: %s", e)
        return {"brightness": 0, "saturation": 100, "white_pct": 0, "use_vision": True}


def _ollama_describe_image(app, image_path: str) -> str:
    """Usa moondream:latest para descrever o OBJETO CENTRAL da imagem."""
    if not image_path or not os.path.exists(image_path):
        return ""
    if not _ollama_is_available(app):
        return ""

    model   = _model_name(app, "vision")
    timeout = _timeout(app, "vision")
    try:
        with Image.open(image_path) as img:
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        payload = {
            "model":  model,
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
        resp = app.http_session.post(
            f"{app.ollama_base_url}/api/generate",
            json=payload,
            timeout=timeout,
        )
        if resp.status_code == 200:
            vision_text = (resp.json().get("response") or "").strip()
            app.logger.info("👁️ [moondream] %s", vision_text[:80])
            return vision_text
    except Exception as e:
        app.logger.warning("Falha ao descrever imagem com moondream: %s", e)
    return ""
