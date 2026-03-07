"""
LASERFLIX v3.4.2.5
Entry point
"""
import tkinter as tk
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from config.settings import VERSION
from ui.main_window import LaserflixMainWindow
from utils.logging_setup import LOGGER


def main():
    try:
        # Exibir informações de inicialização
        print("=" * 80)
        print(f"LASERFLIX v{VERSION}")
        print("=" * 80)
        print("\nℹ️  Inicializando...")
        print("\n📁 Verificando dependências...")
        
        # Verificar imports críticos
        try:
            from ui.controllers.display_controller import DisplayController
            print("✅ DisplayController OK")
        except ImportError as e:
            print(f"❌ Erro ao importar DisplayController: {e}")
            raise
        
        try:
            from ui.controllers.analysis_controller import AnalysisController
            print("✅ AnalysisController OK")
        except ImportError as e:
            print(f"❌ Erro ao importar AnalysisController: {e}")
            raise
        
        print("\n✅ Todas as dependências OK!")
        print("\n🚀 Pronto para iniciar a aplicação.")
        print("\n" + "=" * 80)
        
        # PAUSE ANTES DE ABRIR O APP
        print("\nPressione ENTER para abrir o Laserflix...")
        input()
        
        # Iniciar aplicação
        print("\n💻 Abrindo janela principal...\n")
        root = tk.Tk()
        app = LaserflixMainWindow(root)
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n\n❌ Aplicação cancelada pelo usuário")
        LOGGER.info("Aplicação cancelada pelo usuário")
        print("\nPressione ENTER para sair...")
        input()
        sys.exit(0)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERRO FATAL")
        print("=" * 80)
        print(f"\nErro: {e}")
        print(f"\nTraceback completo:\n")
        print(traceback.format_exc())
        print("=" * 80)
        
        LOGGER.exception("Erro fatal: %s", e)
        
        print("\nPressione ENTER para sair...")
        input()
        sys.exit(1)


if __name__ == "__main__":
    main()
