"""
SelectionController - Gerencia seleção múltipla de projetos.

Responsabilidades:
- Ativar/desativar modo seleção
- Selecionar/deselecionar projetos
- Selecionar todos
- Obter projetos selecionados
- Operações em lote (deletar, analisar)
"""

import logging
from typing import List, Set, Callable, Optional


class SelectionController:
    """
    Controller responsável por seleção múltipla.
    
    Atributos:
        selection_mode: Modo seleção ativo/inativo
        selected_paths: Conjunto de paths selecionados
        on_mode_change: Callback de mudança de modo
        on_selection_change: Callback de mudança de seleção
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Estado
        self.selection_mode = False
        self.selected_paths: Set[str] = set()
        
        # Callbacks
        self.on_mode_change: Optional[Callable] = None
        self.on_selection_change: Optional[Callable] = None
        
        self.logger.info("✨ SelectionController inicializado")
    
    # Métodos serão migrados na Fase 5
