"""Persistência de dados e backups."""
import os
import json
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox
from core.config import CONFIG_FILE, DB_FILE, BACKUP_FOLDER


def save_json_atomic(app, filepath, data, make_backup=True):
    tmp_file = filepath + ".tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        if make_backup and os.path.exists(filepath):
            try:
                shutil.copy2(filepath, filepath + ".bak")
            except Exception:
                app.logger.warning("Falha ao criar .bak de %s", filepath, exc_info=True)
        os.replace(tmp_file, filepath)
    except Exception:
        app.logger.error("Falha ao salvar JSON atômico: %s", filepath, exc_info=True)
        try:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        except Exception:
            pass


def save_config(app):
    save_json_atomic(
        app,
        CONFIG_FILE,
        {"folders": app.folders, "models": app.active_models},
        make_backup=True,
    )


def load_config(app):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            app.folders = config.get("folders", [])
            saved_models = config.get("models", {})
            if saved_models:
                app.active_models.update(saved_models)


def save_database(app):
    save_json_atomic(app, DB_FILE, app.database, make_backup=True)


def load_database(app):
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            app.database = json.load(f)
            for path, data in app.database.items():
                if "category" in data and "categories" not in data:
                    old_cat = data.get("category", "")
                    data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                    del data["category"]


def auto_backup(app):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_FOLDER, f"auto_backup_{timestamp}.json")
        if os.path.exists(DB_FILE):
            shutil.copy2(DB_FILE, backup_file)
        backups = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.startswith("auto_backup_")])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                os.remove(os.path.join(BACKUP_FOLDER, old_backup))
    except Exception:
        app.logger.exception("Falha no auto-backup")


def schedule_auto_backup(app):
    auto_backup(app)
    app.root.after(1800000, lambda: schedule_auto_backup(app))


def manual_backup(app):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_FOLDER, f"manual_backup_{timestamp}.json")
        if os.path.exists(DB_FILE):
            shutil.copy2(DB_FILE, backup_file)
            messagebox.showinfo("✓", f"Backup criado!\n{backup_file}")
        else:
            messagebox.showwarning("Aviso", "Nenhum banco para backup.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro: {e}")


def export_database(app):
    filename = filedialog.asksaveasfilename(
        title="Exportar Banco", defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile=f"laserflix_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )
    if filename:
        try:
            shutil.copy2(DB_FILE, filename)
            messagebox.showinfo("✓", f"Banco exportado!\n{filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")


def import_database(app):
    if messagebox.askyesno("⚠️ Atenção", "Importar substituirá todos os dados. Fazer backup?"):
        manual_backup(app)
    filename = filedialog.askopenfilename(title="Importar Banco", filetypes=[("JSON files", "*.json")])
    if filename:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                imported_data = json.load(f)
            if not isinstance(imported_data, dict):
                messagebox.showerror("Erro", "Arquivo inválido!")
                return
            shutil.copy2(DB_FILE, DB_FILE + ".pre-import.backup")
            app.database = imported_data
            save_database(app)
            
            from ui.sidebar import update_sidebar
            from ui.project_grid import display_projects
            update_sidebar(app)
            display_projects(app)
            messagebox.showinfo("✓", f"Banco importado! {len(app.database)} projetos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")
