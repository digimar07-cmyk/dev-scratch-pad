"""Operações de arquivo e helpers UI."""
import os
import platform
import subprocess
from tkinter import messagebox, simpledialog


def open_folder(folder_path):
    try:
        if not os.path.exists(folder_path):
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{folder_path}")
            return
        if platform.system() == "Windows":
            os.startfile(os.path.abspath(folder_path))
        elif platform.system() == "Darwin":
            subprocess.run(["open", folder_path])
        else:
            subprocess.run(["xdg-open", folder_path])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir pasta:\n{e}")


def open_image(image_path):
    try:
        if platform.system() == "Windows":
            os.startfile(image_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", image_path])
        else:
            subprocess.run(["xdg-open", image_path])
    except Exception:
        messagebox.showerror("Erro", "Erro ao abrir imagem")


def add_tag_to_listbox(app, listbox):
    new_tag = simpledialog.askstring("Nova Tag", "Digite a nova tag:", parent=app.root)
    if new_tag and new_tag.strip():
        new_tag = new_tag.strip()
        if new_tag not in listbox.get(0, "end"):
            listbox.insert("end", new_tag)


def remove_tag_from_listbox(listbox):
    selection = listbox.curselection()
    if selection:
        listbox.delete(selection[0])


def darken_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"#{max(0,int(r*0.8)):02x}{max(0,int(g*0.8)):02x}{max(0,int(b*0.8)):02x}"
