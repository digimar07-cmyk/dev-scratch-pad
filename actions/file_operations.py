"""Operações de arquivo."""
import os
import platform
import subprocess
from tkinter import simpledialog


def open_folder(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"Erro ao abrir pasta: {e}")


def open_image(image_path):
    try:
        if platform.system() == "Windows":
            os.startfile(image_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", image_path])
        else:
            subprocess.Popen(["xdg-open", image_path])
    except Exception as e:
        print(f"Erro ao abrir imagem: {e}")


def add_tag_to_listbox(app, listbox):
    new_tag = simpledialog.askstring("Nova Tag", "Digite a nova tag:")
    if new_tag and new_tag.strip():
        listbox.insert("end", new_tag.strip())


def remove_tag_from_listbox(listbox):
    selection = listbox.curselection()
    if selection:
        listbox.delete(selection[0])
