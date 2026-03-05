# 📋 LASERFLIX v3.3.0.0\_Stable — BACKLOG MASTER OFICIAL

> Lista única, canônica e definitiva de tarefas.
> Atualizada a cada item concluído.
> Regra: **um item por vez**, confirma â✅ antes do próximo.

---

## 🏆 FINALIZADO

| # | Item | Descrição | Commit |
|---|---|---|---|
| ✅ **L-07** | `VERSION` corrigido | `3.0.0` → `3.3.0` em `config/settings.py` | `8f70e9d` |
| ✅ **S-01** | Tela Configuração Modelos IA | Criado `ui/model_settings_dialog.py` + wiring em `main_window_FIXED.py` | `0d2b5de` + `da055ed` |
| ✅ **HOT-01** | Modal sem galeria de imagens | Removida seção "Mais Imagens" e `get_all_project_images()` do modal. Só capa grande permanece. | `pendente` |

---

## 🔴 BLOCO L — LIMPEZA CIRÚRGICA

> Fazer primeiro. Risco mínimo, base sólida.
> ⚠️ Todos os itens abaixo tocam zonas protegidas — aguarda autorização antes de executar.

| # | O que fazer | Impacto | Esforço | Zona Prot.? |
|---|---|---|---|---|
| ◻ **L-01** | Deletar `_clean_name()` de `fallbacks.py`, usar `normalize_project_name()` de `text_utils.py` | 🔴 Bug latente | 🟢 Baixo | ⚠️ Sim |
| ◻ **L-02** | Unificar `_BANNED` (`fallbacks.py`) com `CARD_BANNED_STRINGS` (`ui_constants.py`) → mover para `config/constants.py` | 🔴 Inconsistência | 🟢 Baixo | ⚠️ Sim |
| ◻ **L-03** | Substituir os 2 usos de `_match()` em `_build_tags()` por `_match_all()` e deletar `_match()` | 🟠 Código morto | 🟢 Baixo | ⚠️ Sim |
| ◻ **L-04** | Deletar alias `generate_fallback_description()` em `fallbacks.py` | 🟡 Confusão | 🟢 Baixo | ⚠️ Sim |
| ◻ **L-05** | Remover parâmetro `structure` de `fallback_description()` e de todas as chamadas | 🟡 Ruído | 🟢 Baixo | ⚠️ Sim |
| ◻ **L-06** | Remover `database` do `__init__` do `DuplicateDetector` | 🟠 Acoplamento | 🟢 Baixo | ⚠️ Sim |

---

## 🟠 BLOCO S — ESTABILIDADE CRÍTICA

> Sem isso o app não sobrevive com 500+ projetos.

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ◻ **S-02** | Virtual Scroll no grid de cards | 🔴 Performance | 🟡 Médio | Semana 1 |
| ◻ **S-03** | Thumbnail carregamento assimíncrono via `queue.Queue` | 🔴 UX/Performance | 🟡 Médio | Semana 1 |
| ◻ **S-04** | Quebrar `main_window_FIXED.py` (66KB → 5 arquivos) | 🔴 Manutenção | 🔴 Alto | Semana 1 |
| ◻ **S-05** | Thread watchdog para análise IA | 🟠 Confiabilidade | 🟡 Médio | Semana 1 |

---

## 🟡 BLOCO F — FUNCIONALIDADES CORE

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ◻ **F-01** | Modal de Projeto completo (galeria, nome PT-BR, desc editável, notas) | 🔴 Core do app | 🔴 Alto | Semana 2 |
| ◻ **F-02** | Remoção de projetos do banco (botão remover + confirmação) | 🔴 Funcional faltante | 🟢 Baixo | Semana 2 |
| ◻ **F-03** | Limpeza de órfãos (entradas cujo `path` não existe mais em disco) | 🟠 Integridade dados | 🟢 Baixo | Semana 2 |
| ◻ **F-04** | Busca em tempo real com debounce 300ms | 🟠 UX | 🟢 Baixo | Semana 2 |
| ◻ **F-05** | Badge de status de análise no card (🤖 IA / ⚡ Fallback / ⏳ Na Fila) | 🟠 UX/Info | 🟢 Baixo | Semana 2 |
| ◻ **F-06** | Ordenação configurável (data, A-Z, recente, origem, status) | 🟠 Organização | 🟢 Baixo | Semana 2 |
| ◻ **F-07** | Filtro multi-critério simultâneo (chips empilnáveis AND) | 🟠 Organização | 🟡 Médio | Semana 2 |

---

## 🔵 BLOCO O — ORGANIZAÇÃO E PODER

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ◻ **O-01** | Sistema de Coleções/Playlists | 🔴 Game Changer | 🟡 Médio | Semana 3 |
| ◻ **O-02** | Export CSV/Excel | 🟠 Utilidade | 🟢 Baixo | Semana 3 |
| ◻ **O-03** | Atalhos de teclado (`Ctrl+F`, `Ctrl+A`, `F5`, `Espaço`, `Del`) | 🟠 UX/Power User | 🟢 Baixo | Semana 3 |
| ◻ **O-04** | Fila de análise com prioridade (reordenar antes do lote) | 🟡 Workflow | 🟡 Médio | Semana 3 |
| ◻ **O-05** | Sincronização via Dropbox/OneDrive (apontar `DB_FILE` para pasta cloud) | 🟠 Utilidade | 🟢 Baixo | Semana 4 |
| ◻ **O-06** | Histórico de análises por projeto (versões anteriores de cats/tags) | 🟡 Rastreabilidade | 🟡 Médio | Semana 4 |

---

## 🎨 BLOCO V — EXPERIÊNCIA VISUAL E UX

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ◻ **V-01** | Toast Notifications (não-bloqueantes, canto inferior direito) | 🟠 UX | 🟢 Baixo | Semana 3 |
| ◻ **V-02** | Animação hover nos cards (escala 1.0→1.03 + brilho) | 🟠 Visual | 🟢 Baixo | Semana 3 |
| ◻ **V-03** | Modo Lista vs Modo Galeria (toggle 🎬/📋 na toolbar) | 🟠 UX | 🟡 Médio | Semana 3 |
| ◻ **V-04** | Score de qualidade no card (badge ★★★★☆ por completude) | 🟡 Gamificação | 🟢 Baixo | Semana 4 |
| ◻ **V-05** | Tema Claro/Escuro (toggle no header, CTk nativo) | 🟡 Visual | 🟡 Médio | Semana 4 |
| ◻ **V-06** | Detecção inteligente de capa via Moondream | 🟡 Visual/IA | 🟡 Médio | Semana 4 |

---

## 🚀 BLOCO N — NOVAS FUNÇÕES

| # | O que fazer | Impacto | Esforço | Versão alvo |
|---|---|---|---|---|
| ◻ **N-01** | Dashboard de Estatísticas | 🟠 Valor percebido | 🟡 Médio | v3.4 |
| ◻ **N-02** | Modo Etsy — Gerador de Listing (título + desc EN + 13 tags) | 🔴 Negócio | 🟡 Médio | v3.4 |
| ◻ **N-03** | Gerador de Ficha Técnica PDF | 🟠 Utilidade | 🟡 Médio | v3.4 |
| ◻ **N-04** | Campo de especificação técnica (máquina, potência, velocidade, material) | 🟠 Utilidade técnica | 🟡 Médio | v3.4 |
| ◻ **N-05** | Modo "Sessão de Trabalho" (foco em categoria, esconde o resto) | 🟡 Produtividade | 🟢 Baixo | v3.4 |

---

## 🌌 BLOCO BM — BLOWMIND

| # | O que fazer | Impacto | Esforço | Versão alvo |
|---|---|---|---|---|
| ◻ **BM-01** | Recomendações "Para Você" via embeddings | 🔴 Diferencial IA | 🔴 Alto | v3.5 |
| ◻ **BM-02** | Modo Vitrine/Slideshow (fullscreen para apresentar portfólio) | 🟠 Valor comercial | 🟢 Baixo | v3.4 |
| ◻ **BM-03** | Linha do Tempo (calendário anual estilo GitHub contributions) | 🟡 Visual/Motivação | 🟡 Médio | v3.5 |
| ◻ **BM-04** | Radar de Tendências (categorias que mais cresceram 30/60/90 dias) | 🟠 Negócio/IA | 🔴 Alto | v3.5 |
| ◻ **BM-05** | Tagging por Voz (microfone + Whisper local) | 🟡 WOW Factor | 🔴 Alto | v3.5 |

---

## 🔒 Zonas Protegidas

| Zona | Arquivos |
|---|---|
| 🔒 **IA** | `ai/ollama_client.py` · `ai/analysis_manager.py` · `ai/text_generator.py` · `ai/image_analyzer.py` · `ai/fallbacks.py` · `ai/keyword_maps.py` |
| 🔒 **Importação** | `ui/import_mode_dialog.py` · `ui/recursive_import_integration.py` · `ui/import_preview_dialog.py` · `ui/duplicate_resolution_dialog.py` · `utils/recursive_scanner.py` · `utils/duplicate_detector.py` |

> **Regra inviolable:** Qualquer toque em zona protegida requer alerta + autorização expressa sua antes de qualquer escrita.

---

## 🎯 Regras do Jogo

- Esta lista é **a única lista**. Qualquer nova sessão começa aqui.
- **Um item por vez** — confirma ✅ antes do próximo.
- Prefixo de versão nos commits: `Laserflix_v3.3.0.0_L-01`, `_S-01` etc.
- **Leitura antes de escrever** — sempre lemos o arquivo atual antes de gerar código.
- Nenhum item é pulado sem instrução expressa sua.
