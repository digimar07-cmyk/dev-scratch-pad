"""Image Manager - thumbnails e cache"""
import os
from collections import OrderedDict
from PIL import Image, ImageTk
from core.logging_setup import LOGGER


class ImageManager:
    def __init__(self):
        self.logger = LOGGER
        self.thumbnail_cache = OrderedDict()
        self.thumbnail_cache_limit = 300

    def _find_first_image_path(self, project_path):
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            LOGGER.exception("Falha ao listar %s", project_path)
        return None

    def _load_thumbnail_photo(self, img_path):
        img = Image.open(img_path)
        img.thumbnail((220, 200), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def get_cover_image(self, project_path):
        img_path = self._find_first_image_path(project_path)
        if not img_path:
            return None
        try:
            mtime = os.path.getmtime(img_path)
        except Exception:
            return None
        try:
            cached = self.thumbnail_cache.get(img_path)
            if cached:
                cached_mtime, cached_photo = cached
                if cached_mtime == mtime:
                    self.thumbnail_cache.move_to_end(img_path)
                    return cached_photo
            photo = self._load_thumbnail_photo(img_path)
            self.thumbnail_cache[img_path] = (mtime, photo)
            self.thumbnail_cache.move_to_end(img_path)
            while len(self.thumbnail_cache) > self.thumbnail_cache_limit:
                self.thumbnail_cache.popitem(last=False)
            return photo
        except Exception:
            LOGGER.exception("Erro ao gerar thumbnail de %s", img_path)
            return None

    def get_hero_image(self, project_path):
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
            LOGGER.exception("Falha ao carregar hero image de %s", project_path)
        return None

    def get_all_project_images(self, project_path):
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        images = []
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    images.append(os.path.join(project_path, item))
        except Exception:
            LOGGER.exception("Falha ao listar imagens de %s", project_path)
        return sorted(images)
