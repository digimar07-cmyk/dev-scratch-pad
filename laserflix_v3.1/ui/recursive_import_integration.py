"""
recursive_import_integration.py — Integração completa de importação recursiva.

ORQUESTRA O FLUXO:
  1. ImportModeDialog → Usuário escolhe modo e pasta
  2. RecursiveScanner → Escaneia produtos
  3. Database Check → Detecta novos vs existentes
  4. ImportPreviewDialog → Usuário confirma
  5. Import Loop → Importa com barra de progresso

USO NO MAIN_WINDOW:
    from ui.recursive_import_integration import RecursiveImportManager
    
    manager = RecursiveImportManager(self)
    manager.start_import()
"""

import threading
from typing import List, Dict, Callable
from utils.logging_setup import LOGGER
from utils.recursive_scanner import RecursiveScanner
from ui.import_mode_dialog import ImportModeDialog
from ui.import_preview_dialog import ImportPreviewDialog


class RecursiveImportManager:
    """
    Gerenciador de importação recursiva.
    
    Orquestra todo o fluxo de importação em massa.
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
        3. Verificar existentes no DB
        4. Preview com resumo
        5. Importar com progresso
        """
        self.logger.info("=== INICIANDO IMPORTAÇÃO RECURSIVA ===")
        
        # PASSO 1: Dialog de modo
        mode_dialog = ImportModeDialog(self.parent)
        self.parent.wait_window(mode_dialog)
        
        result = mode_dialog.get_result()
        if not result:
            self.logger.info("Importação cancelada pelo usuário (dialog)")
            return
        
        mode = result['mode']
        base_path = result['base_path']
        
        self.logger.info(f"Modo: {mode}, Pasta: {base_path}")
        
        # PASSO 2: Escanear produtos
        self._show_status("🔍 Escaneando produtos...")
        all_products = self._scan_products(base_path, mode)
        
        if not all_products:
            self._show_warning("⚠️ Nenhum produto encontrado!")
            self.logger.warning(f"Nenhum produto encontrado em {base_path}")
            return
        
        self.logger.info(f"Encontrados {len(all_products)} produtos")
        
        # PASSO 3: Verificar existentes
        self._show_status("📊 Verificando produtos existentes...")
        new_products, existing_products = self._check_existing(all_products)
        
        self.logger.info(
            f"Novos: {len(new_products)}, Existentes: {len(existing_products)}"
        )
        
        # PASSO 4: Preview
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
        
        # PASSO 5: Importar
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
        Verifica quais produtos já existem no banco.
        
        Args:
            products: Lista de produtos escaneados
        
        Returns:
            (new_products, existing_products)
        """
        try:
            # Busca todos IDs existentes no banco
            existing_ids = set()
            
            # Query: SELECT unique_id FROM projects
            cursor = self.database.conn.cursor()
            cursor.execute("SELECT unique_id FROM projects WHERE unique_id IS NOT NULL")
            rows = cursor.fetchall()
            
            for row in rows:
                if row[0]:  # Se unique_id não é NULL
                    existing_ids.add(row[0])
            
            self.logger.debug(f"IDs existentes no banco: {len(existing_ids)}")
            
            # Separa novos vs existentes
            new = []
            existing = []
            
            for product in products:
                uid = product['unique_id']
                if uid in existing_ids:
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
        
        # TODO: Criar progress dialog
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
                progress = (i / total) * 100
                self._update_progress(i, total, product['name'])
                
                # Escaneia projeto
                project_data = self.project_scanner.scan_project(
                    product['path'],
                    include_structure=True
                )
                
                if not project_data:
                    self.logger.warning(f"Falha ao escanear: {product['path']}")
                    failed += 1
                    continue
                
                # Adiciona unique_id
                project_data['unique_id'] = product['unique_id']
                
                # Gera análise (IA ou fallback)
                analysis = self.text_generator.generate_analysis(
                    product['path'],
                    project_data
                )
                
                if analysis:
                    project_data.update(analysis)
                
                # Salva no banco
                self.database.add_project(project_data)
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
    # UI HELPERS (implementar com CTkMessagebox ou similar)
    # ================================================================

    def _show_status(self, message: str):
        """Mostra mensagem de status."""
        self.logger.info(f"[STATUS] {message}")
        # TODO: Implementar com CTkMessagebox ou status bar

    def _update_progress(self, current: int, total: int, name: str):
        """Atualiza barra de progresso."""
        self.logger.debug(f"[{current}/{total}] {name}")
        # TODO: Implementar progress dialog

    def _show_warning(self, message: str):
        """Mostra aviso."""
        self.logger.warning(message)
        # TODO: CTkMessagebox

    def _show_error(self, message: str):
        """Mostra erro."""
        self.logger.error(message)
        # TODO: CTkMessagebox

    def _show_info(self, message: str):
        """Mostra informação."""
        self.logger.info(message)
        # TODO: CTkMessagebox

    def _show_complete(self, success: int, failed: int):
        """Mostra resumo final."""
        message = (
            f"✅ Importação Concluída!\n\n"
            f"Sucesso: {success}\n"
            f"Falhas: {failed}"
        )
        self.logger.info(message)
        # TODO: CTkMessagebox


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
        text="🗂️ Importar Pasta Recursiva",
        command=on_import_recursive,
        height=40
    )
    
    # TODO: Posicionar corretamente (pack, grid, place)
    # btn.pack(pady=10)
    
    return btn
