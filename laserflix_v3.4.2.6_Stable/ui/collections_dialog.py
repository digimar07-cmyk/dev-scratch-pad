"""
ui/collections_dialog.py — Interface de gerenciamento de coleções.

Permite:
  - Criar novas coleções
  - Renomear coleções existentes
  - Deletar coleções
  - Visualizar projetos de uma coleção
  - Adicionar/remover projetos

Integração:
  - Chamado por main_window via botão na sidebar
  - Usa CollectionsManager para persistência
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os

from config.ui_constants import (
    BG_PRIMARY, BG_SECONDARY, BG_CARD,
    ACCENT_RED, ACCENT_GREEN, ACCENT_GOLD,
    FG_PRIMARY, FG_SECONDARY, FG_TERTIARY,
)
from utils.logging_setup import LOGGER


class CollectionsDialog(tk.Toplevel):
    """
    Dialog modal de gerenciamento de coleções.
    Uso:
        dlg = CollectionsDialog(parent, collections_manager, database)
        parent.wait_window(dlg)
    """

    def __init__(self, parent, collections_manager, database):
        super().__init__(parent)
        self.collections_mgr = collections_manager
        self.database = database
        self.logger = LOGGER

        self.title("📁 Gerenciar Coleções")
        self.configure(bg=BG_PRIMARY)
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.bind("<Escape>", lambda e: self.destroy())

        self._build_ui()
        self._refresh_collections_list()
        self._center(parent)

    # -------------------------------------------------------------------------
    # BUILD UI
    # -------------------------------------------------------------------------

    def _build_ui(self):
        PAD = 24

        # Título
        tk.Label(
            self, text="📁  Coleções",
            font=("Arial", 20, "bold"),
            bg=BG_PRIMARY, fg=ACCENT_RED,
        ).pack(anchor="w", padx=PAD, pady=(20, 4))
        tk.Label(
            self, text="Organize projetos em coleções temáticas. Um projeto pode estar em múltiplas coleções.",
            font=("Arial", 10),
            bg=BG_PRIMARY, fg=FG_TERTIARY,
        ).pack(anchor="w", padx=PAD, pady=(0, 16))

        tk.Frame(self, bg="#2A2A2A", height=1).pack(fill="x", padx=PAD)

        # ── Conteúdo Principal ──
        content = tk.Frame(self, bg=BG_PRIMARY)
        content.pack(fill="both", expand=True, padx=PAD, pady=16)

        # Painel esquerdo: Lista de coleções
        left_panel = tk.Frame(content, bg=BG_PRIMARY)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 12))

        tk.Label(
            left_panel, text="🎯  Suas Coleções",
            font=("Arial", 12, "bold"),
            bg=BG_PRIMARY, fg=ACCENT_GOLD,
            anchor="w",
        ).pack(anchor="w", pady=(0, 8))

        # Listbox com scroll
        list_frame = tk.Frame(left_panel, bg=BG_CARD)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=BG_CARD, troughcolor=BG_SECONDARY)
        scrollbar.pack(side="right", fill="y")

        self.collections_listbox = tk.Listbox(
            list_frame,
            bg=BG_CARD,
            fg=FG_PRIMARY,
            font=("Arial", 11),
            selectbackground=ACCENT_RED,
            selectforeground=FG_PRIMARY,
            relief="flat",
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self.collections_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.collections_listbox.yview)

        self.collections_listbox.bind("<<ListboxSelect>>", self._on_collection_select)

        # Botões de ação
        btn_frame = tk.Frame(left_panel, bg=BG_PRIMARY)
        btn_frame.pack(fill="x", pady=(8, 0))

        tk.Button(
            btn_frame, text="➕  Nova",
            command=self._create_collection,
            bg=ACCENT_GREEN, fg=FG_PRIMARY, font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", padx=12, pady=6,
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btn_frame, text="✏️  Renomear",
            command=self._rename_collection,
            bg="#444444", fg=FG_PRIMARY, font=("Arial", 10),
            relief="flat", cursor="hand2", padx=12, pady=6,
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btn_frame, text="🗑️  Deletar",
            command=self._delete_collection,
            bg=ACCENT_RED, fg=FG_PRIMARY, font=("Arial", 10),
            relief="flat", cursor="hand2", padx=12, pady=6,
        ).pack(side="left")

        # Painel direito: Projetos da coleção selecionada
        right_panel = tk.Frame(content, bg=BG_PRIMARY)
        right_panel.pack(side="right", fill="both", expand=True)

        self.projects_label = tk.Label(
            right_panel, text="📂  Projetos (selecione uma coleção)",
            font=("Arial", 12, "bold"),
            bg=BG_PRIMARY, fg=ACCENT_GOLD,
            anchor="w",
        )
        self.projects_label.pack(anchor="w", pady=(0, 8))

        # Listbox de projetos
        projects_list_frame = tk.Frame(right_panel, bg=BG_CARD)
        projects_list_frame.pack(fill="both", expand=True)

        projects_scrollbar = tk.Scrollbar(projects_list_frame, bg=BG_CARD, troughcolor=BG_SECONDARY)
        projects_scrollbar.pack(side="right", fill="y")

        self.projects_listbox = tk.Listbox(
            projects_list_frame,
            bg=BG_CARD,
            fg=FG_PRIMARY,
            font=("Arial", 10),
            selectbackground=ACCENT_RED,
            selectforeground=FG_PRIMARY,
            relief="flat",
            highlightthickness=0,
            yscrollcommand=projects_scrollbar.set,
        )
        self.projects_listbox.pack(side="left", fill="both", expand=True)
        projects_scrollbar.config(command=self.projects_listbox.yview)

        # Botão de remover projeto
        tk.Button(
            right_panel, text="➖  Remover Projeto",
            command=self._remove_project_from_collection,
            bg=ACCENT_RED, fg=FG_PRIMARY, font=("Arial", 10),
            relief="flat", cursor="hand2", padx=12, pady=6,
        ).pack(pady=(8, 0))

        tk.Frame(self, bg="#2A2A2A", height=1).pack(fill="x", padx=PAD)

        # ── Rodapé ──
        footer = tk.Frame(self, bg=BG_PRIMARY)
        footer.pack(fill="x", padx=PAD, pady=16)

        stats = self.collections_mgr.get_stats()
        self.stats_label = tk.Label(
            footer,
            text=f"📊  {stats['total_collections']} coleções | "
                 f"{stats['unique_projects']} projetos únicos | "
                 f"{stats['total_entries']} referências totais",
            font=("Arial", 10),
            bg=BG_PRIMARY, fg=FG_TERTIARY,
            anchor="w",
        )
        self.stats_label.pack(side="left")

        tk.Button(
            footer, text="✖  Fechar",
            command=self.destroy,
            bg=BG_CARD, fg=FG_TERTIARY, font=("Arial", 10),
            relief="flat", cursor="hand2", padx=14, pady=10,
        ).pack(side="right")

    # -------------------------------------------------------------------------
    # REFRESH
    # -------------------------------------------------------------------------

    def _refresh_collections_list(self):
        """Atualiza lista de coleções."""
        self.collections_listbox.delete(0, tk.END)
        
        collections = self.collections_mgr.get_all_collections()
        for name in collections:
            size = self.collections_mgr.get_collection_size(name)
            self.collections_listbox.insert(tk.END, f"{name}  ({size})")

        # Atualiza stats
        stats = self.collections_mgr.get_stats()
        self.stats_label.config(
            text=f"📊  {stats['total_collections']} coleções | "
                 f"{stats['unique_projects']} projetos únicos | "
                 f"{stats['total_entries']} referências totais"
        )

    def _on_collection_select(self, event):
        """Callback quando coleção é selecionada."""
        selection = self.collections_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        raw_text = self.collections_listbox.get(idx)
        # Extrai nome (remove contador "  (N)")
        name = raw_text.split("  (")[0]

        self._load_projects(name)

    def _load_projects(self, collection_name):
        """Carrega projetos da coleção selecionada."""
        self.current_collection = collection_name
        self.projects_label.config(text=f"📂  {collection_name}")

        self.projects_listbox.delete(0, tk.END)
        paths = self.collections_mgr.get_projects(collection_name)

        for path in paths:
            # Mostra nome do projeto ao invés do path completo
            project_name = self.database.get(path, {}).get("name", os.path.basename(path))
            self.projects_listbox.insert(tk.END, project_name)

        # Guarda mapeamento para remoção
        self.project_paths = paths

    # -------------------------------------------------------------------------
    # AÇÕES
    # -------------------------------------------------------------------------

    def _create_collection(self):
        """Cria nova coleção."""
        name = simpledialog.askstring(
            "Nova Coleção",
            "Nome da coleção:",
            parent=self,
        )

        if not name:
            return

        name = name.strip()
        if not name:
            messagebox.showwarning("⚠️ Inválido", "Nome não pode ser vazio.", parent=self)
            return

        success = self.collections_mgr.create_collection(name)
        if success:
            messagebox.showinfo("✨ Criada", f"Coleção '{name}' criada com sucesso!", parent=self)
            self._refresh_collections_list()
        else:
            messagebox.showwarning("⚠️ Erro", f"Coleção '{name}' já existe.", parent=self)

    def _rename_collection(self):
        """Renomeia coleção selecionada."""
        selection = self.collections_listbox.curselection()
        if not selection:
            messagebox.showinfo("ℹ️ Selecione", "Selecione uma coleção para renomear.", parent=self)
            return

        idx = selection[0]
        raw_text = self.collections_listbox.get(idx)
        old_name = raw_text.split("  (")[0]

        new_name = simpledialog.askstring(
            "Renomear Coleção",
            f"Novo nome para '{old_name}':",
            initialvalue=old_name,
            parent=self,
        )

        if not new_name:
            return

        new_name = new_name.strip()
        if not new_name:
            messagebox.showwarning("⚠️ Inválido", "Nome não pode ser vazio.", parent=self)
            return

        success = self.collections_mgr.rename_collection(old_name, new_name)
        if success:
            messagebox.showinfo("✏️ Renomeada", f"'{old_name}' → '{new_name}'", parent=self)
            self._refresh_collections_list()
        else:
            messagebox.showwarning("⚠️ Erro", "Não foi possível renomear.", parent=self)

    def _delete_collection(self):
        """Deleta coleção selecionada."""
        selection = self.collections_listbox.curselection()
        if not selection:
            messagebox.showinfo("ℹ️ Selecione", "Selecione uma coleção para deletar.", parent=self)
            return

        idx = selection[0]
        raw_text = self.collections_listbox.get(idx)
        name = raw_text.split("  (")[0]

        confirm = messagebox.askyesno(
            "🗑️ Confirmar",
            f"Deletar coleção '{name}'?\n\n"
            "Os projetos NÃO serão apagados, apenas a coleção.",
            parent=self,
        )

        if not confirm:
            return

        success = self.collections_mgr.delete_collection(name)
        if success:
            messagebox.showinfo("🗑️ Removida", f"Coleção '{name}' deletada.", parent=self)
            self._refresh_collections_list()
            self.projects_listbox.delete(0, tk.END)
            self.projects_label.config(text="📂  Projetos (selecione uma coleção)")
        else:
            messagebox.showwarning("⚠️ Erro", "Não foi possível deletar.", parent=self)

    def _remove_project_from_collection(self):
        """Remove projeto da coleção atual."""
        if not hasattr(self, "current_collection"):
            messagebox.showinfo("ℹ️ Selecione", "Selecione uma coleção primeiro.", parent=self)
            return

        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showinfo("ℹ️ Selecione", "Selecione um projeto para remover.", parent=self)
            return

        idx = selection[0]
        project_path = self.project_paths[idx]
        project_name = self.projects_listbox.get(idx)

        confirm = messagebox.askyesno(
            "➖ Confirmar",
            f"Remover '{project_name}' da coleção '{self.current_collection}'?\n\n"
            "O projeto NÃO será apagado, apenas removido desta coleção.",
            parent=self,
        )

        if not confirm:
            return

        success = self.collections_mgr.remove_project(self.current_collection, project_path)
        if success:
            self._load_projects(self.current_collection)
            self._refresh_collections_list()
        else:
            messagebox.showwarning("⚠️ Erro", "Não foi possível remover.", parent=self)

    # -------------------------------------------------------------------------
    # UTILITÁRIO
    # -------------------------------------------------------------------------

    def _center(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")
