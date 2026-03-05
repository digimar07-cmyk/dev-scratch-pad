# ✅ CHECKLIST: LAYOUT v740 vs v3.0 FIXED

## 🎯 OBJETIVO
Verificar se o layout da v3.0 FIXED está **100% idêntico** ao v740.

---

## 🎨 HEADER (topo preto 70px)

### v740 (REFERÊNCIA)
- [ ] Logo "LASERFLIX" vermelho (#E50914) + versão cinza à esquerda
- [ ] Botões navegação: 🏠 Home | ⭐ Favoritos | ✓ Já Feitos | 👍 Bons | 👎 Ruins
- [ ] Busca (🔍) à DIREITA com campo de texto
- [ ] Botões à direita: ⚙️ Menu | ➕ Pastas | 🤖 Analisar
- [ ] Menu dropdown com: Dashboard, Edição em Lote, Config IA, Exportar/Importar, Backup
- [ ] Menu Analisar com: Novos | Reanalisar | Filtro Atual | Categoria | Descrições

### v3.0 ORIGINAL (QUEBRADO)
- [x] ~~Logo à esquerda~~ ✅
- [x] ~~Botões DENTRO do header (não como navegação)~~ ❌
- [x] ~~Busca CENTRALIZADA~~ ❌
- [x] ~~SEM menus dropdown~~ ❌

### v3.0 FIXED (CORRIGIDO)
- [ ] Logo + versão à esquerda
- [ ] Botões navegação centralizados (hover muda cor para vermelho)
- [ ] Busca à direita com ícone 🔍
- [ ] 3 botões à direita: Menu (verde) | Pastas (vermelho) | Analisar (verde)
- [ ] Menus dropdown completos e funcionais

---

## 📋 SIDEBAR (250px fixa à esquerda)

### v740 (REFERÊNCIA)
- [ ] Fundo #1A1A1A
- [ ] Canvas scrollable
- [ ] Seção "🌐 Origem" com botões coloridos:
  - Creative Fabrica: #FF6B35 (laranja)
  - Etsy: #F7931E (amarelo)
  - Diversos: #4ECDC4 (ciano)
- [ ] Seção "📂 Categorias" (top 8 + "Ver mais")
- [ ] Seção "🏷️ Tags Populares" (top 20)
- [ ] Separadores cinza (#333333) entre seções
- [ ] Hover muda fundo para #2A2A2A
- [ ] Botão ativo fica vermelho (#E50914)

### v3.0 ORIGINAL (QUEBRADO)
- [x] ~~Sidebar DIREITA (não esquerda)~~ ❌
- [x] ~~Scroll MAL configurado~~ ❌
- [x] ~~Cores ERRADAS~~ ❌

### v3.0 FIXED (CORRIGIDO)
- [ ] Sidebar ESQUERDA, 250px fixo
- [ ] Scroll correto (mouse wheel funciona)
- [ ] Origens com cores EXATAS do v740
- [ ] Categorias limitadas a top 8 + botão "Ver mais"
- [ ] Tags limitadas a top 20
- [ ] Separadores visuais entre seções

---

## 🎴 CARDS (220x420px)

### v740 (REFERÊNCIA)
- [ ] Dimensões: 220px largura x 420px altura
- [ ] Fundo #2A2A2A
- [ ] Cover image 220x200px (fundo #1A1A1A)
- [ ] Nome do projeto (máx 30 chars, bold)
- [ ] Até 3 badges de categoria (cores: #FF6B6B, #4ECDC4, #95E1D3)
- [ ] Até 3 tags (fundo #3A3A3A, hover vermelho)
- [ ] Badge origem colorido
- [ ] 6 botões de ação:
  1. 📂 Abrir pasta (amarelo #FFD700)
  2. ⭐/☆ Favorito (toggle)
  3. ✓/○ Feito (toggle verde)
  4. 👍 Bom (toggle verde)
  5. 👎 Ruim (toggle vermelho)
  6. 🤖 Analisar (verde #1DB954, só se não analisado)

### v3.0 ORIGINAL (QUEBRADO)
- [x] ~~Cards SIMPLIFICADOS~~ ❌
- [x] ~~SEM botões de ação~~ ❌
- [x] ~~Layout DIFERENTE~~ ❌

### v3.0 FIXED (CORRIGIDO)
- [ ] Dimensões EXATAS 220x420px
- [ ] Cover clicável (abre modal)
- [ ] Badges de categoria clicáveis (filtram)
- [ ] Tags clicáveis (filtram)
- [ ] Origem clicável (filtra)
- [ ] TODOS os 6 botões funcionais
- [ ] Cores e espaçamentos idênticos

---

## 👍 GRID DE PROJETOS

### v740 (REFERÊNCIA)
- [ ] 5 colunas
- [ ] Espaçamento: 10px entre cards
- [ ] Título mostra filtro atual (ex: "Todos os Projetos — 🌐 Etsy")
- [ ] Contador de projetos abaixo do título
- [ ] Fundo #141414

### v3.0 ORIGINAL (QUEBRADO)
- [x] ~~Grid MAL alinhado~~ ❌

### v3.0 FIXED (CORRIGIDO)
- [ ] Grid 5 colunas perfeito
- [ ] Título dinâmico reflete filtros ativos
- [ ] Scroll suave

---

## 👀 MODAL (ainda não implementado)

### v740 (REFERÊNCIA)
- [ ] 2 colunas:
  - Esquerda: Galeria de imagens (scrollable)
  - Direita: Nome, categorias, tags, origem, descrição IA
- [ ] Botões de ação no rodapé
- [ ] Fechar com ESC ou X

### v3.0 FIXED (TODO)
- [ ] Implementar modal completo

---

## 🚦 STATUS BAR (rodapé)

### v740 (REFERÊNCIA)
- [ ] Fundo preto #000000
- [ ] Altura 50px
- [ ] Label de status à esquerda
- [ ] Progress bar verde (#1DB954) ao centro (só durante análise)
- [ ] Botão "Parar Análise" vermelho à direita (só durante análise)

### v3.0 FIXED
- [ ] Implementado
- [ ] Progress bar configurada (clam theme)
- [ ] Botão stop funcional

---

## ⚙️ FUNCIONALIDADES CORE

### Filtros
- [ ] Filtro rápido (Home, Favoritos, Feitos, Bons, Ruins)
- [ ] Filtro por origem (sidebar)
- [ ] Filtro por categoria (sidebar + badges nos cards)
- [ ] Filtro por tag (sidebar + tags nos cards)
- [ ] Busca textual (header)
- [ ] Múltiplos filtros combinados
- [ ] Botão ativo destacado em vermelho

### Toggles
- [ ] ⭐ Favorito (persiste no banco)
- [ ] ✓ Feito (persiste no banco)
- [ ] 👍 Bom (persiste, cancela Ruim)
- [ ] 👎 Ruim (persiste, cancela Bom)
- [ ] Atualização instantânea do ícone

### Navegação
- [ ] 📂 Abrir pasta no explorador (Windows/Mac/Linux)
- [ ] Click no card abre modal
- [ ] Click em categoria/tag/origem filtra
- [ ] Scroll com mouse wheel (content + sidebar)

---

## 🎨 CORES (paleta Netflix)

```python
CORES_V740 = {
    "bg_primary":   "#141414",  # fundo geral
    "bg_secondary": "#1A1A1A",  # sidebar
    "bg_header":    "#000000",  # header
    "bg_card":      "#2A2A2A",  # cards
    "fg_primary":   "#FFFFFF",  # texto principal
    "fg_secondary": "#CCCCCC",  # texto secundário
    "fg_tertiary":  "#999999",  # texto desabilitado
    "accent":       "#E50914",  # vermelho Netflix
    "success":      "#1DB954",  # verde (Spotify)
    "warning":      "#FFD700",  # amarelo
}
```

- [ ] Cores EXATAS replicadas

---

## 📦 COMO TESTAR

1. **Backup v740**:
   ```bash
   cp laserflix_v740_Ofline_Stable.py laserflix_v740_BACKUP.py
   ```

2. **Rodar v740** (lado a lado):
   ```bash
   python laserflix_v740_Ofline_Stable.py
   ```

3. **Rodar v3.0 FIXED**:
   ```bash
   cd laserflix_v3.0
   python main.py
   ```

4. **Comparar visualmente**:
   - Abra as duas janelas lado a lado
   - Adicione as mesmas pastas
   - Compare cada elemento desta checklist

5. **Testar funcionalidades**:
   - Clique em cada botão
   - Teste todos os filtros
   - Verifique toggles
   - Scroll em todas as áreas

---

## ⚠️ DIFERENÇAS ESPERADAS (OK)

Estas diferenças são INTENCIONAIS (estrutura modular):

- ✅ Código organizado em módulos (ui/, core/, ai/, utils/)
- ✅ DatabaseManager separado
- ✅ ThumbnailCache modularizado
- ✅ OllamaClient isolado

Mas o VISUAL deve ser **100% idêntico**.

---

## 🐛 PROBLEMAS CONHECIDOS (A CORRIGIR)

- [ ] Modal não implementado (placeholder)
- [ ] Dashboard não implementado (placeholder)
- [ ] Edição em lote não implementada (placeholder)
- [ ] Análise IA ainda usa placeholders

---

## ✅ CONCLUSÃO

Após preencher TODOS os checkboxes acima, você terá:

✅ Layout 100% fiel ao v740  
✅ Estrutura modular (fácil de manter)  
✅ Base sólida para próximas features  

**Próximos passos**: Implementar modal, dashboard e análise IA.
