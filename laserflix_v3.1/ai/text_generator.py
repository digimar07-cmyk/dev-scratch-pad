"""
Gerador de texto com IA - Análises e descrições
Restaurado com lógica refinada da v740 (3 semanas de testes)
"""
import os
import re
from config.settings import FAST_MODEL_THRESHOLD
from utils.logging_setup import LOGGER


class TextGenerator:
    """
    Gera análises (categorias/tags) e descrições de projetos usando Ollama.
    Funciona com ou sem Ollama rodando — fallbacks garantem resultado sempre.
    
    LÓGICA REFINADA v740:
      - Raciocínio estruturado em 3 etapas antes de escrever
      - Hierarquia NOME > Visão rigorosamente aplicada
      - Prompts cirúrgicos para evitar genericidade
      - Temperature 0.78 para criatividade controlada
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

    def _ensure_minimum_categories(self, categories, project_name):
        """
        Garante que SEMPRE existam no mínimo 3 categorias.
        Aplica validação em cascata com 4 níveis de segurança.
        
        Args:
            categories: Lista de categorias retornadas
            project_name: Nome do projeto (para logs)
        
        Returns:
            Lista com NO MÍNIMO 3 categorias (garantido)
        """
        original_count = len(categories)
        
        # NÍVEL 1: Se já tem 3+, apenas loga sucesso
        if original_count >= 3:
            self.logger.info(
                "✅ [CAT-OK] %s: %d categorias geradas pela IA",
                project_name, original_count
            )
            return categories
        
        # NÍVEL 2: Tenta completar com fallback_categories
        self.logger.warning(
            "⚠️ [CAT-FALTA] %s: IA retornou apenas %d cats, chamando fallback",
            project_name, original_count
        )
        
        # Cria caminho fake para fallback (ele só usa o basename)
        fake_path = f"/fake/{project_name}"
        fallback_cats = self.fallback.fallback_categories(fake_path, categories)
        
        if len(fallback_cats) >= 3:
            self.logger.info(
                "✅ [CAT-FALLBACK] %s: Fallback completou para %d categorias",
                project_name, len(fallback_cats)
            )
            return fallback_cats
        
        # NÍVEL 3: Fallback falhou, usa defaults hardcoded
        self.logger.error(
            "❌ [CAT-FALHA] %s: Fallback só retornou %d cats, forçando defaults",
            project_name, len(fallback_cats)
        )
        
        defaults = ["Aniversário", "Diversos", "Diversos"]
        
        # Começa com o que já temos (pode ser vazio)
        result = list(fallback_cats) if fallback_cats else []
        
        # Completa com defaults até ter 3
        idx = 0
        while len(result) < 3:
            result.append(defaults[idx])
            idx += 1
            if idx >= len(defaults):
                idx = 0  # Repete se necessário
        
        # NÍVEL 4: Garantia final (paranoia)
        if len(result) < 3:
            self.logger.critical(
                "🚨 [CAT-CRITICO] %s: Mesmo após defaults ainda tem %d cats!",
                project_name, len(result)
            )
            # Força brutalmente
            result.extend(defaults)
        
        self.logger.info(
            "✅ [CAT-GARANTIDO] %s: Garantidas %d categorias (original: %d)",
            project_name, len(result), original_count
        )
        
        return result[:8]  # Limita a 8 no máximo

    def analyze_project(self, project_path, batch_size=1):
        """
        Analisa projeto e retorna (categories, tags).
        Integra visão (moondream) quando imagem de capa está disponível.

        Funciona com ou sem Ollama:
          - COM Ollama: usa IA + visão + fallback_categories se retorno incompleto
          - SEM Ollama: usa fallback_analysis baseado em keywords do nome

        GARANTIA ABSOLUTA:
          ✅ SEMPRE retorna no mínimo 3 categorias obrigatórias:
             [0] Data comemorativa
             [1] Função/Tipo
             [2] Ambiente
          ✅ Sistema de validação em cascata com 4 níveis:
             1° Parse da IA
             2° fallback_categories() se < 3
             3° Defaults hardcoded se ainda < 3
             4° Garantia final paranoia

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

            # ══════════════════════════════════════════════════════════════════
            # PROMPT REFINADO: Nomes compostos + Inferência de ambiente contextual
            # ══════════════════════════════════════════════════════════════════
            prompt = f"""Analise este produto de corte laser e responda EXATAMENTE no formato solicitado.

📁 NOME: {name}
📊 ARQUIVOS: {structure['total_files']} arquivos | Subpastas: {subfolders_str}
🗂️ TIPOS: {file_types_str}
🔧 FORMATOS: {tech_str}{vision_line}

### INSTRUÇÕES IMPORTANTES ANTES DE COMEÇAR:

1. NOMES COMPOSTOS:
   - Leia o nome COMPLETO como uma UNIDADE, não separe palavras
   - Exemplos corretos de interpretação:
     * "Nook Book" = um nicho decorativo para estantes (NÃO é só "livro")
     * "Bike-Mileage-Tracker" = quadro rastreador de quilometragem de bike (NÃO é só "bicicleta")
     * "Book Stand" = suporte para livros (NÃO é só "livro" ou "suporte" isolados)
     * "Wine Holder" = porta-vinho (NÃO é só "vinho")
   - Sempre entenda o CONCEITO COMPLETO que o nome representa

2. INFERÊNCIA DE AMBIENTE/LOCAL DE USO:
   - Pense: "Onde as pessoas REALMENTE colocariam/usariam este produto no dia a dia?"
   - Analise o NOME + FUNÇÃO juntos para inferir o local
   - Exemplos de raciocínio correto:
     * "Nook Book" (decoração de estante com livros) → Sala
     * "Bike Tracker" (quadro motivacional de ciclismo) → Sala ou Escritório
     * "Kitchen Organizer" (organizador de cozinha) → Cozinha
     * "Bathroom Mirror" (espelho de banheiro) → Banheiro
     * "Kids Name" (nome decorativo infantil) → Quarto Infantil
     * "Wedding Topper" (topo de bolo casamento) → Festa

### TAREFA 1 — CATEGORIAS
Atribua de 3 a 5 categorias, OBRIGATORIAMENTE nesta ordem:

1. Data Comemorativa (escolha UMA):
   Páscoa, Natal, Dia das Mães, Dia dos Pais, Dia dos Namorados, Aniversário, Casamento, 
   Chá de Bebê, Halloween, Dia das Crianças, Ano Novo, Formatura, Diversos

2. Função/Tipo (escolha UMA baseada no NOME COMPLETO):
   Porta-Retrato, Caixa Organizadora, Luminária, Porta-Joias, Porta-Chaves, Suporte, 
   Quadro Decorativo, Painel de Parede, Mandala, Nome Decorativo, Letreiro, Lembrancinha, 
   Chaveiro, Topo de Bolo, Centro de Mesa, Plaquinha, Brinquedo Educativo, Diversos

3. Ambiente/Local de Uso (escolha UM baseado em ONDE este produto seria USADO):
   - Analise: "Qual cômodo/local físico este produto ficaria?"
   - Use o raciocínio NOME + FUNÇÃO para inferir
   - Opções: Quarto, Sala, Cozinha, Banheiro, Escritório, Quarto Infantil, 
     Quarto de Bebê, Área Externa, Festa, Diversos

4. Estilo OPCIONAL (ex: Minimalista, Rústico, Moderno, Vintage, Romântico, Elegante)

5. Público OPCIONAL (ex: Bebê, Criança, Adulto, Casal, Família, Presente)

### TAREFA 2 — TAGS
Crie exatamente 8 tags relevantes:
- Primeiras 3: palavras-chave extraídas do nome COMPLETO "{name}" (mantenha conceitos compostos juntos)
- Demais 5: emoção, ocasião, público, estilo, uso

### FORMATO DE RESPOSTA (siga exatamente):
Categorias: [cat1], [cat2], [cat3], [cat4 opcional], [cat5 opcional]
Tags: [tag1], [tag2], [tag3], [tag4], [tag5], [tag6], [tag7], [tag8]"""

            if self.ollama.stop_flag:
                return self.fallback.fallback_analysis(project_path)

            # Gera resposta com IA
            text = self.ollama.generate_text(
                prompt,
                role=role,
                temperature=0.65,
                num_predict=200,
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

                # ═══════════════════════════════════════════════════════
                # VALIDAÇÃO REFORÇADA (garantia de 3 categorias SEMPRE)
                # ═══════════════════════════════════════════════════════
                categories = self._ensure_minimum_categories(categories, name)

                return categories[:8], tags

            # Ollama retornou vazio (indisponível ou timeout) — usa fallback completo
            self.logger.warning("⚠️ Ollama indisponível para %s, usando fallback completo", name)
            return self.fallback.fallback_analysis(project_path)

        except Exception:
            self.logger.exception("Erro em analyze_project para %s", project_path)
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
            # ═══════════════════════════════════════════════════════
            # 1° NOME — âncora absoluta
            # ═══════════════════════════════════════════════════════
            raw_name = project_data.get("name", os.path.basename(project_path) or "Sem nome")
            clean_name = self._clean_name(raw_name)

            # ═══════════════════════════════════════════════════════
            # 2° VISÃO — só se imagem passa no filtro de qualidade
            # ═══════════════════════════════════════════════════════
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

            # ═══════════════════════════════════════════════════════
            # PROMPT COM RACIOCÍNIO ESTRUTURADO (v740 refinado)
            # ═══════════════════════════════════════════════════════
            prompt = (
                "Você é especialista em peças físicas de corte a laser — placas, espelhos, "
                "porta-retratos, tabuletas, cabides, calendários, nomes decorativos e similares.\n\n"
                "NOME DA PEÇA (use isso como verdade absoluta sobre o que é o produto): "
                + clean_name + vision_context + "\n\n"
                
                # ────────────────────────────────────────────────────────────
                # REGRA FUNDAMENTAL (v740)
                # ────────────────────────────────────────────────────────────
                "### REGRA FUNDAMENTAL:\n"
                "O NOME define o que é o produto. O detalhe visual apenas complementa.\n"
                "Nunca invente função ou formato que contradiga o nome.\n\n"
                
                # ────────────────────────────────────────────────────────────
                # RACIOCÍNIO ESTRUTURADO EM 3 ETAPAS (v740)
                # ────────────────────────────────────────────────────────────
                "### RACIOCINE antes de escrever:\n"
                "1. O que exatamente é esta peça física, baseado no nome? (tipo de objeto)\n"
                "2. Para que serve na prática? (uso real no dia a dia)\n"
                "3. Que emoção ou momento ela representa? (conexão afetiva)\n\n"
                
                # ────────────────────────────────────────────────────────────
                # FORMATO DE SAÍDA
                # ────────────────────────────────────────────────────────────
                "### ESCREVA a descrição EXATAMENTE neste formato (sem nada além disso):\n\n"
                + clean_name + "\n\n"
                "🎨 Por Que Este Produto é Especial:\n"
                "[2 a 3 frases afetivas e únicas. Fale sobre o que torna ESTA peça especial. "
                "Nunca use frases genéricas que servem para qualquer produto.]\n\n"
                "💖 Perfeito Para:\n"
                "[2 a 3 frases práticas com exemplos reais de uso e ocasião para ESTA peça específica.]\n\n"
                
                # ────────────────────────────────────────────────────────────
                # REGRAS ANTI-GENERICIDADE (v740 reforçado)
                # ────────────────────────────────────────────────────────────
                "### REGRAS OBRIGATÓRIAS:\n"
                "- Escreva em português brasileiro\n"
                "- Nunca use a palavra projeto — esta é uma PEÇA ou PRODUTO físico\n"
                "- Nunca mencione arquivos, SVG, PDF, formatos ou etapas de produção\n"
                "- Nunca repita frases que poderiam servir para qualquer outra peça\n"
                "- Seja ESPECÍFICO sobre ESTA peça (não genérico)\n"
                "- Máximo 120 palavras no total\n"
                "- Responda APENAS com o texto no formato acima, sem comentários adicionais"
            )

            # ═══════════════════════════════════════════════════════
            # GERAÇÃO COM TEMPERATURE 0.78 (v740 - criatividade controlada)
            # ═══════════════════════════════════════════════════════
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

    # ────────────────────────────────────────────────────────────────────
    # HELPERS INTERNOS
    # ────────────────────────────────────────────────────────────────────

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
