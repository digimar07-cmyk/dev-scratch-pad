"""
model_settings_dialog.py — Tela de configuração de modelos IA e URL Ollama.

Permite:
  - Configurar URL base do servidor Ollama
  - Configurar 4 modelos por função (text_quality, text_fast, vision, embed)
  - Testar conexão com Ollama em tempo real
  - Salvar configurações em laserflix_config.json via DatabaseManager

Integração:
  - Chamado por main_window_FIXED.open_model_settings()
  - Lê e grava via db_manager.config["ollama_url"] e db_manager.config["models"]
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests

from config.settings import OLLAMA_BASE_URL, OLLAMA_MODELS, OLLAMA_HEALTH_TIMEOUT
from config.ui_constants import (
    BG_PRIMARY, BG_SECONDARY, BG_CARD,
    ACCENT_RED, ACCENT_GREEN, ACCENT_GOLD,
    FG_PRIMARY, FG_SECONDARY, FG_TERTIARY,
)
from utils.logging_setup import LOGGER


class ModelSettingsDialog(tk.Toplevel):
    """
    Dialog modal de configuração de modelos IA.
    Uso:
        dlg = ModelSettingsDialog(parent, db_manager)
        parent.wait_window(dlg)
    """

    _LABELS = {
        "text_quality": ("🧠 Modelo Qualidade",  "Análise individual e descrições detalhadas"),
        "text_fast":    ("⚡ Modelo Rápido",      "Lotes grandes (> 50 projetos)"),
        "vision":       ("👁️ Modelo Visão",        "Análise de imagem de capa (Moondream)"),
        "embed":        ("🔗 Modelo Embeddings",  "Embeddings para similaridade (reservado)"),
    }

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger     = LOGGER
        self._entries   = {}  # key → tk.Entry
        self._url_var   = tk.StringVar()
        self._status_var = tk.StringVar(value="")

        self.title("⚙️ Configuração de Modelos IA")
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.bind("<Escape>", lambda e: self.destroy())

        self._build_ui()
        self._load_current_values()
        self._center(parent)

    # -------------------------------------------------------------------------
    # BUILD UI
    # -------------------------------------------------------------------------

    def _build_ui(self):
        PAD = 24

        # Título
        tk.Label(
            self, text="⚙️  Modelos IA",
            font=("Arial", 20, "bold"),
            bg=BG_PRIMARY, fg=ACCENT_RED,
        ).pack(anchor="w", padx=PAD, pady=(20, 4))
        tk.Label(
            self, text="Configure a URL do Ollama e os modelos por função.",
            font=("Arial", 10),
            bg=BG_PRIMARY, fg=FG_TERTIARY,
        ).pack(anchor="w", padx=PAD, pady=(0, 16))

        tk.Frame(self, bg="#2A2A2A", height=1).pack(fill="x", padx=PAD)

        # ── Seção URL ──
        self._section("🌐  Servidor Ollama")
        url_row = tk.Frame(self, bg=BG_PRIMARY)
        url_row.pack(fill="x", padx=PAD, pady=(0, 4))
        tk.Label(
            url_row, text="URL Base:",
            font=("Arial", 10), bg=BG_PRIMARY, fg=FG_SECONDARY, width=18, anchor="w"
        ).pack(side="left")
        url_entry = tk.Entry(
            url_row, textvariable=self._url_var,
            bg=BG_CARD, fg=FG_PRIMARY, font=("Arial", 11),
            relief="flat", insertbackground=FG_PRIMARY, width=32,
        )
        url_entry.pack(side="left", ipady=6, padx=(0, 8))

        self._test_btn = tk.Button(
            url_row, text="🔌 Testar",
            command=self._test_connection,
            bg="#333333", fg=FG_PRIMARY, font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", padx=12, pady=6,
        )
        self._test_btn.pack(side="left")

        self._status_lbl = tk.Label(
            self, textvariable=self._status_var,
            font=("Arial", 10, "bold"),
            bg=BG_PRIMARY, fg=FG_TERTIARY, anchor="w",
        )
        self._status_lbl.pack(anchor="w", padx=PAD + 110, pady=(2, 8))

        tk.Frame(self, bg="#2A2A2A", height=1).pack(fill="x", padx=PAD, pady=(4, 0))

        # ── Seção Modelos ──
        self._section("🤖  Modelos por Função")
        for key, (label, hint) in self._LABELS.items():
            row = tk.Frame(self, bg=BG_PRIMARY)
            row.pack(fill="x", padx=PAD, pady=4)

            tk.Label(
                row, text=label,
                font=("Arial", 10, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY,
                width=22, anchor="w"
            ).pack(side="left")

            entry = tk.Entry(
                row, bg=BG_CARD, fg=FG_PRIMARY, font=("Arial", 11),
                relief="flat", insertbackground=FG_PRIMARY, width=32,
            )
            entry.pack(side="left", ipady=6)
            self._entries[key] = entry

            tk.Label(
                row, text=hint,
                font=("Arial", 8), bg=BG_PRIMARY, fg=FG_TERTIARY,
                anchor="w"
            ).pack(side="left", padx=(8, 0))

        tk.Frame(self, bg="#2A2A2A", height=1).pack(fill="x", padx=PAD, pady=(12, 0))

        # ── Rodapé ──
        footer = tk.Frame(self, bg=BG_PRIMARY)
        footer.pack(fill="x", padx=PAD, pady=16)

        tk.Button(
            footer, text="💾  Salvar",
            command=self._save,
            bg=ACCENT_GREEN, fg=FG_PRIMARY, font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2", padx=20, pady=10,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            footer, text="🔁  Restaurar Padrões",
            command=self._restore_defaults,
            bg="#444444", fg=FG_PRIMARY, font=("Arial", 10),
            relief="flat", cursor="hand2", padx=14, pady=10,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            footer, text="✕  Fechar",
            command=self.destroy,
            bg=BG_CARD, fg=FG_TERTIARY, font=("Arial", 10),
            relief="flat", cursor="hand2", padx=14, pady=10,
        ).pack(side="right")

    def _section(self, title):
        tk.Label(
            self, text=title,
            font=("Arial", 12, "bold"),
            bg=BG_PRIMARY, fg=ACCENT_GOLD,
            anchor="w",
        ).pack(anchor="w", padx=24, pady=(14, 6))

    # -------------------------------------------------------------------------
    # CARREGAR / SALVAR
    # -------------------------------------------------------------------------

    def _load_current_values(self):
        cfg = self.db_manager.config
        url = cfg.get("ollama_url") or OLLAMA_BASE_URL
        self._url_var.set(url)

        saved_models = cfg.get("models") or {}
        for key, entry in self._entries.items():
            value = saved_models.get(key) or OLLAMA_MODELS.get(key, "")
            entry.delete(0, tk.END)
            entry.insert(0, value)

    def _save(self):
        url = self._url_var.get().strip()
        if not url:
            messagebox.showwarning("⚠️ Campo obrigatório",
                                   "URL do Ollama não pode ficar em branco.",
                                   parent=self)
            return

        models = {key: entry.get().strip() for key, entry in self._entries.items()}
        empty = [k for k, v in models.items() if not v]
        if empty:
            labels = ", ".join(self._LABELS[k][0] for k in empty)
            messagebox.showwarning(
                "⚠️ Campos incompletos",
                f"Preencha todos os modelos:\n{labels}",
                parent=self,
            )
            return

        self.db_manager.config["ollama_url"] = url
        self.db_manager.config["models"]     = models
        self.db_manager.save_config()
        self.logger.info("[ModelSettings] Configuração salva — URL: %s | modelos: %s",
                         url, models)
        messagebox.showinfo("✅ Salvo",
                            "Configurações salvas com sucesso!\n"
                            "Reinicie o Laserflix para aplicar os novos modelos.",
                            parent=self)
        self.destroy()

    def _restore_defaults(self):
        if not messagebox.askyesno(
            "🔁 Restaurar Padrões",
            "Isso vai sobrescrever os campos com os valores padrão do settings.py.\n"
            "Confirma?",
            parent=self,
        ):
            return
        self._url_var.set(OLLAMA_BASE_URL)
        for key, entry in self._entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, OLLAMA_MODELS.get(key, ""))
        self._set_status("", FG_TERTIARY)

    # -------------------------------------------------------------------------
    # TESTE DE CONEXÃO
    # -------------------------------------------------------------------------

    def _test_connection(self):
        url = self._url_var.get().strip()
        if not url:
            self._set_status("⚠️ URL em branco", ACCENT_GOLD)
            return
        self._test_btn.config(state="disabled", text="⏳ Testando...")
        self._set_status("Conectando...", FG_TERTIARY)
        threading.Thread(
            target=self._do_test, args=(url,), daemon=True
        ).start()

    def _do_test(self, url):
        try:
            resp = requests.get(
                f"{url.rstrip('/')}/api/tags",
                timeout=OLLAMA_HEALTH_TIMEOUT,
            )
            if resp.status_code == 200:
                data   = resp.json()
                models = data.get("models", [])
                count  = len(models)
                msg    = f"✅ Conectado — {count} modelo(s) disponível(is)"
                color  = ACCENT_GREEN
                self.logger.info("[ModelSettings] %s", msg)
            else:
                msg   = f"⚠️ Resposta inesperada: HTTP {resp.status_code}"
                color = ACCENT_GOLD
        except requests.exceptions.ConnectionError:
            msg   = "❌ Sem conexão — Ollama offline ou URL incorreta"
            color = ACCENT_RED
        except requests.exceptions.Timeout:
            msg   = "❌ Timeout — servidor demorou demais para responder"
            color = ACCENT_RED
        except Exception as exc:
            msg   = f"❌ Erro inesperado: {exc}"
            color = ACCENT_RED
            self.logger.warning("[ModelSettings] Erro teste: %s", exc)

        self.after(0, lambda: self._set_status(msg, color))
        self.after(0, lambda: self._test_btn.config(
            state="normal", text="🔌 Testar"))

    def _set_status(self, text, color):
        self._status_var.set(text)
        self._status_lbl.config(fg=color)

    # -------------------------------------------------------------------------
    # UTILITÁRIO
    # -------------------------------------------------------------------------

    def _center(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w  = self.winfo_reqwidth()
        h  = self.winfo_reqheight()
        x  = px + (pw - w) // 2
        y  = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")
