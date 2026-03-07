"""
recursive_scanner.py — Escaneamento recursivo inteligente de produtos.

FUNCIONALIDADES:
  1. Modo PURO: Detecta apenas pastas com folder.jpg (controle total)
  2. Modo HÍBRIDO: folder.jpg + fallback inteligente (mais flexível)
  3. Geração de ID único baseado em hash do caminho relativo
  4. Detecção de subpastas técnicas (cdr, svg, jpg, imagens, vetores)
  5. Validação de arquivos de projeto válidos
"""

import os
import hashlib
from typing import List, Dict, Set
from utils.logging_setup import LOGGER


# Extensões válidas de arquivos de projeto
VALID_EXTENSIONS = {
    '.svg', '.pdf', '.dxf', '.ai', '.cdr', '.eps',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp'
}

# Subpastas técnicas que NÃO são produtos
TECHNICAL_SUBFOLDERS = {
    'cdr', 'svg', 'jpg', 'jpeg', 'png', 'pdf', 'dxf',
    'imagens', 'images', 'vetores', 'vectors',
    'backup', 'temp', 'cache', '.git', '__pycache__'
}


class RecursiveScanner:
    """
    Escaneador recursivo de produtos com detecção inteligente.

    Suporta dois modos:
    - PURO: Apenas pastas com folder.jpg (rígido, controle total)
    - HÍBRIDO: folder.jpg + fallback inteligente (flexível, pega mais)
    """

    def __init__(self):
        self.logger = LOGGER
        self.found_products = []
        self.skipped_folders = []
        self.stats = {
            'total_scanned': 0,
            'products_found': 0,
            'with_folder_jpg': 0,
            'via_fallback': 0,
            'technical_skipped': 0
        }

    def scan_folders_pure(self, base_path: str) -> List[Dict]:
        self.logger.info("[SCAN PURO] Iniciando em: %s", base_path)
        self._reset_stats()
        base_path = os.path.abspath(base_path)
        if not os.path.exists(base_path):
            self.logger.error("Pasta base não existe: %s", base_path)
            return []
        self._scan_recursive(base_path, base_path, mode='pure')
        self.logger.info(
            "[SCAN PURO] Concluído: %d produtos, %d pastas escaneadas",
            self.stats['products_found'], self.stats['total_scanned']
        )
        return self.found_products

    def scan_folders_hybrid(self, base_path: str) -> List[Dict]:
        self.logger.info("[SCAN HÍBRIDO] Iniciando em: %s", base_path)
        self._reset_stats()
        base_path = os.path.abspath(base_path)
        if not os.path.exists(base_path):
            self.logger.error("Pasta base não existe: %s", base_path)
            return []
        self._scan_recursive(base_path, base_path, mode='hybrid')
        self.logger.info(
            "[SCAN HÍBRIDO] Concluído: %d produtos (%d folder.jpg, %d fallback)",
            self.stats['products_found'],
            self.stats['with_folder_jpg'],
            self.stats['via_fallback']
        )
        return self.found_products

    def generate_unique_id(self, product_path: str, base_path: str) -> str:
        try:
            relative = os.path.relpath(product_path, base_path)
            normalized = relative.lower().replace('\\', '/')
            return hashlib.md5(normalized.encode('utf-8')).hexdigest()
        except Exception as e:
            self.logger.error("Erro ao gerar ID único: %s", e)
            return hashlib.md5(product_path.encode('utf-8')).hexdigest()

    def get_stats(self) -> Dict:
        return self.stats.copy()

    def _reset_stats(self):
        self.found_products = []
        self.skipped_folders = []
        self.stats = {
            'total_scanned': 0,
            'products_found': 0,
            'with_folder_jpg': 0,
            'via_fallback': 0,
            'technical_skipped': 0
        }

    def _scan_recursive(self, current_path: str, base_path: str, mode: str):
        try:
            try:
                items = os.listdir(current_path)
            except PermissionError:
                self.logger.warning("Sem permissão: %s", current_path)
                return

            files = []
            subdirs = []
            for item in items:
                item_path = os.path.join(current_path, item)
                if os.path.isfile(item_path):
                    files.append(item)
                elif os.path.isdir(item_path):
                    subdirs.append(item)

            self.stats['total_scanned'] += 1

            folder_name = os.path.basename(current_path).lower()
            if self._is_technical_subfolder(folder_name):
                self.stats['technical_skipped'] += 1
                return

            is_product = False
            detection_method = None
            has_folder_jpg = 'folder.jpg' in [f.lower() for f in files]

            if has_folder_jpg:
                is_product = True
                detection_method = 'folder_jpg'
                self.stats['with_folder_jpg'] += 1
            elif mode == 'hybrid':
                if self._has_project_files(files):
                    is_product = True
                    detection_method = 'fallback'
                    self.stats['via_fallback'] += 1

            if is_product:
                self.found_products.append({
                    'path': current_path,
                    'name': os.path.basename(current_path),
                    'unique_id': self.generate_unique_id(current_path, base_path),
                    'has_folder_jpg': has_folder_jpg,
                    'detection_method': detection_method
                })
                self.stats['products_found'] += 1
                return

            for subdir in subdirs:
                self._scan_recursive(os.path.join(current_path, subdir), base_path, mode)

        except Exception as e:
            self.logger.error("Erro ao escanear %s: %s", current_path, e)

    def _is_technical_subfolder(self, folder_name: str) -> bool:
        return folder_name in TECHNICAL_SUBFOLDERS

    def _has_project_files(self, files: List[str]) -> bool:
        for file in files:
            ext = os.path.splitext(file.lower())[1]
            if ext in VALID_EXTENSIONS:
                return True
        return False
