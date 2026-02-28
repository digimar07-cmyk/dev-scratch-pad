"""Gerenciamento de imagens e cache."""
import os
from functools import lru_cache
from PIL import Image, ImageTk

VALID_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")


def init_thumbnail_cache(app):
    """Inicializa cache de thumbnails (LRU automático via decorator)."""
    pass


@lru_cache(maxsize=300)
def get_cover_image(app, project_path):
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(VALID_IMAGE_EXTENSIONS):
                img_path = os.path.join(project_path, item)
                img = Image.open(img_path)
                img.thumbnail((200, 150))
                return ImageTk.PhotoImage(img)
    except Exception:
        pass
    return None


def get_hero_image(project_path):
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(VALID_IMAGE_EXTENSIONS):
                img_path = os.path.join(project_path, item)
                img = Image.open(img_path)
                img.thumbnail((1200, 450))
                return ImageTk.PhotoImage(img)
    except Exception:
        pass
    return None


def get_all_project_images(project_path):
    images = []
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(VALID_IMAGE_EXTENSIONS):
                images.append(os.path.join(project_path, item))
    except Exception:
        pass
    return images
