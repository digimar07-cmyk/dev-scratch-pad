#!/usr/bin/env python3
"""
duplicate_resolution_dialog.py — Dialog para resolver duplicatas.

MOSTRA DUPLICATAS:
  - Lista produtos duplicados encontrados
  - Mostra paths das pastas
  - Permite escolher ação para cada um:
    * Skip: Ignora novo, mantém existente
    * Replace: Substitui existente por novo
    * Merge: Mescla informações

USO:
    from ui.duplicate_resolution_dialog import show_duplicate_resolution
    
    choices = show_duplicate_resolution(parent, duplicates)
    if choices:
        # choices = {normalized_name: 'skip'|'replace'|'merge'}
"""

import customtkinter as ctk
from typing import List, Dict, Optional
from utils.logging_setup import LOGGER


class DuplicateResolutionDialog(ctk.CTkToplevel):
    """
    Dialog para resolver produtos duplicados.
    
    Mostra lista de duplicatas e permite ao usuário escolher
    como resolver cada uma.
    """

    def __init__(self, parent, duplicates: List[Dict]):
        super().__init__(parent)
        
        self.title("⚠️ Produtos Duplicados Encontrados")
        self.geometry("900x700")
        self.resizable(True, True)
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"900x700+{x}+{y}")
        
        # Dados
        self.duplicates = duplicates
        self.choices = {}  # {normalized_name: 'skip'|'replace'|'merge'}
        self.result = None
        
        # Widgets para cada duplicata
        self.choice_vars = {}  # {normalized_name: StringVar}
        
        # Constrói UI
        self._build_ui()
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        LOGGER.info(f"DuplicateResolutionDialog aberto com {len(duplicates)} duplicatas")

    def _build_ui(self):
        """Constrói interface."""
        
        # Container principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ============================================================
        # HEADER
        # ============================================================
        header = ctk.CTkLabel(
            main_frame,
            text=f"⚠️ {len(self.duplicates)} Produtos Duplicados Encontrados",
            font=("Segoe UI", 20, "bold"),
            text_color="#FFA500"
        )
        header.pack(pady=(10, 5))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Escolha como resolver cada duplicata:",
            font=("Segoe UI", 12),
            text_color="gray70"
        )
        subtitle.pack(pady=(0, 20))
        
        # ============================================================
        # LISTA DE DUPLICATAS (SCROLLABLE)
        # ============================================================
        list_frame = ctk.CTkScrollableFrame(
            main_frame,
            label_text="Duplicatas:"
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        for i, dup in enumerate(self.duplicates):
            self._create_duplicate_item(list_frame, dup, i)
        
        # ============================================================
        # AÇÕES EM MASSA
        # ============================================================
        bulk_frame = ctk.CTkFrame(main_frame)
        bulk_frame.pack(fill="x", pady=(0, 20))
        
        bulk_label = ctk.CTkLabel(
            bulk_frame,
            text="Ações em Massa:",
            font=("Segoe UI", 11, "bold")
        )
        bulk_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            bulk_frame,
            text="Skip Todos",
            command=lambda: self._set_all('skip'),
            width=120,
            height=35,
            fg_color="gray50",
            hover_color="gray60"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            bulk_frame,
            text="Replace Todos",
            command=lambda: self._set_all('replace'),
            width=120,
            height=35,
            fg_color="#FF6B6B",
            hover_color="#FF5252"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            bulk_frame,
            text="Merge Todos",
            command=lambda: self._set_all('merge'),
            width=120,
            height=35,
            fg_color="#4ECDC4",
            hover_color="#45B7AF"
        ).pack(side="left", padx=5)
        
        # ============================================================
        # BOTÕES
        # ============================================================
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar Importação",
            command=self._cancel,
            fg_color="gray40",
            hover_color="gray50",
            width=180,
            height=45
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            button_frame,
            text="✅ Confirmar e Continuar",
            command=self._confirm,
            width=220,
            height=45,
            font=("Segoe UI", 13, "bold")
        ).pack(side="right", padx=(0, 10))

    def _create_duplicate_item(self, parent, dup: Dict, index: int):
        """Cria widget para uma duplicata."""
        
        norm_name = dup['normalized_name']
        
        # Frame da duplicata
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(fill="x", padx=10, pady=8)
        
        # ============================================================
        # INFO DO PRODUTO
        # ============================================================
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Nome
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"📦 {dup['name']}",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Paths
        existing_path = dup['existing'].get('path', 'Desconhecido')
        new_path = dup['new'].get('path', 'Desconhecido')
        
        path_text = (
            f"❌ Existente: {existing_path}\n"
            f"✅ Novo: {new_path}"
        )
        
        paths_label = ctk.CTkLabel(
            info_frame,
            text=path_text,
            font=("Segoe UI", 9),
            text_color="gray70",
            anchor="w",
            justify="left"
        )
        paths_label.pack(anchor="w", pady=(5, 0))
        
        # ============================================================
        # OPÇÕES
        # ============================================================
        options_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        options_frame.pack(side="right", padx=10, pady=10)
        
        # StringVar para escolha
        choice_var = ctk.StringVar(value="skip")  # Padrão: Skip
        self.choice_vars[norm_name] = choice_var
        
        # Radio buttons
        ctk.CTkRadioButton(
            options_frame,
            text="Skip (Manter)",
            variable=choice_var,
            value="skip",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkRadioButton(
            options_frame,
            text="Replace (Substituir)",
            variable=choice_var,
            value="replace",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkRadioButton(
            options_frame,
            text="Merge (Mesclar)",
            variable=choice_var,
            value="merge",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=2)

    def _set_all(self, choice: str):
        """Define mesma escolha para todas as duplicatas."""
        for var in self.choice_vars.values():
            var.set(choice)
        
        LOGGER.info(f"Ação em massa: {choice} para {len(self.choice_vars)} duplicatas")

    def _confirm(self):
        """Confirma escolhas."""
        # Coleta escolhas
        for norm_name, var in self.choice_vars.items():
            self.choices[norm_name] = var.get()
        
        self.result = self.choices
        
        # Resumo
        skip_count = sum(1 for c in self.choices.values() if c == 'skip')
        replace_count = sum(1 for c in self.choices.values() if c == 'replace')
        merge_count = sum(1 for c in self.choices.values() if c == 'merge')
        
        LOGGER.info(
            f"Resolução de duplicatas confirmada: "
            f"{skip_count} skip, {replace_count} replace, {merge_count} merge"
        )
        
        self.destroy()

    def _cancel(self):
        """Cancela importação."""
        self.result = None
        LOGGER.info("Resolução de duplicatas cancelada")
        self.destroy()

    def get_result(self):
        """Retorna escolhas do usuário."""
        return self.result


# ================================================================
# FUNÇÃO HELPER
# ================================================================

def show_duplicate_resolution(parent, duplicates: List[Dict]) -> Optional[Dict]:
    """
    Mostra dialog de resolução de duplicatas.
    
    Args:
        parent: Janela pai
        duplicates: Lista de duplicatas (de DuplicateDetector.find_duplicates)
    
    Returns:
        Dict {normalized_name: 'skip'|'replace'|'merge'} ou None se cancelado
    
    Exemplo:
        duplicates = detector.find_duplicates(new_products)
        if duplicates:
            choices = show_duplicate_resolution(main_window, duplicates)
            if choices:
                to_import, to_skip = detector.resolve_duplicates(duplicates, user_choices=choices)
    """
    if not duplicates:
        return {}
    
    dialog = DuplicateResolutionDialog(parent, duplicates)
    parent.wait_window(dialog) if parent else dialog.wait_window()
    return dialog.get_result()


# ================================================================
# TESTE STANDALONE
# ================================================================
if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Dados de teste
    test_duplicates = [
        {
            'name': 'Dragão 3D',
            'normalized_name': 'dragao-3d',
            'existing': {'path': '/pasta1/dragao', 'name': 'Dragão 3D'},
            'new': {'path': '/pasta2/dragao', 'name': 'dragao 3d'},
            'conflict_type': 'database'
        },
        {
            'name': 'Leão Tribal',
            'normalized_name': 'leao-tribal',
            'existing': {'path': '/pasta1/leao', 'name': 'Leão Tribal'},
            'new': {'path': '/pasta3/leao', 'name': 'LEAO TRIBAL'},
            'conflict_type': 'database'
        }
    ]
    
    root = ctk.CTk()
    root.withdraw()
    
    result = show_duplicate_resolution(root, test_duplicates)
    
    if result:
        print("✅ Escolhas:")
        for name, choice in result.items():
            print(f"  {name}: {choice}")
    else:
        print("❌ Cancelado")
    
    root.destroy()
