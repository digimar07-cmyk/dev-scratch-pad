"""
recursive_scanner.py — Escaneamento recursivo inteligente de produtos.

FUNCIONALIDADES:
  1. Modo PURO: Detecta apenas pastas com folder.jpg (controle total)
  2. Modo HÍBRIDO: folder.jpg + fallback inteligente (mais flexível)
  3. Geração de ID único baseado em hash do caminho relativo
  4. Detecção de subpastas técnicas (cdr, svg, jpg, imagens, vetores)
  5. Validação de arquivos de projeto válidos

USO:
    scanner = RecursiveScanner()
    
    # Modo Puro (apenas folder.jpg)
    produtos = scanner.scan_folders_pure("d:/Arquivos Laser")
    
    # Modo Híbrido (folder.jpg + fallback)
    produtos = scanner.scan_folders_hybrid("d:/Arquivos Laser")
    
    # Cada produto retorna:
    {
        'path': 'caminho/completo/produto',
        'name': 'Nome do Produto',
        'unique_id': 'hash_md5_do_caminho',
        'has_folder_jpg': True/False,
        'detection_method': 'folder_jpg' ou 'fallback'
    }
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Set
from utils.logging_setup import LOGGER


# Extensões válidas de arquivos de projeto
VALID_EXTENSIONS = {
    '.svg', '.pdf', '.dxf', '.ai', '.cdr', '.eps',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp'
}

# Subpastas técnicas que NÃO são produtos
TECHNICAL_SUBFOLDERS = {
    'cdr', 'svg', 'jpg', 'jpeg', 'png', 'pdf', 'dxf',
    'imagens', 'images', 'vetores', 'vectors',
    'backup', 'temp', 'cache', '.git', '__pycache__'
}


class RecursiveScanner:
    """
    Escaneador recursivo de produtos com detecção inteligente.
    
    Suporta dois modos:
    - PURO: Apenas pastas com folder.jpg (rígido, controle total)
    - HÍBRIDO: folder.jpg + fallback inteligente (flexível, pega mais)
    """

    def __init__(self):
        self.logger = LOGGER
        self.found_products = []
        self.skipped_folders = []
        self.stats = {
            'total_scanned': 0,
            'products_found': 0,
            'with_folder_jpg': 0,
            'via_fallback': 0,
            'technical_skipped': 0
        }

    # ================================================================
    # MÉTODOS PÚBLICOS
    # ================================================================

    def scan_folders_pure(self, base_path: str) -> List[Dict]:
        """
        MODO PURO: Detecta apenas pastas com folder.jpg.
        
        Args:
            base_path: Caminho da pasta base para escanear
        
        Returns:
            Lista de dicionários com dados dos produtos encontrados
        
        Exemplo:
            [
                {
                    'path': 'd:/Arquivos/Natal/Produto A',
                    'name': 'Produto A',
                    'unique_id': 'a3f2b8c9d1e4f5a6...',
                    'has_folder_jpg': True,
                    'detection_method': 'folder_jpg'
                },
                ...
            ]
        """
        self.logger.info(f"[SCAN PURO] Iniciando em: {base_path}")
        self._reset_stats()
        
        base_path = os.path.abspath(base_path)
        if not os.path.exists(base_path):
            self.logger.error(f"Pasta base não existe: {base_path}")
            return []
        
        self._scan_recursive(base_path, base_path, mode='pure')
        
        self.logger.info(
            f"[SCAN PURO] Concluído: {self.stats['products_found']} produtos, "
            f"{self.stats['total_scanned']} pastas escaneadas"
        )
        
        return self.found_products

    def scan_folders_hybrid(self, base_path: str) -> List[Dict]:
        """
        MODO HÍBRIDO: folder.jpg + fallback inteligente.
        
        Detecta:
        1. Pastas com folder.jpg (prioridade)
        2. Pastas com arquivos válidos (.svg, .pdf) E NÃO são subpastas técnicas
        
        Args:
            base_path: Caminho da pasta base para escanear
        
        Returns:
            Lista de dicionários com dados dos produtos encontrados
        """
        self.logger.info(f"[SCAN HÍBRIDO] Iniciando em: {base_path}")
        self._reset_stats()
        
        base_path = os.path.abspath(base_path)
        if not os.path.exists(base_path):
            self.logger.error(f"Pasta base não existe: {base_path}")
            return []
        
        self._scan_recursive(base_path, base_path, mode='hybrid')
        
        self.logger.info(
            f"[SCAN HÍBRIDO] Concluído: {self.stats['products_found']} produtos "
            f"({self.stats['with_folder_jpg']} com folder.jpg, "
            f"{self.stats['via_fallback']} via fallback)"
        )
        
        return self.found_products

    def generate_unique_id(self, product_path: str, base_path: str) -> str:
        """
        Gera ID único baseado no caminho relativo.
        
        Args:
            product_path: Caminho completo do produto
            base_path: Caminho da pasta base
        
        Returns:
            Hash MD5 do caminho relativo normalizado
        
        Exemplo:
            base: d:/Arquivos Laser
            produto: d:/Arquivos Laser/Religiosos/Natal/Produto A
            relativo: religiosos/natal/produto a
            id: a3f2b8c9d1e4f5a6b7c8d9e0f1a2b3c4
        """
        try:
            # Caminho relativo
            relative = os.path.relpath(product_path, base_path)
            
            # Normaliza: lowercase, barra única
            normalized = relative.lower().replace('\\', '/')
            
            # Hash MD5
            return hashlib.md5(normalized.encode('utf-8')).hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao gerar ID único: {e}")
            # Fallback: hash do caminho completo
            return hashlib.md5(product_path.encode('utf-8')).hexdigest()

    def get_stats(self) -> Dict:
        """Retorna estatísticas do último escaneamento."""
        return self.stats.copy()

    # ================================================================
    # MÉTODOS INTERNOS
    # ================================================================

    def _reset_stats(self):
        """Reseta estatísticas para novo escaneamento."""
        self.found_products = []
        self.skipped_folders = []
        self.stats = {
            'total_scanned': 0,
            'products_found': 0,
            'with_folder_jpg': 0,
            'via_fallback': 0,
            'technical_skipped': 0
        }

    def _scan_recursive(self, current_path: str, base_path: str, mode: str):
        """
        Escaneia pasta recursivamente.
        
        Args:
            current_path: Pasta atual sendo escaneada
            base_path: Pasta base original
            mode: 'pure' ou 'hybrid'
        """
        try:
            # Lista conteúdo da pasta
            try:
                items = os.listdir(current_path)
            except PermissionError:
                self.logger.warning(f"Sem permissão para acessar: {current_path}")
                return
            
            files = []
            subdirs = []
            
            for item in items:
                item_path = os.path.join(current_path, item)
                if os.path.isfile(item_path):
                    files.append(item)
                elif os.path.isdir(item_path):
                    subdirs.append(item)
            
            self.stats['total_scanned'] += 1
            
            # Checa se é subpasta técnica
            folder_name = os.path.basename(current_path).lower()
            if self._is_technical_subfolder(folder_name):
                self.stats['technical_skipped'] += 1
                self.logger.debug(f"Pulando subpasta técnica: {current_path}")
                return
            
            # DETECÇÃO DE PRODUTO
            is_product = False
            detection_method = None
            has_folder_jpg = 'folder.jpg' in [f.lower() for f in files]
            
            # PRIORIDADE 1: folder.jpg (ambos modos)
            if has_folder_jpg:
                is_product = True
                detection_method = 'folder_jpg'
                self.stats['with_folder_jpg'] += 1
            
            # PRIORIDADE 2: Fallback inteligente (apenas modo híbrido)
            elif mode == 'hybrid':
                if self._has_project_files(files):
                    is_product = True
                    detection_method = 'fallback'
                    self.stats['via_fallback'] += 1
            
            # Se detectou produto, adiciona e NÃO entra em subpastas
            if is_product:
                product_data = {
                    'path': current_path,
                    'name': os.path.basename(current_path),
                    'unique_id': self.generate_unique_id(current_path, base_path),
                    'has_folder_jpg': has_folder_jpg,
                    'detection_method': detection_method
                }
                self.found_products.append(product_data)
                self.stats['products_found'] += 1
                
                self.logger.debug(
                    f"Produto detectado ({detection_method}): {current_path}"
                )
                
                # NÃO escaneia subpastas deste produto
                return
            
            # Se NÃO é produto, continua escaneando subpastas
            for subdir in subdirs:
                subdir_path = os.path.join(current_path, subdir)
                self._scan_recursive(subdir_path, base_path, mode)
        
        except Exception as e:
            self.logger.error(f"Erro ao escanear {current_path}: {e}")

    def _is_technical_subfolder(self, folder_name: str) -> bool:
        """
        Verifica se pasta é subpasta técnica (não é produto).
        
        Args:
            folder_name: Nome da pasta (lowercase)
        
        Returns:
            True se for subpasta técnica
        """
        return folder_name in TECHNICAL_SUBFOLDERS

    def _has_project_files(self, files: List[str]) -> bool:
        """
        Verifica se pasta tem arquivos válidos de projeto.
        
        Args:
            files: Lista de nomes de arquivos na pasta
        
        Returns:
            True se tem pelo menos 1 arquivo válido
        """
        for file in files:
            ext = os.path.splitext(file.lower())[1]
            if ext in VALID_EXTENSIONS:
                return True
        return False


# ================================================================
# FUNÇÕES UTILITÁRIAS (para uso externo)
# ================================================================

def scan_pure(base_path: str) -> List[Dict]:
    """Atalho para scan no modo puro."""
    scanner = RecursiveScanner()
    return scanner.scan_folders_pure(base_path)


def scan_hybrid(base_path: str) -> List[Dict]:
    """Atalho para scan no modo híbrido."""
    scanner = RecursiveScanner()
    return scanner.scan_folders_hybrid(base_path)


def generate_id(product_path: str, base_path: str) -> str:
    """Atalho para gerar ID único."""
    scanner = RecursiveScanner()
    return scanner.generate_unique_id(product_path, base_path)


if __name__ == '__main__':
    # Teste rápido
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python recursive_scanner.py <pasta_base> [pure|hybrid]")
        sys.exit(1)
    
    base = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'hybrid'
    
    scanner = RecursiveScanner()
    
    if mode == 'pure':
        produtos = scanner.scan_folders_pure(base)
    else:
        produtos = scanner.scan_folders_hybrid(base)
    
    print(f"\n╔══ RESULTADO ════════════════════════════════════════")
    print(f"║ Modo: {mode.upper()}")
    print(f"║ Produtos encontrados: {len(produtos)}")
    print(f"╚════════════════════════════════════════════════")
    
    stats = scanner.get_stats()
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"  • Total escaneado: {stats['total_scanned']} pastas")
    print(f"  • Com folder.jpg: {stats['with_folder_jpg']}")
    print(f"  • Via fallback: {stats['via_fallback']}")
    print(f"  • Técnicas puladas: {stats['technical_skipped']}")
    
    if produtos:
        print(f"\n📁 PRIMEIROS 10 PRODUTOS:")
        for i, p in enumerate(produtos[:10], 1):
            print(f"  {i}. {p['name']} [{p['detection_method']}]")
            print(f"     ID: {p['unique_id'][:16]}...")
