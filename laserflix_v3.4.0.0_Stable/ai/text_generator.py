"""
Gerador de texto com IA - Análises e descrições
Restaurado com lógica refinada da v740 (3 semanas de testes)

HOT-11: FIX CRÍTICO - Prompt exige 10+ categorias (não 3-5)
"""
import os
import re
from config.settings import FAST_MODEL_THRESHOLD
from utils.logging_setup import LOGGER


class TextGenerator:
    """
    Gera análises (categorias/tags) e descrições de projetos usando Ollama.
    Funciona com ou sem Ollama rodando — fallbacks garantem resultado sempre.
    
    LÓGICA REFINADA v741:
      - Raciocínio estruturado em 3 etapas antes de escrever
      - Hierarquia NOME > Visão rigorosamente aplicada
      - Prompts cirúrgicos para evitar genericidade
      - Temperature 0.65 para criatividade controlada
      - HOT-11: Prompt EXIGE 10+ categorias (3 obrigatórias + até 9 opcionais)
    """

    def __init__(self, ollama_client, image_analyzer, project_scanner, fallback_generator):
        self.ollama = ollama_client
        self.image_analyzer = image_analyzer
        self.scanner = project_scanner
        self.fallback = fallback_generator
        self.logger = LOGGER

    def _choose_model_role(self, batch_size=1):
        """
        Escolhe modelo baseado no tamanho do lote.
        - batch_size > 50: text_fast (qwen2.5:3b)
        - batch_size <= 50: text_quality (qwen2.5:7b)
        """
        if batch_size > FAST_MODEL_THRESHOLD:
            return "text_fast"
        return "text_quality"

    def analyze_project(self, project_path, batch_size=1):
        """
        Analisa projeto e retorna (categories, tags).
        Integra visão (moondream) quando imagem de capa está disponível.

        Funciona com ou sem Ollama:
          - COM Ollama: usa IA + visão + fallback_categories se retorno incompleto
          - SEM Ollama: usa fallback_analysis baseado em keywords do nome

        Args:
            project_path: Caminho completo do projeto
            batch_size: Tamanho do lote (para escolha de modelo)

        Returns:
            Tuple (categories: list, tags: list) — NUNCA vazio, sempre tem fallback
        """
        try:
            name = os.path.basename(project_path)
            structure = self.scanner.analyze_project_structure(project_path)

            # Prepara contexto de tipos de arquivo
            file_types_str = ", ".join(
                f"{ext} ({count}x)"
                for ext, count in structure["file_types"].items()
            )

            subfolders_str = (
                ", ".join(structure["subfolders"][:5])
                if structure["subfolders"]
                else "nenhuma"
            )

            # Contexto técnico
            tech_context = []
            if structure["has_svg"]: tech_context.append("SVG vetorial")
            if structure["has_pdf"]: tech_context.append("PDF")
            if structure["has_dxf"]: tech_context.append("DXF/CAD")
            if structure["has_ai"]:  tech_context.append("Adobe Illustrator")
            tech_str = ", ".join(tech_context) if tech_context else "formatos variados"

            # Tenta descrição visual com moondream (filtro de qualidade aplicado no image_analyzer)
            vision_line = ""
            cover_img = self._find_first_image(project_path)
            if cover_img:
                vision_desc = self.image_analyzer.analyze_cover(cover_img)
                if vision_desc:
                    vision_line = f"\n🖼️ DESCRIÇÃO VISUAL DA CAPA: {vision_desc}"

            # Escolhe modelo baseado no batch_size
            role = self._choose_model_role(batch_size)

            # ═══════════════════════════════════════════════════════════════════
            # HOT-11: PROMPT REFINADO - EXIGE 10+ CATEGORIAS!
            # ═══════════════════════════════════════════════════════════════════
            prompt = f"""Analise este produto de corte laser e responda EXATAMENTE no formato solicitado.

📁 NOME: {name}
📊 ARQUIVOS: {structure['total_files']} arquivos | Subpastas: {subfolders_str}
🗂️ TIPOS: {file_types_str}
🔧 FORMATOS: {tech_str}{vision_line}

### TAREFA 1 — CATEGORIAS (MÍNIMO 10, MÁXIMO 12)
⚠️ OBRIGATÓRIO: Atribua NO MÍNIMO 10 categorias, EXATAMENTE nesta ordem:

🎉 CATEGORIAS OBRIGATÓRIAS (primeiras 3):

1. Data Comemorativa (escolha UMA - NUNCA "Diversos"):
   - Páscoa, Natal, Dia das Mães, Dia dos Pais, Dia dos Namorados
   - Aniversário, Casamento, Chá de Bebê, Halloween, Dia das Crianças
   - Ano Novo, Formatura, Dia da Mulher, Dia do Amigo
   Se não identificar: use "Aniversário" (nunca "Diversos")

2. Função/Tipo (escolha UMA - NUNCA "Diversos"):
   - Porta-Retrato, Caixa Organizadora, Luminária, Porta-Joias, Porta-Chaves
   - Suporte, Quadro Decorativo, Painel de Parede, Mandala, Nome Decorativo
   - Letreiro, Lembrancinha, Chaveiro, Topo de Bolo, Centro de Mesa
   - Plaquinha, Brinquedo Educativo, Espelho Decorativo, Cabide
   - Calendário, Relógio, Bandeja, Porta-Copo, Fruteira
   Se não identificar: analise o NOME e infira a função mais provável

3. Ambiente (escolha UM - NUNCA "Diversos"):
   - Quarto, Sala, Cozinha, Banheiro, Escritório
   - Quarto Infantil, Quarto de Bebê, Área Externa, Festa
   - Sala de Jogos, Área Gourmet, Biblioteca, Garagem
   Se não identificar: infira pelo tipo de produto

✨ CATEGORIAS OPCIONAIS (adicione PELO MENOS mais 7 das opções abaixo):

4-6. Temas (escolha 2-3):
   - Unicórnio, Dinossauro, Espaço, Floresta, Safari, Oceano
   - Super-Herói, Princesa, Astronauta, Pirata, Fada
   - Flamingo, Cactos, Arco-Íris, Nuvens, Estrelas, Lua
   - Tribal, Geométrico, Mandálico, Abstrato, Floral

7-9. Estilos (escolha 2-3):
   - Minimalista, Rústico, Moderno, Vintage, Romântico, Elegante
   - Industrial, Boho, Escandinavo, Provençal, Infantil, Lúdico
   - Clássico, Contemporâneo, Artéstico, Delicado

10-12. Público/Contexto (escolha 2-3):
   - Bebê, Criança, Adolescente, Adulto, Casal, Família
   - Presente, Maternidade, Enxoval, Festa Infantil
   - Decoração, Organização, Personalizado, Artesanal

### TAREFA 2 — TAGS
Crie exatamente 10 tags relevantes:
- Primeiras 3: palavras-chave extraídas do nome "{name}" (sem códigos numéricos)
- Demais 7: emoção, ocasião, público, estilo, uso, material, característica

### FORMATO DE RESPOSTA (siga exatamente):
Categorias: [cat1], [cat2], [cat3], [cat4], [cat5], [cat6], [cat7], [cat8], [cat9], [cat10], [cat11 opcional], [cat12 opcional]
Tags: [tag1], [tag2], [tag3], [tag4], [tag5], [tag6], [tag7], [tag8], [tag9], [tag10]

⚠️ IMPORTANTE:
- Retorne NO MÍNIMO 10 categorias (ideal: 12)
- NUNCA use "Diversos" nas 3 primeiras categorias
- Seja ESPECÍFICO nas categorias opcionais
- Priorize categorias que ajudem na busca/filtragem"""

            if self.ollama.stop_flag:
                return self.fallback.fallback_analysis(project_path)

            # Gera resposta com IA
            text = self.ollama.generate_text(
                prompt,
                role=role,
                temperature=0.65,
                num_predict=300,  # HOT-11: Aumentado de 200 para 300 (mais categorias)
            )

            categories, tags = [], []

            if text:
                # Parse de categorias e tags
                for line in text.split("\n"):
                    line = line.strip()

                    if line.startswith("Categorias:") or line.startswith("Categories:"):
                        raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                        categories = [c.strip().strip('"') for c in raw.split(",") if c.strip()]

                    elif line.startswith("Tags:"):
                        raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                        tags = [t.strip().strip('"') for t in raw.split(",") if t.strip()]

                # Garante tags do nome sempre presentes
                name_tags = self.scanner.extract_tags_from_name(name)
                for tag in name_tags:
                    if tag not in tags:
                        tags.insert(0, tag)

                # Deduplica e limita
                tags = list(dict.fromkeys(tags))[:10]

                # HOT-11: Se IA retornou menos de 10 categorias, completa com fallback
                if len(categories) < 10:
                    self.logger.warning(
                        f"⚠️ IA retornou apenas {len(categories)} categorias para {name}, "
                        f"completando com fallback"
                    )
                    categories = self.fallback.fallback_categories(project_path, categories)

                return categories[:12], tags

            # Ollama retornou vazio (indisponível ou timeout) — usa fallback completo
            self.logger.info(f"🔄 Ollama indisponível para {name}, usando fallback completo")
            return self.fallback.fallback_analysis(project_path)

        except Exception:
            self.logger.exception("❌ Erro em analyze_project para %s", project_path)
            return self.fallback.fallback_analysis(project_path)

    def generate_description(self, project_path, project_data):
        """
        Gera descrição comercial personalizada.
        
        ═══════════════════════════════════════════════════════════════════
        LÓGICA REFINADA v740 (3 SEMANAS DE TESTES)
        ═══════════════════════════════════════════════════════════════════
        
        HIERARQUIA INVIOLÁVEL:
          1° NOME da peça — âncora absoluta. Define o que o produto É.
          2° VISÃO (moondream) — detalhe visual SECUNDÁRIO.
             • Só usado se imagem passa no filtro de qualidade
             • NUNCA contradiz nem substitui o nome
             • Apenas COMPLEMENTA com detalhes visuais
        
        RACIOCÍNIO ESTRUTURADO (3 etapas):
          Antes de escrever, a IA deve responder internamente:
            1. O que exatamente é esta peça física? (baseado no NOME)
            2. Para que serve na prática? (uso real)
            3. Que emoção ela representa? (conexão afetiva)
        
        ANTI-GENERICIDADE:
          • Proíbe frases que servem para qualquer produto
          • Exige especificidade sobre ESTA peça
          • Proíbe mencionar arquivos/formatos/etapas de produção
          • Proíbe palavra "projeto" (é uma PEÇA física)
        
        ═══════════════════════════════════════════════════════════════════

        Formato de saída:
            NOME DA PEÇA

            🎨 Por Que Este Produto é Especial:
            [2-3 frases afetivas e únicas baseadas no nome + visual se disponível]

            💖 Perfeito Para:
            [2-3 frases práticas com exemplos reais de uso e ocasião]

        Args:
            project_path: Caminho do projeto
            project_data: Dict com dados do projeto (name, structure, etc)

        Returns:
            String com descrição formatada (nunca None — sempre tem fallback)
        """
        if self.ollama.stop_flag:
            structure = self._get_structure(project_path, project_data)
            return self.fallback.fallback_description(project_path, project_data, structure)

        try:
            # ═══════════════════════════════════════════════════════════════
            # 1° NOME — âncora absoluta
            # ═══════════════════════════════════════════════════════════════
            raw_name = project_data.get("name", os.path.basename(project_path) or "Sem nome")
            clean_name = self._clean_name(raw_name)

            # ═══════════════════════════════════════════════════════════════
            # 2° VISÃO — só se imagem passa no filtro de qualidade
            # ═══════════════════════════════════════════════════════════════
            vision_context = ""
            cover_img = self._find_first_image(project_path)
            if cover_img:
                # analyze_cover já aplica filtro de qualidade internamente
                vision_desc = self.image_analyzer.analyze_cover(cover_img)
                if vision_desc:
                    vision_context = (
                        "\n\nDETALHE VISUAL (use apenas para complementar, "
                        "nunca contradizer o nome): " + vision_desc
                    )
                else:
                    # Imagem não passou no filtro - log já feito no image_analyzer
                    pass

            if self.ollama.stop_flag:
                structure = self._get_structure(project_path, project_data)
                return self.fallback.fallback_description(project_path, project_data, structure)

            # ═══════════════════════════════════════════════════════════════
            # PROMPT COM RACIOCÍNIO ESTRUTURADO (v740 refinado)
            # ═══════════════════════════════════════════════════════════════
            prompt = (
                "Você é especialista em peças físicas de corte a laser — placas, espelhos, "
                "porta-retratos, tabuletas, cabides, calendários, nomes decorativos e similares.\n\n"
                "NOME DA PEÇA (use isso como verdade absoluta sobre o que é o produto): "
                + clean_name + vision_context + "\n\n"
                
                # ────────────────────────────────────────────────────────────────
                # REGRA FUNDAMENTAL (v740)
                # ────────────────────────────────────────────────────────────────
                "### REGRA FUNDAMENTAL:\n"
                "O NOME define o que é o produto. O detalhe visual apenas complementa.\n"
                "Nunca invente função ou formato que contradiga o nome.\n\n"
                
                # ────────────────────────────────────────────────────────────────
                # RACIOCÍNIO ESTRUTURADO EM 3 ETAPAS (v740)
                # ────────────────────────────────────────────────────────────────
                "### RACIOCINE antes de escrever:\n"
                "1. O que exatamente é esta peça física, baseado no nome? (tipo de objeto)\n"
                "2. Para que serve na prática? (uso real no dia a dia)\n"
                "3. Que emoção ou momento ela representa? (conexão afetiva)\n\n"
                
                # ────────────────────────────────────────────────────────────────
                # FORMATO DE SAÍDA
                # ────────────────────────────────────────────────────────────────
                "### ESCREVA a descrição EXATAMENTE neste formato (sem nada além disso):\n\n"
                + clean_name + "\n\n"
                "🎨 Por Que Este Produto é Especial:\n"
                "[2 a 3 frases afetivas e únicas. Fale sobre o que torna ESTA peça especial. "
                "Nunca use frases genéricas que servem para qualquer produto.]\n\n"
                "💖 Perfeito Para:\n"
                "[2 a 3 frases práticas com exemplos reais de uso e ocasião para ESTA peça específica.]\n\n"
                
                # ────────────────────────────────────────────────────────────────
                # REGRAS ANTI-GENERICIDADE (v740 reforçado)
                # ────────────────────────────────────────────────────────────────
                "### REGRAS OBRIGATÓRIAS:\n"
                "- Escreva em português brasileiro\n"
                "- Nunca use a palavra projeto — esta é uma PEÇA ou PRODUTO físico\n"
                "- Nunca mencione arquivos, SVG, PDF, formatos ou etapas de produção\n"
                "- Nunca repita frases que poderiam servir para qualquer outra peça\n"
                "- Seja ESPECÍFICO sobre ESTA peça (não genérico)\n"
                "- Máximo 120 palavras no total\n"
                "- Responda APENAS com o texto no formato acima, sem comentários adicionais"
            )

            # ═══════════════════════════════════════════════════════════════
            # GERAÇÃO COM TEMPERATURE 0.78 (v740 - criatividade controlada)
            # ═══════════════════════════════════════════════════════════════
            response_text = self.ollama.generate_text(
                prompt,
                role="text_quality",
                temperature=0.78,  # v740: criatividade sem alucinar
                num_predict=250,
            )

            if response_text:
                # Garante que começa com o nome
                if not response_text.strip().startswith(clean_name[:15]):
                    response_text = clean_name + "\n\n" + response_text.strip()
                
                self.logger.info(
                    "✅ Descrição gerada com sucesso para %s (%d chars)",
                    os.path.basename(project_path),
                    len(response_text)
                )
                
                return response_text.strip()

            # Ollama retornou vazio — usa fallback de descrição
            self.logger.warning(
                "⚠️ Ollama retornou vazio para %s, usando fallback",
                os.path.basename(project_path)
            )
            structure = self._get_structure(project_path, project_data)
            return self.fallback.fallback_description(project_path, project_data, structure)

        except Exception as e:
            self.logger.error(
                "❌ Erro ao gerar descrição para %s: %s",
                os.path.basename(project_path),
                e,
                exc_info=True
            )
            structure = self._get_structure(project_path, project_data)
            return self.fallback.fallback_description(project_path, project_data, structure)

    # ──────────────────────────────────────────────────────────────────
    # HELPERS INTERNOS
    # ──────────────────────────────────────────────────────────────────

    def _get_structure(self, project_path, project_data):
        """Retorna estrutura do projeto (do cache ou analisa ao vivo)."""
        return (
            project_data.get("structure")
            or self.scanner.analyze_project_structure(project_path)
        )

    def _find_first_image(self, project_path):
        """Encontra primeira imagem no projeto."""
        from config.constants import FILE_EXTENSIONS
        valid_extensions = FILE_EXTENSIONS["images"]
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            pass
        return None

    def _clean_name(self, raw_name):
        """Limpa nome do projeto removendo extensões e códigos."""
        clean = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"[-_]\d{5,}", "", clean)
        clean = clean.replace("-", " ").replace("_", " ").strip()
        return clean
