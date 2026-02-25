# LASERFLIX — Diário de Versões

> **Instrução permanente:** Toda vez que uma nova versão for criada a partir deste repositório,
> o desenvolvedor (ou assistente de IA) **deve obrigatoriamente** registrar neste arquivo
> a nova versão com: número, data, base de origem e lista detalhada do que foi alterado.
> Nunca pule esta etapa. Este é o diário oficial do LaserFlix.

---

## v8.1.3.0 — Stable
**Data:** Fevereiro 2026  
**Base:** v8.1.2.2  
**Arquivo:** `v8.1.3.py`  
**Status:** ✅ STABLE — NÃO MODIFICAR

### O que foi feito:
- **Patch 5** — Paginação / Lazy loading na listagem (`/api/products` suporta `offset` e `limit`). Frontend com botão "Carregar mais" mostrando quantidade restante.
- **Patch 6** — Modal: edição inline de Nome, Categorias e Tags diretamente na tela de detalhe do produto. Salva via `/api/update_product`.
- **Patch 7** — Card: badge contador de imagens (`cover_count`) exibido no canto superior esquerdo de cada card.

### Arquitetura:
- Backend: Python + Flask (porta 5678)
- Frontend: HTML/CSS/JS single-file embutido na variável `HTML_PAGE`
- IA: Ollama local (qwen2.5:7b, qwen2.5:3b, moondream, nomic-embed-text)
- Banco: JSON (`laserflix_database.json`)
- Config: JSON (`laserflix_config.json`)

---

## v8.1.3_patch01 — Fallbacks Inteligentes
**Data:** 25 de Fevereiro de 2026  
**Base:** v8.1.3.0 (Stable)  
**Arquivo:** `v8.1.3_patch01.py`  
**Módulo auxiliar:** `laserflix_fallbacks.py`  
**Status:** 🔧 EM DESENVOLVIMENTO

### Problema resolvido:
Quando o Ollama não estava ativo no momento da análise, ~90% dos produtos recebiam a categoria
"Diversos" por padrão, pois o sistema de fallback original usava apenas um dicionário
de palavras-chave muito limitado.

### O que foi feito:
- **Patch 8** — Criação do módulo `laserflix_fallbacks.py` com motor de fallback inteligente:
  - `smart_fallback_categories()`: detecta Data Comemorativa, Tipo/Função e Ambiente usando tabelas expandidas de tokens em PT e EN, incluindo bigramas e trigramas. Nunca retorna "Diversos" — usa valores semânticos como fallback mínimo.
  - `smart_fallback_analysis()`: usa `smart_fallback_categories()` + extrai tags semânticas do nome (madeira, presente, personalizado, decoração, etc.).
  - `smart_fallback_description()`: gera descrição comercial completa baseada apenas no nome do produto, com textos específicos por tipo (Separador de Livros, Porta-Retrato, Cabide, Espelho, Calendário, Luminária, Nome Decorativo, Quadro Decorativo, Caixa Organizadora, Topo de Bolo, Lembrancinha, Mandala) e fallback genérico inteligente que ainda usa o nome e o tema sazonal detectado.
  - Suporte a nomes em inglês: "Christmas Nook Book" → Separador de Livros + Natal + Estante
  - Suporte a nomes compostos via bigramas: "book nook", "wall art", "shelf sitter", etc.
- Os 3 métodos originais (`fallback_categories`, `fallback_analysis`, `fallback_description`) foram **substituídos** no Engine por chamadas ao módulo externo.
- O arquivo `v8.1.3.py` (stable) **não foi modificado**.

### Arquivos desta versão:
- `v8.1.3_patch01.py` — app principal com patch 8 aplicado
- `laserflix_fallbacks.py` — módulo auxiliar com os fallbacks inteligentes
- `CHANGELOG.md` — este arquivo

---

## Próximas versões — Sugestões de roadmap

- [ ] Indicador visual no card quando produto foi analisado sem Ollama (fallback)
- [ ] Reprocessar automaticamente produtos com `analyzed_model: fallback` quando Ollama ficar disponível
- [ ] Filtro na sidebar por "Analisado com IA" vs "Analisado sem IA"
- [ ] Exportar catálogo para CSV / Excel
- [ ] Preview de descrição antes de salvar no modal
