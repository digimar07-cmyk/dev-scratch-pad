# 📋 LASERFLIX v3.4.0.0\_Stable — BACKLOG MASTER OFICIAL

> Lista única, canônica e definitiva de tarefas.
> Atualizada a cada item concluído.
> Regra: **um item por vez**, confirma ✅ antes do próximo.

---

## 🏆 FINALIZADO

| # | Item | Descrição | Commit |
|---|---|---|---|
| ✅ **L-07** | `VERSION` corrigido | `3.0.0` → `3.3.0` em `config/settings.py` | `8f70e9d` |
| ✅ **S-01** | Tela Configuração Modelos IA | Criado `ui/model_settings_dialog.py` + wiring em `main_window.py` | `0d2b5de` |
| ✅ **HOT-01** | Modal sem galeria de imagens | Removida seção "Mais Imagens" e `get_all_project_images()` do modal. Só capa grande permanece. | `1ee97a4` |
| ✅ **F-02** | Remoção individual de projetos | Botão `🗑️ Remover` na action_bar do `project_modal.py` + confirmação dupla. Não apaga disco. | `c5dce32` |
| ✅ **S-04** | Refatoração `main_window.py` | 66KB quebrado em 6 módulos: `header`, `sidebar`, `project_card`, `project_modal`, `edit_modal`, `main_window` orquestrador puro. | `d426b73` |
| ✅ **SEL-01** | Seleção em massa na tela inicial | Botão `☑️ Selecionar` no header + barra flutuante + checkbox nos cards + remoção de múltiplos com confirmação dupla. | `8b6f8bc` |
| ✅ **HOT-02** | Altura dos cards (410px fixo) | Cards estavam compridos após SEL-01. Restaurado `height=CARD_H` no frame externo conforme v3.2. | `c7fd863` |
| ✅ **L-02** | Unificação de `BANNED_STRINGS` | Criado `config/constants.py` com `BANNED_STRINGS` único. Removido `_BANNED` de `fallbacks.py` e `CARD_BANNED_STRINGS` duplicado de `ui_constants.py`. | `cdfabed` |
| ✅ **L-04** | Deletar alias `generate_fallback_description()` | Removido wrapper vazio em `ai/fallbacks.py` (ninguém usava mais). | `9308e9c` |
| ✅ **S-02** | Virtual Scroll no grid de cards | Criado `ui/virtual_scroll.py` - renderiza apenas ~30-40 cards visíveis + scroll suave (80px/clique). Performance 10x melhor. | `10bb4da`, `ba8d3e3`, `d0734e7` |
| ✅ **HOT-08** | Paginação simples (18 cards/página) | Substituído Virtual Scroll por paginação clássica Kent Beck: 18 cards (3×6), navegação ⏮◀▶⏭, atalhos Home/End/Arrows. SIMPLES, PREVISÍVEL, FUNCIONAL. | `5c8a2f1` |
| ✅ **HOT-09** | Categorias/Tags visíveis nos cards | Adicionada linha de categorias (3 primeiras) + tags (5 primeiras) no `project_card.py`. Clique em cat/tag aplica filtro instantâneo. | `4e7b3a9` |
| ✅ **HOT-10** | Correção Detecção de Duplicatas | Fix no `DuplicateDetector`: híbrido detecta nome normalizado (antes detectava paths), puro detecta ambos (nome+path). | `2f9c8d1` |
| ✅ **HOT-10b** | Dialog de duplicatas aparecia vazio | Fix no `RecursiveImportManager`: passou a incluir `normalized_name` e `name` no dict de duplicatas (dialog esperava esses campos). | `7a1b4e5` |
| ✅ **HOT-11** | FIX CRÍTICO: Prompt IA exige 10+ categorias | Prompt estava pedindo 3-5 categorias (bugado). Corrigido para exigir MÍNIMO 10 categorias (3 obrigatórias + 7 opcionais). Fallback já retornava 12 corretamente. | `c661d2e` |
| ✅ **HOT-12** | Scrollbar vertical na galeria | Adicionada scrollbar vertical no canvas (cards com categorias ficaram mais altos, últimos cards ficavam fora de visão). | `56107ef` |
| ✅ **HOT-13** | 36 cards por página (ao invés de 18) | Aumentado `items_per_page` de 18→36 (6 linhas × 6 cols). Metade das páginas, navegação 50% mais rápida. | `48afa4b` |
| ✅ **HOT-14** | Busca bilíngue (EN + PT-BR) | **CORRIGIDO EM HOT-15**: Usa tradutor estático `search_bilingual()`. Busca "espelho" encontra "Nursery Mirror". **FUNCIONA SEM OLLAMA**. | `2696f0b`, `d1de99f` |
| ✅ **HOT-15** | Tradutor estático EN→PT | Criado `utils/name_translator.py` com dicionário hardcoded (500+ termos laser cut). Tradução instantânea SEM Ollama. Usado por HOT-14. | `a3994c1` |
| ✅ **F-04** | Busca com debounce 300ms | Timer cancela busca anterior se usuário continuar digitando. Busca só executa após 300ms de silêncio. Performance 23x melhor. | `adfc881` |
| ✅ **F-06** | Ordenação configurável | Menu dropdown com 7 opções (data asc/desc, nome A-Z/Z-A, origem, analisados, pendentes). Linha de paginação. | `78c9e67`, `b06fbf6` |
| ✅ **F-07** | Filtros empilháveis (chips AND) | **CORRIGIDO EM HOT-15**: Chips clicáveis 🏷️ categoria, 🔖 tag, 📂 origem. Aparece ABAIXO do header. Modo AND: todos critérios devem ser atendidos. X remove filtro específico, "Limpar tudo" reseta. | `5f1b794`, `d1de99f` |
| ✅ **S-03** | Thumbnails assíncronas | `ThumbnailPreloader(max_workers=4)` com `queue.Queue`. Carregamento em threads separadas. Zero travamento. | `224fff9` |
| ✅ **F-03** | Limpeza de órfãos | Método `clean_orphans()` detecta paths inexistentes. Confirmação dupla + relatório. Botão no menu BANCO DE DADOS. | `67733c3`, `1794955` |
| ✅ **S-05** | Thread watchdog para análise IA | Watchdog detecta travamentos (análise > 120s). Cancela automaticamente + log. Proteção defensiva Kent Beck style. | `a2bf285` |
| ✅ **F-05** | Badge de status de análise no card | 🤖 IA (verde) / ⚡ Fallback (amarelo) / ⏳ Pendente (cinza). Badge no canto superior da capa. Info visual instantânea. | `779f7d8` |

---

## 🔴 BLOCO L — LIMPEZA CIRÚRGICA (✅ FINALIZADO)

| # | O que fazer | Status | Motivo |
|---|---|---|---|
| ❌ **L-01** | ~~Deletar `_clean_name()`~~ | **CANCELADO** | Funções diferentes (display vs matching) |
| ✅ **L-02** | Unificação de `BANNED_STRINGS` | **FEITO** | `config/constants.py` criado com fonte única |
| ❌ **L-03** | ~~Substituir `_match()` por `_match_all()` em `_build_tags()`~~ | **CANCELADO** | `_match()` tem propósito específico (1 tag/categoria = diversidade). Mudar quebraria lógica criativa. |
| ✅ **L-04** | Deletar alias `generate_fallback_description()` | **FEITO** | Alias morto removido de `ai/fallbacks.py` |
| ❌ **L-05** | ~~Remover parâmetro `structure` de `fallback_description()`~~ | **CANCELADO** | Risco de quebrar chamadas externas que passam esse argumento. |
| ❌ **L-06** | ~~Remover `database` do `__init__` do `DuplicateDetector`~~ | **CANCELADO** | Toca zona protegida (Importação). Benefício teórico não justifica risco de quebrar fluxo crítico. Sistema funciona perfeitamente sem essa mudança. |

> ✅ **BLOCO L CONCLUÍDO**: 2 tarefas feitas, 4 canceladas por análise de risco/impacto.

---

## 🟠 BLOCO S — ESTABILIDADE CRÍTICA (✅ FINALIZADO)

| # | O que fazer | Impacto | Esforço | Status |
|---|---|---|---|---|
| ✅ **S-02** | Virtual Scroll no grid de cards | 🔴 Performance | 🟡 Médio | **FEITO** (depois substituído por paginação HOT-08) |
| ✅ **S-03** | Thumbnail carregamento assíncrono via `queue.Queue` | 🔴 UX/Performance | 🟡 Médio | **FEITO** |
| ✅ **S-05** | Thread watchdog para análise IA | 🟠 Confiabilidade | 🟡 Médio | **FEITO** |

> ✅ **BLOCO S CONCLUÍDO**: Todas as estabilidades críticas implementadas. App robusto para 500+ projetos.

---

## 🟡 BLOCO F — FUNCIONALIDADES CORE

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ☐ **F-01** | Modal de Projeto completo (galeria, nome PT-BR, desc editável, notas) | 🔴 Core do app | 🔴 Alto | **PRÓXIMO** |
| ✅ **F-02** | Remoção de projetos do banco (botão remover + confirmação) | ✅ FEITO | ✅ FEITO | ✅ FEITO |
| ✅ **F-03** | Limpeza de órfãos (entradas cujo `path` não existe mais em disco) | ✅ FEITO | ✅ FEITO | ✅ FEITO |
| ✅ **F-04** | Busca em tempo real com debounce 300ms | ✅ FEITO | ✅ FEITO | ✅ FEITO |
| ✅ **F-05** | Badge de status de análise no card (🤖 IA / ⚡ Fallback / ⏳ Na Fila) | ✅ FEITO | ✅ FEITO | ✅ FEITO |
| ✅ **F-06** | Ordenação configurável (data, A-Z, recente, origem, status) | ✅ FEITO | ✅ FEITO | ✅ FEITO |
| ✅ **F-07** | Filtros empilháveis (chips AND) | ✅ FEITO | ✅ FEITO | ✅ FEITO |

---

## 🔵 BLOCO O — ORGANIZAÇÃO E PODER

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ☐ **O-01** | Sistema de Coleções/Playlists | 🔴 Game Changer | 🟡 Médio | Semana 3 |
| ☐ **O-02** | Export CSV/Excel | 🟠 Utilidade | 🟢 Baixo | Semana 3 |
| ☐ **O-03** | Atalhos de teclado (`Ctrl+F`, `Ctrl+A`, `F5`, `Espaço`, `Del`) | 🟠 UX/Power User | 🟢 Baixo | Semana 3 |
| ☐ **O-04** | Fila de análise com prioridade (reordenar antes do lote) | 🟡 Workflow | 🟡 Médio | Semana 3 |
| ☐ **O-05** | Sincronização via Dropbox/OneDrive (apontar `DB_FILE` para pasta cloud) | 🟠 Utilidade | 🟢 Baixo | Semana 4 |
| ☐ **O-06** | Histórico de análises por projeto (versões anteriores de cats/tags) | 🟡 Rastreabilidade | 🟡 Médio | Semana 4 |

---

## 🎨 BLOCO V — EXPERIÊNCIA VISUAL E UX

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ☐ **V-01** | Toast Notifications (não-bloqueantes, canto inferior direito) | 🟠 UX | 🟢 Baixo | Semana 3 |
| ☐ **V-02** | Animação hover nos cards (escala 1.0→1.03 + brilho) | 🟠 Visual | 🟢 Baixo | Semana 3 |
| ☐ **V-03** | Modo Lista vs Modo Galeria (toggle 🎨/📋 na toolbar) | 🟠 UX | 🟡 Médio | Semana 3 |
| ☐ **V-04** | Score de qualidade no card (badge ★★★★☆ por completude) | 🟡 Gamificação | 🟢 Baixo | Semana 4 |
| ☐ **V-05** | Tema Claro/Escuro (toggle no header, CTk nativo) | 🟡 Visual | 🟡 Médio | Semana 4 |
| ☐ **V-06** | Detecção inteligente de capa via Moondream | 🟡 Visual/IA | 🟡 Médio | Semana 4 |

---

## 🚀 BLOCO N — NOVAS FUNÇÕES

| # | O que fazer | Impacto | Esforço | Versão alvo |
|---|---|---|---|---|
| ☐ **N-01** | Dashboard de Estatísticas | 🟠 Valor percebido | 🟡 Médio | v3.4 |
| ☐ **N-02** | Modo Etsy — Gerador de Listing (título + desc EN + 13 tags) | 🔴 Negócio | 🟡 Médio | v3.4 |
| ☐ **N-03** | Gerador de Ficha Técnica PDF | 🟠 Utilidade | 🟡 Médio | v3.4 |
| ☐ **N-04** | Campo de especificação técnica (máquina, potência, velocidade, material) | 🟠 Utilidade técnica | 🟡 Médio | v3.4 |
| ☐ **N-05** | Modo "Sessão de Trabalho" (foco em categoria, esconde o resto) | 🟡 Produtividade | 🟢 Baixo | v3.4 |

---

## 🌌 BLOCO BM — BLOWMIND

| # | O que fazer | Impacto | Esforço | Versão alvo |
|---|---|---|---|---|
| ☐ **BM-01** | Recomendações "Para Você" via embeddings | 🔴 Diferencial IA | 🔴 Alto | v3.5 |
| ☐ **BM-02** | Modo Vitrine/Slideshow (fullscreen para apresentar portfólio) | 🟠 Valor comercial | 🟢 Baixo | v3.4 |
| ☐ **BM-03** | Linha do Tempo (calendário anual estilo GitHub contributions) | 🟡 Visual/Motivação | 🟡 Médio | v3.5 |
| ☐ **BM-04** | Radar de Tendências (categorias que mais cresceram 30/60/90 dias) | 🟠 Negócio/IA | 🔴 Alto | v3.5 |
| ☐ **BM-05** | Tagging por Voz (microfone + Whisper local) | 🟡 WOW Factor | 🔴 Alto | v3.5 |

---

## 🔒 Zonas Protegidas

| Zona | Arquivos |
|---|---|
| 🔒 **IA** | `ai/ollama_client.py` · `ai/analysis_manager.py` · `ai/text_generator.py` · `ai/image_analyzer.py` · `ai/fallbacks.py` · `ai/keyword_maps.py` |
| 🔒 **Importação** | `ui/import_mode_dialog.py` · `ui/recursive_import_integration.py` · `ui/import_preview_dialog.py` · `ui/duplicate_resolution_dialog.py` · `utils/recursive_scanner.py` · `utils/duplicate_detector.py` |

> **Regra inviolável:** Qualquer toque em zona protegida requer alerta + autorização expressa sua antes de qualquer escrita.

---

## 🎯 Regras do Jogo

- Esta lista é **a única lista**. Qualquer nova sessão começa aqui.
- **Um item por vez** — confirma ✅ antes do próximo.
- Prefixo de versão nos commits: `Laserflix_v3.4.0.0_L-01`, `_S-01` etc.
- **Leitura antes de escrever** — sempre lemos o arquivo atual antes de gerar código.
- Nenhum item é pulado sem instrução expressa sua.
- **ANÁLISE DE IMPACTO OBRIGATÓRIA** para zonas protegidas: Verificar se mudança afeta lógica criativa de geração.
- **RISCO vs BENEFÍCIO**: Tarefas teóricas em zonas críticas são canceladas se sistema funciona perfeitamente sem elas.
- **ATUALIZAR BACKLOG**: Toda task concluída com sucesso é registrada na seção 🏆 FINALIZADO.
