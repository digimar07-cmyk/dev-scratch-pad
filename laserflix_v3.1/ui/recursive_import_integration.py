"""
recursive_import_integration.py — Integração completa de importação recursiva.

ORQUESTRA O FLUXO:
  1. ImportModeDialog → Usuário escolhe modo e pasta
  2. RecursiveScanner → Escaneia produtos
  3. DuplicateDetector → Detecta produtos com mesmo nome
  4. DuplicateResolutionDialog → Usuário resolve duplicatas
  5. ImportPreviewDialog → Usuário confirma
  6. Import Loop → Importa com barra de progresso

USO NO MAIN_WINDOW:
    from ui.recursive_import_integration import RecursiveImportManager
    
    manager = RecursiveImportManager(self)
    manager.start_import()
"""

import threading
from typing import List, Dict, Callable
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
    
    Orquestra todo o fluxo de importação em massa com detecção de duplicatas.
    """

    def __init__(
        self,
        parent,
        database,
        project_scanner,
        text_generator,
        on_complete: Callable = None
    ):
        """
        Args:
            parent: Janela principal (para dialogs)
            database: Instância do Database
            project_scanner: Instância do ProjectScanner
            text_generator: Instância do TextGenerator (para análise)
            on_complete: Callback após importação (opcional)
        """
        self.parent = parent
        self.database = database
        self.project_scanner = project_scanner
        self.text_generator = text_generator
        self.on_complete = on_complete
        self.logger = LOGGER
        
        self.scanner = RecursiveScanner()
        self.duplicate_detector = DuplicateDetector(database)
        self.import_thread = None

    # ================================================================
    # MÉTODO PRINCIPAL
    # ================================================================

    def start_import(self):
        """
        Inicia processo de importação recursiva.
        
        Fluxo completo:
        1. Dialog para escolher modo e pasta
        2. Escanear produtos
        3. Detectar duplicatas por NOME
        4. Dialog para resolver duplicatas (se houver)
        5. Preview com resumo
        6. Importar com progresso
        """
        self.logger.info("=== INICIANDO IMPORTAÇÃO RECURSIVA ===")
        
        # PASSO 1: Dialog de modo
        result = show_import_mode_dialog(self.parent)
        
        if not result:
            self.logger.info("Importação cancelada pelo usuário (dialog)")
            return
        
        # Desempacota tupla (mode, base_path)
        mode, base_path = result
        
        self.logger.info(f"Modo: {mode}, Pasta: {base_path}")
        
        # PASSO 2: Escanear produtos
        self._show_status("🔍 Escaneando produtos...")
        all_products = self._scan_products(base_path, mode)
        
        if not all_products:
            self._show_warning("⚠️ Nenhum produto encontrado!")
            self.logger.warning(f"Nenhum produto encontrado em {base_path}")
            return
        
        self.logger.info(f"Encontrados {len(all_products)} produtos")
        
        # PASSO 3: Detectar duplicatas por NOME
        self._show_status("🔍 Verificando duplicatas...")
        duplicates = self.duplicate_detector.find_duplicates(all_products)
        
        products_to_import = all_products
        
        if duplicates:
            self.logger.warning(f"Encontradas {len(duplicates)} duplicatas")
            
            # PASSO 4: Dialog de resolução de duplicatas
            choices = show_duplicate_resolution(self.parent, duplicates)
            
            if not choices:
                # Usuário cancelou
                self.logger.info("Importação cancelada (duplicatas)")
                return
            
            # Resolve duplicatas
            to_import, to_skip = self.duplicate_detector.resolve_duplicates(
                duplicates,
                user_choices=choices
            )
            
            # Remove duplicatas que serão puladas
            dup_paths = {d['new']['path'] for d in duplicates}
            to_import_paths = {p['path'] for p in to_import}
            
            products_to_import = [
                p for p in all_products
                if p['path'] not in dup_paths or p['path'] in to_import_paths
            ]
            
            self.logger.info(
                f"Após resolução: {len(products_to_import)} produtos para importar"
            )
        
        if not products_to_import:
            self._show_info("ℹ️ Nenhum produto para importar!")
            return
        
        # PASSO 5: Verificar paths existentes
        self._show_status("📋 Verificando produtos existentes...")
        new_products, existing_products = self._check_existing(products_to_import)
        
        self.logger.info(
            f"Novos: {len(new_products)}, Existentes: {len(existing_products)}"
        )
        
        # PASSO 6: Preview
        preview_dialog = ImportPreviewDialog(
            self.parent,
            new_products,
            existing_products,
            mode
        )
        self.parent.wait_window(preview_dialog)
        
        if not preview_dialog.get_confirmed():
            self.logger.info("Importação cancelada pelo usuário (preview)")
            return
        
        # PASSO 7: Importar
        if new_products:
            self._import_products(new_products)
        else:
            self._show_info("ℹ️ Nenhum produto novo para importar!")

    # ================================================================
    # MÉTODOS INTERNOS
    # ================================================================

    def _scan_products(self, base_path: str, mode: str) -> List[Dict]:
        """
        Escaneia produtos usando RecursiveScanner.
        
        Args:
            base_path: Pasta base
            mode: 'pure' ou 'hybrid'
        
        Returns:
            Lista de produtos encontrados
        """
        try:
            if mode == 'pure':
                products = self.scanner.scan_folders_pure(base_path)
            else:
                products = self.scanner.scan_folders_hybrid(base_path)
            
            stats = self.scanner.get_stats()
            self.logger.info(
                f"Scan completo: {stats['products_found']} produtos, "
                f"{stats['total_scanned']} pastas escaneadas"
            )
            
            return products
        
        except Exception as e:
            self.logger.error(f"Erro ao escanear: {e}", exc_info=True)
            self._show_error(f"Erro ao escanear: {e}")
            return []

    def _check_existing(self, products: List[Dict]) -> tuple:
        """
        Verifica quais produtos já existem no banco (por PATH).
        
        Args:
            products: Lista de produtos escaneados
        
        Returns:
            (new_products, existing_products)
        """
        try:
            # Para cada produto, verifica se path já existe no database
            existing_paths = set(self.database.keys())
            
            new = []
            existing = []
            
            for product in products:
                path = product['path']
                if path in existing_paths:
                    existing.append(product)
                else:
                    new.append(product)
            
            return new, existing
        
        except Exception as e:
            self.logger.error(f"Erro ao verificar existentes: {e}", exc_info=True)
            # Em caso de erro, assume todos como novos (mais seguro)
            return products, []

    def _import_products(self, products: List[Dict]):
        """
        Importa produtos com barra de progresso.
        
        Args:
            products: Lista de produtos para importar
        """
        total = len(products)
        self.logger.info(f"Iniciando importação de {total} produtos")
        
        self._show_status(f"📥 Importando {total} produtos...")
        
        # Importa em thread separada (não trava UI)
        self.import_thread = threading.Thread(
            target=self._import_loop,
            args=(products,),
            daemon=True
        )
        self.import_thread.start()

    def _import_loop(self, products: List[Dict]):
        """
        Loop de importação (roda em thread separada).
        
        Args:
            products: Lista de produtos para importar
        """
        total = len(products)
        success = 0
        failed = 0
        
        for i, product in enumerate(products, 1):
            try:
                # Atualiza progresso
                self._update_progress(i, total, product['name'])
                
                # Adiciona ao database
                project_path = product['path']
                
                # Verifica se já existe (segurança)
                if project_path in self.database:
                    self.logger.debug(f"Pulando (já existe): {product['name']}")
                    failed += 1
                    continue
                
                # Estrutura básica do projeto
                project_data = {
                    'path': project_path,
                    'name': product['name'],
                    'origin': 'Importação Recursiva',
                    'cover_image': product.get('cover_image', ''),
                    'images': product.get('images', []),
                    'analyzed': False,
                    'favorite': False,
                    'done': False,
                    'good': False,
                    'bad': False,
                    'categories': [],
                    'tags': []
                }
                
                # Adiciona ao banco
                self.database[project_path] = project_data
                success += 1
                
                self.logger.debug(f"[{i}/{total}] Importado: {product['name']}")
            
            except Exception as e:
                self.logger.error(
                    f"Erro ao importar {product['name']}: {e}",
                    exc_info=True
                )
                failed += 1
        
        # Finaliza
        self.logger.info(
            f"Importação concluída: {success} sucesso, {failed} falhas"
        )
        
        self._show_complete(success, failed)
        
        # Callback (se fornecido)
        if self.on_complete:
            self.on_complete(success, failed)

    # ================================================================
    # UI HELPERS
    # ================================================================

    def _show_status(self, message: str):
        """Mostra mensagem de status."""
        self.logger.info(f"[STATUS] {message}")
        # Atualiza status bar se existir
        if hasattr(self.parent, 'status_bar'):
            self.parent.status_bar.config(text=message)
            self.parent.root.update_idletasks()

    def _update_progress(self, current: int, total: int, name: str):
        """Atualiza barra de progresso."""
        pct = (current / total) * 100
        msg = f"📥 Importando: {name} ({current}/{total} - {pct:.1f}%)"
        self.logger.debug(msg)
        
        if hasattr(self.parent, 'status_bar'):
            self.parent.status_bar.config(text=msg)
            self.parent.root.update_idletasks()

    def _show_warning(self, message: str):
        """Mostra aviso."""
        self.logger.warning(message)
        messagebox.showwarning("⚠️ Aviso", message)

    def _show_error(self, message: str):
        """Mostra erro."""
        self.logger.error(message)
        messagebox.showerror("❌ Erro", message)

    def _show_info(self, message: str):
        """Mostra informação."""
        self.logger.info(message)
        messagebox.showinfo("ℹ️ Informação", message)

    def _show_complete(self, success: int, failed: int):
        """Mostra resumo final."""
        message = (
            f"✅ Importação Concluída!\n\n"
            f"Sucesso: {success}\n"
            f"Falhas: {failed}"
        )
        self.logger.info(message)
        messagebox.showinfo("🎉 Concluído", message)


# ================================================================
# FUNÇÃO DE INTEGRAÇÃO PARA MAIN_WINDOW
# ================================================================

def add_recursive_import_button(main_window):
    """
    Adiciona botão de importação recursiva no main_window.
    
    Uso:
        # No main_window.py, após criar botões:
        from ui.recursive_import_integration import add_recursive_import_button
        add_recursive_import_button(self)
    
    Args:
        main_window: Instância da janela principal
    """
    import customtkinter as ctk
    
    def on_import_recursive():
        """Handler do botão."""
        manager = RecursiveImportManager(
            parent=main_window,
            database=main_window.database,
            project_scanner=main_window.project_scanner,
            text_generator=main_window.text_generator,
            on_complete=lambda s, f: main_window.refresh_library()  # Atualiza biblioteca
        )
        manager.start_import()
    
    # Cria botão (ajustar posicionamento conforme layout do main_window)
    btn = ctk.CTkButton(
        main_window.sidebar_frame,  # Ajustar para frame correto
        text="🚀 Importação em Massa",
        command=on_import_recursive,
        height=40
    )
    
    # TODO: Posicionar corretamente (pack, grid, place)
    # btn.pack(pady=10)
    
    return btn
