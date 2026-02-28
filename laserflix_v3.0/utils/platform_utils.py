"""
Utilidades multiplataforma
"""
import os
import subprocess
import platform
from tkinter import messagebox


def open_folder(folder_path):
    """
    Abre pasta no gerenciador de arquivos do SO.
    """
    try:
        if not os.path.exists(folder_path):
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{folder_path}")
            return
        
        system = platform.system()
        if system == "Windows":
            os.startfile(os.path.abspath(folder_path))
        elif system == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
        else:  # Linux
            subprocess.run(["xdg-open", folder_path])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir pasta:\n{e}")


def open_image(image_path):
    """
    Abre imagem no visualizador padrão do SO.
    """
    try:
        if not os.path.exists(image_path):
            messagebox.showerror("Erro", f"Imagem não encontrada:\n{image_path}")
            return
        
        system = platform.system()
        if system == "Windows":
            os.startfile(image_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", image_path])
        else:  # Linux
            subprocess.run(["xdg-open", image_path])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir imagem:\n{e}")
