# -*- coding: utf-8 -*-
"""Gerencia UI de progresso (progress bar)."""


class ProgressUIManager:
    def __init__(self, progress_bar, stop_btn, status_bar, root):
        self.progress_bar = progress_bar
        self.stop_btn = stop_btn
        self.status_bar = status_bar
        self.root = root
    
    def show(self):
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["value"] = 0
    
    def hide(self):
        self.progress_bar.pack_forget()
        self.stop_btn.pack_forget()
    
    def update(self, current: int, total: int, message: str = ""):
        pct = (current / total) * 100 if total else 0
        self.progress_bar["value"] = pct
        self.status_bar.config(text=f"{message} ({current}/{total} — {pct:.1f}%)")
        self.root.update_idletasks()
