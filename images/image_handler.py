"""Gerenciamento de imagens e thumbnails."""
import os
from collections import OrderedDict
from PIL import Image, ImageTk


def init_thumbnail_cache(app):
    app.thumbnail_cache = OrderedDict()
    app.thumbnail_cache_limit = 300


def _find_first_image_path(project_path):
    valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(valid_extensions):
                return os.path.join(project_path, item)
    except Exception:
        pass
    return None


def _load_thumbnail_photo(img_path):
    img = Image.open(img_path)
    img.thumbnail((220, 200), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def get_cover_image(app, project_path):
    img_path = _find_first_image_path(project_path)
    if not img_path:
        return None
    try:
        mtime = os.path.getmtime(img_path)
    except Exception:
        return None
    try:
        cached = app.thumbnail_cache.get(img_path)
        if cached:
            cached_mtime, cached_photo = cached
            if cached_mtime == mtime:
                app.thumbnail_cache.move_to_end(img_path)
                return cached_photo
        photo = _load_thumbnail_photo(img_path)
        app.thumbnail_cache[img_path] = (mtime, photo)
        app.thumbnail_cache.move_to_end(img_path)
        while len(app.thumbnail_cache) > app.thumbnail_cache_limit:
            app.thumbnail_cache.popitem(last=False)
        return photo
    except Exception:
        app.logger.exception("Erro ao gerar thumbnail de %s", img_path)
        return None


def get_hero_image(project_path):
    try:
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        for item in os.listdir(project_path):
            if item.lower().endswith(valid_extensions):
                img_path = os.path.join(project_path, item)
                img = Image.open(img_path)
                max_width = 800
                if img.width > max_width:
                    ratio = max_width / img.width
                    img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
    except Exception:
        pass
    return None


def get_all_project_images(project_path):
    valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
    images = []
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(valid_extensions):
                images.append(os.path.join(project_path, item))
    except Exception:
        pass
    return sorted(images)
