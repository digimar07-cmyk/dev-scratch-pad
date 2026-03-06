# [APENAS A SEÇÃO _get_thumbnail_async FOI MODIFICADA]
# [RESTO DO ARQUIVO PERMANECE IGUAL]

# Adicionar no início após imports:
# (sem mudanças nos imports)

# MODIFICAR APENAS O MÉTODO:

def _get_thumbnail_async(self, project_path, callback, widget, is_orphan=False):
    """
    Wrapper thread-safe para carregamento assíncrono de thumbnails.
    
    F-03: Adiciona parâmetro is_orphan para aplicar grayscale.
    """
    def _ui_safe_callback(path, photo):
        try:
            if widget and widget.winfo_exists():
                self.root.after(0, lambda: callback(path, photo))
        except Exception as e:
            self.logger.debug(f"Widget destruído antes do callback: {e}")
    
    self.thumbnail_preloader.preload_single(project_path, _ui_safe_callback, is_orphan)

# [TODO O RESTO DO ARQUIVO MAIN_WINDOW.PY PERMANECE INALTERADO]
