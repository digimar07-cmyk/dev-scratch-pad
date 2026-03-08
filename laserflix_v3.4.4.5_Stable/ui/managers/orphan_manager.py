"""
ui/managers/orphan_manager.py — Gerenciador de limpeza de projetos órfãos.

REFACTOR-FASE-1.3: Extraído de main_window.py

Responsabilidades:
- Detectar projetos órfãos (sem pasta no disco)
- Interface de confirmação com usuário
- Limpar órfãos do banco e coleções
"""
import os
from tkinter import messagebox
from typing import Dict, Any, Callable

class OrphanManager:
    """Gerencia limpeza de projetos órfãos do banco de dados."""
    
    def __init__(
        self,
        database: Dict[str, Any],
        db_manager: Any,
        collections_manager: Any,
        on_refresh: Callable[[], None],
        on_status_update: Callable[[str], None]
    ):
        self.database = database
        self.db_manager = db_manager
        self.collections_manager = collections_manager
        self.on_refresh = on_refresh
        self.on_status_update = on_status_update
    
    def clean_orphans(self) -> None:
        """Detecta e remove projetos órfãos (sem pasta no disco)."""
        orphans = [p for p in self.database.keys() if not os.path.isdir(p)]
        
        if not orphans:
            messagebox.showinfo(
                "✅ Banco limpo",
                "Nenhum órfão encontrado!\n\nTodos os projetos têm pastas válidas."
            )
            return
        
        # Montar mensagem de confirmação
        msg = f"Encontrei {len(orphans)} projeto(s) órfão(s):\n\n"
        msg += "\n".join(f"- {os.path.basename(p)}" for p in orphans[:10])
        if len(orphans) > 10:
            msg += f"\n... e mais {len(orphans) - 10}"
        msg += "\n\nEsses projetos não existem mais no disco.\nRemover do banco?"
        
        # Primeira confirmação
        if not messagebox.askyesno("🧹 Limpar órfãos", msg, icon="warning"):
            return
        
        # Segunda confirmação (segurança)
        if not messagebox.askyesno(
            "⚠️ Confirmar remoção",
            f"Segunda confirmação.\n\n{len(orphans)} projeto(s) serão removidos "
            f"PERMANENTEMENTE do banco.\n\nTem certeza?",
            icon="warning"
        ):
            return
        
        # Remover órfãos
        for path in orphans:
            self.database.pop(path, None)
        
        # Salvar e atualizar UI
        self.db_manager.save_database()
        self.collections_manager.clean_orphan_projects(set(self.database.keys()))
        self.on_refresh()
        self.on_status_update(f"🧹 {len(orphans)} órfão(s) removido(s) do banco.")
        
        # Mensagem de sucesso
        messagebox.showinfo(
            "✅ Limpeza concluída",
            f"{len(orphans)} projeto(s) órfão(s) removido(s) do banco.\n\n"
            f"Banco agora está sincronizado com o disco."
        )
