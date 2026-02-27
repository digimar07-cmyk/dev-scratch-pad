"""
LASERFLIX v7.4.0 — Stable
Base para proximas features
"""




import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import json
import os
import threading
import time
import requests
import subprocess
import platform
import shutil
import logging
from logging.handlers import RotatingFileHandler
from PIL import Image, ImageTk
from datetime import datetime
from collections import Counter, OrderedDict
import re
import base64
import io

VERSION = "7.4.0"
CONFIG_FILE = "laserflix_config.json"
DB_FILE = "laserflix_database.json"
BACKUP_FOLDER = "laserflix_backups"

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO CENTRAL DOS MODELOS
# ---------------------------------------------------------------------------
OLLAMA_MODELS = {
    "text_quality":  "qwen2.5:7b-instruct-q4_K_M",   # análise individual, descrições
    "text_fast":     "qwen2.5:3b-instruct-q4_K_M",   # lotes grandes (>50 projetos)
    "vision":        "moondream:latest",               # análise de imagem de capa
    "embed":         "nomic-embed-text:latest",        # embeddings (reservado)
}

# Limiar: acima deste número de projetos, usa modelo rápido no lote
FAST_MODEL_THRESHOLD = 50

# Timeouts por tipo de modelo (connect_timeout, read_timeout)
TIMEOUTS = {
    "text_quality": (5, 120),
    "text_fast":    (5,  75),
    "vision":       (5,  60),
    "embed":        (5,  15),
}


def setup_logging():
    logger = logging.getLogger("Laserflix")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler = RotatingFileHandler(
        "laserflix.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


LOGGER = setup_logging()


class LaserflixNetflix:
    def __init__(self, root):
        self.root = root
        self.logger = LOGGER
        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state('zoomed')
        self.root.configure(bg="#141414")

        self.folders = []
        self.database = {}
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        self.stop_analysis = False

        # HTTP session reutilizável
        self.http_session = requests.Session()
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_retries = 3
        self.ollama_health_timeout = 4
        self._ollama_health_cache = {"ts": 0.0, "ok": None}

        # Modelos ativos (podem ser alterados via configurações)
        self.active_models = dict(OLLAMA_MODELS)

        # Cache de thumbnails (LRU simples)
        self.thumbnail_cache = OrderedDict()
        self.thumbnail_cache_limit = 300

        os.makedirs(BACKUP_FOLDER, exist_ok=True)

        self.load_config()
        self.load_database()
        self.create_ui()
        self.display_projects()
        self.schedule_auto_backup()

    # -----------------------------------------------------------------------
    # BACKUP / PERSISTÊNCIA
    # -----------------------------------------------------------------------
    def schedule_auto_backup(self):
        self.auto_backup()
        self.root.after(1800000, self.schedule_auto_backup)

    def auto_backup(self):
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
            LOGGER.exception("Falha no auto-backup")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.folders = config.get("folders", [])
                saved_models = config.get("models", {})
                if saved_models:
                    self.active_models.update(saved_models)

    def save_json_atomic(self, filepath, data, make_backup=True):
        tmp_file = filepath + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if make_backup and os.path.exists(filepath):
                try:
                    shutil.copy2(filepath, filepath + ".bak")
                except Exception:
                    self.logger.warning("Falha ao criar .bak de %s", filepath, exc_info=True)
            os.replace(tmp_file, filepath)
        except Exception:
            self.logger.error("Falha ao salvar JSON atômico: %s", filepath, exc_info=True)
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass

    def save_config(self):
        self.save_json_atomic(
            CONFIG_FILE,
            {"folders": self.folders, "models": self.active_models},
            make_backup=True,
        )

    def load_database(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                self.database = json.load(f)
                for path, data in self.database.items():
                    if "category" in data and "categories" not in data:
                        old_cat = data.get("category", "")
                        data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                        del data["category"]

    def save_database(self):
        self.save_json_atomic(DB_FILE, self.database, make_backup=True)

    # -----------------------------------------------------------------------
    # OLLAMA — HELPERS DE BAIXO NÍVEL
    # -----------------------------------------------------------------------
    def _ollama_is_available(self) -> bool:
        """Checa disponibilidade do Ollama com cache de 5s."""
        try:
            now = time.time()
            cached = self._ollama_health_cache
            if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < 5.0:
                return bool(cached["ok"])
            resp = self.http_session.get(
                f"{self.ollama_base_url}/api/tags",
                timeout=self.ollama_health_timeout,
            )
            ok = resp.status_code == 200
            self._ollama_health_cache = {"ts": now, "ok": ok}
            return ok
        except Exception:
            self._ollama_health_cache = {"ts": time.time(), "ok": False}
            return False

    def _model_name(self, role: str) -> str:
        """Retorna o nome do modelo configurado para o papel dado."""
        return self.active_models.get(role, OLLAMA_MODELS.get(role, ""))

    def _timeout(self, role: str):
        return TIMEOUTS.get(role, (5, 30))

    def _ollama_generate_text(
        self,
        prompt: str,
        *,
        role: str = "text_quality",
        temperature: float = 0.7,
        num_predict: int = 350,
    ) -> str:
        """
        Gera texto com o modelo definido por `role`.
        Usa instruction format adequado para Qwen2.5-Instruct.
        """
        if getattr(self, "stop_analysis", False):
            return ""
        if not self._ollama_is_available():
            self.logger.warning("Ollama indisponível. Usando fallback.")
            return ""

        model = self._model_name(role)
        timeout = self._timeout(role)

        # Qwen2.5-Instruct responde melhor com chat/messages format
        # Usamos /api/chat para garantir instruction-following correto
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente especialista em produtos de corte laser, "
                        "decoração artesanal e objetos afetivos personalizados. "
                        "Responda SEMPRE em português brasileiro. "
                        "Siga as instruções de formato com precisão."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": num_predict,
                "repeat_penalty": 1.1,
            },
        }

        last_err = None
        for attempt in range(1, self.ollama_retries + 1):
            if getattr(self, "stop_analysis", False):
                return ""
            try:
                resp = self.http_session.post(
                    f"{self.ollama_base_url}/api/chat",
                    json=payload,
                    timeout=timeout,
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                text = (data.get("message") or {}).get("content") or data.get("response") or ""
                self.logger.info("✅ [%s] gerou resposta (%d chars)", model, len(text))
                return text.strip()
            except Exception as e:
                last_err = e
                self.logger.warning("Ollama falhou (tentativa %d/%d) [%s]: %s", attempt, self.ollama_retries, model, e)
                if attempt < self.ollama_retries:
                    time.sleep(2.0)
        if last_err:
            self.logger.error("Ollama falhou definitivamente [%s]: %s", model, last_err, exc_info=True)
        return ""

    # -----------------------------------------------------------------------
    # VISÃO — FILTRO DE QUALIDADE + MOONDREAM
    # -----------------------------------------------------------------------

    def _image_quality_score(self, image_path: str) -> dict:
        """
        Avalia se a imagem tem qualidade suficiente para o Moondream analisar sem alucinar.
        Retorna dict com métricas e flag 'use_vision' (True = pode usar, False = ignora visão).

        Critérios de rejeição (imagem ambígua para visão):
          - Brilho médio > 210  (foto muito clara / fundo branco dominante)
          - Saturação média < 25 (quase monocromática)
          - % de pixels brancos > 50% (mockup com fundo branco)
        """
        try:
            from PIL import ImageStat
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                w, h = img_rgb.size
                # Analisa só a área central (remove bordas com marca d'água)
                box = (int(w*0.05), int(h*0.10), int(w*0.75), int(h*0.90))
                center = img_rgb.crop(box)

                # Brilho médio (canal L)
                gray = center.convert("L")
                stat_g = ImageStat.Stat(gray)
                brightness = stat_g.mean[0]

                # Saturação média (canal S do HSV)
                hsv = center.convert("HSV")
                stat_s = ImageStat.Stat(hsv)
                saturation = stat_s.mean[1]

                # % pixels brancos (R,G,B todos > 220)
                r, g, b = center.split()
                stat_r = ImageStat.Stat(r)
                stat_b = ImageStat.Stat(b)
                # Aproximação: pixels claros = brilho alto E baixo desvio
                white_pct = (brightness / 255.0) * max(0, 1.0 - (stat_g.stddev[0] / 80.0))
                white_pct_normalized = white_pct * 100

                use_vision = not (
                    brightness > 210 or
                    saturation < 25  or
                    white_pct_normalized > 50
                )

                self.logger.info(
                    "📊 [quality] brilho=%.1f sat=%.1f fundo_branco~%.1f%% → vision=%s",
                    brightness, saturation, white_pct_normalized, use_vision
                )
                return {
                    "brightness": brightness,
                    "saturation": saturation,
                    "white_pct":  white_pct_normalized,
                    "use_vision": use_vision,
                }
        except Exception as e:
            self.logger.warning("Falha em _image_quality_score: %s", e)
            return {"brightness": 0, "saturation": 100, "white_pct": 0, "use_vision": True}

    def _ollama_describe_image(self, image_path: str) -> str:
        """
        Usa moondream:latest para descrever o OBJETO CENTRAL da imagem.
        Prompt cirúrgico: ignora fundo, brinquedos e marcas d'água.
        Só é chamado quando _image_quality_score aprova a imagem.
        """
        if not image_path or not os.path.exists(image_path):
            return ""
        if not self._ollama_is_available():
            return ""

        model   = self._model_name("vision")
        timeout = self._timeout("vision")
        try:
            with Image.open(image_path) as img:
                img.thumbnail((512, 512), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            payload = {
                "model":  model,
                "prompt": (
                    "Look only at the main laser-cut wooden object in the center of this image. "
                    "Ignore the background, walls, stuffed animals, toys, watermarks and any text overlays. "
                    "Describe ONLY the central object: its shape, theme and style. "
                    "One short sentence. Be specific and factual."
                ),
                "images": [img_b64],
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 60},
            }
            resp = self.http_session.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=timeout,
            )
            if resp.status_code == 200:
                vision_text = (resp.json().get("response") or "").strip()
                self.logger.info("👁️ [moondream] %s", vision_text[:80])
                return vision_text
        except Exception as e:
            self.logger.warning("Falha ao descrever imagem com moondream: %s", e)
        return ""


    # -----------------------------------------------------------------------
    # ANÁLISE COM IA — PRINCIPAL
    # -----------------------------------------------------------------------
    def _choose_text_role(self, batch_size: int = 1) -> str:
        """Escolhe modelo rápido para lotes grandes, qualidade para análise individual."""
        if batch_size > FAST_MODEL_THRESHOLD:
            return "text_fast"
        return "text_quality"

    def analyze_with_ai(self, project_path: str, batch_size: int = 1):
        """
        Analisa um projeto e retorna (categories, tags).
        Integra visão (moondream) quando há imagem de capa disponível.
        Usa qwen2.5:7b para análise individual, :3b para lotes grandes.
        """
        try:
            name = os.path.basename(project_path)
            structure = self.analyze_project_structure(project_path)

            file_types_str = ", ".join(
                f"{ext} ({count}x)" for ext, count in structure["file_types"].items()
            )
            subfolders_str = (
                ", ".join(structure["subfolders"][:5]) if structure["subfolders"] else "nenhuma"
            )

            tech_context = []
            if structure["has_svg"]: tech_context.append("SVG vetorial")
            if structure["has_pdf"]: tech_context.append("PDF")
            if structure["has_dxf"]: tech_context.append("DXF/CAD")
            if structure["has_ai"]:  tech_context.append("Adobe Illustrator")
            tech_str = ", ".join(tech_context) if tech_context else "formatos variados"

            # Tenta descrição visual com moondream
            vision_line = ""
            cover_img = self._find_first_image_path(project_path)
            if cover_img:
                vision_desc = self._ollama_describe_image(cover_img)
                if vision_desc:
                    vision_line = f"\n🖼️ DESCRIÇÃO VISUAL DA CAPA: {vision_desc}"

            role = self._choose_text_role(batch_size)

            # Prompt otimizado para Qwen2.5-Instruct (instruction-following preciso)
            prompt = f"""Analise este produto de corte laser e responda EXATAMENTE no formato solicitado.

📁 NOME: {name}
📊 ARQUIVOS: {structure['total_files']} arquivos | Subpastas: {subfolders_str}
🗂️ TIPOS: {file_types_str}
🔧 FORMATOS: {tech_str}{vision_line}

### TAREFA 1 — CATEGORIAS
Atribua de 3 a 5 categorias, OBRIGATORIAMENTE nesta ordem:
1. Data Comemorativa (escolha UMA): Páscoa, Natal, Dia das Mães, Dia dos Pais, Dia dos Namorados, Aniversário, Casamento, Chá de Bebê, Halloween, Dia das Crianças, Ano Novo, Formatura, Diversos
2. Função/Tipo (escolha UMA): Porta-Retrato, Caixa Organizadora, Luminária, Porta-Joias, Porta-Chaves, Suporte, Quadro Decorativo, Painel de Parede, Mandala, Nome Decorativo, Letreiro, Lembrancinha, Chaveiro, Topo de Bolo, Centro de Mesa, Plaquinha, Brinquedo Educativo, Diversos
3. Ambiente (escolha UM): Quarto, Sala, Cozinha, Banheiro, Escritório, Quarto Infantil, Quarto de Bebê, Área Externa, Festa, Diversos
4. Estilo OPCIONAL (ex: Minimalista, Rústico, Moderno, Vintage, Romântico, Elegante)
5. Público OPCIONAL (ex: Bebê, Criança, Adulto, Casal, Família, Presente)

### TAREFA 2 — TAGS
Crie exatamente 8 tags relevantes:
- Primeiras 3: palavras-chave extraídas do nome "{name}" (sem códigos numéricos)
- Demais 5: emoção, ocasião, público, estilo, uso

### FORMATO DE RESPOSTA (siga exatamente):
Categorias: [cat1], [cat2], [cat3], [cat4 opcional], [cat5 opcional]
Tags: [tag1], [tag2], [tag3], [tag4], [tag5], [tag6], [tag7], [tag8]"""

            if self.stop_analysis:
                return self.fallback_analysis(project_path)

            text = self._ollama_generate_text(
                prompt,
                role=role,
                temperature=0.65,
                num_predict=200,
            )

            categories, tags = [], []

            if text:
                for line in text.split("\n"):
                    line = line.strip()
                    if line.startswith("Categorias:") or line.startswith("Categories:"):
                        raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                        categories = [c.strip().strip('"') for c in raw.split(",") if c.strip()]
                    elif line.startswith("Tags:"):
                        raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                        tags = [t.strip().strip('"') for t in raw.split(",") if t.strip()]

                # Garante tags do nome sempre presentes
                name_tags = self.extract_tags_from_name(name)
                for tag in name_tags:
                    if tag not in tags:
                        tags.insert(0, tag)

                tags = list(dict.fromkeys(tags))[:10]  # deduplica e limita

                if len(categories) < 3:
                    categories = self.fallback_categories(project_path, categories)

                return categories[:8], tags

        except Exception:
            LOGGER.exception("Erro em analyze_with_ai para %s", project_path)

        return self.fallback_analysis(project_path)

    # -----------------------------------------------------------------------
    # GERAÇÃO DE DESCRIÇÃO
    # -----------------------------------------------------------------------
    def generate_ai_description(self, project_path: str, data: dict):
        """
        Gera descrição comercial personalizada.

        HIERARQUIA (inviolável):
          1° NOME da peça  — âncora absoluta. Define o que o produto É.
          2° VISÃO (moondream) — detalhe visual SECUNDÁRIO, só se a imagem
             passa no filtro de qualidade (_image_quality_score).
             Nunca contradiz nem substitui o nome.

        Formato de saída:
            NOME DA PEÇA

            🎨 Por Que Este Produto é Especial:
            [2-3 frases afetivas e únicas baseadas no nome + visual se disponível]

            💖 Perfeito Para:
            [2-3 frases práticas com exemplos reais de uso e ocasião]
        """
        if getattr(self, "stop_analysis", False):
            return None

        structure = None
        try:
            structure = (
                data.get("structure")
                or self.database.get(project_path, {}).get("structure")
            )
            if not structure:
                structure = self.analyze_project_structure(project_path)
                if project_path in self.database:
                    self.database[project_path]["structure"] = structure
                else:
                    data["structure"] = structure

            # ── 1° NOME — âncora absoluta ──────────────────────────────
            raw_name = data.get("name", os.path.basename(project_path) or "Sem nome")
            clean_name = raw_name
            for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
                clean_name = clean_name.replace(ext, "")
            clean_name = re.sub(r"[-_]\d{5,}", "", clean_name)
            clean_name = clean_name.replace("-", " ").replace("_", " ").strip()

            # ── 2° VISÃO — só se imagem passa no filtro ────────────────
            vision_context = ""
            cover_img = self._find_first_image_path(project_path)
            if cover_img:
                quality = self._image_quality_score(cover_img)
                if quality["use_vision"]:
                    vision_desc = self._ollama_describe_image(cover_img)
                    if vision_desc:
                        vision_context = "\n\nDETALHE VISUAL (use apenas para complementar, nunca contradizer o nome): " + vision_desc
                else:
                    self.logger.info(
                        "⚠️ Visão desativada para %s (brilho=%.1f sat=%.1f fundo~%.1f%%)",
                        os.path.basename(project_path),
                        quality["brightness"], quality["saturation"], quality["white_pct"]
                    )

            if getattr(self, "stop_analysis", False):
                return None

            prompt = (
                "Você é especialista em peças físicas de corte a laser — placas, espelhos, "
                "porta-retratos, tabuletas, cabides, calendários, nomes decorativos e similares.\n\n"
                "NOME DA PEÇA (use isso como verdade absoluta sobre o que é o produto): " + clean_name
                + vision_context + "\n\n"
                "### REGRA FUNDAMENTAL:\n"
                "O NOME define o que é o produto. O detalhe visual apenas complementa.\n"
                "Nunca invente função ou formato que contradiga o nome.\n\n"
                "### RACIOCINE antes de escrever:\n"
                "1. O que exatamente é esta peça física, baseado no nome? (tipo de objeto)\n"
                "2. Para que serve na prática? (uso real no dia a dia)\n"
                "3. Que emoção ou momento ela representa? (conexão afetiva)\n\n"
                "### ESCREVA a descrição EXATAMENTE neste formato (sem nada além disso):\n\n"
                + clean_name + "\n\n"
                "\U0001f3a8 Por Que Este Produto é Especial:\n"
                "[2 a 3 frases afetivas e únicas. Fale sobre o que torna ESTA peça especial. "
                "Nunca use frases genéricas que servem para qualquer produto.]\n\n"
                "\U0001f496 Perfeito Para:\n"
                "[2 a 3 frases práticas com exemplos reais de uso e ocasião para ESTA peça específica.]\n\n"
                "### REGRAS OBRIGATÓRIAS:\n"
                "- Escreva em português brasileiro\n"
                "- Nunca use a palavra projeto — esta é uma PEÇA ou PRODUTO físico\n"
                "- Nunca mencione arquivos, SVG, PDF, formatos ou etapas de produção\n"
                "- Nunca repita frases que poderiam servir para qualquer outra peça\n"
                "- Máximo 120 palavras no total\n"
                "- Responda APENAS com o texto no formato acima, sem comentários adicionais"
            )

            response_text = self._ollama_generate_text(
                prompt,
                role="text_quality",
                temperature=0.78,
                num_predict=250,
            )

            if response_text:
                if not response_text.strip().startswith(clean_name[:15]):
                    response_text = clean_name + "\n\n" + response_text.strip()
                self.database.setdefault(project_path, {})
                self.database[project_path]["ai_description"]           = response_text.strip()
                self.database[project_path]["description_generated_at"] = datetime.now().isoformat()
                self.database[project_path]["description_model"]        = self._model_name("text_quality")
                self.database[project_path].setdefault("structure", structure)
                self.save_database()
                return response_text.strip()

            return self.generate_fallback_description(project_path, data, structure)

        except Exception as e:
            self.logger.error("Erro ao gerar descrição para %s: %s", project_path, e, exc_info=True)
            return self.generate_fallback_description(
                project_path, data,
                structure or self.analyze_project_structure(project_path)
            )

    # -----------------------------------------------------------------------
    # FALLBACKS (mantidos idênticos ao original)
    # -----------------------------------------------------------------------
    def fallback_categories(self, project_path, existing_categories):
        name = os.path.basename(project_path).lower()
        date_map = {
            "pascoa": "Páscoa", "easter": "Páscoa",
            "natal": "Natal", "christmas": "Natal",
            "mae": "Dia das Mães", "mother": "Dia das Mães",
            "pai": "Dia dos Pais", "father": "Dia dos Pais",
            "crianca": "Dia das Crianças", "children": "Dia das Crianças",
            "baby": "Chá de Bebê", "bebe": "Chá de Bebê",
            "wedding": "Casamento", "casamento": "Casamento",
            "birthday": "Aniversário", "aniversario": "Aniversário",
        }
        function_map = {
            "frame": "Porta-Retrato", "foto": "Porta-Retrato",
            "box": "Caixa Organizadora", "caixa": "Caixa Organizadora",
            "name": "Nome Decorativo", "nome": "Nome Decorativo",
            "sign": "Plaquinha Divertida", "placa": "Plaquinha Divertida",
            "quadro": "Quadro Decorativo", "painel": "Painel de Parede",
        }
        ambiente_map = {
            "nursery": "Quarto de Bebê", "baby": "Quarto de Bebê",
            "bedroom": "Quarto", "quarto": "Quarto",
            "kitchen": "Cozinha", "cozinha": "Cozinha",
            "living": "Sala", "sala": "Sala",
            "kids": "Quarto Infantil", "infantil": "Quarto Infantil",
        }
        result = list(existing_categories)
        date_cats = ["Páscoa", "Natal", "Dia das Mães", "Dia dos Pais", "Casamento", "Chá de Bebê", "Aniversário", "Dia das Crianças"]
        if not any(c in date_cats for c in result):
            for key, val in date_map.items():
                if key in name:
                    result.insert(0, val)
                    break
            else:
                result.insert(0, "Diversos")
        if len(result) < 2:
            for key, val in function_map.items():
                if key in name:
                    result.append(val)
                    break
            else:
                result.append("Diversos")
        if len(result) < 3:
            for key, val in ambiente_map.items():
                if key in name:
                    result.append(val)
                    break
            else:
                result.append("Diversos")
        return result

    def fallback_analysis(self, project_path):
        name = os.path.basename(project_path).lower()
        name_tags = self.extract_tags_from_name(os.path.basename(project_path))
        categories = ["Diversos", "Diversos", "Diversos"]
        context_tags = ["personalizado", "artesanal"]
        checks = [
            (["pascoa","easter","coelho"], 0, "Páscoa"),
            (["natal","christmas","noel"], 0, "Natal"),
            (["mae","mom","mother"],       0, "Dia das Mães"),
            (["pai","dad","father"],       0, "Dia dos Pais"),
            (["baby","bebe","shower"],     0, "Chá de Bebê"),
            (["frame","foto","photo"],     1, "Porta-Retrato"),
            (["box","caixa"],              1, "Caixa Organizadora"),
            (["name","nome","sign"],       1, "Nome Decorativo"),
            (["quadro","painel"],          1, "Quadro Decorativo"),
            (["nursery","baby"],           2, "Quarto de Bebê"),
            (["bedroom","quarto"],         2, "Quarto"),
            (["kitchen","cozinha"],        2, "Cozinha"),
            (["sala","living"],            2, "Sala"),
        ]
        for words, idx, val in checks:
            if any(w in name for w in words):
                categories[idx] = val
        all_tags = name_tags + context_tags
        seen, unique_tags = set(), []
        for tag in all_tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)
        return categories, unique_tags[:10]

    def generate_fallback_description(self, project_path, data, structure):
        """
        Fallback sem IA: respeita o formato obrigatório Nome / Especial / Perfeito Para.
        Baseado no nome e tags — nunca menciona arquivos ou formatos.
        """
        raw_name = data.get("name", "Sem nome")
        clean_name = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            clean_name = clean_name.replace(ext, "")
        clean_name = re.sub(r"[-_]\d{5,}", "", clean_name)
        clean_name = clean_name.replace("-", " ").replace("_", " ").strip()

        tags      = data.get("tags", [])
        tags_lower = " ".join(tags).lower()
        name_lower = clean_name.lower()

        if any(w in name_lower or w in tags_lower for w in ["hanger", "coat hanger", "cabide"]):
            especial = (
                "Um cabide infantil encantador que transforma o quarto da criança "
                "em um cantinho cheio de personalidade e organização."
            )
            perfeito = (
                "Perfeito para organizar roupinhas no quarto infantil com charme. "
                "Ótimo presente para bebês e crianças em aniversários ou chá de bebê."
            )
        elif any(w in name_lower or w in tags_lower for w in ["mirror", "espelho"]):
            especial = (
                "Um espelho decorativo único, cortado a laser com precisão, "
                "que combina funcionalidade e arte para o ambiente infantil."
            )
            perfeito = (
                "Ideal para decorar quarto de bebê ou quarto infantil com estilo. "
                "Um presente memorável para maternidades e enxovais."
            )
        elif any(w in name_lower or w in tags_lower for w in ["calendar", "calendário", "calendario"]):
            especial = (
                "Um calendário decorativo que une organização e arte, "
                "tornando cada dia especial com detalhes únicos e lúdicos."
            )
            perfeito = (
                "Perfeito para quartos infantis, escritórios ou como presente criativo. "
                "Ideal para datas especiais e presentes personalizados."
            )
        elif any(w in name_lower or w in tags_lower for w in ["frame", "quadro", "porta-retrato"]):
            especial = (
                "Um porta-retrato artesanal que transforma memórias em arte, "
                "criando um objeto único cheio de afeto e significado."
            )
            perfeito = (
                "Exaltar momentos especiais na decoração de qualquer ambiente. "
                "Presente ideal para aniversários, casamentos e datas comemorativas."
            )
        elif any(w in name_lower or w in tags_lower for w in ["bebe", "baby", "nursery", "maternidade"]):
            especial = (
                "Uma peça especial que marca os primeiros momentos da vida, "
                "cheia de carinho e significado para toda a família."
            )
            perfeito = (
                "Presente perfeito para chá de bebê, decoração de quarto de bebê "
                "ou como lembrança afetiva dos primeiros anos."
            )
        elif any(w in name_lower or w in tags_lower for w in ["wedding", "casamento", "noiva"]):
            especial = (
                "Uma peça elegante que celebra o amor e marca para sempre "
                "o dia mais especial do casal."
            )
            perfeito = (
                "Ideal para decoração de cerimônia, recepção de convidados "
                "ou como presente inesquecível para os noivos."
            )
        elif any(w in name_lower or w in tags_lower for w in ["natal", "christmas", "pascoa", "easter"]):
            especial = (
                "Uma peça que traz o espírito da data para o ambiente, "
                "criando memórias afetivas para toda a família."
            )
            perfeito = (
                "Ideal para decoração sazonal, presente personalizado "
                "ou lembrancinha especial da época."
            )
        else:
            categories  = data.get("categories", ["Diversos"])
            cat_display = " | ".join(categories[:3]) if categories else "Produto personalizado"
            especial = (
                f"Uma peça de corte a laser em {cat_display}, "
                "criada para ser única e transmitir afeto em cada detalhe."
            )
            perfeito = (
                "Ideal como presente personalizado, decoração de ambiente "
                "ou lembrança especial para quem você ama."
            )

        description = (
            clean_name + "\n\n"
            "\U0001f3a8 Por Que Este Produto é Especial:\n"
            + especial + "\n\n"
            "\U0001f496 Perfeito Para:\n"
            + perfeito
        )

        self.database.setdefault(project_path, {})
        self.database[project_path]["ai_description"]           = description
        self.database[project_path]["description_generated_at"] = datetime.now().isoformat()
        self.save_database()
        return description

    # -----------------------------------------------------------------------
    # ANÁLISE DE ESTRUTURA / TAGS (sem alterações)
    # -----------------------------------------------------------------------
    def get_origin_from_path(self, project_path):
        try:
            parent_folder = os.path.basename(os.path.dirname(project_path))
            parent_upper = parent_folder.upper()
            if "CREATIVE" in parent_upper or "FABRICA" in parent_upper:
                return "Creative Fabrica"
            elif "ETSY" in parent_upper:
                return "Etsy"
            else:
                return parent_folder
        except Exception:
            return "Diversos"

    def analyze_project_structure(self, project_path):
        structure = {
            "total_files": 0, "total_subfolders": 0,
            "file_types": {}, "subfolders": [],
            "images": [], "documents": [],
            "has_svg": False, "has_pdf": False, "has_dxf": False, "has_ai": False,
        }
        try:
            for root, dirs, files in os.walk(project_path):
                structure["total_files"] += len(files)
                if root == project_path:
                    structure["subfolders"] = dirs
                    structure["total_subfolders"] = len(dirs)
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                    if ext == ".svg": structure["has_svg"] = True
                    elif ext == ".pdf": structure["has_pdf"] = True
                    elif ext == ".dxf": structure["has_dxf"] = True
                    elif ext == ".ai":  structure["has_ai"]  = True
                    if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"):
                        structure["images"].append(file)
                    elif ext in (".pdf", ".txt", ".doc", ".docx"):
                        structure["documents"].append(file)
        except Exception:
            LOGGER.exception("Falha ao analisar estrutura de %s", project_path)
        return structure

    def extract_tags_from_name(self, name):
        name_clean = name
        for ext in [".zip", ".rar", ".7z", ".svg", ".pdf", ".dxf"]:
            name_clean = name_clean.replace(ext, "")
        name_clean = re.sub(r"[-_]\d{5,}", "", name_clean)
        name_clean = name_clean.replace("-", " ").replace("_", " ")
        stop_words = {"file", "files", "project", "design", "laser", "cut", "svg",
                      "pdf", "vector", "bundle", "pack", "set", "collection"}
        words = [w for w in name_clean.split() if len(w) >= 2 and not w.isdigit() and w.lower() not in stop_words]
        tags = []
        if len(words) >= 2:
            phrase = " ".join(words[:4])
            if len(phrase) > 3:
                tags.append(phrase.title())
        for w in words[:5]:
            if len(w) >= 3:
                tags.append(w.capitalize())
        seen, unique = set(), []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                unique.append(t)
        return unique[:5]

    # -----------------------------------------------------------------------
    # IMAGENS / THUMBNAILS (sem alterações)
    # -----------------------------------------------------------------------
    def _find_first_image_path(self, project_path):
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            LOGGER.exception("Falha ao listar %s", project_path)
        return None

    def _load_thumbnail_photo(self, img_path):
        img = Image.open(img_path)
        img.thumbnail((220, 200), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def get_cover_image(self, project_path):
        img_path = self._find_first_image_path(project_path)
        if not img_path:
            return None
        try:
            mtime = os.path.getmtime(img_path)
        except Exception:
            return None
        try:
            cached = self.thumbnail_cache.get(img_path)
            if cached:
                cached_mtime, cached_photo = cached
                if cached_mtime == mtime:
                    self.thumbnail_cache.move_to_end(img_path)
                    return cached_photo
            photo = self._load_thumbnail_photo(img_path)
            self.thumbnail_cache[img_path] = (mtime, photo)
            self.thumbnail_cache.move_to_end(img_path)
            while len(self.thumbnail_cache) > self.thumbnail_cache_limit:
                self.thumbnail_cache.popitem(last=False)
            return photo
        except Exception:
            LOGGER.exception("Erro ao gerar thumbnail de %s", img_path)
            return None

    def get_hero_image(self, project_path):
        try:
            valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    img_path = os.path.join(project_path, item)
                    img = Image.open(img_path)
                    max_width = 800
                    if img.width > max_width:
                        ratio = max_width / img.width
                        img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
        except Exception:
            LOGGER.exception("Falha ao carregar hero image de %s", project_path)
        return None

    def get_all_project_images(self, project_path):
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        images = []
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    images.append(os.path.join(project_path, item))
        except Exception:
            LOGGER.exception("Falha ao listar imagens de %s", project_path)
        return sorted(images)

    # -----------------------------------------------------------------------
    # AÇÕES INDIVIDUAIS
    # -----------------------------------------------------------------------
    def toggle_favorite(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("favorite", False)
            self.database[project_path]["favorite"] = new_val
            self.save_database()
            if btn:
                btn.config(text="⭐" if new_val else "☆",
                           fg="#FFD700" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_done(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("done", False)
            self.database[project_path]["done"] = new_val
            self.save_database()
            if btn:
                btn.config(text="✓" if new_val else "○",
                           fg="#00FF00" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_good(self, project_path, btn=None):
        if project_path in self.database:
            current = self.database[project_path].get("good", False)
            new_val = not current
            self.database[project_path]["good"] = new_val
            if new_val:
                self.database[project_path]["bad"] = False
            self.save_database()
            if btn:
                btn.config(fg="#00FF00" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_bad(self, project_path, btn=None):
        if project_path in self.database:
            current = self.database[project_path].get("bad", False)
            new_val = not current
            self.database[project_path]["bad"] = new_val
            if new_val:
                self.database[project_path]["good"] = False
            self.save_database()
            if btn:
                btn.config(fg="#FF0000" if new_val else "#666666")
            else:
                self.display_projects()

    def analyze_single_project(self, project_path):
        self.status_bar.config(text="🤖 Analisando com IA...")
        def analyze():
            categories, tags = self.analyze_with_ai(project_path, batch_size=1)
            self.database[project_path]["categories"] = categories
            self.database[project_path]["tags"] = tags
            self.database[project_path]["analyzed"] = True
            self.database[project_path]["analyzed_model"] = self._model_name("text_quality")
            self.save_database()
            self.root.after(0, self.update_sidebar)
            self.root.after(0, self.display_projects)
            self.root.after(0, lambda: self.status_bar.config(text="✓ Análise concluída"))
        threading.Thread(target=analyze, daemon=True).start()

    def open_folder(self, folder_path):
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

    def open_image(self, image_path):
        try:
            if platform.system() == "Windows":
                os.startfile(image_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", image_path])
            else:
                subprocess.run(["xdg-open", image_path])
        except Exception:
            messagebox.showerror("Erro", "Erro ao abrir imagem")

    def add_tag_to_listbox(self, listbox):
        new_tag = simpledialog.askstring("Nova Tag", "Digite a nova tag:", parent=self.root)
        if new_tag and new_tag.strip():
            new_tag = new_tag.strip()
            if new_tag not in listbox.get(0, tk.END):
                listbox.insert(tk.END, new_tag)

    def remove_tag_from_listbox(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"#{max(0,int(r*0.8)):02x}{max(0,int(g*0.8)):02x}{max(0,int(b*0.8)):02x}"

    # -----------------------------------------------------------------------
    # SCAN / FILTROS
    # -----------------------------------------------------------------------
    def add_folders(self):
        folder = filedialog.askdirectory(title="Selecione uma pasta de projetos")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.save_config()
            self.scan_projects()
            messagebox.showinfo("✓", f"Pasta adicionada!\n{folder}")

    def scan_projects(self):
        new_count = 0
        for root_folder in self.folders:
            if not os.path.exists(root_folder):
                continue
            for item in os.listdir(root_folder):
                project_path = os.path.join(root_folder, item)
                if os.path.isdir(project_path) and project_path not in self.database:
                    self.database[project_path] = {
                        "name": item,
                        "origin": self.get_origin_from_path(project_path),
                        "favorite": False, "done": False, "good": False, "bad": False,
                        "categories": [], "tags": [], "analyzed": False,
                        "ai_description": "", "added_date": datetime.now().isoformat(),
                    }
                    new_count += 1
        if new_count > 0:
            self.save_database()
            self.update_sidebar()
            self.display_projects()
            self.status_bar.config(text=f"✓ {new_count} novos projetos")

    def get_filtered_projects(self):
        filtered = []
        for project_path, data in self.database.items():
            show = (
                self.current_filter == "all"
                or (self.current_filter == "favorite" and data.get("favorite"))
                or (self.current_filter == "done"     and data.get("done"))
                or (self.current_filter == "good"     and data.get("good"))
                or (self.current_filter == "bad"      and data.get("bad"))
            )
            if not show: continue
            if self.current_origin != "all" and data.get("origin") != self.current_origin: continue
            if self.current_categories and not any(c in data.get("categories", []) for c in self.current_categories): continue
            if self.current_tag and self.current_tag not in data.get("tags", []): continue
            if self.search_query and self.search_query not in data.get("name", "").lower(): continue
            filtered.append(project_path)
        return filtered

    # -----------------------------------------------------------------------
    # ANÁLISE EM LOTE
    # -----------------------------------------------------------------------
    def analyze_only_new(self):
        if self.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        unanalyzed = [p for p, d in self.database.items() if not d.get("analyzed")]
        if not unanalyzed:
            messagebox.showinfo("ℹ️", "Todos os projetos já foram analisados!")
            return
        model_info = self._model_name("text_fast") if len(unanalyzed) > FAST_MODEL_THRESHOLD else self._model_name("text_quality")
        if messagebox.askyesno("🆕 Analisar Novos",
                               f"Analisar {len(unanalyzed)} projetos novos?\n\n"
                               f"Modelo: {model_info}\n"
                               f"Você poderá interromper a qualquer momento."):
            self.run_analysis(unanalyzed, "novos")

    def reanalyze_all(self):
        if self.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        all_projects = list(self.database.keys())
        if not all_projects:
            messagebox.showinfo("ℹ️", "Nenhum projeto encontrado!")
            return
        if messagebox.askyesno("⚠️ Reanalisar Todos",
                               f"Reanalisar TODOS os {len(all_projects)} projetos?\n"
                               f"Categorias e tags existentes serão SUBSTITUÍDAS.\n\n"
                               f"Deseja criar um backup antes?", icon="warning"):
            self.manual_backup()
        if messagebox.askyesno("🔄 Confirmar Reanalise",
                               f"Prosseguir com a reanálise de {len(all_projects)} projetos?"):
            self.run_analysis(all_projects, "todos")

    def analyze_current_filter(self):
        if self.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        filtered = self.get_filtered_projects()
        if not filtered:
            messagebox.showinfo("ℹ️", "Nenhum projeto no filtro atual!")
            return
        if messagebox.askyesno("📊 Analisar Filtro", f"Analisar {len(filtered)} projetos?"):
            self.run_analysis(filtered, "filtro atual")

    def reanalyze_specific_category(self):
        if self.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        all_cats = set()
        for d in self.database.values():
            all_cats.update(d.get("categories", []))
        categories = sorted([c for c in all_cats if c and c != "Sem Categoria"])
        if not categories:
            messagebox.showinfo("ℹ️", "Nenhuma categoria encontrada!")
            return
        cat_win = tk.Toplevel(self.root)
        cat_win.title("🎯 Selecionar Categoria")
        cat_win.state("zoomed")
        cat_win.configure(bg="#141414")
        cat_win.transient(self.root)
        cat_win.grab_set()
        tk.Label(cat_win, text="🎯 Reanalisar Categoria", font=("Arial", 18, "bold"),
                 bg="#141414", fg="#E50914").pack(pady=15)
        tk.Label(cat_win, text="Selecione a categoria:", font=("Arial", 11),
                 bg="#141414", fg="#FFFFFF").pack(pady=(0, 10))
        list_frame = tk.Frame(cat_win, bg="#2A2A2A")
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        listbox = tk.Listbox(list_frame, bg="#2A2A2A", fg="#FFFFFF", font=("Arial", 11),
                             selectmode=tk.SINGLE, yscrollcommand=scrollbar.set,
                             relief="flat", selectbackground="#E50914", selectforeground="#FFFFFF")
        listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=listbox.yview)
        for cat in categories:
            count = sum(1 for d in self.database.values() if cat in d.get("categories", []))
            listbox.insert(tk.END, f"{cat} ({count} projetos)")
        selected_category = [None]
        def on_select():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Atenção", "Selecione uma categoria!")
                return
            selected_category[0] = categories[selection[0]]
            cat_win.destroy()
        btn_frame = tk.Frame(cat_win, bg="#141414")
        btn_frame.pack(fill="x", padx=20, pady=15)
        tk.Button(btn_frame, text="✓ Confirmar", command=on_select,
                  bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="✕ Cancelar", command=cat_win.destroy,
                  bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10).pack(side="right", padx=5)
        cat_win.wait_window()
        if not selected_category[0]:
            return
        projects = [p for p, d in self.database.items() if selected_category[0] in d.get("categories", [])]
        if messagebox.askyesno("🎯 Confirmar",
                               f"Reanalisar {len(projects)} projetos da categoria '{selected_category[0]}'?"):
            self.run_analysis(projects, f"categoria '{selected_category[0]}'")

    def run_analysis(self, projects_list, description):
        self.analyzing = True
        self.stop_analysis = False
        total = len(projects_list)
        role = self._choose_text_role(total)
        model_used = self._model_name(role)

        def analyze_batch():
            self.root.after(0, self.show_progress_ui)
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.stop_analysis:
                    break
                project_name = self.database[path].get("name", "Sem nome")[:30]
                self.root.after(0, lambda i=i, t=total, n=project_name:
                                self.update_progress(i, t, f"🤖 [{model_used[:15]}] {n}"))
                categories, tags = self.analyze_with_ai(path, batch_size=total)
                self.database[path]["categories"] = categories
                self.database[path]["tags"] = tags
                self.database[path]["analyzed"] = True
                self.database[path]["analyzed_model"] = model_used
                self.save_database()
                completed = i
            self.analyzing = False
            final_msg = f"✓ {completed} projetos analisados ({description}) [{model_used}]"
            if self.stop_analysis and completed < total:
                final_msg = f"⏹ Parado: {completed}/{total} ({description})"
            self.root.after(0, self.update_sidebar)
            self.root.after(0, self.display_projects)
            self.root.after(0, lambda: self.status_bar.config(text=final_msg))
            self.root.after(0, self.hide_progress_ui)
            self.root.after(0, lambda: messagebox.showinfo(
                "✓ Concluído" if not self.stop_analysis else "⏹ Interrompido", final_msg))
            self.stop_analysis = False

        threading.Thread(target=analyze_batch, daemon=True).start()

    # -----------------------------------------------------------------------
    # GERAÇÃO DE DESCRIÇÕES EM LOTE
    # -----------------------------------------------------------------------
    def generate_descriptions_for_new(self):
        if self.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        projects = [p for p, d in self.database.items()
                    if not (d.get("ai_description") or "").strip()]
        if not projects:
            messagebox.showinfo("ℹ️", "Todos os projetos já têm descrição!")
            return
        if messagebox.askyesno("📝 Gerar Descrições",
                               f"Gerar descrições com IA para {len(projects)} projetos?\n"
                               f"Modelo: {self._model_name('text_quality')}"):
            self.run_description_generation(projects, "projetos sem descrição")

    def generate_descriptions_for_all(self):
        if self.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        all_projects = list(self.database.keys())
        if not all_projects:
            messagebox.showinfo("ℹ️", "Nenhum projeto encontrado!")
            return
        if messagebox.askyesno("⚠️ Gerar para Todos",
                               f"Substituir descrições de TODOS os {len(all_projects)} projetos?\n"
                               f"Deseja backup antes?", icon="warning"):
            self.manual_backup()
        if messagebox.askyesno("📝 Confirmar", f"Gerar {len(all_projects)} descrições?"):
            self.run_description_generation(all_projects, "todos os projetos")

    def generate_descriptions_for_filter(self):
        if self.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        filtered = self.get_filtered_projects()
        if not filtered:
            messagebox.showinfo("ℹ️", "Nenhum projeto no filtro atual!")
            return
        if messagebox.askyesno("📝 Gerar Descrições do Filtro",
                               f"Gerar descrições para {len(filtered)} projetos do filtro atual?"):
            self.run_description_generation(filtered, "filtro atual")

    def run_description_generation(self, projects_list, description):
        self.analyzing = True
        self.stop_analysis = False
        total = len(projects_list)

        def generate_batch():
            self.root.after(0, self.show_progress_ui)
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.stop_analysis:
                    break
                project_name = self.database[path].get("name", "Sem nome")[:30]
                self.root.after(0, lambda i=i, t=total, n=project_name:
                                self.update_progress(i, t, f"📝 Gerando: {n}"))
                self.generate_ai_description(path, self.database[path])
                completed = i
            self.analyzing = False
            final_msg = f"✓ {completed} descrições geradas ({description})"
            if self.stop_analysis and completed < total:
                final_msg = f"⏹ Parado: {completed}/{total} descrições ({description})"
            self.root.after(0, lambda: self.status_bar.config(text=final_msg))
            self.root.after(0, self.hide_progress_ui)
            self.root.after(0, lambda: messagebox.showinfo(
                "✓ Concluído" if not self.stop_analysis else "⏹ Interrompido", final_msg))
            self.stop_analysis = False

        threading.Thread(target=generate_batch, daemon=True).start()

    # -----------------------------------------------------------------------
    # BACKUP MANUAL / IMPORT / EXPORT
    # -----------------------------------------------------------------------
    def manual_backup(self):
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

    def export_database(self):
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

    def import_database(self):
        if messagebox.askyesno("⚠️ Atenção", "Importar substituirá todos os dados. Fazer backup?"):
            self.manual_backup()
        filename = filedialog.askopenfilename(title="Importar Banco", filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    imported_data = json.load(f)
                if not isinstance(imported_data, dict):
                    messagebox.showerror("Erro", "Arquivo inválido!")
                    return
                shutil.copy2(DB_FILE, DB_FILE + ".pre-import.backup")
                self.database = imported_data
                self.save_database()
                self.update_sidebar()
                self.display_projects()
                messagebox.showinfo("✓", f"Banco importado! {len(self.database)} projetos.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}")

    # -----------------------------------------------------------------------
    # CONFIGURAÇÕES DE MODELOS (NOVO)
    # -----------------------------------------------------------------------
    def open_model_settings(self):
        """Janela para configurar qual modelo usar em cada papel."""
        win = tk.Toplevel(self.root)
        win.title("⚙️ Configurar Modelos de IA")
        win.configure(bg="#141414")
        win.geometry("600x420")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="⚙️ Configurar Modelos Ollama", font=("Arial", 16, "bold"),
                 bg="#141414", fg="#E50914").pack(pady=15)

        # Detecta modelos disponíveis
        available = []
        try:
            resp = self.http_session.get(f"{self.ollama_base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                available = [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            pass

        roles_labels = {
            "text_quality": "🧠 Modelo Qualidade (análise individual/descrições)",
            "text_fast":    "⚡ Modelo Rápido (lotes grandes)",
            "vision":       "👁️ Modelo Visão (análise de imagens)",
            "embed":        "🔗 Modelo Embeddings (busca semântica)",
        }

        entries = {}
        for role, label in roles_labels.items():
            frame = tk.Frame(win, bg="#141414")
            frame.pack(fill="x", padx=25, pady=6)
            tk.Label(frame, text=label, font=("Arial", 10, "bold"),
                     bg="#141414", fg="#CCCCCC", width=48, anchor="w").pack(side="left")
            var = tk.StringVar(value=self.active_models.get(role, ""))
            if available:
                cb = ttk.Combobox(frame, textvariable=var, values=available, width=32, state="normal")
            else:
                cb = tk.Entry(frame, textvariable=var, bg="#2A2A2A", fg="#FFFFFF",
                              font=("Arial", 10), width=35, relief="flat")
            cb.pack(side="left", padx=5)
            entries[role] = var

        status_lbl = tk.Label(win, text="", bg="#141414", fg="#1DB954", font=("Arial", 10))
        status_lbl.pack(pady=5)

        if not available:
            status_lbl.config(text="⚠️ Ollama offline — digitando modelos manualmente", fg="#FF6B6B")

        def save_models():
            for role, var in entries.items():
                val = var.get().strip()
                if val:
                    self.active_models[role] = val
            self.save_config()
            status_lbl.config(text="✓ Modelos salvos!", fg="#1DB954")
            self.root.after(1500, win.destroy)

        btn_frame = tk.Frame(win, bg="#141414")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="💾 Salvar", command=save_models,
                  bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="✕ Cancelar", command=win.destroy,
                  bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)

    # -----------------------------------------------------------------------
    # UI PRINCIPAL
    # -----------------------------------------------------------------------
    def create_ui(self):
        header = tk.Frame(self.root, bg="#000000", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="LASERFLIX", font=("Arial", 28, "bold"),
                 bg="#000000", fg="#E50914").pack(side="left", padx=20, pady=10)
        tk.Label(header, text=f"v{VERSION}", font=("Arial", 10),
                 bg="#000000", fg="#666666").pack(side="left", padx=5)
        nav_frame = tk.Frame(header, bg="#000000")
        nav_frame.pack(side="left", padx=30)
        for text, filter_type in [("🏠 Home","all"),("⭐ Favoritos","favorite"),
                                   ("✓ Já Feitos","done"),("👍 Bons","good"),("👎 Ruins","bad")]:
            btn = tk.Button(nav_frame, text=text, command=lambda f=filter_type: self.set_filter(f),
                            bg="#000000", fg="#FFFFFF", font=("Arial", 12),
                            relief="flat", cursor="hand2", padx=10)
            btn.pack(side="left", padx=5)
            btn.bind("<Enter>", lambda e, w=btn: w.config(fg="#E50914"))
            btn.bind("<Leave>", lambda e, w=btn: w.config(fg="#FFFFFF"))
        search_frame = tk.Frame(header, bg="#000000")
        search_frame.pack(side="right", padx=20)
        tk.Label(search_frame, text="🔍", bg="#000000", fg="#FFFFFF", font=("Arial", 16)).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search())
        tk.Entry(search_frame, textvariable=self.search_var, bg="#333333", fg="#FFFFFF",
                 font=("Arial", 12), width=30, relief="flat", insertbackground="#FFFFFF"
                 ).pack(side="left", padx=5, ipady=5)
        extras_frame = tk.Frame(header, bg="#000000")
        extras_frame.pack(side="right", padx=10)
        # Menu principal
        menu_btn = tk.Menubutton(extras_frame, text="⚙️ Menu", bg="#1DB954", fg="#FFFFFF",
                                 font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8)
        menu_btn.pack(side="left", padx=5)
        menu = tk.Menu(menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF")
        menu_btn["menu"] = menu
        menu.add_command(label="📊 Dashboard", command=self.open_dashboard)
        menu.add_command(label="📝 Edição em Lote", command=self.open_batch_edit)
        menu.add_separator()
        menu.add_command(label="🤖 Configurar Modelos IA", command=self.open_model_settings)
        menu.add_separator()
        menu.add_command(label="💾 Exportar Banco", command=self.export_database)
        menu.add_command(label="📥 Importar Banco", command=self.import_database)
        menu.add_command(label="🔄 Backup Manual", command=self.manual_backup)
        # Botão pastas
        tk.Button(extras_frame, text="➕ Pastas", command=self.add_folders,
                  bg="#E50914", fg="#FFFFFF", font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)
        # Menu analisar
        ai_menu_btn = tk.Menubutton(extras_frame, text="🤖 Analisar", bg="#1DB954", fg="#FFFFFF",
                                    font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8)
        ai_menu_btn.pack(side="left", padx=5)
        ai_menu = tk.Menu(ai_menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF",
                          font=("Arial", 10), activebackground="#E50914", activeforeground="#FFFFFF")
        ai_menu_btn["menu"] = ai_menu
        ai_menu.add_command(label="🆕 Analisar apenas novos", command=self.analyze_only_new)
        ai_menu.add_command(label="🔄 Reanalisar todos", command=self.reanalyze_all)
        ai_menu.add_command(label="📊 Analisar filtro atual", command=self.analyze_current_filter)
        ai_menu.add_separator()
        ai_menu.add_command(label="🎯 Reanalisar categoria específica", command=self.reanalyze_specific_category)
        ai_menu.add_separator()
        ai_menu.add_command(label="📝 Gerar descrições para novos", command=self.generate_descriptions_for_new)
        ai_menu.add_command(label="📝 Gerar descrições para todos", command=self.generate_descriptions_for_all)
        ai_menu.add_command(label="📝 Gerar descrições do filtro atual", command=self.generate_descriptions_for_filter)
        # Área de conteúdo
        main_container = tk.Frame(self.root, bg="#141414")
        main_container.pack(fill="both", expand=True)
        self.create_sidebar(main_container)
        content_frame = tk.Frame(main_container, bg="#141414")
        content_frame.pack(side="left", fill="both", expand=True)
        self.content_canvas = tk.Canvas(content_frame, bg="#141414", highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_canvas.yview)
        self.scrollable_frame = tk.Frame(self.content_canvas, bg="#141414")
        self.scrollable_frame.bind("<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all")))
        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=content_scrollbar.set)
        self.content_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        content_scrollbar.pack(side="right", fill="y")
        def _on_mw(event): self.content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.content_canvas.bind("<Enter>", lambda e: self.content_canvas.bind("<MouseWheel>", _on_mw))
        self.content_canvas.bind("<Leave>", lambda e: self.content_canvas.unbind("<MouseWheel>"))
        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#000000", height=50)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        self.status_bar = tk.Label(self.status_frame, text="Pronto", bg="#000000",
                                   fg="#FFFFFF", font=("Arial", 10), anchor="w")
        self.status_bar.pack(side="left", padx=10, fill="both", expand=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor="#2A2A2A", background="#1DB954",
                        bordercolor="#000000", lightcolor="#1DB954", darkcolor="#1DB954")
        self.progress_bar = ttk.Progressbar(self.status_frame, mode="determinate",
                                            length=300, style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.pack_forget()
        self.stop_button = tk.Button(self.status_frame, text="⏹ Parar Análise",
                                     command=self.stop_analysis_process,
                                     bg="#E50914", fg="#FFFFFF", font=("Arial", 10, "bold"),
                                     relief="flat", cursor="hand2", padx=15, pady=8)
        self.stop_button.pack(side="right", padx=10)
        self.stop_button.pack_forget()

    def stop_analysis_process(self):
        self.stop_analysis = True
        self.status_bar.config(text="⏹ Parando análise...")

    def update_progress(self, current, total, message=""):
        percentage = (current / total) * 100
        self.progress_bar["value"] = percentage
        self.status_bar.config(text=f"{message} ({current}/{total} — {percentage:.1f}%)")
        self.root.update_idletasks()

    def show_progress_ui(self):
        self.progress_bar.pack(side="left", padx=10)
        self.stop_button.pack(side="right", padx=10)
        self.progress_bar["value"] = 0

    def hide_progress_ui(self):
        self.progress_bar.pack_forget()
        self.stop_button.pack_forget()

    def set_filter(self, filter_type):
        self.current_filter = filter_type
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_var.set("")
        self._set_active_sidebar_btn(None)
        self.display_projects()

    def on_search(self):
        self.search_query = self.search_var.get().strip().lower()
        self.display_projects()

    # -----------------------------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------------------------
    def _bind_sidebar_scroll(self, widget):
        """Propaga MouseWheel recursivamente a todos os filhos da sidebar."""
        def _scroll(e):
            self.sidebar_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        widget.bind("<MouseWheel>", _scroll)
        for child in widget.winfo_children():
            self._bind_sidebar_scroll(child)

    def _set_active_sidebar_btn(self, btn):
        try:
            if getattr(self, "_active_sidebar_btn", None) is not None:
                self._active_sidebar_btn.config(bg="#1A1A1A")
        except Exception: pass
        self._active_sidebar_btn = btn
        try:
            if btn is not None: btn.config(bg="#E50914")
        except Exception: pass

    def create_sidebar(self, parent):
        sidebar_container = tk.Frame(parent, bg="#1A1A1A", width=250)
        sidebar_container.pack(side="left", fill="both")
        sidebar_container.pack_propagate(False)
        self.sidebar_canvas = tk.Canvas(sidebar_container, bg="#1A1A1A", highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(sidebar_container, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_content = tk.Frame(self.sidebar_canvas, bg="#1A1A1A")
        self.sidebar_content.bind("<Configure>",
            lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar_content, anchor="nw", width=230)
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        self.sidebar_canvas.bind("<MouseWheel>",
            lambda e: self.sidebar_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        for title, attr in [
            ("🌐 Origem", "origins_frame"),
            ("📂 Categorias", "categories_frame"),
            ("🏷️ Tags Populares", "tags_frame"),
        ]:
            tk.Label(self.sidebar_content, text=title, font=("Arial", 14, "bold"),
                     bg="#1A1A1A", fg="#FFFFFF", anchor="w").pack(fill="x", padx=15, pady=(15, 5))
            frame = tk.Frame(self.sidebar_content, bg="#1A1A1A")
            frame.pack(fill="x", padx=10, pady=5)
            setattr(self, attr, frame)
            tk.Frame(self.sidebar_content, bg="#333333", height=2).pack(fill="x", padx=10, pady=10)

        tk.Frame(self.sidebar_content, bg="#1A1A1A", height=50).pack(fill="x")
        self.update_sidebar()

    def update_sidebar(self):
        self.update_origins_list()
        self.update_categories_list()
        self.update_tags_list()
        self._bind_sidebar_scroll(self.sidebar_content)

    def update_origins_list(self):
        for w in self.origins_frame.winfo_children(): w.destroy()
        origins = {}
        for d in self.database.values():
            o = d.get("origin", "Desconhecido")
            origins[o] = origins.get(o, 0) + 1
        colors = {"Creative Fabrica": "#FF6B35", "Etsy": "#F7931E", "Diversos": "#4ECDC4"}
        for origin in sorted(origins):
            color = colors.get(origin, "#9B59B6")
            btn = tk.Button(self.origins_frame, text=f"{origin} ({origins[origin]})",
                            bg="#1A1A1A", fg=color, font=("Arial", 10, "bold"),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=8)
            btn.config(command=lambda o=origin, b=btn: self.set_origin_filter(o, b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2A2A2A") if b is not getattr(self, "_active_sidebar_btn", None) else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1A1A1A") if b is not getattr(self, "_active_sidebar_btn", None) else None)
        self._bind_sidebar_scroll(self.origins_frame)

    def update_categories_list(self):
        for w in self.categories_frame.winfo_children(): w.destroy()
        all_cats = {}
        for d in self.database.values():
            for c in d.get("categories", []):
                c = c.strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c, 0) + 1
        if not all_cats:
            tk.Label(self.categories_frame, text="Nenhuma categoria", bg="#1A1A1A", fg="#666666",
                     font=("Arial", 10, "italic"), anchor="w", padx=15, pady=10).pack(fill="x")
            return
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        more_count = max(0, len(cats_sorted) - 8)
        for cat, count in cats_sorted[:8]:
            btn = tk.Button(self.categories_frame, text=f"{cat} ({count})",
                            bg="#1A1A1A", fg="#CCCCCC", font=("Arial", 10),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=8)
            btn.config(command=lambda c=cat, b=btn: self.set_category_filter([c], b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2A2A2A") if b is not getattr(self, "_active_sidebar_btn", None) else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1A1A1A") if b is not getattr(self, "_active_sidebar_btn", None) else None)
        if more_count > 0:
            more_btn = tk.Button(self.categories_frame, text=f"+ Ver mais ({more_count})",
                                 bg="#2A2A2A", fg="#888888", font=("Arial", 9),
                                 relief="flat", cursor="hand2", anchor="w", padx=15, pady=6)
            more_btn.config(command=self.open_categories_picker)
            more_btn.pack(fill="x", pady=(4, 2))
            more_btn.bind("<Enter>", lambda e, w=more_btn: w.config(fg="#FFFFFF"))
            more_btn.bind("<Leave>", lambda e, w=more_btn: w.config(fg="#888888"))
        self._bind_sidebar_scroll(self.categories_frame)

    def open_categories_picker(self):
        all_cats = {}
        for d in self.database.values():
            for c in d.get("categories", []):
                c = (c or "").strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c, 0) + 1
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        win = tk.Toplevel(self.root)
        win.title("Todas as Categorias")
        win.configure(bg="#141414")
        win.geometry("400x600")
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="Selecione uma categoria", font=("Arial", 13, "bold"),
                 bg="#141414", fg="#FFFFFF").pack(pady=10)
        frm = tk.Frame(win, bg="#141414")
        frm.pack(fill="both", expand=True, padx=10, pady=5)
        cv = tk.Canvas(frm, bg="#141414", highlightthickness=0)
        sb = ttk.Scrollbar(frm, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg="#141414")
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))
        for cat, count in cats_sorted:
            b = tk.Button(inner, text=f"{cat} ({count})",
                          command=lambda c=cat: (self.set_category_filter([c]), win.destroy()),
                          bg="#2A2A2A", fg="#FFFFFF", font=("Arial", 10),
                          relief="flat", cursor="hand2", anchor="w", padx=12, pady=8)
            b.pack(fill="x", pady=2, padx=5)
            b.bind("<Enter>", lambda e, w=b: w.config(bg="#E50914"))
            b.bind("<Leave>", lambda e, w=b: w.config(bg="#2A2A2A"))
        tk.Button(win, text="Fechar", command=win.destroy,
                  bg="#555555", fg="#FFFFFF", font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=14, pady=8).pack(pady=10)

    def update_tags_list(self):
        for w in self.tags_frame.winfo_children(): w.destroy()
        tag_count = {}
        for d in self.database.values():
            for t in d.get("tags", []):
                t = t.strip()
                if t: tag_count[t] = tag_count.get(t, 0) + 1
        tags_sorted = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        popular = tags_sorted[:20]
        if not popular:
            tk.Label(self.tags_frame, text="Nenhuma tag", bg="#1A1A1A", fg="#666666",
                     font=("Arial", 10, "italic"), anchor="w", padx=15, pady=10).pack(fill="x")
            return
        if len(tags_sorted) > 20:
            tk.Label(self.tags_frame, text=f"Top 20 de {len(tags_sorted)} tags",
                     bg="#1A1A1A", fg="#666666", font=("Arial", 9),
                     anchor="w", padx=15, pady=3).pack(fill="x")
        for tag, count in popular:
            btn = tk.Button(self.tags_frame, text=f"{tag} ({count})",
                            bg="#1A1A1A", fg="#CCCCCC", font=("Arial", 10),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=6)
            btn.config(command=lambda t=tag, b=btn: self.set_tag_filter(t, b))
            btn.pack(fill="x", pady=1)
            btn.bind("<Enter>", lambda e, w=btn: w.config(bg="#2A2A2A"))
            btn.bind("<Leave>", lambda e, w=btn: w.config(bg="#1A1A1A"))
        self._bind_sidebar_scroll(self.tags_frame)

    def set_origin_filter(self, origin, btn=None):
        self.current_filter = "all"
        self.current_origin = origin
        self.current_categories = []
        self.current_tag = None
        self._set_active_sidebar_btn(btn)
        self.display_projects()
        count = sum(1 for d in self.database.values() if d.get("origin") == origin)
        self.status_bar.config(text="Todas as Origens" if origin == "all" else f"Origem: {origin} ({count} projetos)")

    def set_category_filter(self, categories, btn=None):
        self.current_filter = "all"
        self.current_categories = categories
        self.current_tag = None
        self.current_origin = "all"
        self._set_active_sidebar_btn(btn)
        self.display_projects()
        if not categories:
            self.status_bar.config(text="Todas as Categorias")
        else:
            count = sum(1 for d in self.database.values() if any(c in d.get("categories", []) for c in categories))
            self.status_bar.config(text=f"Categorias: {', '.join(categories)} ({count} projetos)")

    def set_tag_filter(self, tag, btn=None):
        self.current_filter = "all"
        self.current_tag = tag
        self.current_categories = []
        self.current_origin = "all"
        self._set_active_sidebar_btn(btn)
        self.display_projects()
        if tag is None:
            self.status_bar.config(text="Todas as Tags")
        else:
            count = sum(1 for d in self.database.values() if tag in d.get("tags", []))
            self.status_bar.config(text=f"Tag: {tag} ({count} projetos)")

    # -----------------------------------------------------------------------
    # GRID DE PROJETOS
    # -----------------------------------------------------------------------
    def display_projects(self):
        for w in self.scrollable_frame.winfo_children(): w.destroy()
        title_text = "Todos os Projetos"
        if self.current_filter == "favorite": title_text = "⭐ Favoritos"
        elif self.current_filter == "done":    title_text = "✓ Já Feitos"
        elif self.current_filter == "good":    title_text = "👍 Bons"
        elif self.current_filter == "bad":     title_text = "👎 Ruins"
        if self.current_origin != "all":    title_text += f" — 🌐 {self.current_origin}"
        if self.current_categories:         title_text += f" — {', '.join(self.current_categories)}"
        if self.current_tag:                title_text += f" — 🏷️ {self.current_tag}"
        if self.search_query:               title_text += f' ("{self.search_query}")'
        tk.Label(self.scrollable_frame, text=title_text, font=("Arial", 20, "bold"),
                 bg="#141414", fg="#FFFFFF", anchor="w").grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(0,20))
        filtered = [(p, self.database[p]) for p in self.get_filtered_projects() if p in self.database]
        tk.Label(self.scrollable_frame, text=f"{len(filtered)} projeto(s)", font=("Arial", 12),
                 bg="#141414", fg="#999999").grid(row=1, column=0, columnspan=5, sticky="w", padx=10, pady=(0,10))
        row, col = 2, 0
        for project_path, data in filtered:
            self.create_project_card(project_path, data, row, col)
            col += 1
            if col >= 5: col = 0; row += 1

    def create_project_card(self, project_path, data, row, col):
        card = tk.Frame(self.scrollable_frame, bg="#2A2A2A", width=220, height=420)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        card.grid_propagate(False)
        cover_frame = tk.Frame(card, bg="#1A1A1A", width=220, height=200)
        cover_frame.pack(fill="x")
        cover_frame.pack_propagate(False)
        cover_frame.bind("<Button-1>", lambda e: self.open_project_modal(project_path))
        cover_image = self.get_cover_image(project_path)
        if cover_image:
            lbl = tk.Label(cover_frame, image=cover_image, bg="#1A1A1A", cursor="hand2")
            lbl.image = cover_image
            lbl.pack(expand=True)
            lbl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))
        else:
            ph = tk.Label(cover_frame, text="📁", font=("Arial", 60), bg="#1A1A1A", fg="#666666", cursor="hand2")
            ph.pack(expand=True)
            ph.bind("<Button-1>", lambda e: self.open_project_modal(project_path))
        info_frame = tk.Frame(card, bg="#2A2A2A")
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        name = data.get("name", "Sem nome")
        if len(name) > 30: name = name[:27] + "..."
        name_lbl = tk.Label(info_frame, text=name, font=("Arial", 11, "bold"),
                            bg="#2A2A2A", fg="#FFFFFF", wraplength=200, justify="left", cursor="hand2")
        name_lbl.pack(anchor="w")
        name_lbl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))
        categories = data.get("categories", [])
        if categories:
            cats_display = tk.Frame(info_frame, bg="#2A2A2A")
            cats_display.pack(anchor="w", pady=(5, 0), fill="x")
            for i, cat in enumerate(categories[:3]):
                color = ["#FF6B6B", "#4ECDC4", "#95E1D3"][i] if i < 3 else "#9B59B6"
                btn = tk.Button(cats_display, text=cat[:12], command=lambda c=cat: self.set_category_filter([c]),
                                bg=color, fg="#000000", font=("Arial", 8, "bold"),
                                relief="flat", cursor="hand2", padx=6, pady=3)
                btn.pack(side="left", padx=2, pady=2)
                orig = color
                btn.bind("<Enter>", lambda e, b=btn, c=orig: b.config(bg=self.darken_color(c)))
                btn.bind("<Leave>", lambda e, b=btn, c=orig: b.config(bg=c))
        tags = data.get("tags", [])
        if tags:
            tags_container = tk.Frame(info_frame, bg="#2A2A2A")
            tags_container.pack(anchor="w", pady=(5, 0), fill="x")
            for tag in tags[:3]:
                disp = (tag[:10] + "...") if len(tag) > 12 else tag
                btn = tk.Button(tags_container, text=disp, command=lambda t=tag: self.set_tag_filter(t),
                                bg="#3A3A3A", fg="#FFFFFF", font=("Arial", 8),
                                relief="flat", cursor="hand2", padx=6, pady=2)
                btn.pack(side="left", padx=2, pady=2)
                btn.bind("<Enter>", lambda e, w=btn: w.config(bg="#E50914"))
                btn.bind("<Leave>", lambda e, w=btn: w.config(bg="#3A3A3A"))
        origin = data.get("origin", "Desconhecido")
        colors = {"Creative Fabrica": "#FF6B35", "Etsy": "#F7931E", "Diversos": "#4ECDC4"}
        origin_btn = tk.Button(info_frame, text=origin, font=("Arial", 8),
                               bg=colors.get(origin, "#9B59B6"), fg="#FFFFFF",
                               padx=5, pady=2, relief="flat", cursor="hand2",
                               command=lambda o=origin: self.set_origin_filter(o),
                               activeforeground="#FFD700",
                               activebackground=colors.get(origin, "#9B59B6"))
        origin_btn.pack(anchor="w", pady=(5, 0))
        actions_frame = tk.Frame(info_frame, bg="#2A2A2A")
        actions_frame.pack(fill="x", pady=(10, 0))

        # 📂 Pasta
        tk.Button(actions_frame, text="📂", font=("Arial", 14),
                  command=lambda: self.open_folder(project_path),
                  bg="#2A2A2A", fg="#FFD700", relief="flat", cursor="hand2",
                  activebackground="#3A3A3A").pack(side="left", padx=2)

        # ⭐ Favorito — botão com referência para atualização in-place
        btn_fav = tk.Button(actions_frame, font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_fav.config(
            text="⭐" if data.get("favorite") else "☆",
            fg="#FFD700" if data.get("favorite") else "#666666",
            command=lambda b=btn_fav: self.toggle_favorite(project_path, b)
        )
        btn_fav.pack(side="left", padx=2)

        # ✓ Feito
        btn_done = tk.Button(actions_frame, font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_done.config(
            text="✓" if data.get("done") else "○",
            fg="#00FF00" if data.get("done") else "#666666",
            command=lambda b=btn_done: self.toggle_done(project_path, b)
        )
        btn_done.pack(side="left", padx=2)

        # 👍 Bom
        btn_good = tk.Button(actions_frame, font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_good.config(
            fg="#00FF00" if data.get("good") else "#666666",
            command=lambda b=btn_good, bb=None: self.toggle_good(project_path, b)
        )
        btn_good.config(text="👍")
        btn_good.pack(side="left", padx=2)

        # 👎 Ruim
        btn_bad = tk.Button(actions_frame, font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_bad.config(
            fg="#FF0000" if data.get("bad") else "#666666",
            command=lambda b=btn_bad: self.toggle_bad(project_path, b)
        )
        btn_bad.config(text="👎")
        btn_bad.pack(side="left", padx=2)

        if not data.get("analyzed"):
            tk.Button(actions_frame, text="🤖", font=("Arial", 14),
                      command=lambda: self.analyze_single_project(project_path),
                      bg="#2A2A2A", fg="#1DB954", relief="flat", cursor="hand2").pack(side="left", padx=2)

    # -----------------------------------------------------------------------
    # MODAL DE PROJETO
    # -----------------------------------------------------------------------
    def open_project_modal(self, project_path):
        BG       = "#0F0F0F"
        BG_CARD  = "#1A1A1A"
        BG_HOVER = "#242424"
        SEP_CLR  = "#2A2A2A"
        FG_PRI   = "#F0F0F0"
        FG_SEC   = "#999999"
        FG_TER   = "#555555"
        ACCENT   = "#E50914"
        GREEN    = "#1DB954"
        PAD      = 24
        FONT_TITLE   = ("Arial", 24, "bold")
        FONT_SECTION = ("Arial", 9, "bold")
        FONT_BODY    = ("Arial", 11)
        FONT_SMALL   = ("Arial", 9)

        data      = self.database.get(project_path, {})
        all_paths = [p for p in self.database if os.path.isdir(p)]
        try:    nav_idx = all_paths.index(project_path)
        except: nav_idx = 0
        nav_tot = len(all_paths)

        modal = tk.Toplevel(self.root)
        modal.title("Laserflix — Detalhes")
        modal.state("zoomed")
        modal.configure(bg=BG)
        modal.transient(self.root)
        modal.grab_set()
        modal.bind("<Escape>", lambda e: modal.destroy())
        modal.bind("<Left>",   lambda e: _nav(-1))
        modal.bind("<Right>",  lambda e: _nav(+1))

        def _nav(delta):
            ni = nav_idx + delta
            if 0 <= ni < nav_tot:
                modal.destroy()
                self.open_project_modal(all_paths[ni])

        main = tk.Frame(modal, bg=BG)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.columnconfigure(2, weight=1)
        main.rowconfigure(0, weight=1)

        # ── COLUNA ESQUERDA ───────────────────────────────────────
        left_outer = tk.Frame(main, bg=BG)
        left_outer.grid(row=0, column=0, sticky="nsew")
        lc  = tk.Canvas(left_outer, bg=BG, highlightthickness=0)
        lsb = ttk.Scrollbar(left_outer, orient="vertical", command=lc.yview)
        lp  = tk.Frame(lc, bg=BG)
        lp.bind("<Configure>", lambda e: lc.configure(scrollregion=lc.bbox("all")))
        lc_win = lc.create_window((0, 0), window=lp, anchor="nw")
        lc.configure(yscrollcommand=lsb.set)
        lc.pack(side="left", fill="both", expand=True)
        lsb.pack(side="right", fill="y")
        lc.bind("<MouseWheel>", lambda ev: lc.yview_scroll(int(-1*(ev.delta/120)), "units"))

        _desc_lbl_ref = [None]
        def _on_left_resize(e):
            w = e.width - 18
            if w < 60: return
            lc.itemconfig(lc_win, width=w)
            lbl = _desc_lbl_ref[0]
            if lbl:
                lbl.config(wraplength=w - PAD * 2 - 24)
        left_outer.bind("<Configure>", _on_left_resize)

        def _section_label(text):
            tk.Label(lp, text=text.upper(), font=FONT_SECTION,
                     bg=BG, fg=FG_TER, anchor="w").pack(fill="x", padx=PAD, pady=(20, 6))

        def _sep():
            tk.Frame(lp, bg=SEP_CLR, height=1).pack(fill="x", padx=PAD, pady=(4, 0))

        # 1. NOME
        tk.Frame(lp, bg=BG, height=8).pack()
        origin       = data.get("origin", "Desconhecido")
        col_map      = {"Creative Fabrica": "#FF6B35", "Etsy": "#F7931E", "Diversos": "#4ECDC4"}
        origin_color = col_map.get(origin, "#9B59B6")
        tk.Label(lp, text="  " + origin + "  ", font=FONT_SMALL,
                 bg=origin_color, fg="#FFFFFF").pack(anchor="w", padx=PAD, pady=(8, 4))
        tk.Label(lp, text=data.get("name", "Sem nome"),
                 font=FONT_TITLE, bg=BG, fg=FG_PRI,
                 wraplength=500, justify="left", anchor="w").pack(fill="x", padx=PAD, pady=(0, 4))

        # 2. MARCADORES — ícones compactos (13px)
        _sep()
        _section_label("Marcadores")
        act = tk.Frame(lp, bg=BG)
        act.pack(anchor="w", padx=PAD, pady=(0, 4))

        def _make_toggle(parent, emoji, label, key, active_fg):
            is_on = data.get(key, False)
            f = tk.Frame(parent, bg=BG_CARD, cursor="hand2")
            f.pack(side="left", padx=(0, 6), pady=4)
            inner_f = tk.Frame(f, bg=BG_CARD, padx=10, pady=7)
            inner_f.pack()
            il = tk.Label(inner_f, text=emoji, font=("Arial", 13), bg=BG_CARD,
                          fg=active_fg if is_on else FG_TER)
            il.pack()
            tl = tk.Label(inner_f, text=label, font=("Arial", 8), bg=BG_CARD,
                          fg=FG_SEC if is_on else FG_TER)
            tl.pack()
            all_w = [f, inner_f, il, tl]
            def _toggle(ev=None):
                nv = not self.database.get(project_path, {}).get(key, False)
                if project_path in self.database:
                    if key == "good" and nv: self.database[project_path]["bad"]  = False
                    if key == "bad"  and nv: self.database[project_path]["good"] = False
                    self.database[project_path][key] = nv
                    self.save_database()
                    il.config(fg=active_fg if nv else FG_TER)
                    tl.config(fg=FG_SEC   if nv else FG_TER)
                    self.display_projects()
            def _enter(ev, ws=all_w): [w.config(bg=BG_HOVER) for w in ws]
            def _leave(ev, ws=all_w): [w.config(bg=BG_CARD)  for w in ws]
            for w in all_w:
                w.bind("<Button-1>", _toggle)
                w.bind("<Enter>", _enter)
                w.bind("<Leave>", _leave)

        _make_toggle(act, "⭐", "Favorito",  "favorite", "#FFD700")
        _make_toggle(act, "✓",  "Feito",     "done",     "#1DB954")
        _make_toggle(act, "👍", "Bom",   "good",     "#4FC3F7")
        _make_toggle(act, "👎", "Ruim",  "bad",      "#EF5350")

        # 3. DESCRICAO IA
        _sep()
        _section_label("Descricao IA")
        desc_text = (data.get("ai_description") or "").strip()
        desc_box  = tk.Frame(lp, bg=BG_CARD)
        desc_box.pack(fill="x", padx=PAD, pady=(0, 8))
        desc_lbl  = tk.Label(
            desc_box,
            text=desc_text if desc_text else "Nenhuma descricao gerada. Clique em Gerar abaixo.",
            font=FONT_BODY, bg=BG_CARD,
            fg=FG_SEC if desc_text else FG_TER,
            justify="left", anchor="nw",
            wraplength=480, padx=16, pady=14,
        )
        desc_lbl.pack(fill="both", expand=True)
        _desc_lbl_ref[0] = desc_lbl

        def _gen_desc():
            gen_btn.config(state="disabled", text="Gerando...")
            desc_lbl.config(text="Gerando descricao com IA...", fg=FG_TER)
            modal.update()
            def _t():
                self.generate_ai_description(project_path, data)
                modal.after(0, modal.destroy)
                modal.after(50, lambda: self.open_project_modal(project_path))
            import threading
            threading.Thread(target=_t, daemon=True).start()
        gen_btn = tk.Button(lp, text="🤖  Gerar com IA", command=_gen_desc,
                            bg=GREEN, fg="#FFFFFF", font=("Arial", 10, "bold"),
                            relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        gen_btn.pack(anchor="w", padx=PAD, pady=(0, 4))

        # 4. CATEGORIAS
        _sep()
        _section_label("Categorias")
        cats_row = tk.Frame(lp, bg=BG)
        cats_row.pack(anchor="w", padx=PAD, fill="x", pady=(0, 4))
        cats = data.get("categories", []) or []
        if cats:
            for cat in cats:
                tk.Label(cats_row, text=cat, font=FONT_SMALL,
                         bg="#1E3A2F", fg="#1DB954",
                         padx=10, pady=5).pack(side="left", padx=(0, 6), pady=2)
        else:
            tk.Label(cats_row, text="Sem categoria", font=FONT_SMALL,
                     bg=BG, fg=FG_TER).pack(anchor="w")

        # 5. TAGS
        _sep()
        _section_label("Tags")
        tw = tk.Frame(lp, bg=BG)
        tw.pack(anchor="w", padx=PAD, fill="x", pady=(0, 4))
        for tag in (data.get("tags", []) or ["Nenhuma tag"]):
            t = tk.Label(tw, text=tag, font=FONT_SMALL,
                         bg=BG_CARD, fg=FG_SEC, padx=10, pady=5, cursor="hand2")
            t.pack(side="left", padx=(0, 4), pady=3)
            t.bind("<Enter>", lambda e, w=t: w.config(bg=ACCENT, fg="#FFFFFF"))
            t.bind("<Leave>", lambda e, w=t: w.config(bg=BG_CARD, fg=FG_SEC))
            t.bind("<Button-1>", lambda e, tg=tag: (modal.destroy(), self.set_tag_filter(tg)))

        # 6. ARQUIVOS
        _sep()
        _section_label("Arquivos")
        struct = data.get("structure") or self.analyze_project_structure(project_path)
        fmt_row = tk.Frame(lp, bg=BG)
        fmt_row.pack(anchor="w", padx=PAD, pady=(0, 4))
        for lbl_t, lbl_c, present in [
            ("SVG", "#FF6B6B", struct.get("has_svg")),
            ("PDF", "#4ECDC4", struct.get("has_pdf")),
            ("DXF", "#95E1D3", struct.get("has_dxf")),
            ("AI",  "#F7DC6F", struct.get("has_ai")),
        ]:
            tk.Label(fmt_row, text=lbl_t, font=("Arial", 9, "bold"),
                     bg=BG_CARD if present else BG,
                     fg=lbl_c if present else FG_TER,
                     padx=10, pady=5).pack(side="left", padx=(0, 4))
        tf  = struct.get("total_files", 0)
        sf  = struct.get("total_subfolders", 0)
        suf = "s" if tf != 1 else ""
        tk.Label(lp, text=str(tf) + " arquivo" + suf + "  ·  " + str(sf) + " subpasta(s)",
                 font=FONT_SMALL, bg=BG, fg=FG_TER).pack(anchor="w", padx=PAD, pady=(4, 4))

        # 7. LOCALIZACAO
        _sep()
        _section_label("Localizacao")
        par_f = os.path.basename(os.path.dirname(project_path))
        prj_n = os.path.basename(project_path)
        lr = tk.Frame(lp, bg=BG)
        lr.pack(fill="x", padx=PAD, pady=(0, 4))
        tk.Label(lr, text=par_f + " / " + prj_n, font=FONT_SMALL,
                 bg=BG, fg=FG_SEC).pack(side="left")
        def _copy_path():
            modal.clipboard_clear()
            modal.clipboard_append(project_path)
            cp_btn.config(text="✅ Copiado!")
            modal.after(1500, lambda: cp_btn.config(text="📋 Copiar"))
        cp_btn = tk.Button(lr, text="📋 Copiar", command=_copy_path,
                           bg=BG_CARD, fg=FG_SEC, font=FONT_SMALL,
                           relief="flat", cursor="hand2", padx=8, pady=3, bd=0)
        cp_btn.pack(side="left", padx=10)
        added   = (data.get("added_date") or "")[:10] or "—"
        model_u = data.get("analyzed_model", "nao analisado")
        tk.Label(lp, text="Adicionado: " + added + "   ·   Modelo IA: " + model_u,
                 font=FONT_SMALL, bg=BG, fg=FG_TER).pack(anchor="w", padx=PAD, pady=(2, 4))

        # 8. BARRA DE ACOES
        tk.Frame(lp, bg=SEP_CLR, height=1).pack(fill="x", pady=(16, 0))
        action_bar = tk.Frame(lp, bg=BG)
        action_bar.pack(fill="x", padx=PAD, pady=12)
        BTN_PRIMARY = dict(bg=ACCENT,  fg="#FFFFFF", font=("Arial", 10, "bold"), relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        BTN_GHOST   = dict(bg=BG_CARD, fg=FG_PRI,   font=("Arial", 10),         relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        BTN_NAV     = dict(bg=BG_CARD, fg=FG_SEC,   font=("Arial", 11),         relief="flat", cursor="hand2", padx=14, pady=9, bd=0)
        tk.Button(action_bar, text="✏️  Editar",
                  command=lambda: self.open_edit_mode(modal, project_path, data),
                  **BTN_PRIMARY).pack(side="left", padx=(0, 6))
        tk.Button(action_bar, text="📂  Pasta",
                  command=lambda: self.open_folder(project_path),
                  **BTN_GHOST).pack(side="left", padx=(0, 6))
        tk.Button(action_bar, text="🤖  Reanalisar",
                  command=lambda: [self.analyze_single_project(project_path), modal.destroy()],
                  **BTN_GHOST).pack(side="left", padx=(0, 6))
        tk.Button(action_bar, text="✕",
                  command=modal.destroy,
                  bg=BG, fg=FG_TER, font=("Arial", 14),
                  relief="flat", cursor="hand2", padx=10, pady=9, bd=0).pack(side="right")
        tk.Label(action_bar, text=str(nav_idx + 1) + " / " + str(nav_tot),
                 font=FONT_SMALL, bg=BG, fg=FG_TER).pack(side="right", padx=8)
        tk.Button(action_bar, text="▶",
                  command=lambda: _nav(+1),
                  state="normal" if nav_idx < nav_tot - 1 else "disabled",
                  **BTN_NAV).pack(side="right", padx=(0, 2))
        tk.Button(action_bar, text="◀",
                  command=lambda: _nav(-1),
                  state="normal" if nav_idx > 0 else "disabled",
                  **BTN_NAV).pack(side="right", padx=(0, 4))

        # ── SEPARADOR VERTICAL ────────────────────────────────────
        tk.Frame(main, bg=SEP_CLR, width=1).grid(row=0, column=1, sticky="ns")

        # ── COLUNA DIREITA — hero full-width + galeria ────────────
        right_outer = tk.Frame(main, bg="#0A0A0A")
        right_outer.grid(row=0, column=2, sticky="nsew")
        rc  = tk.Canvas(right_outer, bg="#0A0A0A", highlightthickness=0, bd=0)
        rsb = ttk.Scrollbar(right_outer, orient="vertical", command=rc.yview)
        rp  = tk.Frame(rc, bg="#0A0A0A")
        rp.bind("<Configure>", lambda e: rc.configure(scrollregion=rc.bbox("all")))
        rc_win = rc.create_window((0, 0), window=rp, anchor="nw")
        rc.configure(yscrollcommand=rsb.set)
        rc.pack(side="left", fill="both", expand=True)
        rsb.pack(side="right", fill="y")
        rc.bind("<MouseWheel>", lambda ev: rc.yview_scroll(int(-1*(ev.delta/120)), "units"))

        images = self.get_all_project_images(project_path)

        if not images:
            tk.Label(rp, text="🖼️", font=("Arial", 64),
                     bg="#0A0A0A", fg="#1E1E1E").pack(expand=True, pady=100)
            tk.Label(rp, text="Sem imagens nesta pasta",
                     font=FONT_BODY, bg="#0A0A0A", fg=FG_TER).pack()
            def _redraw_cover(cw=None): pass
        else:
            cover_lbl = tk.Label(rp, bg="#0A0A0A", cursor="hand2", bd=0)
            cover_lbl.pack(fill="x")
            cover_lbl.bind("<Button-1>", lambda e, p=images[0]: self.open_image(p))

            def _redraw_cover(cw=None, _lbl=cover_lbl, _path=images[0]):
                if cw is None:
                    cw = rc.winfo_width() - 18
                if cw < 10: return
                try:
                    img   = Image.open(_path).convert("RGB")
                    ratio = cw / img.width
                    nw    = cw
                    nh    = max(1, int(img.height * ratio))
                    img   = img.resize((nw, nh), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    _lbl.config(image=photo)
                    _lbl.image = photo
                except Exception:
                    pass

            def _on_right_resize(e):
                cw = e.width - 18
                if cw < 10: return
                rc.itemconfig(rc_win, width=cw)
                _redraw_cover(cw)
            right_outer.bind("<Configure>", _on_right_resize)
            modal.after(80, _redraw_cover)

            rest = images[1:]
            if rest:
                tk.Frame(rp, bg=SEP_CLR, height=1).pack(fill="x", pady=8)
                tk.Label(rp, text="MAIS IMAGENS  (" + str(len(rest)) + ")",
                         font=FONT_SECTION, bg="#0A0A0A", fg=FG_TER,
                         anchor="w").pack(fill="x", padx=12, pady=(0, 6))
                gf = tk.Frame(rp, bg="#0A0A0A")
                gf.pack(fill="x", padx=6)
                THUMB = 200
                col_idx = row_idx = 0
                for img_path in rest[:30]:
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((THUMB, THUMB), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        lbl = tk.Label(gf, image=photo, bg="#0A0A0A", cursor="hand2", bd=0)
                        lbl.image = photo
                        lbl.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nw")
                        lbl.bind("<Button-1>", lambda e, p=img_path: self.open_image(p))
                        col_idx += 1
                        if col_idx >= 2:
                            col_idx = 0
                            row_idx += 1
                    except Exception:
                        pass
            tk.Frame(rp, bg="#0A0A0A", height=24).pack()

    def open_edit_mode(self, parent_modal, project_path, data):
        parent_modal.destroy()
        edit_win = tk.Toplevel(self.root)
        edit_win.title("✏️ Editar Projeto")
        edit_win.state("zoomed")
        edit_win.configure(bg="#181818")
        edit_win.transient(self.root)
        edit_win.grab_set()
        tk.Label(edit_win, text="✏️ Editar Projeto", font=("Arial",20,"bold"),
                 bg="#181818", fg="#E50914").pack(pady=20)
        tk.Label(edit_win, text="📁 Nome do Projeto", font=("Arial",12,"bold"),
                 bg="#181818", fg="#FFFFFF").pack(anchor="w", padx=30, pady=(10,5))
        name_text = tk.Text(edit_win, height=2, bg="#2A2A2A", fg="#FFFFFF", font=("Arial",11), relief="flat", wrap="word")
        name_text.insert("1.0", data.get("name",""))
        name_text.config(state="disabled")
        name_text.pack(fill="x", padx=30, pady=(0,15))
        tk.Label(edit_win, text="📂 Categorias (separadas por vírgula)", font=("Arial",12,"bold"),
                 bg="#181818", fg="#FFFFFF").pack(anchor="w", padx=30, pady=(10,5))
        categories_text = tk.Text(edit_win, height=3, bg="#2A2A2A", fg="#FFFFFF", font=("Arial",11), relief="flat", wrap="word")
        categories_text.insert("1.0", ", ".join(data.get("categories",[])))
        categories_text.pack(fill="x", padx=30, pady=(0,15))
        tk.Label(edit_win, text="🏷️ Tags", font=("Arial",12,"bold"),
                 bg="#181818", fg="#FFFFFF").pack(anchor="w", padx=30, pady=(10,5))
        tags_container = tk.Frame(edit_win, bg="#181818")
        tags_container.pack(fill="x", padx=30, pady=(0,10))
        tags_list_frame = tk.Frame(tags_container, bg="#2A2A2A")
        tags_list_frame.pack(side="left", fill="both", expand=True, padx=(0,10))
        tags_scrollbar = ttk.Scrollbar(tags_list_frame, orient="vertical")
        tags_listbox = tk.Listbox(tags_list_frame, bg="#2A2A2A", fg="#FFFFFF", font=("Arial",10),
                                  height=6, yscrollcommand=tags_scrollbar.set,
                                  selectmode=tk.SINGLE, relief="flat")
        tags_scrollbar.config(command=tags_listbox.yview)
        tags_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        tags_scrollbar.pack(side="right", fill="y")
        for tag in data.get("tags",[]): tags_listbox.insert(tk.END, tag)
        tags_buttons_frame = tk.Frame(tags_container, bg="#181818")
        tags_buttons_frame.pack(side="right")
        for text, cmd, color in [
            ("➕ Add",    lambda: self.add_tag_to_listbox(tags_listbox),           "#1DB954"),
            ("➖ Remover",lambda: self.remove_tag_from_listbox(tags_listbox),      "#E50914"),
            ("🗑️ Limpar", lambda: tags_listbox.delete(0, tk.END),                 "#666666"),
        ]:
            tk.Button(tags_buttons_frame, text=text, command=cmd, bg=color, fg="#FFFFFF",
                      font=("Arial",10), relief="flat", cursor="hand2", padx=10, pady=8, width=10).pack(pady=2)
        final_buttons = tk.Frame(edit_win, bg="#181818")
        final_buttons.pack(fill="x", padx=30, pady=30)
        tk.Button(final_buttons, text="💾 Salvar e Fechar",
                  command=lambda: self.save_edit_modal(edit_win, project_path, categories_text, tags_listbox),
                  bg="#1DB954", fg="#FFFFFF", font=("Arial",12,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=12).pack(side="left", padx=5)
        tk.Button(final_buttons, text="✕ Cancelar", command=edit_win.destroy,
                  bg="#E50914", fg="#FFFFFF", font=("Arial",12,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=12).pack(side="right", padx=5)

    def save_edit_modal(self, modal, project_path, categories_text, tags_listbox):
        if project_path in self.database:
            cats_str = categories_text.get("1.0","end-1c").strip()
            new_cats = [c.strip() for c in cats_str.split(",") if c.strip()]
            if new_cats: self.database[project_path]["categories"] = new_cats
            self.database[project_path]["tags"] = list(tags_listbox.get(0, tk.END))
            self.database[project_path]["analyzed"] = True
            self.save_database()
            self.update_sidebar()
            self.display_projects()
            modal.destroy()
            self.status_bar.config(text="✓ Projeto atualizado!")

    # -----------------------------------------------------------------------
    # DASHBOARD
    # -----------------------------------------------------------------------
    def open_dashboard(self):
        total = len(self.database)
        stats = {
            "Total de Projetos": total,
            "Favoritos":  sum(1 for d in self.database.values() if d.get("favorite")),
            "Já Feitos":  sum(1 for d in self.database.values() if d.get("done")),
            "Bons":       sum(1 for d in self.database.values() if d.get("good")),
            "Ruins":      sum(1 for d in self.database.values() if d.get("bad")),
            "Analisados": sum(1 for d in self.database.values() if d.get("analyzed")),
            "Com Descrição": sum(1 for d in self.database.values() if d.get("ai_description","")),
        }
        all_cats = Counter(c for d in self.database.values() for c in d.get("categories",[]))
        all_tags = Counter(t for d in self.database.values() for t in d.get("tags",[]))
        origins = Counter(d.get("origin","") for d in self.database.values())
        model_usage = Counter(d.get("analyzed_model","?") for d in self.database.values() if d.get("analyzed"))

        dash = tk.Toplevel(self.root)
        dash.title("📊 Dashboard")
        dash.state("zoomed")
        dash.configure(bg="#141414")
        dash.transient(self.root)
        canvas = tk.Canvas(dash, bg="#141414", highlightthickness=0)
        scrollbar = ttk.Scrollbar(dash, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg="#141414")
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=content, anchor="nw", width=780)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def add_section(title, items_dict, color="#CCCCCC"):
            frame = tk.Frame(content, bg="#2A2A2A")
            frame.pack(fill="x", padx=20, pady=10)
            tk.Label(frame, text=title, font=("Arial",16,"bold"), bg="#2A2A2A", fg="#FFFFFF").pack(anchor="w", padx=15, pady=10)
            for label, value in items_dict:
                row = tk.Frame(frame, bg="#2A2A2A")
                row.pack(fill="x", padx=15, pady=3)
                tk.Label(row, text=str(label), font=("Arial",11), bg="#2A2A2A", fg="#FFFFFF").pack(side="left")
                tk.Label(row, text=str(value), font=("Arial",11,"bold"), bg="#2A2A2A", fg=color).pack(side="right")

        tk.Label(content, text="📊 Dashboard de Estatísticas", font=("Arial",24,"bold"),
                 bg="#141414", fg="#E50914").pack(pady=20)
        add_section("📈 Estatísticas Gerais", [(k, v) for k,v in stats.items()], "#1DB954")
        add_section("🤖 Uso de Modelos", list(model_usage.items()), "#4ECDC4")
        if all_cats: add_section("📂 Top 10 Categorias", all_cats.most_common(10), "#CCCCCC")
        if all_tags: add_section("🏷️ Top 10 Tags", all_tags.most_common(10), "#CCCCCC")
        if total > 0: add_section("🌐 Origens", [(o, f"{c} ({c/total*100:.1f}%)") for o,c in origins.items()], "#FF6B35")
        tk.Frame(content, bg="#141414", height=30).pack()

    def open_batch_edit(self):
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de edição em lote em desenvolvimento...")


def main():
    root = tk.Tk()
    app = LaserflixNetflix(root)
    root.mainloop()


if __name__ == "__main__":
    main()
