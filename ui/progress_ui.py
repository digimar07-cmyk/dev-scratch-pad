"""UI de progresso para análises em lote."""

def show_progress_ui(app):
    app.progress_bar.pack(side="left", padx=10)
    app.stop_button.pack(side="right", padx=10)
    app.progress_bar["value"] = 0


def hide_progress_ui(app):
    app.progress_bar.pack_forget()
    app.stop_button.pack_forget()


def update_progress(app, current, total, message=""):
    percentage = (current / total) * 100
    app.progress_bar["value"] = percentage
    app.status_bar.config(text=f"{message} ({current}/{total} — {percentage:.1f}%)")
    app.root.update_idletasks()


def stop_analysis_process(app):
    app.stop_analysis = True
    app.status_bar.config(text="⏹ Parando análise...")
