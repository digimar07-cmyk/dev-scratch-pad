"""
recursive_import_integration.py — Orquestra o fluxo completo de importação.
Tkinter puro — sem customtkinter.

FLUXO (todos os modos):
  1. ImportModeDialog  → usuário escolhe modo e pasta
  2. Scan              → escaneia produtos
  3. DuplicateDetector → detecta duplicatas por nome (CONTRA DATABASE EXISTENTE!)
  4. DuplicateResolutionDialog → usuário resolve (se houver)
  5. ImportPreviewDialog → usuário confirma
  6. Import Loop       → importa em thread separada
  7. AUTO-ANALYSIS     → SEQUENCIAL: categorias/tags → descrições

Modos:
  'hybrid'  — recursivo, folder.jpg + fallback
  'pure'    — recursivo, apenas folder.jpg
  'simple'  — 1 nível, qualquer subpasta direta (com dedup)

HOT-10: FIX duplicatas entre métodos
  - Agora compara produtos escaneados com database existente
  - Evita duplicatas ao usar métodos diferentes na mesma pasta
  - Hybrid → Pure → Simple na mesma pasta = SEM duplicatas!

HOT-10b: FIX dialog duplicatas
  - Adiciona normalized_name e name no formato esperado pelo dialog

FEATURE: Análise automática SEQUENCIAL pós-importação
  - Após importação bem-sucedida, pergunta se quer analisar
  - Se sim, executa SEQUENCIALMENTE:
    1. Categorias + Tags (analysis_manager)
    2. Descrições (text_generator)
  - Apenas para produtos recém-importados

USO:
    from ui.recursive_import_integration import RecursiveImportManager
    manager = RecursiveImportManager(
        parent, database, 
        analysis_manager=analysis_manager,  # ← Necessário
        text_generator=text_generator,      # ← Necessário
        on_complete=callback
    )
    manager.start_import()
"""

import os
import threading
from datetime import datetime
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
    Gerenciador unificado de importação — recursiva (hybrid/pure) e simples.
    Todos os modos passam pelo mesmo pipeline de dedup + preview.
    
    HOT-10: Detecta duplicatas comparando com database existente!
    FEATURE: Análise SEQUENCIAL pós-importação (categorias+tags → descrições)
    """

    def __init__(
        self,
        parent,
        database,
        project_scanner=None,
        text_generator=None,
        analysis_manager=None,
        on_complete: Optional[Callable] = None,
    ):
        self.parent          = parent
        self.database        = database
        self.project_scanner = project_scanner
        self.text_generator  = text_generator
        self.analysis_manager = analysis_manager
        self.on_complete     = on_complete
        self.logger          = LOGGER
        self.scanner         = RecursiveScanner()
        self.duplicate_detector = DuplicateDetector()
        self.import_thread   = None
        self.imported_paths  = []

    # ================================================================
    # MÉTODO PRINCIPAL
    # ================================================================

    def start_import(self):
        """Inicia o fluxo unificado de importação."""
        self.logger.info("=== INICIANDO IMPORTAÇÃO ===")
        self.imported_paths = []  # Reset

        # 1 ─ Modo + pasta
        result = show_import_mode_dialog(self.parent)
        if not result:
            self.logger.info("Importação cancelada (dialog modo)")
            return
        mode, base_path = result
        self.logger.info("Modo: %s | Pasta: %s", mode, base_path)

        # 2 ─ Scan (os três modos)
        all_products = self._scan_products(base_path, mode)
        if not all_products:
            messagebox.showwarning(
                "⚠️ Nenhum Produto",
                "Nenhum produto encontrado na pasta selecionada.",
                parent=self.parent,
            )
            return
        self.logger.info("Encontrados: %d produtos", len(all_products))

        # ═══════════════════════════════════════════════════════════════
        # 3 ─ DUPLICATAS (HOT-10: COMPARA COM DATABASE EXISTENTE!)
        # ═══════════════════════════════════════════════════════════════
        
        # 3.1 - Cria dict dos produtos escaneados
        scanned_db = {p["path"]: {"name": p["name"]} for p in all_products}
        
        # 3.2 - COMBINA com database existente (CRUCIAL!)
        combined_db = {**self.database, **scanned_db}
        
        # 3.3 - Detecta duplicatas no conjunto COMPLETO
        duplicates_result = self.duplicate_detector.find_duplicates(combined_db)
        
        self.logger.info(
            f"🔍 Verificação: {len(self.database)} existentes + "
            f"{len(scanned_db)} escaneados = {len(combined_db)} total"
        )
        
        # 3.4 - Filtra apenas duplicatas envolvendo produtos NOVOS
        duplicates = []
        scanned_paths = set(scanned_db.keys())
        existing_paths = set(self.database.keys())
        
        if duplicates_result:
            for norm_name, paths in duplicates_result.items():
                if len(paths) < 2:
                    continue
                
                # Separa existentes vs novos
                existing_in_group = [p for p in paths if p in existing_paths]
                new_in_group = [p for p in paths if p in scanned_paths]
                
                # Só reporta se tem NOVOS duplicando algo
                if new_in_group:
                    # Se tem existente, compara novo vs existente
                    if existing_in_group:
                        for new_path in new_in_group:
                            duplicates.append({
                                "normalized_name": norm_name,
                                "name": os.path.basename(new_path),
                                "existing": {
                                    "path": existing_in_group[0],
                                    "name": os.path.basename(existing_in_group[0]),
                                },
                                "new": {
                                    "path": new_path,
                                    "name": os.path.basename(new_path),
                                },
                            })
                    # Se não tem existente, compara novos entre si
                    elif len(new_in_group) >= 2:
                        first_new = new_in_group[0]
                        for other_new in new_in_group[1:]:
                            duplicates.append({
                                "normalized_name": norm_name,
                                "name": os.path.basename(first_new),
                                "existing": {
                                    "path": first_new,
                                    "name": os.path.basename(first_new),
                                },
                                "new": {
                                    "path": other_new,
                                    "name": os.path.basename(other_new),
                                },
                            })
        
        products_to_import = all_products

        if duplicates:
            self.logger.warning("⚠️ %d duplicatas encontradas (contra database existente)", len(duplicates))
            
            # Mostra dialog de resolução
            choices = show_duplicate_resolution(self.parent, duplicates)
            if choices is None:
                self.logger.info("Importação cancelada (resolução duplicatas)")
                return
            
            # HOT-10b: Processa escolhas por normalized_name
            skip_paths = set()
            for dup in duplicates:
                norm_name = dup["normalized_name"]
                choice = choices.get(norm_name, "skip")
                
                if choice == "skip":  # Pula novo
                    skip_paths.add(dup["new"]["path"])
                elif choice == "replace":  # Remove existente + importa novo
                    existing_path = dup["existing"]["path"]
                    if existing_path in self.database:
                        self.logger.info(f"🔄 Substituindo: {os.path.basename(existing_path)}")
                        self.database.pop(existing_path)
                # merge: importa ambos (não adiciona a skip_paths)
            
            products_to_import = [
                p for p in all_products
                if p["path"] not in skip_paths
            ]
            self.logger.info(f"Após resolução: {len(products_to_import)} produtos")
        else:
            self.logger.info("✅ Nenhuma duplicata encontrada")

        if not products_to_import:
            messagebox.showinfo("ℹ️ Importação",
                                "Nenhum produto para importar!",
                                parent=self.parent)
            return

        # 4 ─ Existentes por path exato (redundante mas mantido por segurança)
        new_products, existing_products = self._check_existing(products_to_import)
        self.logger.info("Novos: %d | Existentes: %d",
                         len(new_products), len(existing_products))

        # 5 ─ Preview
        preview = ImportPreviewDialog(
            self.parent, new_products, existing_products, mode
        )
        self.parent.wait_window(preview)
        if not preview.get_confirmed():
            self.logger.info("Importação cancelada (preview)")
            return

        # 6 ─ Importar
        if new_products:
            self._import_products(new_products)
        else:
            messagebox.showinfo("ℹ️ Importação",
                                "Nenhum produto novo para importar!",
                                parent=self.parent)

    # ================================================================
    # SCAN — os três modos
    # ================================================================

    def _scan_products(self, base_path: str, mode: str) -> List[Dict]:
        """Escaneia e retorna lista de produtos no formato padronizado."""
        try:
            if mode == "pure":
                products = self.scanner.scan_folders_pure(base_path)

            elif mode == "hybrid":
                products = self.scanner.scan_folders_hybrid(base_path)

            else:  # 'simple' ─ 1 nível, qualquer subpasta direta
                products = self._scan_simple(base_path)

            stats = self.scanner.get_stats()
            self.logger.info(
                "Scan '%s': %d produtos | pastas escaneadas: %d",
                mode, len(products), stats.get("total_scanned", len(products)),
            )
            return products

        except Exception as e:
            self.logger.error("Erro ao escanear: %s", e, exc_info=True)
            messagebox.showerror("❌ Erro", f"Erro ao escanear:\n{e}",
                                 parent=self.parent)
            return []

    def _scan_simple(self, base_path: str) -> List[Dict]:
        """
        Modo Simples: lista apenas as subpastas diretas de base_path.
        Retorna a mesma estrutura de dict que o RecursiveScanner.
        """
        products = []
        try:
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if not os.path.isdir(item_path):
                    continue
                products.append({
                    "path":             item_path,
                    "name":             item,
                    "unique_id":        self.scanner.generate_unique_id(
                                            item_path, base_path),
                    "has_folder_jpg":   os.path.isfile(
                                            os.path.join(item_path, "folder.jpg")),
                    "detection_method": "simple",
                })
            self.logger.info("[SCAN SIMPLES] %d pastas encontradas em %s",
                             len(products), base_path)
        except PermissionError:
            self.logger.warning("Sem permissão para acessar: %s", base_path)
        except Exception as e:
            self.logger.error("Erro no scan simples: %s", e, exc_info=True)
        return products

    # ================================================================
    # HELPERS
    # ================================================================

    def _check_existing(self, products: List[Dict]):
        """Separa produtos novos dos que já existem no database (por path)."""
        try:
            existing_paths = set(self.database.keys())
            new, existing  = [], []
            for p in products:
                (existing if p["path"] in existing_paths else new).append(p)
            return new, existing
        except Exception as e:
            self.logger.error("Erro ao verificar existentes: %s", e, exc_info=True)
            return products, []

    def _import_products(self, products: List[Dict]):
        self.logger.info("Iniciando import de %d produtos em thread", len(products))
        self.import_thread = threading.Thread(
            target=self._import_loop,
            args=(products,),
            daemon=True,
        )
        self.import_thread.start()

    def _import_loop(self, products: List[Dict]):
        total   = len(products)
        success = 0
        failed  = 0

        for i, product in enumerate(products, 1):
            try:
                path = product["path"]
                if path in self.database:
                    self.logger.debug("Pulando (já existe por path): %s", product["name"])
                    failed += 1
                    continue

                # Detecta origin pelo nome da pasta-pai (compatível com + Pastas)
                origin = self._detect_origin(path, product.get("detection_method", ""))

                self.database[path] = {
                    "path":         path,
                    "name":         product["name"],
                    "origin":       origin,
                    "cover_image":  product.get("cover_image", ""),
                    "images":       product.get("images", []),
                    "analyzed":     False,
                    "favorite":     False,
                    "done":         False,
                    "good":         False,
                    "bad":          False,
                    "categories":   [],
                    "tags":         [],
                    "added_date":   datetime.now().isoformat(),
                }
                success += 1
                self.imported_paths.append(path)
                self.logger.debug("[%d/%d] Importado: %s", i, total, product["name"])

            except Exception as e:
                self.logger.error("Erro ao importar %s: %s",
                                  product.get("name"), e)
                failed += 1

        self.logger.info("Import concluído: %d ok | %d falha", success, failed)

        # ══════════════════════════════════════════════════════════════════
        # ANÁLISE AUTOMÁTICA SEQUENCIAL: categorias+tags → descrições
        # ══════════════════════════════════════════════════════════════════
        if success > 0 and self.analysis_manager and self.text_generator:
            try:
                self.parent.after(0, lambda: self._ask_auto_analysis(success))
            except RuntimeError:
                # Main loop encerrado
                self.logger.warning("⚠️ Main loop encerrado, pulando auto-analysis")
        else:
            # Callback normal sem análise
            if self.on_complete:
                self.parent.after(0, self.on_complete)
            
            self.parent.after(0, lambda: messagebox.showinfo(
                "✅ Importação Concluída",
                f"Importados: {success} produto(s)\nPulados/erros: {failed}",
                parent=self.parent,
            ))

    def _ask_auto_analysis(self, success_count: int):
        """
        Pergunta se quer analisar automaticamente.
        Se sim, executa SEQUENCIALMENTE:
          1. Categorias + Tags (analysis_manager)
          2. Descrições (text_generator)
        """
        response = messagebox.askyesno(
            "🤖 Análise Automática",
            f"✅ {success_count} produto(s) importado(s)!\n\n"
            f"🤔 Deseja analisar AGORA?\n\n"
            f"SEQUENCIAL:\n"
            f"1️⃣ Categorias + Tags (IA)\n"
            f"2️⃣ Descrições (IA)\n\n"
            f"Isso pode levar alguns minutos.",
            parent=self.parent,
        )
        
        if response:
            self.logger.info("🤖 Iniciando análise SEQUENCIAL de %d produtos", len(self.imported_paths))
            self._run_sequential_analysis()
        else:
            self.logger.info("⏭️ Usuário optou por NÃO analisar")
            if self.on_complete:
                self.on_complete()

    def _run_sequential_analysis(self):
        """
        Executa análise SEQUENCIAL:
        1. Categorias + Tags para todos
        2. Aguarda conclusão
        3. Descrições para todos
        """
        def _worker():
            try:
                # ETAPA 1: Categorias + Tags
                self.logger.info("📊 ETAPA 1/2: Analisando categorias e tags...")
                
                # Aguarda análise de categorias/tags terminar
                self._wait_for_analysis_manager()
                
                # ETAPA 2: Descrições
                self.logger.info("📝 ETAPA 2/2: Gerando descrições...")
                self._generate_descriptions_batch()
                
                self.logger.info("✅ Análise sequencial concluída!")
                
            except Exception as e:
                self.logger.error("Erro na análise sequencial: %s", e, exc_info=True)
            finally:
                # Callback final
                if self.on_complete:
                    self.parent.after(0, self.on_complete)
        
        threading.Thread(target=_worker, daemon=True).start()
        
        # Inicia análise de categorias/tags (não bloqueia)
        self.analysis_manager.analyze_batch(self.imported_paths, self.database)
    
    def _wait_for_analysis_manager(self):
        """Aguarda analysis_manager terminar."""
        import time
        while self.analysis_manager.is_analyzing:
            time.sleep(0.5)
        self.logger.info("✅ Categorias e tags finalizadas")
    
    def _generate_descriptions_batch(self):
        """Gera descrições para os produtos recém-importados."""
        done = 0
        for path in self.imported_paths:
            if not os.path.isdir(path):
                continue
            try:
                desc = self.text_generator.generate_description(path, self.database[path])
                self.database[path]["ai_description"] = desc
                done += 1
                self.logger.debug(f"📝 [{done}/{len(self.imported_paths)}] {os.path.basename(path)}")
            except Exception as e:
                self.logger.error(f"Erro ao gerar descrição para {path}: {e}")
        
        self.logger.info(f"📝 {done} descrições geradas")

    def _detect_origin(self, product_path: str, detection_method: str) -> str:
        """
        Detecta a origem pelo nome da pasta-pai — mesma lógica do ProjectScanner.
        Modo recursivo usa 'Importação Recursiva' como fallback.
        """
        try:
            parent_folder = os.path.basename(os.path.dirname(product_path))
            upper = parent_folder.upper()
            if "CREATIVE" in upper or "FABRICA" in upper:
                return "Creative Fabrica"
            elif "ETSY" in upper:
                return "Etsy"
            elif detection_method == "simple":
                return parent_folder or "Importação Simples"
            else:
                return parent_folder or "Importação Recursiva"
        except Exception:
            return "Desconhecido"
