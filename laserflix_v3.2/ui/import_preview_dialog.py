"""
import_preview_dialog.py — Preview de produtos antes de importar.

Mostra:
  1. Quantos produtos NOVOS serão importados
  2. Quantos produtos JÁ EXISTEM (serão pulados)
  3. Lista de produtos com status
  4. Tempo estimado de importação
  5. Modo usado (Puro/Híbrido)

USO:
    dialog = ImportPreviewDialog(
        parent,
        new_products=[...],
        existing_products=[...],
        mode='hybrid'
    )
    
    if dialog.get_confirmed():
        # Prossegue com importação
"""

import customtkinter as ctk
from typing import List, Dict
from utils.logging_setup import LOGGER


class ImportPreviewDialog(ctk.CTkToplevel):
    """
    Dialog de preview antes de importar produtos.
    
    Mostra resumo e pede confirmação do usuário.
    """

    def __init__(
        self,
        parent,
        new_products: List[Dict],
        existing_products: List[Dict],
        mode: str = 'hybrid'
    ):
        super().__init__(parent)
        
        self.title("🔍 Preview de Importação")
        self.geometry("700x600")
        self.resizable(True, True)
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"700x600+{x}+{y}")
        
        # Dados
        self.new_products = new_products
        self.existing_products = existing_products
        self.mode = mode
        self.confirmed = False
        self.details_visible = False
        
        # Constrói interface
        self._build_ui()
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        LOGGER.info(
            f"Preview aberto: {len(new_products)} novos, "
            f"{len(existing_products)} existentes"
        )

    def _build_ui(self):
        """Constrói interface do dialog."""
        
        # Container principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ============================================================
        # HEADER
        # ============================================================
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📂 PRODUTOS ENCONTRADOS",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # Separador
        separator = ctk.CTkFrame(header_frame, height=2, fg_color="gray30")
        separator.pack(fill="x", padx=10)
        
        # ============================================================
        # RESUMO
        # ============================================================
        summary_frame = ctk.CTkFrame(main_frame)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        # Novos
        new_frame = ctk.CTkFrame(summary_frame)
        new_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        new_icon = ctk.CTkLabel(
            new_frame,
            text="✅",
            font=("Segoe UI", 32)
        )
        new_icon.pack(pady=(10, 5))
        
        new_count = ctk.CTkLabel(
            new_frame,
            text=str(len(self.new_products)),
            font=("Segoe UI", 28, "bold"),
            text_color="#4CAF50"
        )
        new_count.pack()
        
        new_label = ctk.CTkLabel(
            new_frame,
            text="produtos novos\n(serão importados)",
            font=("Segoe UI", 11),
            text_color="gray70"
        )
        new_label.pack(pady=(5, 10))
        
        # Existentes
        existing_frame = ctk.CTkFrame(summary_frame)
        existing_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        existing_icon = ctk.CTkLabel(
            existing_frame,
            text="⏭️",
            font=("Segoe UI", 32)
        )
        existing_icon.pack(pady=(10, 5))
        
        existing_count = ctk.CTkLabel(
            existing_frame,
            text=str(len(self.existing_products)),
            font=("Segoe UI", 28, "bold"),
            text_color="#FF9800"
        )
        existing_count.pack()
        
        existing_label = ctk.CTkLabel(
            existing_frame,
            text="já existem\n(serão pulados)",
            font=("Segoe UI", 11),
            text_color="gray70"
        )
        existing_label.pack(pady=(5, 10))
        
        # ============================================================
        # INFO ADICIONAL
        # ============================================================
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        # Modo usado
        mode_text = "Híbrido" if self.mode == "hybrid" else "Puro"
        mode_emoji = "🔄" if self.mode == "hybrid" else "🔒"
        
        mode_label = ctk.CTkLabel(
            info_frame,
            text=f"{mode_emoji} Modo usado: {mode_text}",
            font=("Segoe UI", 11)
        )
        mode_label.pack(side="left", padx=10, pady=10)
        
        # Tempo estimado
        total = len(self.new_products)
        estimated_time = self._estimate_time(total)
        
        time_label = ctk.CTkLabel(
            info_frame,
            text=f"⏱️ Tempo estimado: {estimated_time}",
            font=("Segoe UI", 11)
        )
        time_label.pack(side="right", padx=10, pady=10)
        
        # ============================================================
        # LISTA DE DETALHES (oculta inicialmente)
        # ============================================================
        self.details_frame = ctk.CTkFrame(main_frame)
        # Não empacota ainda (só quando clicar "Ver Detalhes")
        
        details_title = ctk.CTkLabel(
            self.details_frame,
            text="📝 Detalhes dos Produtos:",
            font=("Segoe UI", 12, "bold")
        )
        details_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Textbox com scroll
        self.details_text = ctk.CTkTextbox(
            self.details_frame,
            height=200,
            wrap="none"
        )
        self.details_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Preenche detalhes
        self._fill_details()
        
        # Botão Ver Detalhes
        self.toggle_details_btn = ctk.CTkButton(
            main_frame,
            text="🔽 Ver Detalhes",
            command=self._toggle_details,
            fg_color="gray40",
            hover_color="gray50"
        )
        self.toggle_details_btn.pack(pady=(0, 20))
        
        # ============================================================
        # BOTÕES
        # ============================================================
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=120,
            height=40,
            fg_color="gray40",
            hover_color="gray50",
            command=self._cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        continue_btn = ctk.CTkButton(
            button_frame,
            text="➡️ Continuar",
            width=120,
            height=40,
            command=self._confirm
        )
        continue_btn.pack(side="right")

    def _fill_details(self):
        """Preenche textbox com lista de produtos."""
        self.details_text.delete("1.0", "end")
        
        # Novos
        if self.new_products:
            self.details_text.insert("end", "✅ NOVOS:\n", "header")
            for i, product in enumerate(self.new_products[:100], 1):  # Limite 100
                name = product.get('name', 'Sem nome')
                self.details_text.insert("end", f"  {i}. {name}\n")
            
            if len(self.new_products) > 100:
                remaining = len(self.new_products) - 100
                self.details_text.insert(
                    "end",
                    f"  ... e mais {remaining} produtos\n",
                    "info"
                )
            self.details_text.insert("end", "\n")
        
        # Existentes
        if self.existing_products:
            self.details_text.insert("end", "⏭️ JÁ EXISTEM:\n", "header")
            for i, product in enumerate(self.existing_products[:50], 1):  # Limite 50
                name = product.get('name', 'Sem nome')
                self.details_text.insert("end", f"  {i}. {name}\n")
            
            if len(self.existing_products) > 50:
                remaining = len(self.existing_products) - 50
                self.details_text.insert(
                    "end",
                    f"  ... e mais {remaining} produtos\n",
                    "info"
                )
        
        # Desabilita edição
        self.details_text.configure(state="disabled")

    def _toggle_details(self):
        """Mostra/esconde detalhes."""
        if self.details_visible:
            # Esconde
            self.details_frame.pack_forget()
            self.toggle_details_btn.configure(text="🔽 Ver Detalhes")
            self.geometry("700x600")
            self.details_visible = False
        else:
            # Mostra
            self.details_frame.pack(fill="both", expand=True, pady=(0, 20), before=self.toggle_details_btn)
            self.toggle_details_btn.configure(text="🔼 Ocultar Detalhes")
            self.geometry("700x800")
            self.details_visible = True

    def _estimate_time(self, total: int) -> str:
        """Estima tempo de importação."""
        # Assume ~1 segundo por produto (com análise)
        seconds = total * 1
        
        if seconds < 60:
            return f"~{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"~{minutes} min"
        else:
            hours = seconds // 3600
            return f"~{hours}h"

    def _confirm(self):
        """Confirma e fecha dialog."""
        self.confirmed = True
        LOGGER.info("Importação confirmada pelo usuário")
        self.destroy()

    def _cancel(self):
        """Cancela e fecha dialog."""
        self.confirmed = False
        LOGGER.info("Importação cancelada no preview")
        self.destroy()

    # ================================================================
    # MÉTODOS PÚBLICOS
    # ================================================================

    def get_confirmed(self) -> bool:
        """Retorna se usuário confirmou importação."""
        return self.confirmed


# ================================================================
# TESTE
# ================================================================
if __name__ == '__main__':
    # Teste standalone
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.withdraw()
    
    # Dados fake para teste
    new = [
        {'name': f'Produto Novo {i}', 'path': f'/path/{i}'}
        for i in range(1, 151)
    ]
    existing = [
        {'name': f'Produto Existente {i}', 'path': f'/path/{i}'}
        for i in range(1, 33)
    ]
    
    dialog = ImportPreviewDialog(root, new, existing, mode='hybrid')
    root.wait_window(dialog)
    
    if dialog.get_confirmed():
        print("\n✅ USUÁRIO CONFIRMOU")
    else:
        print("\n❌ USUÁRIO CANCELOU")
    
    root.destroy()
