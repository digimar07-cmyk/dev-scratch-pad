"""
Cache LRU de thumbnails com carregamento assíncrono.

NOVO EM S-03:
  - queue.Queue para carregar imagens em background
  - Thread worker que não trava UI
  - Callback para atualizar card quando imagem carregar
  - get_cover_image_async() retorna placeholder instantâneo

HOT-06a:
  - Callback agora é thread-safe (valida se widget existe)
  - Não causa erro "main thread is not in main loop"
"""
import os
import queue
import threading
from collections import OrderedDict
from PIL import Image, ImageTk
from config.settings import THUMBNAIL_CACHE_LIMIT, THUMBNAIL_SIZE
from config.constants import FILE_EXTENSIONS
from utils.logging_setup import LOGGER


class ThumbnailCache:
    """
    Cache LRU (Least Recently Used) para thumbnails.
    Limite padrão: 300 imagens.
    
    NOVO: Carregamento assíncrono via queue.Queue.
    """

    def __init__(self, limit=THUMBNAIL_CACHE_LIMIT):
        self.cache = OrderedDict()
        self.limit = limit
        self.logger = LOGGER
        
        # ← NOVO: Fila assíncrona
        self.load_queue = queue.Queue()
        self.stop_worker = False
        self.worker_thread = None
        self.root_widget = None  # ← HOT-06a: Referência para Tk root
        self._start_worker()

    def set_root(self, root):
        """
        Define widget root do Tkinter para callbacks thread-safe.
        Deve ser chamado no __init__ do MainWindow.
        
        Args:
            root: tk.Tk instance
        """
        self.root_widget = root

    def _start_worker(self):
        """
        Inicia thread worker que processa fila de thumbnails.
        Roda em background sem travar UI.
        """
        def _worker():
            self.logger.info("📷 Thumbnail worker iniciado")
            while not self.stop_worker:
                try:
                    # Timeout de 0.5s para verificar stop_worker periodicamente
                    task = self.load_queue.get(timeout=0.5)
                    if task is None:  # Sinal de parada
                        break
                    
                    project_path, callback, widget = task
                    
                    # Carrega thumbnail de forma síncrona (mas em thread separada)
                    img_path = self.find_first_image(project_path)
                    if img_path:
                        photo = self.load_thumbnail(img_path)
                        if photo and callback:
                            # ← HOT-06a: Valida se widget ainda existe antes de callback
                            if widget and self.root_widget:
                                try:
                                    # Executa callback na thread principal (Tkinter-safe)
                                    self.root_widget.after(0, lambda: self._safe_callback(
                                        callback, widget, project_path, photo))
                                except Exception as e:
                                    self.logger.warning(
                                        "Erro ao agendar callback para %s: %s", project_path, e)
                    
                    self.load_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error("🚨 Erro no thumbnail worker: %s", e)
        
        self.worker_thread = threading.Thread(target=_worker, daemon=True, name="ThumbnailWorker")
        self.worker_thread.start()

    def _safe_callback(self, callback, widget, project_path, photo):
        """
        Executa callback de forma segura, validando se widget ainda existe.
        Previne erro "main thread is not in main loop".
        
        Args:
            callback: Função a ser chamada
            widget: Widget Tkinter associado
            project_path: Caminho do projeto
            photo: PhotoImage carregada
        """
        try:
            # Valida se widget ainda existe
            if widget and widget.winfo_exists():
                callback(project_path, photo)
        except Exception as e:
            # Widget foi destruído entre o carregamento e o callback
            self.logger.debug("Widget destruído antes de callback: %s", e)

    def stop(self):
        """
        Para o worker thread de forma limpa.
        """
        self.stop_worker = True
        self.load_queue.put(None)  # Sinal de parada
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
        self.logger.info("📷 Thumbnail worker parado")

    def get(self, image_path):
        if not image_path or not os.path.exists(image_path):
            return None
        try:
            mtime = os.path.getmtime(image_path)
        except Exception:
            return None
        cached = self.cache.get(image_path)
        if cached:
            cached_mtime, cached_photo = cached
            if cached_mtime == mtime:
                self.cache.move_to_end(image_path)
                return cached_photo
            else:
                del self.cache[image_path]
        return None

    def set(self, image_path, photo):
        if not image_path:
            return
        try:
            mtime = os.path.getmtime(image_path)
            self.cache[image_path] = (mtime, photo)
            self.cache.move_to_end(image_path)
            while len(self.cache) > self.limit:
                oldest_key, _ = self.cache.popitem(last=False)
                self.logger.debug("🗑️ Cache LRU: removido %s", oldest_key)
        except Exception as e:
            self.logger.warning("Erro ao adicionar ao cache: %s", e)

    def load_thumbnail(self, image_path):
        """
        Carrega thumbnail de forma síncrona.
        NOTA: Chamado pela thread worker, não pela UI.
        """
        cached = self.get(image_path)
        if cached:
            return cached
        try:
            img = Image.open(image_path)
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.set(image_path, photo)
            return photo
        except Exception as e:
            self.logger.warning("Erro ao gerar thumbnail de %s: %s", image_path, e)
            return None

    def find_first_image(self, project_path):
        """
        Encontra primeira imagem válida na pasta do projeto.
        Retorna caminho completo ou None.
        """
        valid_extensions = FILE_EXTENSIONS["images"]
        try:
            for item in sorted(os.listdir(project_path)):
                if item.lower().endswith(valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            self.logger.exception("Falha ao listar %s", project_path)
        return None

    def get_cover_image(self, project_path):
        """
        Retorna PhotoImage da capa do projeto (primeira imagem encontrada).
        
        DEPRECATED: Use get_cover_image_async() para não travar UI.
        Esta função síncrona ainda existe para compatibilidade.
        """
        img_path = self.find_first_image(project_path)
        if not img_path:
            return None
        return self.load_thumbnail(img_path)

    def get_cover_image_async(self, project_path, callback, widget=None):
        """
        Agenda carregamento assíncrono de thumbnail.
        
        Args:
            project_path: Caminho do projeto
            callback: Função(project_path, photo) chamada quando carregar
            widget: Widget Tkinter associado (para validar se ainda existe)
        
        Returns:
            None (imagem será entregue via callback)
        
        Exemplo:
            def on_thumb_loaded(path, photo):
                label.config(image=photo)
                label.image = photo  # Prevent GC
            
            cache.get_cover_image_async(project_path, on_thumb_loaded, label)
        """
        # Verifica se já está em cache
        img_path = self.find_first_image(project_path)
        if img_path:
            cached = self.get(img_path)
            if cached:
                # Já em cache - retorna imediatamente
                if callback and widget and widget.winfo_exists():
                    try:
                        callback(project_path, cached)
                    except Exception as e:
                        self.logger.debug("Callback falhou para cached image: %s", e)
                return
        
        # Não está em cache - agenda para carregar
        self.load_queue.put((project_path, callback, widget))

    def get_all_project_images(self, project_path, max_images=40):
        """
        Retorna lista de caminhos de TODAS as imagens do projeto
        (busca recursiva em subpastas), limitado a max_images.
        Retorna lista de strings (caminhos absolutos).
        """
        valid_extensions = FILE_EXTENSIONS["images"]
        found = []
        try:
            for root, dirs, files in os.walk(project_path):
                dirs.sort()
                for fname in sorted(files):
                    if fname.lower().endswith(valid_extensions):
                        found.append(os.path.join(root, fname))
                        if len(found) >= max_images:
                            return found
        except Exception:
            self.logger.exception("Falha ao listar imagens de %s", project_path)
        return found

    def clear(self):
        self.cache.clear()
        self.logger.info("🗑️ Cache de thumbnails limpo")

    def get_stats(self):
        return {
            "size": len(self.cache),
            "limit": self.limit,
            "usage_pct": (len(self.cache) / self.limit * 100) if self.limit > 0 else 0,
            "queue_size": self.load_queue.qsize(),  # ← NOVO
        }
