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


def open_file(file_path):
    """
    Abre arquivo (imagem ou qualquer outro) no aplicativo padrão do SO.
    """
    try:
        if not os.path.exists(file_path):
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{file_path}")
            return

        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir arquivo:\n{e}")
