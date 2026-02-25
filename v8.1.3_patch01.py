#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LASERFLIX v8.1.3.0
Base: v8.1.2.2

Patches v8.1.3.0:
  5 - Paginação / Lazy loading na listagem (/api/products suporta offset/limit + frontend "Carregar mais")
  6 - Modal: edicao inline de Nome / Categorias / Tags (UI + /api/update_product)
  7 - Card: contador de imagens (cover_count) exibido no canto do card
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

VERSION       = "8.1.3.0"
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
# ENGINE  (identico ao v8.1.1 Stable — NAO ALTERAR)
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

    def generate_description(self, project_path, data, force_new=False):
        """Gera descricao. force_new=True ignora descricao existente e usa temperature alta para variar."""
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
            temp = 0.92 if force_new else 0.78
            force_hint = "\n\nIMPORTANTE: Crie uma descricao COMPLETAMENTE NOVA e DIFERENTE da versao anterior. Use palavras e angulos distintos." if force_new else ""
            prompt = (
                f"Especialista em pecas fisicas de corte a laser.\n\n"
                f"NOME DA PECA: {clean}{vision_ctx}{force_hint}\n\n"
                "REGRA: O NOME define o produto. Visual apenas complementa.\n\n"
                f"ESCREVA exatamente:\n\n{clean}\n\n"
                "Por Que Este Produto e Especial:\n[2-3 frases unicas e afetivas]\n\n"
                "Perfeito Para:\n[2-3 frases praticas com exemplos reais]\n\n"
                "REGRAS: portugues BR, sem palavras 'projeto'/'arquivo'/'SVG', max 120 palavras."
            )
            resp = self._ollama_text(prompt, role="text_quality", temperature=temp, num_predict=250)
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

    def run_analysis_thread(self, projects_list, on_progress=None, on_done=None, with_description=False, force_desc=False):
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
                if with_description and not self.stop_analysis:
                    d = self.database.get(path, {})
                    self.generate_description(path, d, force_new=force_desc)
                completed += 1
            self.analyzing = False
            if on_done: on_done(completed, len(projects_list))
        threading.Thread(target=_run, daemon=True).start()

    def run_description_thread(self, projects_list, on_progress=None, on_done=None, force_new=False):
        self.analyzing     = True
        self.stop_analysis = False
        def _run():
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.stop_analysis: break
                data = self.database.get(path, {})
                name = data.get("name","?")[:30]
                if on_progress: on_progress(i, len(projects_list), name)
                self.generate_description(path, data, force_new=force_new)
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
engine             = LaserflixEngine()
app                = Flask(__name__)
_analysis_progress = {"current": 0, "total": 0, "name": "", "type": ""}

@app.route("/api/products")
def api_products():
    ft     = request.args.get("filter","all")
    origin = request.args.get("origin","all")
    cats   = [c for c in request.args.get("categories","").split(",") if c]
    tag    = request.args.get("tag","") or None
    search = request.args.get("search","")

    # PATCH 5 — paginacao
    try:
        offset = int(request.args.get("offset", "0"))
        limit  = int(request.args.get("limit",  "120"))
    except Exception:
        offset, limit = 0, 120
    offset = max(0, offset)
    limit  = max(20, min(500, limit))

    paths_all = engine.get_filtered(ft, origin, cats or None, tag, search)
    total     = len(paths_all)
    paths     = paths_all[offset:offset+limit]

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
    return jsonify({"items": items, "total": total, "offset": offset, "limit": limit})

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
    d = engine.database.get(pp, {})
    return jsonify({"key": key, "value": new_val,
                    "favorite": bool(d.get("favorite")),
                    "done":     bool(d.get("done")),
                    "good":     bool(d.get("good")),
                    "bad":      bool(d.get("bad"))})

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
    data         = request.get_json()
    mode         = data.get("mode","new")
    with_desc    = data.get("with_description", False)
    force_desc   = data.get("force_description", False)
    if engine.analyzing: return jsonify({"error":"Analise em andamento"}), 409
    if   mode == "new":    projects = [p for p,d in engine.database.items() if not d.get("analyzed")]
    elif mode == "all":    projects = list(engine.database.keys())
    elif mode == "single": projects = [data.get("path","")]
    else:                  projects = []
    if not projects: return jsonify({"ok":True,"count":0})
    def on_progress(i,t,name): _analysis_progress.update({"current":i,"total":t,"name":name,"type":"analyze"})
    def on_done(done,total):   _analysis_progress.update({"current":done,"total":total,"name":"Concluido","type":""})
    engine.run_analysis_thread(projects, on_progress, on_done, with_description=with_desc, force_desc=force_desc)
    return jsonify({"ok":True,"count":len(projects)})

@app.route("/api/describe", methods=["POST"])
def api_describe():
    data      = request.get_json()
    mode      = data.get("mode","single")
    force_new = data.get("force_new", False)
    if engine.analyzing: return jsonify({"error":"Analise em andamento"}), 409
    if mode == "single":
        pp = data.get("path","")
        d  = engine.database.get(pp, {})
        def _gen():
            _analysis_progress.update({"current":0,"total":1,"name":d.get("name","")[:30],"type":"describe"})
            engine.generate_description(pp, d, force_new=True)
            _analysis_progress.update({"current":1,"total":1,"name":"Concluido","type":""})
        threading.Thread(target=_gen, daemon=True).start()
        return jsonify({"ok":True})
    elif mode == "new": projects = [p for p,d in engine.database.items() if not (d.get("ai_description") or "").strip()]
    elif mode == "all": projects = list(engine.database.keys())
    else:               projects = []
    def on_progress(i,t,n):  _analysis_progress.update({"current":i,"total":t,"name":n,"type":"describe"})
    def on_done(done,total): _analysis_progress.update({"current":done,"total":total,"name":"Concluido","type":""})
    engine.run_description_thread(projects, on_progress, on_done, force_new=force_new)
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
# HTML — v8.1.3.0
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

/* ── TOPBAR ── */
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

/* ── DROPDOWN ── */
.menu-dropdown{position:fixed;top:68px;right:24px;background:var(--surface2);
  border:1px solid var(--border);border-radius:10px;padding:8px;min-width:280px;
  z-index:200;display:none;box-shadow:0 8px 32px rgba(0,0,0,.6)}
.menu-dropdown.open{display:block;animation:fadeIn .15s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
.menu-item{display:flex;align-items:flex-start;gap:10px;padding:10px 12px;border-radius:6px;
  cursor:pointer;font-size:13px;color:var(--text2);transition:var(--transition);
  border:none;background:transparent;width:100%;text-align:left;font-family:'Inter',sans-serif}
.menu-item:hover{background:rgba(255,255,255,.07);color:var(--text)}
.mi-icon{font-size:15px;width:20px;text-align:center;flex-shrink:0;margin-top:1px}
.mi-text{display:flex;flex-direction:column;gap:2px}
.mi-label{font-weight:600;color:var(--text)}
.mi-desc{font-size:11px;color:var(--text3);line-height:1.4}
.menu-sep{height:1px;background:var(--border);margin:6px 0}
.menu-section-title{font-size:10px;font-weight:700;color:var(--text3);letter-spacing:1.5px;
  text-transform:uppercase;padding:8px 12px 4px}

/* ── PROGRESSO ── */
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

/* ── LAYOUT ── */
#app{display:flex;padding-top:64px;min-height:100vh}

/* ── SIDEBAR ── */
#sidebar{width:240px;flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);
  padding:16px 0;overflow-y:auto;position:sticky;top:64px;height:calc(100vh - 64px)}
.sb-title{font-size:10px;font-weight:700;color:var(--text3);letter-spacing:1.5px;
  text-transform:uppercase;padding:12px 16px 6px}
.sb-item{display:flex;align-items:center;justify-content:space-between;padding:7px 16px;
  cursor:pointer;border-radius:0;transition:var(--transition);font-size:13px;color:var(--text2);
  border:none;background:transparent;width:100%;text-align:left;font-family:'Inter',sans-serif;
  border-left:3px solid transparent}
.sb-item:hover{background:rgba(255,255,255,.05);color:var(--text)}
.sb-item.active{background:rgba(229,9,20,.12) !important;color:var(--red) !important;
  border-left:3px solid var(--red) !important;font-weight:600}
.sb-count{font-size:11px;color:var(--text3);background:var(--surface3);padding:1px 6px;border-radius:10px}
.sb-sep{height:1px;background:var(--border);margin:8px 16px}

/* ── MAIN ── */
#main{flex:1;padding:24px;overflow-x:hidden;min-width:0}
.section-title{font-size:20px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:10px}
.section-count{font-size:13px;font-weight:400;color:var(--text3)}

/* ── GRID ── */
.cards-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}

/* ── CARD ── */
.card{background:var(--surface);border-radius:var(--card-radius);overflow:hidden;cursor:pointer;
  transition:transform .2s ease,box-shadow .2s ease;position:relative}
.card:hover{transform:scale(1.03);box-shadow:0 8px 32px rgba(0,0,0,.6);z-index:2}
.card-img{width:100%;aspect-ratio:3/2;object-fit:cover;display:block;background:var(--surface2)}
.card-img-ph{width:100%;aspect-ratio:3/2;background:linear-gradient(135deg,#1e1e1e 0,#2a2a2a 100%);
  display:flex;align-items:center;justify-content:center;font-size:40px;color:#333}

.card-info{padding:8px 10px 10px;background:#111}
.card-name{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  color:var(--text);margin-bottom:6px}

.card-actions{display:flex;align-items:center;gap:4px;margin-bottom:7px}
.ca-btn{background:none;border:none;cursor:pointer;font-size:16px;line-height:1;padding:2px 5px;
  border-radius:4px;transition:transform .12s,background .12s,filter .12s;user-select:none;
  filter:grayscale(1) opacity(.35)}
.ca-btn:hover{background:rgba(255,255,255,.1);transform:scale(1.2);filter:none}
.ca-btn.on{filter:grayscale(0) opacity(1) !important}
.ca-btn.fav{color:#FFD700}
.ca-btn.done{color:#27ae60}
.ca-btn.good{color:#2980b9}
.ca-btn.bad{color:#e74c3c}
.ca-btn.folder-btn{color:#f39c12;filter:grayscale(0) opacity(.6)}
.ca-btn.folder-btn:hover{filter:grayscale(0) opacity(1)}

.card-cats{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:3px;min-height:18px}
.card-tags-row{display:flex;flex-wrap:wrap;gap:3px;min-height:16px}
.cc-badge{background:#1a3050;color:#7ab8e8;border-radius:3px;font-size:9px;padding:1px 5px;
  white-space:nowrap;overflow:hidden;max-width:76px;text-overflow:ellipsis}
.ct-badge{background:#27184a;color:#b89ef0;border-radius:3px;font-size:9px;padding:1px 5px;
  white-space:nowrap;overflow:hidden;max-width:76px;text-overflow:ellipsis}

.flag{font-size:11px;background:rgba(0,0,0,.7);padding:2px 6px;border-radius:4px;backdrop-filter:blur(4px)}
/* PATCH 7 — badge contador imagens */
.img-count-badge{position:absolute;top:8px;left:8px}

/* ── EMPTY ── */
.empty-state{text-align:center;padding:80px 24px;color:var(--text3)}
.empty-state .es-icon{font-size:64px;margin-bottom:16px;opacity:.3}
.empty-state h2{font-size:20px;font-weight:600;color:var(--text2);margin-bottom:8px}
.empty-state p{font-size:14px;line-height:1.6}
.es-btn{display:inline-block;margin-top:20px;background:var(--red);color:#fff;border:none;
  padding:10px 24px;border-radius:6px;cursor:pointer;font-size:14px;font-family:'Inter',sans-serif;
  font-weight:600;transition:background .15s}
.es-btn:hover{background:var(--red2)}
.es-btn:disabled{background:#444;cursor:default}

/* MODAL FULL-SCREEN */
#modal-bg{display:none;position:fixed;inset:0;z-index:500;background:#000;overflow:hidden}
#modal-bg.open{display:block;animation:mFadeIn .25s ease}
@keyframes mFadeIn{from{opacity:0}to{opacity:1}}

#modal-backdrop{position:absolute;inset:0;background-size:cover;background-position:center top;background-repeat:no-repeat;transition:background-image .4s ease}
#modal-backdrop::after{
  content:'';position:absolute;inset:0;
  background:
    linear-gradient(to right, rgba(0,0,0,.88) 0%, rgba(0,0,0,.6) 45%, rgba(0,0,0,.18) 75%, transparent 100%),
    linear-gradient(to top,   rgba(0,0,0,.96) 0%, rgba(0,0,0,.5) 40%, transparent 70%);
}
#modal-close-fs{position:absolute;top:20px;right:24px;z-index:20;
  background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.2);
  color:#fff;width:42px;height:42px;border-radius:50%;
  cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center;
  transition:background .2s,transform .2s;backdrop-filter:blur(6px)}
#modal-close-fs:hover{background:rgba(229,9,20,.7);transform:scale(1.08)}

#modal-content-fs{position:absolute;inset:0;right:auto;width:58%;max-width:760px;
  padding:72px 56px 36px 56px;z-index:10;display:flex;flex-direction:column;justify-content:flex-end;overflow:hidden}

.fs-meta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;animation:mSlideUp .35s ease .05s both}
.fs-cat-chip{background:rgba(229,9,20,.25);color:#ff6b6b;border:1px solid rgba(229,9,20,.4);
  padding:3px 12px;border-radius:20px;font-size:11px;font-weight:600;backdrop-filter:blur(4px)}
.fs-tag-chip{background:rgba(255,255,255,.12);color:rgba(255,255,255,.8);border:1px solid rgba(255,255,255,.2);
  padding:3px 10px;border-radius:20px;font-size:11px;backdrop-filter:blur(4px)}

.fs-title{font-size:clamp(26px,3.5vw,48px);font-weight:900;line-height:1.05;letter-spacing:-.5px;color:#fff;
  text-shadow:0 2px 16px rgba(0,0,0,.8);margin-bottom:6px;animation:mSlideUp .35s ease .1s both}
.fs-origin{font-size:13px;color:rgba(255,255,255,.5);margin-bottom:14px;letter-spacing:.5px;animation:mSlideUp .35s ease .12s both}

.fs-actions{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;animation:mSlideUp .35s ease .15s both}
.fs-btn{display:flex;align-items:center;gap:6px;padding:9px 18px;border-radius:6px;font-size:13px;font-weight:600;
  font-family:'Inter',sans-serif;cursor:pointer;transition:transform .15s,background .15s;border:none}
.fs-btn:hover{transform:scale(1.04)}
.fs-btn.primary{background:var(--red);color:#fff}
.fs-btn.primary:hover{background:var(--red2)}
.fs-btn.secondary{background:rgba(255,255,255,.18);color:#fff;border:1px solid rgba(255,255,255,.3);backdrop-filter:blur(6px)}
.fs-btn.secondary:hover{background:rgba(255,255,255,.28)}
.fs-btn.active-green{background:rgba(39,174,96,.3);color:#2ecc71;border:1px solid rgba(39,174,96,.5)}
.fs-btn.active-red{background:rgba(229,9,20,.25);color:#ff6b6b;border:1px solid rgba(229,9,20,.5)}
.fs-btn.active-blue{background:rgba(52,152,219,.25);color:#5dade2;border:1px solid rgba(52,152,219,.5)}

.fs-desc-wrap{flex:1;max-height:200px;overflow-y:auto;margin-bottom:14px;animation:mSlideUp .35s ease .18s both}
.fs-desc-wrap::-webkit-scrollbar{width:3px}
.fs-desc-wrap::-webkit-scrollbar-thumb{background:rgba(255,255,255,.2);border-radius:2px}
.fs-desc{font-size:15px;line-height:1.8;color:rgba(255,255,255,.85);white-space:pre-wrap;text-shadow:0 1px 6px rgba(0,0,0,.6)}
.fs-desc-empty{font-size:14px;color:rgba(255,255,255,.35);font-style:italic}
.fs-gen-btn{flex-shrink:0;background:var(--red);border:none;color:#fff;padding:9px 18px;border-radius:6px;cursor:pointer;
  font-size:13px;font-family:'Inter',sans-serif;font-weight:600;transition:background .15s;display:inline-flex;align-items:center;gap:6px;
  animation:mSlideUp .35s ease .2s both;align-self:flex-start}
.fs-gen-btn:hover{background:var(--red2)}
.fs-gen-btn:disabled{background:#444;cursor:default}

@keyframes mSlideUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}

#modal-thumbs{position:absolute;right:24px;top:50%;transform:translateY(-50%);z-index:10;display:flex;flex-direction:column;gap:8px;
  max-height:70vh;overflow-y:auto;padding:4px}
#modal-thumbs::-webkit-scrollbar{width:3px}
#modal-thumbs::-webkit-scrollbar-thumb{background:rgba(255,255,255,.2)}
.thumb-item{width:72px;height:54px;object-fit:cover;border-radius:4px;cursor:pointer;border:2px solid transparent;
  transition:border-color .15s,transform .15s,opacity .15s;opacity:.55;flex-shrink:0}
.thumb-item:hover{opacity:.85;transform:scale(1.05)}
.thumb-item.active{border-color:#fff;opacity:1}
.thumb-ph{width:72px;height:54px;border-radius:4px;background:var(--surface3);display:flex;align-items:center;justify-content:center;
  font-size:22px;border:2px solid transparent;flex-shrink:0;opacity:.4}

.fs-nav-btn{position:absolute;top:50%;transform:translateY(-50%);z-index:15;background:rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.2);
  color:#fff;width:44px;height:44px;border-radius:50%;cursor:pointer;font-size:22px;display:flex;align-items:center;justify-content:center;
  transition:background .2s,transform .2s;backdrop-filter:blur(4px)}
.fs-nav-btn:hover{background:rgba(0,0,0,.75);transform:translateY(-50%) scale(1.08)}
#fs-prev{left:16px}
#fs-next{right:110px}

/* ── TOAST ── */
#toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
  background:var(--surface2);border:1px solid var(--border);color:var(--text);
  padding:10px 20px;border-radius:8px;font-size:13px;z-index:999;white-space:nowrap;
  box-shadow:0 4px 16px rgba(0,0,0,.5);animation:toastIn .2s ease;display:none}
#toast.show{display:block}
@keyframes toastIn{from{opacity:0;transform:translateX(-50%) translateY(10px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
</style>
</head>
<body>

<header id="topbar">
  <div id="logo" onclick="setFilter('all',null)">LASERFLIX</div>
  <nav class="topnav">
    <button class="topnav-btn active" onclick="setFilter('all',this)">Início</button>
    <button class="topnav-btn" onclick="setFilter('favorite',this)">⭐ Favoritos</button>
    <button class="topnav-btn" onclick="setFilter('done',this)">✓ Feitos</button>
    <button class="topnav-btn" onclick="setFilter('good',this)">👍 Bons</button>
    <button class="topnav-btn" onclick="setFilter('bad',this)">👎 Ruins</button>
  </nav>
  <div class="search-wrap">
    <span class="search-icon">🔍</span>
    <input type="text" id="search-input" placeholder="Buscar produtos..." oninput="onSearch(this.value)">
  </div>
  <button class="menu-btn" onclick="toggleMenu()" title="Menu">⋮</button>
</header>

<div class="menu-dropdown" id="menu-dd">
  <div class="menu-section-title">Catalogar</div>
  <button class="menu-item" onclick="addFolder();closeMenu()">
    <span class="mi-icon">📂</span>
    <span class="mi-text">
      <span class="mi-label">Adicionar Pasta</span>
      <span class="mi-desc">Adiciona nova pasta ao catálogo</span>
    </span>
  </button>
  <button class="menu-item" onclick="doScan();closeMenu()">
    <span class="mi-icon">🌀</span>
    <span class="mi-text">
      <span class="mi-label">Escanear Pastas</span>
      <span class="mi-desc">Encontra novos produtos nas pastas</span>
    </span>
  </button>

  <div class="menu-sep"></div>
  <div class="menu-section-title">Inteligência Artificial</div>

  <button class="menu-item" onclick="doAnalyze('new',false);closeMenu()">
    <span class="mi-icon">🏷️</span>
    <span class="mi-text">
      <span class="mi-label">Adicionar Categorias e Tags</span>
      <span class="mi-desc">Classifica apenas os produtos novos (sem categoria)</span>
    </span>
  </button>
  <button class="menu-item" onclick="doDescribe('new');closeMenu()">
    <span class="mi-icon">✍️</span>
    <span class="mi-text">
      <span class="mi-label">Adicionar Descrições</span>
      <span class="mi-desc">Gera descrição para produtos sem texto</span>
    </span>
  </button>
  <button class="menu-item" onclick="doAnalyzeFull();closeMenu()">
    <span class="mi-icon">🤖</span>
    <span class="mi-text">
      <span class="mi-label">Analisar Novos Completo</span>
      <span class="mi-desc">Tags + categorias + descrição para todos os novos de uma vez</span>
    </span>
  </button>
  <button class="menu-item" onclick="doReanalyzeAll();closeMenu()">
    <span class="mi-icon">🌀</span>
    <span class="mi-text">
      <span class="mi-label">Reanalisar Tudo</span>
      <span class="mi-desc">Reprocessa todos com nova classificação e descrição diferente</span>
    </span>
  </button>

  <div class="menu-sep"></div>

  <button class="menu-item" onclick="doBackup();closeMenu()">
    <span class="mi-icon">💾</span>
    <span class="mi-text">
      <span class="mi-label">Backup Manual</span>
      <span class="mi-desc">Salva cópia do banco de dados agora</span>
    </span>
  </button>
</div>

<div id="progress-bar">
  <span class="pb-label" id="pb-label">Analisando...</span>
  <div class="pb-track"><div class="pb-fill" id="pb-fill"></div></div>
  <span class="pb-pct" id="pb-pct">0%</span>
  <button class="pb-stop" onclick="doStop()">■ Parar</button>
</div>

<div id="app">
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

  <main id="main">
    <div class="section-title">
      <span id="section-label">Todos os Produtos</span>
      <span class="section-count" id="section-count"></span>
    </div>
    <div class="cards-grid" id="cards-grid">
      <div class="empty-state" style="grid-column:1/-1">
        <div class="es-icon">📦</div>
        <h2>Carregando catálogo...</h2>
        <p>Aguarde um momento.</p>
      </div>
    </div>
  </main>
</div>

<div id="modal-bg">
  <div id="modal-backdrop"></div>
  <button id="modal-close-fs" onclick="closeModal()">✕</button>
  <button class="fs-nav-btn" id="fs-prev" onclick="galleryNav(-1)" style="display:none">‹</button>
  <button class="fs-nav-btn" id="fs-next" onclick="galleryNav(1)"  style="display:none">›</button>
  <div id="modal-thumbs"></div>
  <div id="modal-content-fs">
    <div class="fs-meta"    id="fs-meta"></div>
    <div class="fs-title"   id="fs-title"></div>
    <div class="fs-origin"  id="fs-origin"></div>
    <div class="fs-actions" id="fs-actions"></div>
    <div class="fs-desc-wrap" id="fs-desc-wrap"></div>
    <button class="fs-gen-btn" id="fs-gen-btn" onclick="generateDesc()">✍️ Gerar Descrição</button>
  </div>
</div>

<div id="toast"></div>

<script>
// ─── STATE ───
let state = {
  filter:'all', origin:'all', categories:[], tag:null, search:'',
  products:[], currentProduct:null, galleryIdx:0, galleryImgs:[],
  total:0, pageOffset:0, pageLimit:120, loading:false
};
let progressInterval = null;
let _activeSbOrigin = null, _activeSbCat = null, _activeSbTag = null;

// PATCH 6 — edicao modal
let modalEdit = { on:false };

// ─── BOOT ───
document.addEventListener('DOMContentLoaded', () => { loadSidebar(); loadProducts(true); });
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
function setFilter(f, btn){
  state.filter = f; state.origin = 'all'; state.categories = []; state.tag = null;
  document.querySelectorAll('.topnav-btn').forEach(b => b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  _clearSidebarActive();
  loadProducts(true);
}
function setOrigin(o, btn){
  if(state.origin === o){ state.origin='all'; if(btn) btn.classList.remove('active'); _activeSbOrigin=null; }
  else { state.origin=o; if(_activeSbOrigin) _activeSbOrigin.classList.remove('active'); if(btn){btn.classList.add('active');_activeSbOrigin=btn;} }
  state.filter='all'; state.categories=[]; state.tag=null;
  document.querySelectorAll('.topnav-btn').forEach(b=>b.classList.remove('active'));
  document.querySelector('.topnav-btn').classList.add('active');
  if(_activeSbCat){_activeSbCat.classList.remove('active');_activeSbCat=null;}
  if(_activeSbTag){_activeSbTag.classList.remove('active');_activeSbTag=null;}
  loadProducts(true);
}
function toggleCat(c, btn){
  const idx = state.categories.indexOf(c);
  if(idx>=0){ state.categories.splice(idx,1); if(btn) btn.classList.remove('active'); _activeSbCat=null; }
  else { state.categories.push(c); if(_activeSbCat) _activeSbCat.classList.remove('active'); if(btn){btn.classList.add('active');_activeSbCat=btn;} }
  state.filter='all'; state.origin='all'; state.tag=null;
  document.querySelectorAll('.topnav-btn').forEach(b=>b.classList.remove('active'));
  document.querySelector('.topnav-btn').classList.add('active');
  if(_activeSbOrigin){_activeSbOrigin.classList.remove('active');_activeSbOrigin=null;}
  if(_activeSbTag){_activeSbTag.classList.remove('active');_activeSbTag=null;}
  loadProducts(true);
}
function setTag(t, btn){
  if(state.tag===t){ state.tag=null; if(btn) btn.classList.remove('active'); _activeSbTag=null; }
  else { state.tag=t; if(_activeSbTag) _activeSbTag.classList.remove('active'); if(btn){btn.classList.add('active');_activeSbTag=btn;} }
  state.filter='all'; state.origin='all'; state.categories=[];
  document.querySelectorAll('.topnav-btn').forEach(b=>b.classList.remove('active'));
  document.querySelector('.topnav-btn').classList.add('active');
  if(_activeSbOrigin){_activeSbOrigin.classList.remove('active');_activeSbOrigin=null;}
  if(_activeSbCat){_activeSbCat.classList.remove('active');_activeSbCat=null;}
  loadProducts(true);
}
function _clearSidebarActive(){
  if(_activeSbOrigin){_activeSbOrigin.classList.remove('active');_activeSbOrigin=null;}
  if(_activeSbCat){_activeSbCat.classList.remove('active');_activeSbCat=null;}
  if(_activeSbTag){_activeSbTag.classList.remove('active');_activeSbTag=null;}
}
let searchTimer;
function onSearch(v){ clearTimeout(searchTimer); searchTimer=setTimeout(()=>{state.search=v;loadProducts(true);},300); }

// ─── SIDEBAR ───
async function loadSidebar(){
  const data = await api('/api/sidebar');
  if(!data) return;
  document.getElementById('sb-origins').innerHTML =
    `<button class="sb-item active" onclick="setOrigin('all',this)"><span>Todos</span><span class="sb-count">${data.total}</span></button>` +
    data.origins.map(o=>`<button class="sb-item" onclick="setOrigin(${escAttr(o.name)},this)"><span>${escHtml(o.name)}</span><span class="sb-count">${o.count}</span></button>`).join('');
  document.getElementById('sb-cats').innerHTML =
    data.categories.map(c=>`<button class="sb-item" onclick="toggleCat(${escAttr(c.name)},this)"><span>${escHtml(c.name)}</span><span class="sb-count">${c.count}</span></button>`).join('');
  document.getElementById('sb-tags').innerHTML =
    data.tags.map(t=>`<button class="sb-item" onclick="setTag(${escAttr(t.name)},this)"><span>${escHtml(t.name)}</span><span class="sb-count">${t.count}</span></button>`).join('');
}

// ─── PRODUTOS (PATCH 5 — paginacao) ───
async function loadProducts(reset=true){
  if(state.loading) return;
  state.loading = true;

  if(reset){
    state.pageOffset = 0;
    state.total = 0;
    state.products = [];
    renderCards([], 0);
  }

  const params = new URLSearchParams({
    filter:state.filter, origin:state.origin,
    categories:state.categories.join(','), tag:state.tag||'', search:state.search,
    offset:String(state.pageOffset), limit:String(state.pageLimit)
  });

  const data = await api('/api/products?'+params);
  if(!data){ state.loading=false; return; }

  state.total = data.total || 0;
  const newItems = data.items || [];

  state.products = state.products.concat(newItems);
  state.pageOffset += newItems.length;

  renderCards(state.products, state.total);

  state.loading = false;
}

function renderCards(items, total){
  const grid = document.getElementById('cards-grid');
  document.getElementById('section-count').textContent = items.length+' / '+(total||items.length)+' produto(s)';
  let label='Todos os Produtos';
  if(state.filter==='favorite') label='⭐ Favoritos';
  else if(state.filter==='done') label='✓ Feitos';
  else if(state.filter==='good') label='👍 Bons';
  else if(state.filter==='bad')  label='👎 Ruins';
  else if(state.origin!=='all')  label='Origem: '+escHtml(state.origin);
  else if(state.categories.length) label='Categoria: '+escHtml(state.categories[0]);
  else if(state.tag) label='Tag: '+escHtml(state.tag);
  document.getElementById('section-label').innerHTML = label;

  if(!items.length){
    grid.innerHTML=`<div class="empty-state" style="grid-column:1/-1">
      <div class="es-icon">📦</div>
      <h2>${total===0 ? 'Nenhum produto encontrado' : 'Carregando...'}</h2>
      <p>Tente outros filtros ou adicione uma pasta.</p>
      <button class="es-btn" onclick="addFolder()">📂 Adicionar Pasta</button>
    </div>`;
    return;
  }

  grid.innerHTML='';
  items.forEach(p => {
    const div = document.createElement('div');
    div.className='card';
    div.setAttribute('data-id', p.id);
    div.onclick = e => { if(!e.target.closest('.ca-btn')) openModal(p.id); };

    const imgHtml = p.has_cover
      ? `<img class="card-img" src="/api/cover?path=${encodeURIComponent(p.id)}&idx=0" alt="${escHtml(p.name)}" loading="lazy"
            onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
         <div class="card-img-ph" style="display:none">📦</div>`
      : `<div class="card-img-ph">📦</div>`;

    const cats = (p.categories||[]).slice(0,3).map(c=>`<span class="cc-badge">${escHtml(c)}</span>`).join('');
    const tags = (p.tags||[]).slice(0,3).map(t=>`<span class="ct-badge">#${escHtml(t)}</span>`).join('');
    const pid  = escAttr2(p.id);

    // PATCH 7 — badge contador imagens
    const imgCount = (p.cover_count||0);
    const imgBadge = imgCount>0 ? `<div class="flag img-count-badge">🖼 ${imgCount}</div>` : '';

    div.innerHTML=`
      ${imgHtml}
      ${imgBadge}
      <div class="card-info">
        <div class="card-name">${escHtml(p.name)}</div>
        <div class="card-actions">
          <button class="ca-btn fav${p.favorite?' on':''}" title="Favorito"  onclick="toggleFlag(event,'${pid}','favorite',this)">⭐</button>
          <button class="ca-btn done${p.done?' on':''}"    title="Feito"     onclick="toggleFlag(event,'${pid}','done',this)">✓</button>
          <button class="ca-btn good${p.good?' on':''}"    title="Bom"       onclick="toggleFlag(event,'${pid}','good',this)">👍</button>
          <button class="ca-btn bad${p.bad?' on':''}"      title="Ruim"      onclick="toggleFlag(event,'${pid}','bad',this)">👎</button>
          <span style="flex:1"></span>
          <button class="ca-btn folder-btn" title="Abrir pasta" onclick="openFolder(event,'${pid}')">📁</button>
        </div>
        <div class="card-cats">${cats}</div>
        <div class="card-tags-row">${tags}</div>
      </div>`;
    grid.appendChild(div);
  });

  // PATCH 5 — botao "Carregar mais"
  if(items.length < (total||items.length)){
    const more = document.createElement('div');
    more.style.gridColumn = '1/-1';
    more.style.display = 'flex';
    more.style.justifyContent = 'center';
    more.style.padding = '8px 0 18px';
    const remaining = (total - items.length);
    more.innerHTML = `<button class="es-btn" onclick="loadProducts(false)" ${state.loading?'disabled':''}>
      Carregar mais (${items.length}/${total}) — faltam ${remaining}
    </button>`;
    grid.appendChild(more);
  }
}

// PATCH 1 — toggle cirurgico
async function toggleFlag(e, pid, key, btn){
  e.stopPropagation();
  const r = await api('/api/toggle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:pid,key})});
  if(!r) return;

  const p = state.products.find(x=>x.id===pid);
  if(p){ p.favorite=r.favorite; p.done=r.done; p.good=r.good; p.bad=r.bad; }

  const card = btn.closest('.card');
  if(card){
    const btns = {
      favorite: card.querySelector('.ca-btn.fav'),
      done:     card.querySelector('.ca-btn.done'),
      good:     card.querySelector('.ca-btn.good'),
      bad:      card.querySelector('.ca-btn.bad'),
    };
    if(btns.favorite) btns.favorite.classList.toggle('on', r.favorite);
    if(btns.done)     btns.done.classList.toggle('on', r.done);
    if(btns.good)     btns.good.classList.toggle('on', r.good);
    if(btns.bad)      btns.bad.classList.toggle('on', r.bad);
  }
  const msgs={favorite:'⭐ Favorito',done:'✓ Feito',good:'👍 Bom',bad:'👎 Ruim'};
  showToast(msgs[key]+' '+(r[key]?'ativado':'removido'));
}

async function openFolder(e,pid){
  e.stopPropagation();
  await api('/api/open_folder',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:pid})});
  showToast('📁 Abrindo pasta...');
}

// ─── MODAL ───
async function openModal(pid){
  const p = await api('/api/product/'+encodeURIComponent(pid).replace(/%2F/g,'/').replace(/%3A/g,':'));
  if(!p) return;
  state.currentProduct = p;
  state.galleryImgs    = p.images || [];
  state.galleryIdx     = 0;
  modalEdit.on         = false;
  _renderModalFS(p);
  document.getElementById('modal-bg').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function _renderModalFS(p){
  _setBackdrop(p, 0);
  const editOn = !!modalEdit.on;

  if(!editOn){
    document.getElementById('fs-title').textContent = p.name;
    const chips  = (p.categories||[]).slice(0,3).map(c=>`<span class="fs-cat-chip">${escHtml(c)}</span>`).join('');
    const tchips = (p.tags||[]).slice(0,4).map(t=>`<span class="fs-tag-chip">#${escHtml(t)}</span>`).join('');
    document.getElementById('fs-meta').innerHTML = chips + tchips;
  } else {
    document.getElementById('fs-title').innerHTML =
      `<input id="edit-name"
        style="width:100%;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.22);
               background:rgba(0,0,0,.35);color:#fff;font-size:18px;font-weight:900;outline:none"
        value="${escHtml(p.name)}">`;

    document.getElementById('fs-meta').innerHTML = `
      <div style="display:flex;flex-direction:column;gap:8px;width:100%">
        <input id="edit-cats" placeholder="Categorias (separadas por vírgula)"
          style="width:100%;padding:9px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.18);
                 background:rgba(0,0,0,.25);color:#fff;outline:none"
          value="${escHtml((p.categories||[]).join(', '))}">
        <input id="edit-tags" placeholder="Tags (separadas por vírgula)"
          style="width:100%;padding:9px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.18);
                 background:rgba(0,0,0,.25);color:#fff;outline:none"
          value="${escHtml((p.tags||[]).join(', '))}">
      </div>`;
  }

  document.getElementById('fs-origin').innerHTML  = p.origin ? '🌐 '+escHtml(p.origin) : '';

  const dw = document.getElementById('fs-desc-wrap');
  dw.innerHTML = p.ai_description
    ? `<div class="fs-desc">${escHtml(p.ai_description)}</div>`
    : `<div class="fs-desc-empty">Sem descrição. Clique em "Gerar" para criar.</div>`;

  const gb = document.getElementById('fs-gen-btn');
  gb.disabled = false;
  gb.innerHTML = '✍️ '+(p.ai_description?'Regenerar Descrição':'Gerar Descrição');

  _renderFSActions(p);
  _renderGallery(p);
}

function _renderFSActions(p){
  const editOn = !!modalEdit.on;
  document.getElementById('fs-actions').innerHTML = `
    <button class="fs-btn ${p.favorite?'active-red':'secondary'}" onclick="modalToggle('favorite')">⭐ ${p.favorite?'Favoritado':'Favoritar'}</button>
    <button class="fs-btn ${p.done?'active-green':'secondary'}" onclick="modalToggle('done')">✓ ${p.done?'Feito':'Marcar Feito'}</button>
    <button class="fs-btn ${p.good?'active-blue':'secondary'}" onclick="modalToggle('good')">👍 ${p.good?'Bom':'Marcar Bom'}</button>
    <button class="fs-btn ${p.bad?'active-red':'secondary'}" onclick="modalToggle('bad')">👎 ${p.bad?'Ruim':'Marcar Ruim'}</button>
    <button class="fs-btn secondary" onclick="modalOpenFolder()">📁 Abrir Pasta</button>
    <button class="fs-btn secondary" onclick="toggleEditModal()">${editOn?'Cancelar':'Editar'}</button>
    ${editOn ? `<button class="fs-btn primary" onclick="saveEditModal()">Salvar</button>` : ``}
  `;
}

function toggleEditModal(){
  modalEdit.on = !modalEdit.on;
  if(state.currentProduct) _renderModalFS(state.currentProduct);
}

async function saveEditModal(){
  const p = state.currentProduct; if(!p) return;

  const name = (document.getElementById('edit-name')?.value || p.name).trim();
  const cats = (document.getElementById('edit-cats')?.value || '')
                .split(',').map(s=>s.trim()).filter(Boolean);
  const tags = (document.getElementById('edit-tags')?.value || '')
                .split(',').map(s=>s.trim()).filter(Boolean);

  const r = await api('/api/update_product',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({path:p.id,name, categories:cats, tags})
  });
  if(!r || r.error){ showToast('Erro ao salvar'); return; }

  p.name = name; p.categories = cats; p.tags = tags;
  modalEdit.on = false;
  _renderModalFS(p);

  // Atualiza card visivel (nome + badges simples)
  const card = document.querySelector(`.card[data-id="${CSS.escape(p.id)}"]`);
  if(card){
    const nm = card.querySelector('.card-name');
    if(nm) nm.textContent = name;
    // (para atualizar os badges, deixamos a lista recarregar leve)
  }
  showToast('Salvo!');
  loadSidebar();
  // Mantem pagina atual, mas recarrega do zero para refletir chips no card
  loadProducts(true);
}

function _setBackdrop(p, idx){
  const bd = document.getElementById('modal-backdrop');
  if(p.images && p.images.length > 0){
    bd.style.backgroundImage = 'url(/api/cover?path='+encodeURIComponent(p.id)+'&idx='+idx+')';
  } else {
    bd.style.backgroundImage = 'none';
    bd.style.background = 'linear-gradient(135deg,#111,#1a1a1a)';
  }
}

function _renderGallery(p){
  const imgs     = state.galleryImgs;
  const prevBtn  = document.getElementById('fs-prev');
  const nextBtn  = document.getElementById('fs-next');
  const thumbsEl = document.getElementById('modal-thumbs');
  if(!imgs || imgs.length === 0){ prevBtn.style.display='none'; nextBtn.style.display='none'; thumbsEl.innerHTML=''; return; }
  prevBtn.style.display = state.galleryIdx > 0             ? 'flex' : 'none';
  nextBtn.style.display = state.galleryIdx < imgs.length-1 ? 'flex' : 'none';
  thumbsEl.innerHTML = imgs.length > 1
    ? imgs.map((_,i)=>`<img class="thumb-item${i===state.galleryIdx?' active':''}" src="/api/cover?path=${encodeURIComponent(p.id)}&idx=${i}" onclick="setGallery(${i})" onerror="this.outerHTML='<div class=\\'thumb-ph\\'>📦</div>'">`).join('')
    : '';
}

function setGallery(i){ state.galleryIdx=i; _setBackdrop(state.currentProduct,i); _renderGallery(state.currentProduct); }
function galleryNav(dir){
  const n=state.galleryImgs.length; if(!n) return;
  state.galleryIdx=Math.max(0,Math.min(n-1,state.galleryIdx+dir));
  _setBackdrop(state.currentProduct,state.galleryIdx); _renderGallery(state.currentProduct);
}

async function modalToggle(key){
  const p=state.currentProduct; if(!p) return;
  const r=await api('/api/toggle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:p.id,key})});
  if(!r) return;
  p.favorite=r.favorite; p.done=r.done; p.good=r.good; p.bad=r.bad;
  _renderFSActions(p);

  const card = document.querySelector(`.card[data-id="${CSS.escape(p.id)}"]`);
  if(card){
    const btns = { favorite:card.querySelector('.ca-btn.fav'), done:card.querySelector('.ca-btn.done'), good:card.querySelector('.ca-btn.good'), bad:card.querySelector('.ca-btn.bad') };
    if(btns.favorite) btns.favorite.classList.toggle('on',r.favorite);
    if(btns.done)     btns.done.classList.toggle('on',r.done);
    if(btns.good)     btns.good.classList.toggle('on',r.good);
    if(btns.bad)      btns.bad.classList.toggle('on',r.bad);
  }
  showToast('Atualizado!');
}

async function modalOpenFolder(){
  const p=state.currentProduct; if(!p) return;
  await api('/api/open_folder',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:p.id})});
  showToast('📁 Abrindo pasta...');
}

async function generateDesc(){
  const p=state.currentProduct; if(!p) return;
  const btn=document.getElementById('fs-gen-btn');
  btn.disabled=true; btn.innerHTML='⏳ Gerando...';
  const r=await api('/api/describe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'single',path:p.id})});
  if(r){
    showToast('✍️ Gerando em segundo plano...');
    setTimeout(async()=>{
      const updated=await api('/api/product/'+encodeURIComponent(p.id).replace(/%2F/g,'/').replace(/%3A/g,':'));
      if(updated&&updated.ai_description){
        document.getElementById('fs-desc-wrap').innerHTML=`<div class="fs-desc">${escHtml(updated.ai_description)}</div>`;
        state.currentProduct.ai_description=updated.ai_description;
      }
      btn.disabled=false; btn.innerHTML='✍️ Regenerar Descrição';
    },3500);
  } else { btn.disabled=false; btn.innerHTML='✍️ Gerar Descrição'; }
}

function closeModal(){
  document.getElementById('modal-bg').classList.remove('open');
  document.body.style.overflow='';
  state.currentProduct=null;
  modalEdit.on=false;
}

// ─── MENU ───
function toggleMenu(){ document.getElementById('menu-dd').classList.toggle('open'); }
function closeMenu(){  document.getElementById('menu-dd').classList.remove('open'); }

// ─── ACOES MENU ───
async function addFolder(){
  const folder=prompt('Cole o caminho completo da pasta:');
  if(!folder) return;
  const r=await api('/api/add_folder',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({folder})});
  if(!r) return;
  if(r.error){ showToast('❌ '+r.error); return; }
  showToast('✅ '+r.new_count+' produto(s) encontrado(s)!');
  loadSidebar(); loadProducts(true);
}
async function doScan(){
  const r=await api('/api/scan',{method:'POST'});
  if(!r) return;
  showToast('✅ '+r.new_count+' novo(s) produto(s)!');
  loadSidebar(); loadProducts(true);
}
async function doAnalyze(mode, withDesc){
  const r=await api('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode,with_description:!!withDesc,force_description:false})});
  if(!r||r.error){ showToast('❌ '+(r&&r.error?r.error:'Erro')); return; }
  if(r.count===0){ showToast('✅ Nenhum produto novo para analisar'); return; }
  showToast('🏷️ Classificando '+r.count+' produto(s)...');
  startProgress();
}
async function doDescribe(mode){
  const r=await api('/api/describe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode,force_new:false})});
  if(!r||r.error){ showToast('❌ '+(r&&r.error?r.error:'Erro')); return; }
  if(r.count===0){ showToast('✅ Nenhum produto sem descrição'); return; }
  showToast('✍️ Gerando descrições para '+r.count+' produto(s)...');
  startProgress();
}
async function doAnalyzeFull(){
  const r=await api('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'new',with_description:true,force_description:false})});
  if(!r||r.error){ showToast('❌ '+(r&&r.error?r.error:'Erro')); return; }
  if(r.count===0){ showToast('✅ Nenhum produto novo para analisar'); return; }
  showToast('🤖 Análise completa de '+r.count+' produto(s)...');
  startProgress();
}
async function doReanalyzeAll(){
  if(!confirm('Reanalisar TODOS os produtos com nova classificação e descrição? Isso pode demorar bastante.')) return;
  const r=await api('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'all',with_description:true,force_description:true})});
  if(!r||r.error){ showToast('❌ '+(r&&r.error?r.error:'Erro')); return; }
  showToast('🌀 Reanalisando '+r.count+' produto(s)...');
  startProgress();
}
async function doBackup(){
  const r=await api('/api/backup',{method:'POST'});
  if(r) showToast('💾 Backup salvo!');
}
async function doStop(){
  await api('/api/stop',{method:'POST'});
  showToast('■ Análise interrompida.');
}

// ─── PROGRESSO ───
function startProgress(){
  const bar=document.getElementById('progress-bar');
  bar.classList.add('visible');
  if(progressInterval) clearInterval(progressInterval);
  progressInterval=setInterval(async()=>{
    const r=await api('/api/progress');
    if(!r) return;
    const pct=r.total>0?Math.round(r.current/r.total*100):0;
    document.getElementById('pb-fill').style.width=pct+'%';
    document.getElementById('pb-pct').textContent=pct+'%';
    document.getElementById('pb-label').textContent=r.name||'Analisando...';
    if(!r.analyzing){
      clearInterval(progressInterval); progressInterval=null;
      bar.classList.remove('visible');
      showToast('✅ Concluído!');
      loadSidebar(); loadProducts(true);
    }
  },1200);
}

// ─── UTILS ───
async function api(url,opts){ try{ const r=await fetch(url,opts); return await r.json(); }catch(e){ console.error(url,e); return null; } }
function escHtml(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function escAttr(s){ return '"'+String(s||'').replace(/\\\\/g,'\\\\\\\\').replace(/"/g,'\\\\"')+'"'; }
function escAttr2(s){ return String(s||'').replace(/\\\\/g,'\\\\\\\\').replace(/'/g,"\\\\'"); }
function showToast(msg){
  const t=document.getElementById('toast');
  t.innerHTML=msg; t.classList.add('show');
  clearTimeout(t._tid); t._tid=setTimeout(()=>t.classList.remove('show'),2800);
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
    print(f"\n  LASERFLIX v{VERSION}")
    print(f"  http://localhost:{port}")
    print("  Ctrl+C para encerrar\n")
    app.run(port=port, debug=False, use_reloader=False)
