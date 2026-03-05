"""
recursive_import_integration.py — Orquestra o fluxo completo de importação recursiva.
Tkinter puro — sem customtkinter.

FLUXO:
  1. ImportModeDialog → usuário escolhe modo e pasta
  2. RecursiveScanner → escaneia produtos
  3. DuplicateDetector → detecta duplicatas por nome
  4. DuplicateResolutionDialog → usuário resolve duplicatas
  5. ImportPreviewDialog → usuário confirma
  6. Import Loop → importa em thread separada

USO:
    from ui.recursive_import_integration import RecursiveImportManager
    manager = RecursiveImportManager(parent, database, on_complete=callback)
    manager.start_import()
"""

import threading
from typing import List, Dict, Callable, Optional
from tkinter import messagebox
from utils.logging_setup import LOGGER
from utils.recursive_scanner import RecursiveScanner
from utils.duplicate_detector import DuplicateDetector
from ui.import_mode_dialog import show_import_mode_dialog
from ui.import_preview_dialog import ImportPreviewDialog
from ui.duplicate_resolution_dialog import show_duplicate_resolution


class RecursiveImportManager:
    """
    Gerenciador de importação recursiva.
    Orquestra todo o fluxo com detecção de duplicatas.
    """

    def __init__(
        self,
        parent,
        database,
        project_scanner=None,
        text_generator=None,
        on_complete: Optional[Callable] = None
    ):
        self.parent         = parent
        self.database       = database
        self.project_scanner = project_scanner
        self.text_generator = text_generator
        self.on_complete    = on_complete
        self.logger         = LOGGER
        self.scanner        = RecursiveScanner()
        self.duplicate_detector = DuplicateDetector(database)
        self.import_thread  = None

    # ================================================================
    # MÉTODO PRINCIPAL
    # ================================================================

    def start_import(self):
        """Inicia processo completo de importação recursiva."""
        self.logger.info("=== INICIANDO IMPORTAÇÃO RECURSIVA ===")

        # Passo 1: Escolher modo e pasta
        result = show_import_mode_dialog(self.parent)
        if not result:
            self.logger.info("Importação cancelada (dialog modo)")
            return
        mode, base_path = result
        self.logger.info("Modo: %s | Pasta: %s", mode, base_path)

        # Passo 2: Escanear
        all_products = self._scan_products(base_path, mode)
        if not all_products:
            messagebox.showwarning("⚠️ Nenhum Produto",
                                   "Nenhum produto encontrado na pasta selecionada.",
                                   parent=self.parent)
            return
        self.logger.info("Encontrados: %d produtos", len(all_products))

        # Passo 3: Detectar duplicatas
        duplicates = self.duplicate_detector.find_duplicates(all_products)
        products_to_import = all_products

        if duplicates:
            self.logger.warning("%d duplicatas encontradas", len(duplicates))
            choices = show_duplicate_resolution(self.parent, duplicates)
            if choices is None:
                self.logger.info("Importação cancelada (resolução duplicatas)")
                return
            to_import, _ = self.duplicate_detector.resolve_duplicates(
                duplicates, user_choices=choices
            )
            dup_paths      = {d['new']['path'] for d in duplicates}
            to_import_paths = {p['path'] for p in to_import}
            products_to_import = [
                p for p in all_products
                if p['path'] not in dup_paths or p['path'] in to_import_paths
            ]
            self.logger.info("Após resolução: %d produtos", len(products_to_import))

        if not products_to_import:
            messagebox.showinfo("ℹ️ Importação",
                                "Nenhum produto para importar!",
                                parent=self.parent)
            return

        # Passo 4: Verificar existentes por path
        new_products, existing_products = self._check_existing(products_to_import)
        self.logger.info("Novos: %d | Existentes: %d",
                         len(new_products), len(existing_products))

        # Passo 5: Preview
        preview = ImportPreviewDialog(
            self.parent, new_products, existing_products, mode
        )
        self.parent.wait_window(preview)
        if not preview.get_confirmed():
            self.logger.info("Importação cancelada (preview)")
            return

        # Passo 6: Importar
        if new_products:
            self._import_products(new_products)
        else:
            messagebox.showinfo("ℹ️ Importação",
                                "Nenhum produto novo para importar!",
                                parent=self.parent)

    # ================================================================
    # MÉTODOS INTERNOS
    # ================================================================

    def _scan_products(self, base_path: str, mode: str) -> List[Dict]:
        try:
            if mode == 'pure':
                products = self.scanner.scan_folders_pure(base_path)
            else:
                products = self.scanner.scan_folders_hybrid(base_path)
            stats = self.scanner.get_stats()
            self.logger.info("Scan: %d produtos, %d pastas",
                             stats['products_found'], stats['total_scanned'])
            return products
        except Exception as e:
            self.logger.error("Erro ao escanear: %s", e, exc_info=True)
            messagebox.showerror("❌ Erro", f"Erro ao escanear:\n{e}",
                                 parent=self.parent)
            return []

    def _check_existing(self, products: List[Dict]):
        try:
            existing_paths = set(self.database.keys())
            new, existing = [], []
            for p in products:
                (existing if p['path'] in existing_paths else new).append(p)
            return new, existing
        except Exception as e:
            self.logger.error("Erro ao verificar existentes: %s", e, exc_info=True)
            return products, []

    def _import_products(self, products: List[Dict]):
        self.logger.info("Iniciando importação de %d produtos", len(products))
        self.import_thread = threading.Thread(
            target=self._import_loop,
            args=(products,),
            daemon=True
        )
        self.import_thread.start()

    def _import_loop(self, products: List[Dict]):
        total = len(products)
        success = 0
        failed  = 0

        for i, product in enumerate(products, 1):
            try:
                path = product['path']
                if path in self.database:
                    self.logger.debug("Pulando (já existe): %s", product['name'])
                    failed += 1
                    continue

                self.database[path] = {
                    'path':        path,
                    'name':        product['name'],
                    'origin':      'Importação Recursiva',
                    'cover_image': product.get('cover_image', ''),
                    'images':      product.get('images', []),
                    'analyzed':    False,
                    'favorite':    False,
                    'done':        False,
                    'good':        False,
                    'bad':         False,
                    'categories':  [],
                    'tags':        []
                }
                success += 1
                self.logger.debug("[%d/%d] Importado: %s", i, total, product['name'])

            except Exception as e:
                self.logger.error("Erro ao importar %s: %s", product.get('name'), e)
                failed += 1

        self.logger.info("Importação concluída: %d ok, %d falha", success, failed)

        # Callback na thread principal
        if self.on_complete:
            self.parent.after(0, self.on_complete)

        self.parent.after(0, lambda: messagebox.showinfo(
            "✅ Importação Concluída",
            f"Importados: {success} produtos\nFalhas: {failed}",
            parent=self.parent
        ))
