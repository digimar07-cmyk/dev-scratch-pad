#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LASERFLIX v8.1.1 (Patch 1) — Merge Completo
Layout: laserflix_v810_netflix_redesign.py
Engine IA: laserflix_v740_Ofline_Stable.py
Correcoes: setOrigin, setTag, setFilter reset, CSS sidebar,
           innerHTML btn Regenerar, icones/cats/tags sempre visiveis,
           estrela amarela, zero surrogates.
Roda: python laserflix_v811_patch1.py -> http://localhost:5678
"""

import json, os, sys, re, shutil, threading, time, logging, base64, io, platform, subprocess, webbrowser
from datetime import datetime
from collections import Counter, OrderedDict
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, send_file, abort, Response

try:
    import requests as req_lib
except ImportError:
    req_lib = None

VERSION       = "8.1.1"
CONFIG_FILE   = "laserflix_config.json"
DB_FILE       = "laserflix_database.json"
BACKUP_FOLDER = "laserflix_backups"
FAST_MODEL_THRESHOLD = 50

OLLAMA_MODELS = {
    "text_quality": "qwen2.5:7b-instruct-q4_K_M",
    "text_fast":    "qwen2.5:3b-instruct-q4_K_M",
    "vision":       "moondream:latest",
    "embed":        "nomic-embed-text:latest",
}
TIMEOUTS = {
    "text_quality": (5, 120),
    "text_fast":    (5, 75),
    "vision":       (5, 60),
    "embed":        (5, 15),
}

def setup_logging():
    logger = logging.getLogger("Laserflix")
    if logger.handlers: return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh = RotatingFileHandler("laserflix.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

LOGGER = setup_logging()

# ===========================================================================
# ENGINE
# ===========================================================================
class LaserflixEngine:
    def __init__(self):
        self.folders        = []
        self.database       = {}
        self.analyzing      = False
        self.stop_analysis  = False
        self.active_models  = dict(OLLAMA_MODELS)
        self.thumbnail_cache = OrderedDict()
        self.thumbnail_cache_limit = 300
        self.http_session   = req_lib.Session() if req_lib else None
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_retries  = 3
        self._ollama_health_cache = {"ts": 0.0, "ok": None}
        os.makedirs(BACKUP_FOLDER, exist_ok=True)
        self._load_config()
        self._load_database()

    # --- CONFIG / DB ---
    def _save_json_atomic(self, filepath, data):
        tmp = filepath + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if os.path.exists(filepath):
                shutil.copy2(filepath, filepath + ".bak")
            os.replace(tmp, filepath)
        except Exception:
            LOGGER.exception("Falha ao salvar %s", filepath)
            if os.path.exists(tmp): os.remove(tmp)

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.folders = cfg.get("folders", [])
            self.active_models.update(cfg.get("models", {}))

    def save_config(self):
        self._save_json_atomic(CONFIG_FILE, {"folders": self.folders, "models": self.active_models})

    def _load_database(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                self.database = json.load(f)
            for path, data in self.database.items():
                if "category" in data and "categories" not in data:
                    old = data.pop("category", "")
                    data["categories"] = [old] if (old and old != "Sem Categoria") else []

    def save_database(self):
        self._save_json_atomic(DB_FILE, self.database)

    def auto_backup(self):
        try:
            ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = os.path.join(BACKUP_FOLDER, f"auto_backup_{ts}.json")
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, dst)
            baks = sorted(f for f in os.listdir(BACKUP_FOLDER) if f.startswith("auto_backup_"))
            for old in baks[:-10]: os.remove(os.path.join(BACKUP_FOLDER, old))
        except Exception:
            LOGGER.exception("Falha no auto-backup")

    def manual_backup(self):
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(BACKUP_FOLDER, f"manual_backup_{ts}.json")
        if os.path.exists(DB_FILE):
            shutil.copy2(DB_FILE, dst)
            return dst
        return None

    # --- OLLAMA ---
    def _ollama_ok(self):
        if not req_lib: return False
        try:
            now = time.time()
            c = self._ollama_health_cache
            if c.get("ok") is not None and (now - c.get("ts", 0)) < 5:
                return bool(c["ok"])
            r  = self.http_session.get(f"{self.ollama_base_url}/api/tags", timeout=4)
            ok = r.status_code == 200
            self._ollama_health_cache = {"ts": now, "ok": ok}
            return ok
        except Exception:
            self._ollama_health_cache = {"ts": time.time(), "ok": False}
            return False

    def _model(self, role):   return self.active_models.get(role, OLLAMA_MODELS.get(role, ""))
    def _timeout(self, role): return TIMEOUTS.get(role, (5, 30))

    def _ollama_text(self, prompt, *, role="text_quality", temperature=0.7, num_predict=350):
        if getattr(self, "stop_analysis", False): return ""
        if not self._ollama_ok(): return ""
        model   = self._model(role)
        timeout = self._timeout(role)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Voce e especialista em produtos de corte laser. Responda em portugues brasileiro. Siga o formato com precisao."},
                {"role": "user",   "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature, "top_p": 0.9, "num_predict": num_predict, "repeat_penalty": 1.1},
        }
        for attempt in range(1, self.ollama_retries + 1):
            if getattr(self, "stop_analysis", False): return ""
            try:
                r = self.http_session.post(f"{self.ollama_base_url}/api/chat", json=payload, timeout=timeout)
                if r.status_code != 200: raise RuntimeError(f"HTTP {r.status_code}")
                data = r.json()
                return ((data.get("message") or {}).get("content") or data.get("response") or "").strip()
            except Exception as e:
                LOGGER.warning("Ollama tentativa %d/%d: %s", attempt, self.ollama_retries, e)
                if attempt < self.ollama_retries: time.sleep(2)
        return ""

    def _describe_image(self, image_path):
        if not image_path or not os.path.exists(image_path) or not self._ollama_ok(): return ""
        model = self._model("vision")
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                img.thumbnail((512, 512))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                b64 = base64.b64encode(buf.getvalue()).decode()
            payload = {"model": model, "prompt": "Look only at the main laser-cut wooden object in the center. Describe ONLY the central object: shape, theme and style. One short sentence.", "images": [b64], "stream": False, "options": {"temperature": 0.2, "num_predict": 60}}
            r = self.http_session.post(f"{self.ollama_base_url}/api/generate", json=payload, timeout=self._timeout("vision"))
            if r.status_code == 200: return (r.json().get("response") or "").strip()
        except Exception as e:
            LOGGER.warning("Falha moondream: %s", e)
        return ""

    def _image_quality(self, image_path):
        try:
            from PIL import Image, ImageStat
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                w, h    = img_rgb.size
                box     = (int(w*0.05), int(h*0.10), int(w*0.75), int(h*0.90))
                center  = img_rgb.crop(box)
                gray    = center.convert("L")
                stat    = ImageStat.Stat(gray)
                brightness = stat.mean[0]
                hsv     = center.convert("HSV")
                sat     = ImageStat.Stat(hsv).mean[1]
                white_pct = (brightness / 255.0) * max(0, 1.0 - stat.stddev[0]/80.0) * 100
                return {"brightness": brightness, "saturation": sat, "white_pct": white_pct,
                        "use_vision": not (brightness > 210 or sat < 25 or white_pct > 50)}
        except Exception:
            return {"use_vision": True, "brightness": 0, "saturation": 100, "white_pct": 0}

    # --- ANALISE ---
    def _choose_role(self, batch_size=1):
        return "text_fast" if batch_size > FAST_MODEL_THRESHOLD else "text_quality"

    def analyze_with_ai(self, project_path, batch_size=1):
        try:
            name    = os.path.basename(project_path)
            struct  = self.analyze_structure(project_path)
            ft_str  = ", ".join(f"{e}({c}x)" for e, c in struct["file_types"].items())
            tech    = []
            if struct["has_svg"]: tech.append("SVG")
            if struct["has_pdf"]: tech.append("PDF")
            if struct["has_dxf"]: tech.append("DXF")
            if struct["has_ai"]:  tech.append("AI")
            vision_line = ""
            cover = self._first_image(project_path)
            if cover:
                q = self._image_quality(cover)
                if q["use_vision"]:
                    vd = self._describe_image(cover)
                    if vd: vision_line = f"\nVISUAL: {vd}"
            role   = self._choose_role(batch_size)
            prompt = f"""Analise este produto de corte laser.
NOME: {name}
ARQUIVOS: {struct['total_files']} | TIPOS: {ft_str} | FORMATOS: {', '.join(tech) or 'variados'}{vision_line}

TAREFA 1 - CATEGORIAS (3 a 5):
1. Data: Pascoa/Natal/Dia das Maes/Dia dos Pais/Aniversario/Casamento/Cha de Bebe/Dia das Criancas/Diversos
2. Tipo: Porta-Retrato/Caixa Organizadora/Luminaria/Nome Decorativo/Quadro Decorativo/Painel/Mandala/Lembrancinha/Brinquedo Educativo/Diversos
3. Ambiente: Quarto/Sala/Cozinha/Quarto Infantil/Quarto de Bebe/Festa/Diversos
4. Estilo (opcional)
5. Publico (opcional)

TAREFA 2 - TAGS (exatamente 8):
- 3 do nome, 5 de emocao/ocasiao/publico/estilo/uso

FORMATO (exato):
Categorias: cat1, cat2, cat3
Tags: tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8"""
            if self.stop_analysis: return self.fallback_analysis(project_path)
            text = self._ollama_text(prompt, role=role, temperature=0.65, num_predict=200)
            categories, tags = [], []
            if text:
                for line in text.split("\n"):
                    line = line.strip()
                    if line.startswith("Categorias:") or line.startswith("Categories:"):
                        raw = line.split(":", 1)[1].strip().replace("[","").replace("]","")
                        categories = [c.strip().strip('"') for c in raw.split(",") if c.strip()]
                    elif line.startswith("Tags:"):
                        raw = line.split(":", 1)[1].strip().replace("[","").replace("]","")
                        tags = [t.strip().strip('"') for t in raw.split(",") if t.strip()]
            name_tags = self.extract_tags(name)
            for t in name_tags:
                if t not in tags: tags.insert(0, t)
            tags = list(dict.fromkeys(tags))[:10]
            if len(categories) < 3:
                categories = self.fallback_categories(project_path, categories)
            return categories[:8], tags
        except Exception:
            LOGGER.exception("Erro analyze_with_ai %s", project_path)
            return self.fallback_analysis(project_path)

    def generate_description(self, project_path, data):
        if getattr(self, "stop_analysis", False): return None
        try:
            struct = data.get("structure") or self.database.get(project_path, {}).get("structure") or self.analyze_structure(project_path)
            if project_path in self.database: self.database[project_path]["structure"] = struct
            raw_name = data.get("name", os.path.basename(project_path))
            clean = raw_name
            for ext in [".zip",".rar",".svg",".pdf",".dxf",".cdr",".ai"]: clean = clean.replace(ext,"")
            clean = re.sub(r"[-_]\d{5,}", "", clean).replace("-"," ").replace("_"," ").strip()
            vision_ctx = ""
            cover = self._first_image(project_path)
            if cover:
                q = self._image_quality(cover)
                if q["use_vision"]:
                    vd = self._describe_image(cover)
                    if vd: vision_ctx = f"\n\nDETALHE VISUAL (complementar, nunca contradizer): {vd}"
            if getattr(self, "stop_analysis", False): return None
            prompt = (
                f"Especialista em pecas fisicas de corte a laser.\n\n"
                f"NOME DA PECA: {clean}{vision_ctx}\n\n"
                "REGRA: O NOME define o produto. Visual apenas complementa.\n\n"
                f"ESCREVA exatamente:\n\n{clean}\n\n"
                "Por Que Este Produto e Especial:\n[2-3 frases unicas e afetivas]\n\n"
                "Perfeito Para:\n[2-3 frases praticas com exemplos reais]\n\n"
                "REGRAS: portugues BR, sem palavras 'projeto'/'arquivo'/'SVG', max 120 palavras."
            )
            resp = self._ollama_text(prompt, role="text_quality", temperature=0.78, num_predict=250)
            if resp:
                if not resp.strip().startswith(clean[:15]): resp = clean + "\n\n" + resp.strip()
                self.database.setdefault(project_path, {})
                self.database[project_path]["ai_description"]           = resp.strip()
                self.database[project_path]["description_generated_at"] = datetime.now().isoformat()
                self.database[project_path]["description_model"]        = self._model("text_quality")
                self.save_database()
                return resp.strip()
            return self.fallback_description(project_path, data, struct)
        except Exception:
            LOGGER.exception("Erro generate_description %s", project_path)
            return self.fallback_description(project_path, data, {})

    # --- FALLBACKS ---
    def fallback_categories(self, project_path, existing):
        name = os.path.basename(project_path).lower()
        date_map = {"pascoa":"Pascoa","easter":"Pascoa","natal":"Natal","christmas":"Natal","mae":"Dia das Maes","mother":"Dia das Maes","pai":"Dia dos Pais","father":"Dia dos Pais","crianca":"Dia das Criancas","children":"Dia das Criancas","baby":"Cha de Bebe","bebe":"Cha de Bebe","wedding":"Casamento","casamento":"Casamento","birthday":"Aniversario","aniversario":"Aniversario"}
        func_map = {"frame":"Porta-Retrato","foto":"Porta-Retrato","box":"Caixa Organizadora","caixa":"Caixa Organizadora","name":"Nome Decorativo","nome":"Nome Decorativo","sign":"Plaquinha","placa":"Plaquinha","quadro":"Quadro Decorativo","painel":"Painel de Parede"}
        amb_map  = {"nursery":"Quarto de Bebe","baby":"Quarto de Bebe","bedroom":"Quarto","quarto":"Quarto","kitchen":"Cozinha","cozinha":"Cozinha","living":"Sala","sala":"Sala","kids":"Quarto Infantil","infantil":"Quarto Infantil"}
        result = list(existing)
        dates  = list(date_map.values())
        if not any(c in dates for c in result):
            result.insert(0, next((v for k,v in date_map.items() if k in name), "Diversos"))
        if len(result) < 2: result.append(next((v for k,v in func_map.items() if k in name), "Diversos"))
        if len(result) < 3: result.append(next((v for k,v in amb_map.items()  if k in name), "Diversos"))
        return result

    def fallback_analysis(self, project_path):
        name = os.path.basename(project_path).lower()
        name_tags = self.extract_tags(os.path.basename(project_path))
        cats   = ["Diversos","Diversos","Diversos"]
        checks = [
            (["pascoa","easter","coelho"],0,"Pascoa"),(["natal","christmas","noel"],0,"Natal"),
            (["mae","mom","mother"],0,"Dia das Maes"),(["pai","dad","father"],0,"Dia dos Pais"),
            (["baby","bebe","shower"],0,"Cha de Bebe"),(["frame","foto","photo"],1,"Porta-Retrato"),
            (["box","caixa"],1,"Caixa Organizadora"),(["name","nome","sign"],1,"Nome Decorativo"),
            (["nursery","baby"],2,"Quarto de Bebe"),(["bedroom","quarto"],2,"Quarto"),
            (["kitchen","cozinha"],2,"Cozinha"),(["sala","living"],2,"Sala"),
        ]
        for words, idx, val in checks:
            if any(w in name for w in words): cats[idx] = val
        tags = name_tags + ["personalizado","artesanal"]
        seen, unique = set(), []
        for t in tags:
            if t.lower() not in seen: seen.add(t.lower()); unique.append(t)
        return cats, unique[:10]

    def fallback_description(self, project_path, data, structure):
        raw   = data.get("name","Sem nome")
        clean = raw
        for ext in [".zip",".rar",".svg",".pdf",".dxf",".cdr",".ai"]: clean = clean.replace(ext,"")
        clean = re.sub(r"[-_]\d{5,}","",clean).replace("-"," ").replace("_"," ").strip()
        nl = clean.lower()
        tl = " ".join(data.get("tags",[])).lower()
        if any(w in nl or w in tl for w in ["hanger","cabide"]):
            esp = "Um cabide infantil encantador que transforma o quarto da crianca em um cantinho cheio de personalidade."
            prf = "Perfeito para organizar roupinhas com charme. Otimo presente para bebes e criancas."
        elif any(w in nl or w in tl for w in ["mirror","espelho"]):
            esp = "Um espelho decorativo unico, cortado a laser com precisao, que combina funcionalidade e arte."
            prf = "Ideal para decorar quarto de bebe ou quarto infantil com estilo."
        elif any(w in nl or w in tl for w in ["calendar","calendario"]):
            esp = "Um calendario decorativo que une organizacao e arte, tornando cada dia especial."
            prf = "Perfeito para quartos infantis ou como presente criativo."
        elif any(w in nl or w in tl for w in ["frame","quadro","porta-retrato"]):
            esp = "Um porta-retrato artesanal que transforma memorias em arte."
            prf = "Presente ideal para aniversarios, casamentos e datas comemorativas."
        elif any(w in nl or w in tl for w in ["natal","christmas"]):
            esp = "Uma peca que traz o espirito natalino para o lar, criando memorias afetivas."
            prf = "Ideal para decoracao sazonal ou como lembrancinha especial."
        else:
            cats = data.get("categories",["Produto personalizado"])
            cd   = " | ".join(cats[:2]) if cats else "Produto personalizado"
            esp  = f"Uma peca de corte a laser em {cd}, criada para ser unica e transmitir afeto."
            prf  = "Ideal como presente personalizado ou decoracao de ambiente."
        desc = f"{clean}\n\nPor Que Este Produto e Especial:\n{esp}\n\nPerfeito Para:\n{prf}"
        self.database.setdefault(project_path, {})
        self.database[project_path]["ai_description"]           = desc
        self.database[project_path]["description_generated_at"] = datetime.now().isoformat()
        self.save_database()
        return desc

    # --- ESTRUTURA / TAGS / IMAGENS ---
    def get_origin(self, project_path):
        try:
            p  = os.path.basename(os.path.dirname(project_path))
            pu = p.upper()
            if "CREATIVE" in pu or "FABRICA" in pu: return "Creative Fabrica"
            if "ETSY" in pu: return "Etsy"
            return p
        except Exception: return "Diversos"

    def analyze_structure(self, project_path):
        s = {"total_files":0,"total_subfolders":0,"file_types":{},"subfolders":[],"images":[],"documents":[],"has_svg":False,"has_pdf":False,"has_dxf":False,"has_ai":False}
        try:
            for root, dirs, files in os.walk(project_path):
                s["total_files"] += len(files)
                if root == project_path:
                    s["subfolders"]       = dirs
                    s["total_subfolders"] = len(dirs)
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext: s["file_types"][ext] = s["file_types"].get(ext,0)+1
                    if ext == ".svg": s["has_svg"] = True
                    elif ext == ".pdf": s["has_pdf"] = True
                    elif ext == ".dxf": s["has_dxf"] = True
                    elif ext == ".ai":  s["has_ai"]  = True
                    if ext in (".png",".jpg",".jpeg",".gif",".bmp"): s["images"].append(f)
        except Exception: pass
        return s

    def extract_tags(self, name):
        clean = name
        for ext in [".zip",".rar",".7z",".svg",".pdf",".dxf"]: clean = clean.replace(ext,"")
        clean = re.sub(r"[-_]\d{5,}","",clean).replace("-"," ").replace("_"," ")
        stops = {"file","files","project","design","laser","cut","svg","pdf","vector","bundle","pack","set","collection"}
        words = [w for w in clean.split() if len(w)>=2 and not w.isdigit() and w.lower() not in stops]
        tags  = []
        if len(words)>=2: tags.append(" ".join(words[:4]).title())
        for w in words[:5]:
            if len(w)>=3: tags.append(w.capitalize())
        seen, unique = set(), []
        for t in tags:
            if t.lower() not in seen: seen.add(t.lower()); unique.append(t)
        return unique[:5]

    def _first_image(self, project_path):
        exts = (".png",".jpg",".jpeg",".gif",".bmp",".webp")
        try:
            for f in os.listdir(project_path):
                if f.lower().endswith(exts): return os.path.join(project_path, f)
        except Exception: pass
        return None

    def all_images(self, project_path):
        exts = (".png",".jpg",".jpeg",".gif",".bmp")
        imgs = []
        try:
            for f in os.listdir(project_path):
                if f.lower().endswith(exts): imgs.append(os.path.join(project_path, f))
        except Exception: pass
        return sorted(imgs)

    # --- SCAN / FILTROS ---
    def scan_projects(self):
        new_count = 0
        for root_folder in self.folders:
            if not os.path.exists(root_folder): continue
            for item in os.listdir(root_folder):
                pp = os.path.join(root_folder, item)
                if os.path.isdir(pp) and pp not in self.database:
                    self.database[pp] = {"name":item,"origin":self.get_origin(pp),"favorite":False,"done":False,"good":False,"bad":False,"categories":[],"tags":[],"analyzed":False,"ai_description":"","added_date":datetime.now().isoformat()}
                    new_count += 1
        if new_count > 0: self.save_database()
        return new_count

    def get_filtered(self, filter_type="all", origin="all", categories=None, tag=None, search=""):
        result = []
        for pp, data in self.database.items():
            show = (filter_type=="all" or
                    (filter_type=="favorite" and data.get("favorite")) or
                    (filter_type=="done"     and data.get("done"))     or
                    (filter_type=="good"     and data.get("good"))     or
                    (filter_type=="bad"      and data.get("bad")))
            if not show: continue
            if origin != "all" and data.get("origin") != origin: continue
            if categories and not any(c in data.get("categories",[]) for c in categories): continue
            if tag and tag not in data.get("tags",[]): continue
            if search and search.lower() not in data.get("name","").lower(): continue
            result.append(pp)
        return result

    def toggle(self, project_path, key):
        if project_path not in self.database: return False
        new_val = not self.database[project_path].get(key, False)
        if key == "good" and new_val: self.database[project_path]["bad"]  = False
        if key == "bad"  and new_val: self.database[project_path]["good"] = False
        self.database[project_path][key] = new_val
        self.save_database()
        return new_val

    # --- THREADS ---
    def run_analysis_thread(self, projects_list, on_progress=None, on_done=None):
        self.analyzing     = True
        self.stop_analysis = False
        def _run():
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.stop_analysis: break
                name = self.database.get(path,{}).get("name","?")[:30]
                if on_progress: on_progress(i, len(projects_list), name)
                cats, tags = self.analyze_with_ai(path, batch_size=len(projects_list))
                self.database[path]["categories"]     = cats
                self.database[path]["tags"]           = tags
                self.database[path]["analyzed"]       = True
                self.database[path]["analyzed_model"] = self._model(self._choose_role(len(projects_list)))
                self.save_database()
                completed += 1
            self.analyzing = False
            if on_done: on_done(completed, len(projects_list))
        threading.Thread(target=_run, daemon=True).start()

    def run_description_thread(self, projects_list, on_progress=None, on_done=None):
        self.analyzing     = True
        self.stop_analysis = False
        def _run():
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.stop_analysis: break
                data = self.database.get(path, {})
                name = data.get("name","?")[:30]
                if on_progress: on_progress(i, len(projects_list), name)
                self.generate_description(path, data)
                completed += 1
            self.analyzing = False
            if on_done: on_done(completed, len(projects_list))
        threading.Thread(target=_run, daemon=True).start()

    def open_folder(self, folder_path):
        try:
            if platform.system() == "Windows": os.startfile(os.path.abspath(folder_path))
            elif platform.system() == "Darwin": subprocess.run(["open", folder_path])
            else: subprocess.run(["xdg-open", folder_path])
        except Exception as e: LOGGER.error("Erro ao abrir pasta: %s", e)


# ===========================================================================
# FLASK
# ===========================================================================
engine           = LaserflixEngine()
app              = Flask(__name__)
_analysis_progress = {"current": 0, "total": 0, "name": "", "type": ""}

@app.route("/api/products")
def api_products():
    ft     = request.args.get("filter","all")
    origin = request.args.get("origin","all")
    cats   = [c for c in request.args.get("categories","").split(",") if c]
    tag    = request.args.get("tag","") or None
    search = request.args.get("search","")
    paths  = engine.get_filtered(ft, origin, cats or None, tag, search)
    items  = []
    for pp in paths:
        d     = engine.database.get(pp, {})
        cover = engine.all_images(pp)
        items.append({
            "id": pp, "name": d.get("name", os.path.basename(pp)),
            "origin": d.get("origin",""), "categories": d.get("categories",[]),
            "tags": d.get("tags",[]), "favorite": bool(d.get("favorite")),
            "done": bool(d.get("done")), "good": bool(d.get("good")), "bad": bool(d.get("bad")),
            "analyzed": bool(d.get("analyzed")), "ai_description": d.get("ai_description",""),
            "analyzed_model": d.get("analyzed_model",""),
            "added_date": (d.get("added_date","") or "")[:10],
            "has_cover": len(cover) > 0, "cover_count": len(cover),
            "structure": d.get("structure") or engine.analyze_structure(pp),
        })
    return jsonify(items)

@app.route("/api/product/<path:project_path>")
def api_product(project_path):
    if not project_path.startswith("/"): project_path = "/" + project_path
    if len(project_path) > 2 and project_path[0] == "/" and project_path[2] == ":":
        project_path = project_path[1:]
    d = engine.database.get(project_path, {})
    if not d: abort(404)
    cover = engine.all_images(project_path)
    return jsonify({
        "id": project_path, "name": d.get("name", os.path.basename(project_path)),
        "origin": d.get("origin",""), "categories": d.get("categories",[]),
        "tags": d.get("tags",[]), "favorite": bool(d.get("favorite")),
        "done": bool(d.get("done")), "good": bool(d.get("good")), "bad": bool(d.get("bad")),
        "analyzed": bool(d.get("analyzed")), "ai_description": d.get("ai_description",""),
        "analyzed_model": d.get("analyzed_model",""),
        "added_date": (d.get("added_date","") or "")[:10],
        "has_cover": len(cover) > 0, "cover_count": len(cover),
        "structure": d.get("structure") or engine.analyze_structure(project_path),
        "images": cover,
    })

@app.route("/api/cover")
def api_cover():
    pp  = request.args.get("path","")
    idx = int(request.args.get("idx","0"))
    imgs = engine.all_images(pp)
    if not imgs or idx >= len(imgs): abort(404)
    img_path = imgs[idx]
    if not os.path.exists(img_path): abort(404)
    return send_file(img_path)

@app.route("/api/toggle", methods=["POST"])
def api_toggle():
    data = request.get_json()
    pp   = data.get("path","")
    key  = data.get("key","")
    if not pp or key not in ("favorite","done","good","bad"): abort(400)
    new_val = engine.toggle(pp, key)
    return jsonify({"key": key, "value": new_val})

@app.route("/api/sidebar")
def api_sidebar():
    origins = Counter(d.get("origin","") for d in engine.database.values() if d.get("origin"))
    cats    = Counter(c for d in engine.database.values() for c in d.get("categories",[]))
    tags    = Counter(t for d in engine.database.values() for t in d.get("tags",[]))
    return jsonify({
        "origins":    [{"name":k,"count":v} for k,v in origins.most_common()],
        "categories": [{"name":k,"count":v} for k,v in cats.most_common(20)],
        "tags":       [{"name":k,"count":v} for k,v in tags.most_common(30)],
        "total":      len(engine.database),
    })

@app.route("/api/add_folder", methods=["POST"])
def api_add_folder():
    folder = request.get_json().get("folder","")
    if not folder or not os.path.isdir(folder):
        return jsonify({"error":"Pasta nao encontrada"}), 400
    if folder not in engine.folders:
        engine.folders.append(folder)
        engine.save_config()
    new_count = engine.scan_projects()
    return jsonify({"ok": True, "new_count": new_count})

@app.route("/api/scan", methods=["POST"])
def api_scan():
    n = engine.scan_projects()
    return jsonify({"ok": True, "new_count": n})

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json()
    mode = data.get("mode","new")
    if engine.analyzing: return jsonify({"error":"Analise em andamento"}), 409
    if   mode == "new":    projects = [p for p,d in engine.database.items() if not d.get("analyzed")]
    elif mode == "all":    projects = list(engine.database.keys())
    elif mode == "single": projects = [data.get("path","")]
    else:                  projects = []
    if not projects: return jsonify({"ok":True,"count":0})
    def on_progress(i,t,name): _analysis_progress.update({"current":i,"total":t,"name":name,"type":"analyze"})
    def on_done(done,total):   _analysis_progress.update({"current":done,"total":total,"name":"Concluido","type":""})
    engine.run_analysis_thread(projects, on_progress, on_done)
    return jsonify({"ok":True,"count":len(projects)})

@app.route("/api/describe", methods=["POST"])
def api_describe():
    data = request.get_json()
    mode = data.get("mode","single")
    if engine.analyzing: return jsonify({"error":"Analise em andamento"}), 409
    if mode == "single":
        pp = data.get("path","")
        d  = engine.database.get(pp, {})
        def _gen():
            _analysis_progress.update({"current":0,"total":1,"name":d.get("name","")[:30],"type":"describe"})
            engine.generate_description(pp, d)
            _analysis_progress.update({"current":1,"total":1,"name":"Concluido","type":""})
        threading.Thread(target=_gen, daemon=True).start()
        return jsonify({"ok":True})
    elif mode == "new": projects = [p for p,d in engine.database.items() if not (d.get("ai_description") or "").strip()]
    elif mode == "all": projects = list(engine.database.keys())
    else:               projects = []
    def on_progress(i,t,n):  _analysis_progress.update({"current":i,"total":t,"name":n,"type":"describe"})
    def on_done(done,total): _analysis_progress.update({"current":done,"total":total,"name":"Concluido","type":""})
    engine.run_description_thread(projects, on_progress, on_done)
    return jsonify({"ok":True,"count":len(projects)})

@app.route("/api/progress")
def api_progress():
    return jsonify({**_analysis_progress, "analyzing": engine.analyzing})

@app.route("/api/stop", methods=["POST"])
def api_stop():
    engine.stop_analysis = True
    return jsonify({"ok":True})

@app.route("/api/open_folder", methods=["POST"])
def api_open_folder():
    pp = request.get_json().get("path","")
    engine.open_folder(pp)
    return jsonify({"ok":True})

@app.route("/api/backup", methods=["POST"])
def api_backup():
    dst = engine.manual_backup()
    return jsonify({"ok":True,"file":dst or ""})

@app.route("/api/update_product", methods=["POST"])
def api_update_product():
    data = request.get_json()
    pp   = data.get("path","")
    if pp not in engine.database: abort(404)
    for key in ["name","categories","tags","ai_description","favorite","done","good","bad"]:
        if key in data: engine.database[pp][key] = data[key]
    engine.save_database()
    return jsonify({"ok":True})

@app.route("/api/models", methods=["GET","POST"])
def api_models():
    if request.method == "GET": return jsonify(engine.active_models)
    engine.active_models.update(request.get_json())
    engine.save_config()
    return jsonify({"ok":True})

@app.route("/api/ollama_status")
def api_ollama_status():
    return jsonify({"ok": engine._ollama_ok()})

@app.route("/api/folders", methods=["GET"])
def api_folders():
    return jsonify({"folders": engine.folders})

@app.route("/")
def index():
    return Response(HTML_PAGE, mimetype="text/html; charset=utf-8")

# ===========================================================================
# HTML — v8.1.1 Patch1 — layout v810 + correcoes completas
# ===========================================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LASERFLIX</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0a0a0a;--surface:#141414;--surface2:#1a1a1a;--surface3:#222;
  --red:#e50914;--red2:#b20710;--text:#fff;--text2:#b3b3b3;--text3:#666;
  --border:#2a2a2a;--card-radius:8px;--transition:.2s ease
}
html,body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh;overflow-x:hidden}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:#333;border-radius:3px}

/* TOPBAR */
#topbar{position:fixed;top:0;left:0;right:0;z-index:100;height:64px;
  display:flex;align-items:center;padding:0 24px;gap:16px;
  background:linear-gradient(to bottom,rgba(0,0,0,.95) 0,rgba(0,0,0,.7) 100%);
  backdrop-filter:blur(8px);border-bottom:1px solid rgba(255,255,255,.05)}
#logo{font-size:26px;font-weight:900;color:var(--red);letter-spacing:3px;
  text-decoration:none;flex-shrink:0;cursor:pointer;user-select:none}
#logo:hover{color:#ff1a27}
.topnav{display:flex;gap:4px;align-items:center}
.topnav-btn{background:transparent;border:none;color:var(--text2);font-family:'Inter',sans-serif;
  font-size:13px;font-weight:500;padding:6px 12px;border-radius:4px;cursor:pointer;
  transition:var(--transition);white-space:nowrap}
.topnav-btn:hover{color:var(--text);background:rgba(255,255,255,.08)}
.topnav-btn.active{color:var(--text);font-weight:600}
.search-wrap{flex:1;max-width:320px;margin-left:auto;position:relative}
.search-wrap input{width:100%;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);
  border-radius:6px;padding:8px 12px 8px 36px;color:var(--text);font-family:'Inter',sans-serif;
  font-size:13px;outline:none;transition:var(--transition)}
.search-wrap input:focus{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.25)}
.search-wrap input::placeholder{color:var(--text3)}
.search-icon{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--text3);font-size:14px;pointer-events:none}
.menu-btn{background:transparent;border:1px solid rgba(255,255,255,.15);color:var(--text2);
  width:36px;height:36px;border-radius:6px;cursor:pointer;font-size:18px;
  display:flex;align-items:center;justify-content:center;transition:var(--transition);flex-shrink:0}
.menu-btn:hover{background:rgba(255,255,255,.1);color:var(--text)}

/* DROPDOWN */
.menu-dropdown{position:fixed;top:68px;right:24px;background:var(--surface2);
  border:1px solid var(--border);border-radius:10px;padding:8px;min-width:220px;
  z-index:200;display:none;box-shadow:0 8px 32px rgba(0,0,0,.6)}
.menu-dropdown.open{display:block;animation:fadeIn .15s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
.menu-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:6px;
  cursor:pointer;font-size:13px;color:var(--text2);transition:var(--transition);
  border:none;background:transparent;width:100%;text-align:left;font-family:'Inter',sans-serif}
.menu-item:hover{background:rgba(255,255,255,.07);color:var(--text)}
.mi-icon{font-size:15px;width:20px;text-align:center}
.menu-sep{height:1px;background:var(--border);margin:6px 0}

/* PROGRESSO */
#progress-bar{display:none;position:fixed;top:64px;left:0;right:0;z-index:99;
  background:var(--surface2);border-bottom:1px solid var(--border);
  padding:8px 24px;align-items:center;gap:12px}
#progress-bar.visible{display:flex}
.pb-label{font-size:12px;color:var(--text2);white-space:nowrap}
.pb-track{flex:1;height:4px;background:var(--border);border-radius:2px;overflow:hidden}
.pb-fill{height:100%;background:var(--red);border-radius:2px;transition:width .3s ease;width:0}
.pb-pct{font-size:12px;color:var(--text3);white-space:nowrap;min-width:36px;text-align:right}
.pb-stop{background:transparent;border:1px solid #555;color:var(--text2);padding:4px 10px;
  border-radius:4px;cursor:pointer;font-size:11px;font-family:'Inter',sans-serif}
.pb-stop:hover{border-color:var(--red);color:var(--red)}

/* LAYOUT */
#app{display:flex;padding-top:64px;min-height:100vh}

/* SIDEBAR */
#sidebar{width:240px;flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);
  padding:16px 0;overflow-y:auto;position:sticky;top:64px;height:calc(100vh - 64px)}
.sb-title{font-size:10px;font-weight:700;color:var(--text3);letter-spacing:1.5px;
  text-transform:uppercase;padding:12px 16px 6px}
/* CORRECAO: hover e active sem conflito */
.sb-item{display:flex;align-items:center;justify-content:space-between;padding:7px 16px;
  cursor:pointer;border-radius:0;transition:var(--transition);font-size:13px;color:var(--text2);
  border:none;background:transparent;width:100%;text-align:left;font-family:'Inter',sans-serif;
  border-left:3px solid transparent}
.sb-item:hover{background:rgba(255,255,255,.05);color:var(--text)}
.sb-item.active{background:rgba(229,9,20,.12) !important;color:var(--red) !important;
  border-left:3px solid var(--red) !important;font-weight:600}
.sb-count{font-size:11px;color:var(--text3);background:var(--surface3);padding:1px 6px;border-radius:10px}
.sb-sep{height:1px;background:var(--border);margin:8px 16px}

/* MAIN */
#main{flex:1;padding:24px;overflow-x:hidden;min-width:0}
.section-title{font-size:20px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:10px}
.section-count{font-size:13px;font-weight:400;color:var(--text3)}

/* GRID */
.cards-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}

/* CARD */
.card{background:var(--surface);border-radius:var(--card-radius);overflow:hidden;cursor:pointer;
  transition:transform .2s ease,box-shadow .2s ease;position:relative}
.card:hover{transform:scale(1.03);box-shadow:0 8px 32px rgba(0,0,0,.6);z-index:2}
.card-img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:var(--surface2)}
.card-img-ph{width:100%;aspect-ratio:4/3;background:linear-gradient(135deg,#1e1e1e 0,#2a2a2a 100%);
  display:flex;align-items:center;justify-content:center;font-size:40px;color:#333}

/* AREA INFO — sempre visivel embaixo da thumbnail */
.card-info{padding:8px 10px 10px;background:#111}
.card-name{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  color:var(--text);margin-bottom:6px}

/* ACOES — sempre visiveis */
.card-actions{display:flex;align-items:center;gap:4px;margin-bottom:7px}
.ca-btn{background:none;border:none;cursor:pointer;font-size:16px;line-height:1;padding:2px 4px;
  border-radius:4px;transition:transform .12s,background .12s;user-select:none}
.ca-btn:hover{background:rgba(255,255,255,.1);transform:scale(1.2)}
.ca-btn.fav-on{color:#FFD700}
.ca-btn.fav-off{color:#555}
.ca-btn.done-on{color:#27ae60}
.ca-btn.done-off{color:#555}
.ca-btn.good-on{color:#2980b9}
.ca-btn.good-off{color:#555}
.ca-btn.bad-on{color:#e74c3c}
.ca-btn.bad-off{color:#555}
.ca-btn.folder-btn{color:#f39c12}
.ca-spacer{flex:1}

/* CATEGORIAS e TAGS — sempre visiveis */
.card-cats{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:3px;min-height:18px}
.card-tags-row{display:flex;flex-wrap:wrap;gap:3px;min-height:16px}
.cc-badge{background:#1a3050;color:#7ab8e8;border-radius:3px;font-size:9px;padding:1px 5px;
  white-space:nowrap;overflow:hidden;max-width:76px;text-overflow:ellipsis}
.ct-badge{background:#27184a;color:#b89ef0;border-radius:3px;font-size:9px;padding:1px 5px;
  white-space:nowrap;overflow:hidden;max-width:76px;text-overflow:ellipsis}

/* BADGE flags no topo do card */
.card-flags{position:absolute;top:8px;right:8px;display:flex;gap:4px}
.flag{font-size:11px;background:rgba(0,0,0,.7);padding:2px 5px;border-radius:4px;backdrop-filter:blur(4px)}

/* EMPTY */
.empty-state{text-align:center;padding:80px 24px;color:var(--text3)}
.empty-state .es-icon{font-size:64px;margin-bottom:16px;opacity:.3}
.empty-state h2{font-size:20px;font-weight:600;color:var(--text2);margin-bottom:8px}
.empty-state p{font-size:14px;line-height:1.6}
.es-btn{display:inline-block;margin-top:20px;background:var(--red);color:#fff;border:none;
  padding:10px 24px;border-radius:6px;cursor:pointer;font-size:14px;font-family:'Inter',sans-serif;
  font-weight:600;transition:background .15s}
.es-btn:hover{background:var(--red2)}

/* MODAL */
#modal-bg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:500;
  backdrop-filter:blur(4px);align-items:center;justify-content:center}
#modal-bg.open{display:flex;animation:fadeBg .2s ease}
@keyframes fadeBg{from{opacity:0}to{opacity:1}}
#modal{background:var(--surface);border-radius:12px;width:90%;max-width:900px;
  max-height:90vh;overflow:hidden;display:flex;flex-direction:column;position:relative;
  animation:slideUp .2s ease}
@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.modal-close{position:absolute;top:12px;right:12px;z-index:10;background:rgba(0,0,0,.5);
  border:none;color:var(--text2);width:36px;height:36px;border-radius:50%;cursor:pointer;
  font-size:18px;display:flex;align-items:center;justify-content:center;transition:var(--transition)}
.modal-close:hover{background:rgba(0,0,0,.8);color:var(--text)}
.modal-hero{position:relative;height:300px;overflow:hidden;flex-shrink:0}
.modal-hero img{width:100%;height:100%;object-fit:cover}
.modal-hero-ph{width:100%;height:100%;background:linear-gradient(135deg,#1a1a1a,#2a2a2a);
  display:flex;align-items:center;justify-content:center;font-size:64px;color:#333}
.modal-hero-grad{position:absolute;inset:0;background:linear-gradient(to top,var(--surface) 0,transparent 60%)}
.modal-gallery-nav{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);display:flex;gap:6px;z-index:5}
.gn-dot{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.3);cursor:pointer;transition:var(--transition)}
.gn-dot.active{background:#fff;width:20px;border-radius:4px}
.modal-nav-btn{position:absolute;top:50%;transform:translateY(-50%);background:rgba(0,0,0,.5);
  border:none;color:#fff;width:40px;height:40px;border-radius:50%;cursor:pointer;font-size:18px;
  display:flex;align-items:center;justify-content:center;transition:var(--transition)}
.modal-nav-btn:hover{background:rgba(0,0,0,.8)}
#modal-prev{left:12px}
#modal-next{right:12px}
.modal-body{padding:20px 24px 24px;overflow-y:auto;flex:1}
.modal-title{font-size:22px;font-weight:700;margin-bottom:4px}
.modal-origin{font-size:12px;color:var(--text3);margin-bottom:12px}
.modal-cats{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.cat-chip{background:rgba(229,9,20,.15);color:var(--red);border:1px solid rgba(229,9,20,.3);
  padding:3px 10px;border-radius:20px;font-size:11px;font-weight:500}
.modal-tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}
.tag-chip{background:var(--surface3);color:var(--text2);border:1px solid var(--border);
  padding:3px 10px;border-radius:20px;font-size:11px}
.modal-desc{font-size:13px;line-height:1.7;color:var(--text2);white-space:pre-wrap;
  background:var(--surface2);padding:14px;border-radius:8px;margin-bottom:16px}
.modal-desc-empty{font-size:13px;color:var(--text3);font-style:italic;margin-bottom:16px}
.modal-actions{display:flex;gap:10px;flex-wrap:wrap}
.ma-btn{display:flex;align-items:center;gap:6px;padding:8px 16px;border-radius:6px;
  border:1px solid var(--border);background:var(--surface2);color:var(--text2);cursor:pointer;
  font-size:13px;font-family:'Inter',sans-serif;font-weight:500;transition:var(--transition)}
.ma-btn:hover{background:var(--surface3);color:var(--text)}
.ma-btn.active{background:rgba(229,9,20,.15);border-color:rgba(229,9,20,.4);color:var(--red)}
.ma-btn.green.active{background:rgba(39,174,96,.15);border-color:rgba(39,174,96,.4);color:#27ae60}
.ma-btn.blue{border-color:rgba(52,152,219,.3)}
.ma-btn.blue:hover{background:rgba(52,152,219,.1);color:#3498db}
.modal-ai-row{display:flex;align-items:center;gap:8px;margin-top:8px}
.gen-desc-btn{background:var(--red);border:none;color:#fff;padding:8px 16px;border-radius:6px;
  cursor:pointer;font-size:13px;font-family:'Inter',sans-serif;font-weight:600;transition:background .15s}
.gen-desc-btn:hover{background:var(--red2)}
.gen-desc-btn:disabled{background:#444;cursor:default}

/* TOAST */
#toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
  background:var(--surface2);border:1px solid var(--border);color:var(--text);
  padding:10px 20px;border-radius:8px;font-size:13px;z-index:999;white-space:nowrap;
  box-shadow:0 4px 16px rgba(0,0,0,.5);animation:toastIn .2s ease;display:none}
#toast.show{display:block}
@keyframes toastIn{from{opacity:0;transform:translateX(-50%) translateY(10px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}

.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#555;margin-right:6px}
.status-dot.ok{background:#27ae60}
</style>
</head>
<body>

<!-- TOPBAR -->
<header id="topbar">
  <div id="logo" onclick="setFilter('all',null)">LASERFLIX</div>
  <nav class="topnav">
    <button class="topnav-btn active" onclick="setFilter('all',this)">In&#237;cio</button>
    <button class="topnav-btn" onclick="setFilter('favorite',this)">&#11088; Favoritos</button>
    <button class="topnav-btn" onclick="setFilter('done',this)">&#10003; Feitos</button>
    <button class="topnav-btn" onclick="setFilter('good',this)">&#128077; Bons</button>
    <button class="topnav-btn" onclick="setFilter('bad',this)">&#128078; Ruins</button>
  </nav>
  <div class="search-wrap">
    <span class="search-icon">&#128269;</span>
    <input type="text" id="search-input" placeholder="Buscar produtos..." oninput="onSearch(this.value)">
  </div>
  <button class="menu-btn" onclick="toggleMenu()" title="Menu">&#8942;</button>
</header>

<!-- DROPDOWN -->
<div class="menu-dropdown" id="menu-dd">
  <button class="menu-item" onclick="addFolder();closeMenu()"><span class="mi-icon">&#128194;</span> Adicionar Pasta</button>
  <button class="menu-item" onclick="doScan();closeMenu()"><span class="mi-icon">&#128260;</span> Escanear Pastas</button>
  <div class="menu-sep"></div>
  <button class="menu-item" onclick="doAnalyze('new');closeMenu()"><span class="mi-icon">&#129302;</span> Analisar Novos (IA)</button>
  <button class="menu-item" onclick="doAnalyze('all');closeMenu()"><span class="mi-icon">&#128260;</span> Reanalisar Todos</button>
  <button class="menu-item" onclick="doDescribe('new');closeMenu()"><span class="mi-icon">&#9997;</span> Gerar Descri&#231;&#245;es Novas</button>
  <div class="menu-sep"></div>
  <button class="menu-item" onclick="doBackup();closeMenu()"><span class="mi-icon">&#128190;</span> Backup Manual</button>
</div>

<!-- PROGRESSO -->
<div id="progress-bar">
  <span class="pb-label" id="pb-label">Analisando...</span>
  <div class="pb-track"><div class="pb-fill" id="pb-fill"></div></div>
  <span class="pb-pct" id="pb-pct">0%</span>
  <button class="pb-stop" onclick="doStop()">&#9632; Parar</button>
</div>

<!-- APP -->
<div id="app">
  <!-- SIDEBAR -->
  <aside id="sidebar">
    <div class="sb-title">Origem</div>
    <div id="sb-origins"></div>
    <div class="sb-sep"></div>
    <div class="sb-title">Categorias</div>
    <div id="sb-cats"></div>
    <div class="sb-sep"></div>
    <div class="sb-title">Tags</div>
    <div id="sb-tags"></div>
  </aside>

  <!-- MAIN -->
  <main id="main">
    <div class="section-title">
      <span id="section-label">Todos os Produtos</span>
      <span class="section-count" id="section-count"></span>
    </div>
    <div class="cards-grid" id="cards-grid">
      <div class="empty-state" style="grid-column:1/-1">
        <div class="es-icon">&#128230;</div>
        <h2>Carregando cat&#225;logo...</h2>
        <p>Aguarde um momento.</p>
      </div>
    </div>
  </main>
</div>

<!-- MODAL -->
<div id="modal-bg" onclick="closeModalBg(event)">
  <div id="modal">
    <button class="modal-close" onclick="closeModal()">&#10005;</button>
    <div class="modal-hero" id="modal-hero">
      <div class="modal-hero-ph" id="modal-hero-ph">&#128230;</div>
      <img id="modal-hero-img" src="" alt="" style="display:none" onerror="this.style.display='none';document.getElementById('modal-hero-ph').style.display='flex'">
      <div class="modal-hero-grad"></div>
      <button class="modal-nav-btn" id="modal-prev" onclick="galleryNav(-1)">&#8249;</button>
      <button class="modal-nav-btn" id="modal-next" onclick="galleryNav(1)">&#8250;</button>
      <div class="modal-gallery-nav" id="modal-gallery-nav"></div>
    </div>
    <div class="modal-body">
      <div class="modal-title" id="modal-title"></div>
      <div class="modal-origin" id="modal-origin"></div>
      <div class="modal-cats"  id="modal-cats"></div>
      <div class="modal-tags"  id="modal-tags"></div>
      <div id="modal-desc-wrap"></div>
      <div class="modal-ai-row">
        <button class="gen-desc-btn" id="gen-desc-btn" onclick="generateDesc()">&#9997;&#65039; Gerar Descri&#231;&#227;o</button>
      </div>
      <div class="modal-actions" id="modal-actions" style="margin-top:14px"></div>
    </div>
  </div>
</div>

<!-- TOAST -->
<div id="toast"></div>

<script>
// ─── STATE ───
let state = {filter:'all', origin:'all', categories:[], tag:null, search:'', products:[], currentProduct:null, galleryIdx:0, galleryImgs:[]};
let progressInterval = null;
let _activeNavBtn    = null;
let _activeSbOrigin  = null;
let _activeSbCat     = null;
let _activeSbTag     = null;

// ─── BOOT ───
document.addEventListener('DOMContentLoaded', () => { loadSidebar(); loadProducts(); });
document.addEventListener('keydown', e => {
  if(e.key==='Escape') closeModal();
  if(document.getElementById('modal-bg').classList.contains('open')){
    if(e.key==='ArrowLeft')  galleryNav(-1);
    if(e.key==='ArrowRight') galleryNav(1);
  }
});
document.addEventListener('click', e => {
  const dd = document.getElementById('menu-dd');
  if(dd.classList.contains('open') && !dd.contains(e.target) && !e.target.closest('.menu-btn'))
    dd.classList.remove('open');
});

// ─── FILTROS ───
// CORRIGIDO: reseta TODOS os filtros especificos + destaque sidebar
function setFilter(f, btn){
  state.filter     = f;
  state.origin     = 'all';
  state.categories = [];
  state.tag        = null;

  // nav topbar
  document.querySelectorAll('.topnav-btn').forEach(b => b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  _activeNavBtn = btn;

  // sidebar: remove active de todas as origens/cats/tags
  _clearSidebarActive();

  loadProducts();
}

// CORRIGIDO: setOrigin
function setOrigin(o, btn){
  if(state.origin === o){
    state.origin = 'all';
    if(btn) btn.classList.remove('active');
    _activeSbOrigin = null;
  } else {
    state.origin = o;
    if(_activeSbOrigin) _activeSbOrigin.classList.remove('active');
    if(btn){ btn.classList.add('active'); _activeSbOrigin = btn; }
  }
  state.filter     = 'all';
  state.categories = [];
  state.tag        = null;
  document.querySelectorAll('.topnav-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('.topnav-btn').classList.add('active');
  if(_activeSbCat){ _activeSbCat.classList.remove('active'); _activeSbCat=null; }
  if(_activeSbTag){ _activeSbTag.classList.remove('active'); _activeSbTag=null; }
  loadProducts();
}

function toggleCat(c, btn){
  const idx = state.categories.indexOf(c);
  if(idx >= 0){
    state.categories.splice(idx,1);
    if(btn) btn.classList.remove('active');
    _activeSbCat = null;
  } else {
    state.categories.push(c);
    if(_activeSbCat) _activeSbCat.classList.remove('active');
    if(btn){ btn.classList.add('active'); _activeSbCat = btn; }
  }
  state.filter = 'all';
  state.origin = 'all';
  state.tag    = null;
  document.querySelectorAll('.topnav-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('.topnav-btn').classList.add('active');
  if(_activeSbOrigin){ _activeSbOrigin.classList.remove('active'); _activeSbOrigin=null; }
  if(_activeSbTag)   { _activeSbTag.classList.remove('active');    _activeSbTag=null; }
  loadProducts();
}

// CORRIGIDO: setTag
function setTag(t, btn){
  if(state.tag === t){
    state.tag = null;
    if(btn) btn.classList.remove('active');
    _activeSbTag = null;
  } else {
    state.tag = t;
    if(_activeSbTag) _activeSbTag.classList.remove('active');
    if(btn){ btn.classList.add('active'); _activeSbTag = btn; }
  }
  state.filter     = 'all';
  state.origin     = 'all';
  state.categories = [];
  document.querySelectorAll('.topnav-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('.topnav-btn').classList.add('active');
  if(_activeSbOrigin){ _activeSbOrigin.classList.remove('active'); _activeSbOrigin=null; }
  if(_activeSbCat)   { _activeSbCat.classList.remove('active');    _activeSbCat=null; }
  loadProducts();
}

function _clearSidebarActive(){
  if(_activeSbOrigin){ _activeSbOrigin.classList.remove('active'); _activeSbOrigin=null; }
  if(_activeSbCat)   { _activeSbCat.classList.remove('active');    _activeSbCat=null; }
  if(_activeSbTag)   { _activeSbTag.classList.remove('active');    _activeSbTag=null; }
}

let searchTimer;
function onSearch(v){
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { state.search = v; loadProducts(); }, 300);
}

// ─── SIDEBAR ───
async function loadSidebar(){
  const data = await api('/api/sidebar');
  if(!data) return;
  const originsEl = document.getElementById('sb-origins');
  const catsEl    = document.getElementById('sb-cats');
  const tagsEl    = document.getElementById('sb-tags');

  originsEl.innerHTML = `<button class="sb-item active" onclick="setOrigin('all',this)"><span>Todos</span><span class="sb-count">${data.total}</span></button>`;
  originsEl.innerHTML += data.origins.map(o =>
    `<button class="sb-item" onclick="setOrigin(${escAttr(o.name)},this)"><span>${escHtml(o.name)}</span><span class="sb-count">${o.count}</span></button>`
  ).join('');

  catsEl.innerHTML = data.categories.map(c =>
    `<button class="sb-item" onclick="toggleCat(${escAttr(c.name)},this)"><span>${escHtml(c.name)}</span><span class="sb-count">${c.count}</span></button>`
  ).join('');

  tagsEl.innerHTML = data.tags.map(t =>
    `<button class="sb-item" onclick="setTag(${escAttr(t.name)},this)"><span>${escHtml(t.name)}</span><span class="sb-count">${t.count}</span></button>`
  ).join('');
}

// ─── PRODUTOS ───
async function loadProducts(){
  const params = new URLSearchParams({
    filter: state.filter, origin: state.origin,
    categories: state.categories.join(','), tag: state.tag||'', search: state.search,
  });
  const data = await api('/api/products?' + params);
  if(!data) return;
  state.products = data;
  renderCards(data);
}

function renderCards(items){
  const grid = document.getElementById('cards-grid');
  document.getElementById('section-count').textContent = items.length + ' produto(s)';

  let label = 'Todos os Produtos';
  if(state.filter==='favorite') label='&#11088; Favoritos';
  else if(state.filter==='done') label='&#10003; Feitos';
  else if(state.filter==='good') label='&#128077; Bons';
  else if(state.filter==='bad')  label='&#128078; Ruins';
  else if(state.origin!=='all')  label='Origem: '+escHtml(state.origin);
  else if(state.categories.length) label='Categoria: '+escHtml(state.categories[0]);
  else if(state.tag) label='Tag: '+escHtml(state.tag);
  document.getElementById('section-label').innerHTML = label;

  if(!items.length){
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
      <div class="es-icon">&#128230;</div>
      <h2>Nenhum produto encontrado</h2>
      <p>Tente outros filtros ou adicione uma pasta.</p>
      <button class="es-btn" onclick="addFolder()">&#128194; Adicionar Pasta</button>
    </div>`;
    return;
  }

  grid.innerHTML = '';
  items.forEach(p => {
    const div = document.createElement('div');
    div.className = 'card';
    div.onclick = (e) => { if(!e.target.closest('.ca-btn')) openModal(p.id); };

    // Imagem
    let imgHtml = p.has_cover
      ? `<img class="card-img" src="/api/cover?path=${encodeURIComponent(p.id)}&idx=0" alt="${escHtml(p.name)}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">`+
        `<div class="card-img-ph" style="display:none">&#128230;</div>`
      : `<div class="card-img-ph">&#128230;</div>`;

    // Flags badge topo
    let flags = '';
    if(p.favorite) flags += `<span class="flag">&#11088;</span>`;
    if(p.done)     flags += `<span class="flag">&#10003;</span>`;

    // Categorias top 3
    const cats = (p.categories||[]).slice(0,3).map(c=>`<span class="cc-badge">${escHtml(c)}</span>`).join('');
    // Tags top 3
    const tags = (p.tags||[]).slice(0,3).map(t=>`<span class="ct-badge">#${escHtml(t)}</span>`).join('');

    div.innerHTML = `
      ${imgHtml}
      ${flags ? `<div class="card-flags">${flags}</div>` : ''}
      <div class="card-info">
        <div class="card-name">${escHtml(p.name)}</div>
        <div class="card-actions">
          <button class="ca-btn ${p.favorite?'fav-on':'fav-off'}" title="Favorito"
            onclick="toggleFlag(event,'${escAttr2(p.id)}','favorite',this)">&#11088;</button>
          <button class="ca-btn ${p.done?'done-on':'done-off'}" title="Feito"
            onclick="toggleFlag(event,'${escAttr2(p.id)}','done',this)">&#10003;</button>
          <button class="ca-btn ${p.good?'good-on':'good-off'}" title="Bom"
            onclick="toggleFlag(event,'${escAttr2(p.id)}','good',this)">&#128077;</button>
          <button class="ca-btn ${p.bad?'bad-on':'bad-off'}" title="Ruim"
            onclick="toggleFlag(event,'${escAttr2(p.id)}','bad',this)">&#128078;</button>
          <span style="flex:1"></span>
          <button class="ca-btn folder-btn" title="Abrir pasta"
            onclick="openFolder(event,'${escAttr2(p.id)}')">&#128193;</button>
        </div>
        <div class="card-cats">${cats}</div>
        <div class="card-tags-row">${tags}</div>
      </div>`;
    grid.appendChild(div);
  });
}

// ─── TOGGLE FLAG NO CARD ───
async function toggleFlag(e, pid, key, btn){
  e.stopPropagation();
  const r = await api('/api/toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({path:pid, key})});
  if(!r) return;
  const p = state.products.find(x => x.id===pid);
  if(p){
    p[key] = r.value;
    if(key==='good' && r.value) p.bad=false;
    if(key==='bad'  && r.value) p.good=false;
  }
  // atualiza so o botao clicado (sem re-render total)
  const classMap = {
    favorite: ['fav-on','fav-off'],
    done:     ['done-on','done-off'],
    good:     ['good-on','good-off'],
    bad:      ['bad-on','bad-off'],
  };
  const [on,off] = classMap[key];
  btn.className = 'ca-btn ' + (r.value ? on : off);
  // se good/bad, atualiza o oposto
  if(key==='good' && r.value){
    const badBtn = btn.parentElement.querySelector('.bad-on');
    if(badBtn){ badBtn.className='ca-btn bad-off'; if(p) p.bad=false; }
  }
  if(key==='bad' && r.value){
    const goodBtn = btn.parentElement.querySelector('.good-on');
    if(goodBtn){ goodBtn.className='ca-btn good-off'; if(p) p.good=false; }
  }
  const msgs = {favorite:'&#11088; Favorito atualizado',done:'&#10003; Feito atualizado',good:'&#128077; Bom',bad:'&#128078; Ruim'};
  showToast(msgs[key]);
}

async function openFolder(e, pid){
  e.stopPropagation();
  await api('/api/open_folder', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({path:pid})});
  showToast('&#128193; Abrindo pasta...');
}

// ─── MODAL ───
async function openModal(pid){
  const p = await api('/api/product/' + encodeURIComponent(pid).replace(/%2F/g,'/').replace(/%3A/g,':'));
  if(!p) return;
  state.currentProduct = p;
  state.galleryImgs    = p.images || [];
  state.galleryIdx     = 0;

  document.getElementById('modal-title').textContent  = p.name;
  document.getElementById('modal-origin').textContent = p.origin ? '&#127757;&#65039; '+p.origin : '';
  document.getElementById('modal-origin').innerHTML   = p.origin ? '&#127757;&#65039; '+escHtml(p.origin) : '';

  const catsEl = document.getElementById('modal-cats');
  catsEl.innerHTML = (p.categories||[]).map(c=>`<span class="cat-chip">${escHtml(c)}</span>`).join('');

  const tagsEl = document.getElementById('modal-tags');
  tagsEl.innerHTML = (p.tags||[]).map(t=>`<span class="tag-chip">#${escHtml(t)}</span>`).join('');

  const descWrap = document.getElementById('modal-desc-wrap');
  if(p.ai_description){
    descWrap.innerHTML = `<div class="modal-desc">${escHtml(p.ai_description)}</div>`;
  } else {
    descWrap.innerHTML = `<div class="modal-desc-empty">Nenhuma descri&#231;&#227;o gerada ainda.</div>`;
  }

  // acoes
  const actEl = document.getElementById('modal-actions');
  actEl.innerHTML = `
    <button class="ma-btn ${p.favorite?'active':''}" onclick="modalToggle('favorite')">&#11088; Favorito</button>
    <button class="ma-btn green ${p.done?'active':''}" onclick="modalToggle('done')">&#10003; Feito</button>
    <button class="ma-btn ${p.good?'active':''}" onclick="modalToggle('good')">&#128077; Bom</button>
    <button class="ma-btn ${p.bad?'active':''}" onclick="modalToggle('bad')">&#128078; Ruim</button>
    <button class="ma-btn blue" onclick="modalOpenFolder()">&#128193; Abrir Pasta</button>`;

  // galeria
  updateGallery();
  document.getElementById('modal-bg').classList.add('open');
}

function updateGallery(){
  const p       = state.currentProduct;
  const imgs    = state.galleryImgs;
  const idx     = state.galleryIdx;
  const heroImg = document.getElementById('modal-hero-img');
  const heroPh  = document.getElementById('modal-hero-ph');
  const navEl   = document.getElementById('modal-gallery-nav');
  const prevBtn = document.getElementById('modal-prev');
  const nextBtn = document.getElementById('modal-next');

  if(imgs && imgs.length > 0){
    heroImg.src = '/api/cover?path='+encodeURIComponent(p.id)+'&idx='+idx;
    heroImg.style.display = 'block';
    heroPh.style.display  = 'none';
    navEl.innerHTML = imgs.map((_,i)=>`<div class="gn-dot${i===idx?' active':''}" onclick="setGallery(${i})"></div>`).join('');
    prevBtn.style.display = idx>0 ? 'flex' : 'none';
    nextBtn.style.display = idx<imgs.length-1 ? 'flex' : 'none';
  } else {
    heroImg.style.display = 'none';
    heroPh.style.display  = 'flex';
    navEl.innerHTML       = '';
    prevBtn.style.display = 'none';
    nextBtn.style.display = 'none';
  }
}

function setGallery(i){ state.galleryIdx=i; updateGallery(); }
function galleryNav(dir){
  const n = state.galleryImgs.length;
  if(!n) return;
  state.galleryIdx = Math.max(0, Math.min(n-1, state.galleryIdx+dir));
  updateGallery();
}

async function modalToggle(key){
  const p = state.currentProduct;
  if(!p) return;
  const r = await api('/api/toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({path:p.id, key})});
  if(!r) return;
  p[key] = r.value;
  if(key==='good' && r.value) p.bad=false;
  if(key==='bad'  && r.value) p.good=false;
  // re-render acoes
  const actEl = document.getElementById('modal-actions');
  actEl.innerHTML = `
    <button class="ma-btn ${p.favorite?'active':''}" onclick="modalToggle('favorite')">&#11088; Favorito</button>
    <button class="ma-btn green ${p.done?'active':''}" onclick="modalToggle('done')">&#10003; Feito</button>
    <button class="ma-btn ${p.good?'active':''}" onclick="modalToggle('good')">&#128077; Bom</button>
    <button class="ma-btn ${p.bad?'active':''}" onclick="modalToggle('bad')">&#128078; Ruim</button>
    <button class="ma-btn blue" onclick="modalOpenFolder()">&#128193; Abrir Pasta</button>`;
  showToast('Atualizado!');
}

async function modalOpenFolder(){
  const p = state.currentProduct;
  if(!p) return;
  await api('/api/open_folder', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({path:p.id})});
  showToast('&#128193; Abrindo pasta...');
}

// CORRIGIDO: innerHTML no botao Regenerar
async function generateDesc(){
  const p   = state.currentProduct;
  if(!p) return;
  const btn = document.getElementById('gen-desc-btn');
  btn.disabled = true;
  btn.innerHTML = '&#9203;&#65039; Gerando...';
  const r = await api('/api/describe', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({mode:'single', path:p.id})});
  if(r){
    showToast('&#9997;&#65039; Gerando descri&#231;&#227;o em segundo plano...');
    setTimeout(async ()=>{
      const updated = await api('/api/product/'+encodeURIComponent(p.id).replace(/%2F/g,'/').replace(/%3A/g,':'));
      if(updated && updated.ai_description){
        document.getElementById('modal-desc-wrap').innerHTML = `<div class="modal-desc">${escHtml(updated.ai_description)}</div>`;
        state.currentProduct.ai_description = updated.ai_description;
      }
      btn.disabled = false;
      btn.innerHTML = '&#9997;&#65039; Regenerar Descri&#231;&#227;o';
    }, 3000);
  } else {
    btn.disabled = false;
    btn.innerHTML = '&#9997;&#65039; Regenerar Descri&#231;&#227;o';
  }
}

function closeModal(){
  document.getElementById('modal-bg').classList.remove('open');
  state.currentProduct = null;
}
function closeModalBg(e){
  if(e.target === document.getElementById('modal-bg')) closeModal();
}

// ─── ACOES MENU ───
async function addFolder(){
  const folder = prompt('Cole o caminho completo da pasta:');
  if(!folder) return;
  const r = await api('/api/add_folder', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({folder})});
  if(!r) return;
  if(r.error){ showToast('&#10060; '+r.error); return; }
  showToast('&#10004; '+r.new_count+' produto(s) encontrado(s)!');
  loadSidebar();
  loadProducts();
}

async function doScan(){
  const r = await api('/api/scan', {method:'POST'});
  if(!r) return;
  showToast('&#10004; '+r.new_count+' novo(s) produto(s)!');
  loadSidebar();
  loadProducts();
}

async function doAnalyze(mode){
  const r = await api('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({mode})});
  if(!r || r.error){ showToast('&#10060; '+(r&&r.error?r.error:'Erro')); return; }
  showToast('&#129302; Analisando '+r.count+' produto(s)...');
  startProgress();
}

async function doDescribe(mode){
  const r = await api('/api/describe', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({mode})});
  if(!r || r.error){ showToast('&#10060; '+(r&&r.error?r.error:'Erro')); return; }
  showToast('&#9997; Gerando descri&#231;&#245;es...');
  startProgress();
}

async function doBackup(){
  const r = await api('/api/backup', {method:'POST'});
  if(r) showToast('&#128190; Backup salvo!');
}

async function doStop(){
  await api('/api/stop', {method:'POST'});
  showToast('&#9632; Analise interrompida.');
}

// ─── PROGRESSO ───
function startProgress(){
  const bar = document.getElementById('progress-bar');
  bar.classList.add('visible');
  if(progressInterval) clearInterval(progressInterval);
  progressInterval = setInterval(async ()=>{
    const r = await api('/api/progress');
    if(!r) return;
    const pct = r.total>0 ? Math.round(r.current/r.total*100) : 0;
    document.getElementById('pb-fill').style.width  = pct+'%';
    document.getElementById('pb-pct').textContent   = pct+'%';
    document.getElementById('pb-label').textContent = r.name || 'Analisando...';
    if(!r.analyzing){
      clearInterval(progressInterval);
      progressInterval = null;
      bar.classList.remove('visible');
      showToast('&#10004; Conclu&#237;do!');
      loadSidebar();
      loadProducts();
    }
  }, 1200);
}

// ─── MENU ───
function toggleMenu(){
  document.getElementById('menu-dd').classList.toggle('open');
}
function closeMenu(){
  document.getElementById('menu-dd').classList.remove('open');
}

// ─── UTILS ───
async function api(url, opts){
  try{ const r = await fetch(url, opts); return await r.json(); }
  catch(e){ console.error(url,e); return null; }
}
function escHtml(s){
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escAttr(s){
  return '"'+String(s||'').replace(/\\\\/g,'\\\\\\\\').replace(/"/g,'\\\\"')+'"';
}
function escAttr2(s){
  return String(s||'').replace(/\\\\/g,'\\\\\\\\').replace(/'/g,"\\\\'");
}
function showToast(msg){
  const t = document.getElementById('toast');
  t.innerHTML = msg;
  t.classList.add('show');
  clearTimeout(t._tid);
  t._tid = setTimeout(()=>t.classList.remove('show'), 2800);
}
</script>
</body>
</html>"""

if __name__ == "__main__":
    port = 5678
    def _open():
        time.sleep(1.2)
        webbrowser.open(f"http://localhost:{port}")
    threading.Thread(target=_open, daemon=True).start()
    engine.auto_backup()
    print(f"\n  LASERFLIX v{VERSION} (Patch 1)")
    print(f"  http://localhost:{port}")
    print("  Ctrl+C para encerrar\n")
    app.run(port=port, debug=False, use_reloader=False)
