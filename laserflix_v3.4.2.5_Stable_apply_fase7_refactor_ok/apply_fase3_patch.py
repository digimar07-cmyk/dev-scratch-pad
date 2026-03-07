#!/usr/bin/env python3
"""
apply_fase3_patch.py — Aplica modificações da Fase 3 no main_window.py
Autor: Claude Sonnet 4.5
Data: 2026-03-06

Uso:
    python apply_fase3_patch.py
"""

import re
import sys

def apply_fase3_patch():
    file_path = "laserflix_v3.4.1.1_Stable_antes do translate/ui/main_window.py"
    
    print("=" * 80)
    print("FASE 3: APLICANDO PATCH NO main_window.py")
    print("=" * 80)
    print()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo não encontrado: {file_path}")
        print("Execute este script na raiz do repositório!")
        sys.exit(1)
    
    original_lines = len(content.split('\n'))
    print(f"📄 Arquivo original: {original_lines} linhas")
    print()
    
    # OPERAÇÃO 1: Adicionar import AnalysisController
    print("🔧 [1/7] Adicionando import AnalysisController...")
    content = content.replace(
        "# FASE 2: Importa DisplayController\nfrom ui.controllers.display_controller import DisplayController",
        "# FASE 2: Importa DisplayController\nfrom ui.controllers.display_controller import DisplayController\n\n# FASE 3: Importa AnalysisController\nfrom ui.controllers.analysis_controller import AnalysisController"
    )
    
    # OPERAÇÃO 2: Remover _setup_analysis_callbacks()
    print("🔧 [2/7] Removendo _setup_analysis_callbacks()...")
    content = re.sub(
        r'\s+self\._setup_analysis_callbacks\(\)',
        '',
        content
    )
    
    # OPERAÇÃO 3: Adicionar instanciação AnalysisController
    print("🔧 [3/7] Adicionando instanciação AnalysisController...")
    insertion = """
        
        # FASE 3: AnalysisController gerencia análise IA + descrições
        self.analysis_ctrl = AnalysisController(
            analysis_manager=self.analysis_manager,
            text_generator=self.text_generator,
            db_manager=self.db_manager,
            ollama_client=self.ollama
        )
        # Conecta callbacks de UI
        self.analysis_ctrl.on_show_progress = self.show_progress_ui
        self.analysis_ctrl.on_hide_progress = self.hide_progress_ui
        self.analysis_ctrl.on_update_progress = self.update_progress
        self.analysis_ctrl.on_analysis_complete = lambda msg: self.status_bar.config(text=msg)
        self.analysis_ctrl.on_refresh_ui = lambda: (
            self._invalidate_cache(),
            self.display_projects(),
            self.sidebar.refresh(self.database, self.collections_manager)
        )
        self.analysis_ctrl.setup_callbacks()
"""
    content = content.replace(
        "        self.display_ctrl.on_display_update = self.display_projects",
        "        self.display_ctrl.on_display_update = self.display_projects" + insertion
    )
    
    # OPERAÇÃO 4: Deletar funções obsoletas
    print("🔧 [4/7] Deletando funções obsoletas...")
    
    # Deleta _setup_analysis_callbacks
    content = re.sub(
        r'    def _setup_analysis_callbacks\(self\) -> None:.*?(?=\n    def |\n    # =)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Deleta _on_analysis_complete
    content = re.sub(
        r'    def _on_analysis_complete\(self, done, skipped\) -> None:.*?(?=\n    def |\n    # =)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Deleta _on_analysis_error
    content = re.sub(
        r'    def _on_analysis_error\(self, error_msg\) -> None:.*?(?=\n    def |\n    # =)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Deleta _batch_generate_descriptions
    content = re.sub(
        r'    def _batch_generate_descriptions\(self, targets\) -> None:.*?(?=\n    def |\n    # =)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # OPERAÇÃO 5: Substituir corpo das funções delegadoras
    print("🔧 [5/7] Substituindo funções por delegadores...")
    
    # analyze_single_project
    content = re.sub(
        r'    def analyze_single_project\(self, path\) -> None:.*?(?=\n    def )',
        '    def analyze_single_project(self, path) -> None:\n        """FASE 3: Delega para AnalysisController."""\n        self.analysis_ctrl.analyze_single(path, self.database)\n\n',
        content,
        flags=re.DOTALL
    )
    
    # analyze_only_new
    content = re.sub(
        r'    def analyze_only_new\(self\) -> None:.*?(?=\n    def )',
        '    def analyze_only_new(self) -> None:\n        """FASE 3: Delega para AnalysisController."""\n        self.analysis_ctrl.analyze_only_new(self.database)\n\n',
        content,
        flags=re.DOTALL
    )
    
    # reanalyze_all
    content = re.sub(
        r'    def reanalyze_all\(self\) -> None:.*?(?=\n    def )',
        '    def reanalyze_all(self) -> None:\n        """FASE 3: Delega para AnalysisController."""\n        self.analysis_ctrl.reanalyze_all(self.database)\n\n',
        content,
        flags=re.DOTALL
    )
    
    # generate_descriptions_for_new
    content = re.sub(
        r'    def generate_descriptions_for_new\(self\) -> None:.*?(?=\n    def )',
        '    def generate_descriptions_for_new(self) -> None:\n        """FASE 3: Delega para AnalysisController."""\n        self.analysis_ctrl.generate_descriptions_for_new(self.database)\n\n',
        content,
        flags=re.DOTALL
    )
    
    # generate_descriptions_for_all
    content = re.sub(
        r'    def generate_descriptions_for_all\(self\) -> None:.*?(?=\n    def )',
        '    def generate_descriptions_for_all(self) -> None:\n        """FASE 3: Delega para AnalysisController."""\n        self.analysis_ctrl.generate_descriptions_for_all(self.database)\n\n',
        content,
        flags=re.DOTALL
    )
    
    # OPERAÇÃO 6: Atualizar strings
    print("🔧 [6/7] Atualizando strings...")
    content = content.replace(
        '"DisplayController ativo"',
        '"Display+Analysis Controllers"'
    )
    content = content.replace(
        'REFACTOR-FASE-2: DisplayController extraído (filtros/ordenação/paginação) ✅',
        'REFACTOR-FASE-2: DisplayController extraído (filtros/ordenação/paginação) ✅\nREFACTOR-FASE-3: AnalysisController extraído (análise IA + descrições) ✅'
    )
    
    # OPERAÇÃO 7: Salvar arquivo modificado
    print("🔧 [7/7] Salvando arquivo modificado...")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    final_lines = len(content.split('\n'))
    reduction = original_lines - final_lines
    
    print()
    print("=" * 80)
    print("✅ PATCH APLICADO COM SUCESSO!")
    print("=" * 80)
    print(f"Linhas antes:  {original_lines}")
    print(f"Linhas depois: {final_lines}")
    print(f"Redução:       {reduction} linhas ({(reduction/original_lines)*100:.1f}%)")
    print()
    print("PRÓXIMOS PASSOS:")
    print("1. Teste o aplicativo: python main.py")
    print("2. Commit: git add ui/main_window.py")
    print("3. Commit: git commit -m 'refactor(fase3): Integra AnalysisController em main_window'")
    print("4. Push: git push origin main")
    print("=" * 80)

if __name__ == "__main__":
    apply_fase3_patch()
