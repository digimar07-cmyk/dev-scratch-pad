"""
ui/managers/modal_generator.py — Gerenciador de geração de descrição em modal.

REFACTOR-FASE-1.2.2: Extraído de main_window.py

Responsabilidades:
- Gerenciar processo de geração de descrição IA em thread
- Atualizar UI do modal durante geração
- Reabrir modal com descrição gerada
"""
import threading
from typing import Any, Callable
from utils.logging_setup import LOGGER


class ModalGenerator:
    """Gerencia geração de descrição IA em modal."""
    
    def __init__(
        self,
        text_generator: Any,
        database: dict,
        db_manager: Any
    ):
        self.text_generator = text_generator
        self.database = database
        self.db_manager = db_manager
        self.logger = LOGGER
    
    def generate_description(
        self,
        path: str,
        desc_lbl: Any,
        gen_btn: Any,
        modal: Any,
        on_complete: Callable[[str], None]
    ) -> None:
        """
        Gera descrição IA para projeto em background.
        
        Args:
            path: Caminho do projeto
            desc_lbl: Label do modal para atualizar status
            gen_btn: Botão de gerar para desabilitar/habilitar
            modal: Modal para fechar/reabrir
            on_complete: Callback chamado após geração (recebe path)
        """
        # Atualizar UI - estado "gerando"
        gen_btn.config(state="disabled", text="⏳ Gerando...")
        desc_lbl.config(text="⏳ Gerando descrição...", fg="#555555")
        modal.update()
        
        def _run():
            try:
                # Gerar descrição usando IA
                desc = self.text_generator.generate_description(
                    path, 
                    self.database[path]
                )
                
                # Salvar no banco
                self.database[path]["ai_description"] = desc
                self.db_manager.save_database()
                
                # Fechar modal e reabrir com descrição nova
                modal.after(0, modal.destroy)
                modal.after(50, lambda: on_complete(path))
                
            except Exception as e:
                self.logger.error("Erro ao gerar descrição: %s", e)
                
                # Atualizar UI - estado de erro
                modal.after(0, lambda: desc_lbl.config(
                    text="❌ Erro ao gerar descrição", 
                    fg="#EF5350"
                ))
                modal.after(0, lambda: gen_btn.config(
                    state="normal", 
                    text="🤖 Gerar"
                ))
        
        # Executar em thread separada
        threading.Thread(target=_run, daemon=True).start()
