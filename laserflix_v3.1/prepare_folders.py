#!/usr/bin/env python3
"""
prepare_folders.py — Prepara pastas de produtos gerando folder.jpg automaticamente.

PREPARA PRODUTOS PARA IMPORTAÇÃO:
  - Gera folder.jpg em pastas sem esse arquivo
  - Usa primeira imagem encontrada (.jpg, .png, .svg)
  - Converte SVG → JPG se necessário
  - Redimensiona para thumbnail (500x500px)
  - Relatório completo ao final

MODOS:
  --all:   Gera folder.jpg em TODAS as pastas com imagens
  --smart: Apenas pastas com arquivos de projeto (.svg, .pdf, .dxf)
  --list:  Dry-run (só lista, não cria nada)

USO:
    python prepare_folders.py "d:/Arquivos Laser" --smart
    python prepare_folders.py "d:/Arquivos Laser" --list
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️  Aviso: Pillow não instalado. Instale: pip install Pillow")

try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False


# Extensões de imagens válidas
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
PROJECT_EXTENSIONS = {'.svg', '.pdf', '.dxf', '.ai', '.cdr', '.eps'}
TECHNICAL_FOLDERS = {'cdr', 'svg', 'jpg', 'jpeg', 'png', 'pdf', 'imagens', 'vetores', 'backup', 'temp'}

# Config
THUMBNAIL_SIZE = (500, 500)
FOLDER_JPG_NAME = "folder.jpg"


class FolderPreparer:
    """Preparador de pastas com geração de folder.jpg."""

    def __init__(self, base_path: str, mode: str = 'smart'):
        self.base_path = os.path.abspath(base_path)
        self.mode = mode
        self.stats = {
            'total_folders': 0,
            'with_folder_jpg': 0,
            'without_folder_jpg': 0,
            'can_generate': 0,
            'generated': 0,
            'failed': 0,
            'no_images': 0,
            'technical_skipped': 0
        }
        self.folders_to_process = []

    def scan(self):
        """Escaneia pastas e identifica as que precisam folder.jpg."""
        print(f"\n🔍 Escaneando: {self.base_path}")
        print("━" * 60)
        
        for root, dirs, files in os.walk(self.base_path):
            self.stats['total_folders'] += 1
            
            # Pula subpastas técnicas
            folder_name = os.path.basename(root).lower()
            if folder_name in TECHNICAL_FOLDERS:
                self.stats['technical_skipped'] += 1
                continue
            
            files_lower = [f.lower() for f in files]
            
            # Tem folder.jpg?
            if FOLDER_JPG_NAME in files_lower:
                self.stats['with_folder_jpg'] += 1
                continue
            
            # Não tem folder.jpg
            self.stats['without_folder_jpg'] += 1
            
            # Tem imagens?
            images = self._find_images(files)
            has_project_files = any(
                os.path.splitext(f.lower())[1] in PROJECT_EXTENSIONS
                for f in files
            )
            
            if not images:
                self.stats['no_images'] += 1
                continue
            
            # Modo SMART: só pastas com arquivos de projeto
            if self.mode == 'smart' and not has_project_files:
                continue
            
            # Pode gerar!
            self.stats['can_generate'] += 1
            self.folders_to_process.append({
                'path': root,
                'images': images,
                'has_project_files': has_project_files
            })

    def _find_images(self, files: List[str]) -> List[str]:
        """Encontra imagens válidas na lista de arquivos."""
        images = []
        for f in files:
            ext = os.path.splitext(f.lower())[1]
            if ext in IMAGE_EXTENSIONS or ext == '.svg':
                images.append(f)
        return images

    def generate(self):
        """Gera folder.jpg nas pastas identificadas."""
        total = len(self.folders_to_process)
        
        if total == 0:
            print("\nℹ️  Nenhuma pasta precisa de folder.jpg!")
            return
        
        print(f"\n📥 Gerando folder.jpg em {total} pastas...")
        print("━" * 60)
        
        for i, folder_data in enumerate(self.folders_to_process, 1):
            folder_path = folder_data['path']
            images = folder_data['images']
            
            # Progress
            progress = int((i / total) * 40)
            bar = '█' * progress + '░' * (40 - progress)
            percent = (i / total) * 100
            folder_name = os.path.basename(folder_path)
            print(f"\r[{bar}] {percent:.1f}% - {folder_name[:40]}", end='', flush=True)
            
            # Tenta gerar
            try:
                self._create_folder_jpg(folder_path, images)
                self.stats['generated'] += 1
            except Exception as e:
                print(f"\n⚠️  Erro em {folder_path}: {e}")
                self.stats['failed'] += 1
        
        print()  # Nova linha após progress bar

    def _create_folder_jpg(self, folder_path: str, images: List[str]):
        """Cria folder.jpg a partir da primeira imagem."""
        if not HAS_PIL:
            raise Exception("Pillow não instalado")
        
        # Usa primeira imagem
        first_image = images[0]
        image_path = os.path.join(folder_path, first_image)
        output_path = os.path.join(folder_path, FOLDER_JPG_NAME)
        
        ext = os.path.splitext(first_image.lower())[1]
        
        # Se é SVG, converte
        if ext == '.svg':
            if HAS_CAIROSVG:
                self._convert_svg_to_jpg(image_path, output_path)
            else:
                # Fallback: copia como é (não ideal, mas funciona para import)
                import shutil
                shutil.copy(image_path, output_path)
        else:
            # Imagem raster: redimensiona
            self._resize_image(image_path, output_path)

    def _resize_image(self, input_path: str, output_path: str):
        """Redimensiona imagem para thumbnail."""
        img = Image.open(input_path)
        img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        img = img.convert('RGB')  # Garante JPEG compatível
        img.save(output_path, 'JPEG', quality=85, optimize=True)

    def _convert_svg_to_jpg(self, svg_path: str, jpg_path: str):
        """Converte SVG para JPG."""
        # Converte SVG → PNG temporário
        png_bytes = cairosvg.svg2png(url=svg_path, output_width=500, output_height=500)
        
        # Abre PNG e salva como JPG
        from io import BytesIO
        img = Image.open(BytesIO(png_bytes))
        img = img.convert('RGB')
        img.save(jpg_path, 'JPEG', quality=85, optimize=True)

    def print_report(self):
        """Imprime relatório final."""
        print(f"\n\n╔══ RELATÓRIO ════════════════════════════════════════════")
        print(f"║")
        print(f"║ 📊 ESTATÍSTICAS:")
        print(f"║")
        print(f"║   Total de pastas escaneadas: {self.stats['total_folders']}")
        print(f"║")
        print(f"║   ✅ Com folder.jpg (OK): {self.stats['with_folder_jpg']}")
        print(f"║   ⚠️  Sem folder.jpg: {self.stats['without_folder_jpg']}")
        print(f"║")
        
        if self.mode != 'list':
            print(f"║   📦 Podem gerar: {self.stats['can_generate']}")
            print(f"║   ✅ Gerados com sucesso: {self.stats['generated']}")
            print(f"║   ❌ Falhas: {self.stats['failed']}")
        else:
            print(f"║   📦 Podem gerar: {self.stats['can_generate']}")
        
        print(f"║")
        print(f"║   📁 Sem imagens: {self.stats['no_images']}")
        print(f"║   ⏭️  Técnicas puladas: {self.stats['technical_skipped']}")
        print(f"║")
        print(f"╚════════════════════════════════════════════════════")
        
        # Recomendações
        if self.mode == 'list':
            print(f"\n💡 RECOMENDAÇÃO:")
            if self.stats['can_generate'] > 0:
                print(f"   Rodar: python prepare_folders.py \"{self.base_path}\" --smart")
                print(f"   (Gera folder.jpg nos {self.stats['can_generate']} válidos)")
            print(f"\n   Depois: Importar no app com Modo Híbrido")
        elif self.stats['generated'] > 0:
            print(f"\n✅ SUCESSO!")
            print(f"   {self.stats['generated']} pastas preparadas.")
            print(f"   Agora pode importar no app (Modo Puro ou Híbrido).")


def main():
    """Entry point do script."""
    parser = argparse.ArgumentParser(
        description='Prepara pastas de produtos gerando folder.jpg automaticamente.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python prepare_folders.py "d:/Arquivos Laser" --smart
  python prepare_folders.py "d:/Arquivos Laser" --all
  python prepare_folders.py "d:/Arquivos Laser" --list
        """
    )
    
    parser.add_argument(
        'base_path',
        help='Caminho da pasta base'
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--all',
        action='store_const',
        const='all',
        dest='mode',
        help='Gera folder.jpg em TODAS as pastas com imagens'
    )
    mode_group.add_argument(
        '--smart',
        action='store_const',
        const='smart',
        dest='mode',
        default='smart',
        help='Apenas pastas com arquivos de projeto (.svg, .pdf) [PADRÃO]'
    )
    mode_group.add_argument(
        '--list',
        action='store_const',
        const='list',
        dest='mode',
        help='Dry-run: apenas lista, não cria nada'
    )
    
    args = parser.parse_args()
    
    # Validações
    if not os.path.exists(args.base_path):
        print(f"❌ Erro: Pasta não existe: {args.base_path}")
        sys.exit(1)
    
    if not HAS_PIL and args.mode != 'list':
        print("❌ Erro: Pillow não instalado. Instale: pip install Pillow")
        sys.exit(1)
    
    # Banner
    print("\n" + "=" * 60)
    print("🗂️  PREPARADOR DE PASTAS - folder.jpg Generator")
    print("=" * 60)
    
    # Processa
    preparer = FolderPreparer(args.base_path, args.mode)
    preparer.scan()
    
    if args.mode != 'list':
        preparer.generate()
    
    preparer.print_report()
    print()


if __name__ == '__main__':
    main()
