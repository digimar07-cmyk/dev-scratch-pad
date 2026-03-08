# CHANGELOG - Laserflix

Todas as mudanças importantes serão documentadas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [3.4.3.4] - 2026-03-07 22:23:56

### 🎉 REFATORAÇÃO FASE-1A CONCLUÍDA

**Mudanças principais:**
- ✂️  Removido método `_update_chips_bar()` duplicado (~44 linhas)
- 🧹 Eliminadas todas as chamadas ao método obsoleto
- 📊 Redução: 868 → 646 linhas no `main_window.py` (-25.6%)
- ✅ App testado e funcional
- 💾 Backup automático criado (`.backup_20260307_222213`)

**Componentes existentes identificados:**
- `ui/components/chips_bar.py` - Já existia mas não estava integrado
- `ui/components/pagination_controls.py` - Próximo alvo FASE-1B
- `ui/components/selection_bar.py` - Próximo alvo FASE-1C

**Técnica aplicada:**
- Kent Beck "Tidy First" - Micro-refactorings incrementais
- Script 100% automático com validação de sintaxe
- Zero passos manuais

**Modelo usado**: Claude Sonnet 4.5

**Commits:**
- `4dbb8a6` - Mudança de versão + refatoração aplicada
- `39bb6d7` - Script de refatoração automática criado

**Próximos passos:**
- FASE-1B: Extrair/integrar `pagination_controls.py`
- FASE-1C: Extrair/integrar `selection_bar.py`
- FASE-1D: Simplificar `display_projects()` - Header

---

## [3.4.2.5] - 2026-03-07 09:13:00

### Sistema de versionamento automático implementado

**Mudanças:**
- Criado `version_manager.py` - Gerenciador de versões
- Criado arquivo `VERSION` para rastreamento único
- Criado `CHANGELOG.md` para histórico de mudanças
- Integrado com `apply_fase7_refactor.py`
- Auto-incremento de versão em cada modificação
- Atualização automática de `config/settings.py`
- Documentação de cada passo da refatoração

---

## [3.4.2.4] - 2026-03-07 08:00:00

### Versão stable com FASE 2 e FASE 3 aplicadas

**Mudanças:**
- FASE 2: DisplayController aplicado (filtros, ordenação, paginação)
- FASE 3: AnalysisController aplicado (análise IA, descrições)
- App funcional e testado
- 859 linhas de código

---

## [3.4.2.3] - 2026-03-06

### Estado anterior à refatoração Fase 7

**Mudanças:**
- Código original com 868 linhas
- Todas as funcionalidades inline no main_window.py

---
