# 🗂️ Importação Recursiva de Produtos - Documentação Completa

## 🎯 Visão Geral

Sistema completo de **importação em massa** de produtos do Laserflix, capaz de processar **2000+ produtos** de uma vez, com detecção inteligente e controle total sobre o processo.

### 🌟 Principais Recursos

✅ **Importação Recursiva Inteligente**
- Escaneia pastas recursivamente
- 2 modos: Puro (rígido) e Híbrido (flexível)
- Detecção automática de produtos

✅ **Controle de Duplicatas**
- ID único baseado em hash do caminho
- Previne reimportação automática
- Mostra preview antes de importar

✅ **Preparação de Pastas**
- Script para gerar `folder.jpg` automaticamente
- Converte SVG → JPG
- Redimensiona para thumbnail (500x500px)

✅ **Interface Gráfica Completa**
- Dialogs modernos com CustomTkinter
- Preview visual
- Barra de progresso
- Output em tempo real

---

## 📚 Arquitetura do Sistema

### **6 Módulos Implementados (6 Commits)**

```
📦 laserflix_v3.1/
├── utils/
│   └── recursive_scanner.py        [1/6] Core - Lógica de escaneamento
├── ui/
│   ├── import_mode_dialog.py       [2/6] Dialog de escolha de modo
│   ├── import_preview_dialog.py    [3/6] Preview de importação
│   ├── recursive_import_integration.py [4/6] Orquestrador
│   └── prepare_folders_dialog.py  [6/6] Preparador integrado
└── prepare_folders.py              [5/6] Script standalone
```

---

## 🔧 Integração no Main Window

### **Passo 1: Importar Módulos**

```python
# No início do main_window.py (ou main_window_FIXED.py)
from ui.recursive_import_integration import RecursiveImportManager
from ui.prepare_folders_dialog import add_prepare_button
```

### **Passo 2: Adicionar Botões**

```python
class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        # ... seu código existente ...
        
        # Adiciona botões no sidebar (ou onde preferir)
        self._create_import_buttons()
    
    def _create_import_buttons(self):
        """Cria botões de importação."""
        
        # Botão 1: Preparar Pastas
        btn_prepare = add_prepare_button(self, self.sidebar_frame)
        btn_prepare.pack(pady=10, padx=20, fill="x")
        
        # Botão 2: Importar Pasta Recursiva
        btn_import = ctk.CTkButton(
            self.sidebar_frame,
            text="🗂️ Importar Pasta Recursiva",
            command=self._import_recursive,
            height=40
        )
        btn_import.pack(pady=10, padx=20, fill="x")
    
    def _import_recursive(self):
        """Handler do botão de importação recursiva."""
        manager = RecursiveImportManager(
            parent=self,
            database=self.database,
            project_scanner=self.project_scanner,
            text_generator=self.text_generator,
            on_complete=self._on_import_complete
        )
        manager.start_import()
    
    def _on_import_complete(self, success: int, failed: int):
        """Callback após importação."""
        print(f"✅ Importação concluída: {success} sucesso, {failed} falhas")
        # Atualiza biblioteca
        self.refresh_library()  # ou método equivalente
```

---

## 📚 Guia de Uso

### **Cenário 1: Primeira Importação (2000 produtos)**

#### **ETAPA 1: Preparar Pastas (Recomendado)**

1. Clique em **"📦 Preparar Pastas"**
2. Selecione sua pasta base: `d:/Arquivos Laser`
3. Escolha modo: **Smart** (apenas pastas com .svg/.pdf)
4. Clique **"Executar"**
5. Aguarde o relatório:
   ```
   ✅ 153 folder.jpg gerados
   ⏭️ 1847 já tinham
   📁 475 sem imagens (ignoradas)
   ```

#### **ETAPA 2: Importar Produtos**

1. Clique em **"🗂️ Importar Pasta Recursiva"**
2. Escolha modo: **Híbrido** (mais flexível)
3. Selecione: `d:/Arquivos Laser`
4. Clique **"Escanear"**
5. Preview:
   ```
   ✅ 2000 produtos novos
   ⏭️ 0 já existem
   ⏱️ Tempo estimado: ~33 min
   ```
6. Clique **"Continuar"**
7. Aguarde conclusão
8. ✅ **Pronto!** 2000 produtos importados

---

### **Cenário 2: Adicionar Nova Categoria**

1. Organize nova categoria: `d:/Arquivos Laser/Nova Categoria/`
2. Adicione `folder.jpg` em cada produto (ou rode script preparador)
3. Clique **"Importar Pasta Recursiva"**
4. Modo: **Puro** (controle preciso)
5. Selecione: `d:/Arquivos Laser/Nova Categoria`
6. Preview:
   ```
   ✅ 50 produtos novos
   ⏭️ 0 já existem
   ```
7. Confirma e importa

---

### **Cenário 3: Reimportar Tudo (com novos produtos)**

1. Clique **"Importar Pasta Recursiva"**
2. Modo: **Híbrido**
3. Selecione: `d:/Arquivos Laser` (mesma base)
4. Preview:
   ```
   ✅ 50 produtos novos
   ⏭️ 2000 já existem (serão pulados)
   ```
5. **Apenas os 50 novos serão importados!**

---

## 🧠 Como Funciona

### **Modo Puro vs Híbrido**

| Aspecto | Modo Puro | Modo Híbrido |
|---------|-----------|----------------|
| **Detecção** | Apenas `folder.jpg` | `folder.jpg` + fallback |
| **Controle** | 🔒 Total (você decide) | 🔄 Flexível (detecta mais) |
| **Falsos Positivos** | ❌ Zero | ⚠️ Raros mas possíveis |
| **Uso Ideal** | Reimportação, controle cirúrgico | Primeira importação, exploração |

### **Detecção de Duplicatas**

Cada produto gera um **ID único** baseado no caminho:

```python
# Exemplo:
Caminho: d:/Arquivos Laser/Religiosos/Natal/Produto A
Relativo: religiosos/natal/produto a
ID: a3f2b8c9d1e4f5a6b7c8d9e0f1a2b3c4 (hash MD5)
```

- **Mesmo produto** = mesmo ID = pula
- **Produto diferente** = ID diferente = importa
- **Produto movido** = ID muda = reimporta

### **Subpastas Técnicas Ignoradas**

O sistema **NÃO** trata como produtos:
- `cdr/`, `svg/`, `jpg/`, `png/`, `pdf/`
- `imagens/`, `vetores/`, `images/`, `vectors/`
- `backup/`, `temp/`, `cache/`

---

## 🔧 Script Standalone (CLI)

### **Uso Direto no Terminal**

```bash
# Modo Smart (só pastas com .svg/.pdf)
python laserflix_v3.1/prepare_folders.py "d:/Arquivos Laser" --smart

# Modo All (todas com imagens)
python laserflix_v3.1/prepare_folders.py "d:/Arquivos Laser" --all

# Modo List (dry-run, só lista)
python laserflix_v3.1/prepare_folders.py "d:/Arquivos Laser" --list
```

### **Saída do Script**

```
🔍 Escaneando: d:/Arquivos Laser
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 Gerando folder.jpg em 153 pastas...
[████████████████████] 100% - Produto X

╔══ RELATÓRIO ══════════════════════════════════
║ 📊 ESTATÍSTICAS:
║   Total escaneado: 2500 pastas
║   ✅ Com folder.jpg: 1847
║   ⚠️  Sem folder.jpg: 653
║   📦 Podem gerar: 153
║   ✅ Gerados: 153
║   ❌ Falhas: 0
╚════════════════════════════════════════
```

---

## ❓ FAQ

### **1. O que acontece se eu importar a mesma pasta duas vezes?**

O sistema detecta automaticamente produtos já existentes pelo **ID único**. No preview, verá:
```
✅ 50 produtos novos
⏭️ 2000 já existem (serão pulados)
```

Apenas os 50 novos serão importados.

---

### **2. Posso importar subpastas específicas?**

**Sim!** Basta selecionar a subpasta:
```
Em vez de: d:/Arquivos Laser
Selecione: d:/Arquivos Laser/Religiosos/Natal
```

O sistema escaneia recursivamente a partir dali.

---

### **3. E se eu mover um produto de pasta?**

O **ID muda** (baseado no caminho), então o sistema trata como produto novo e reimporta.

---

### **4. Modo Puro ou Híbrido para primeira importação?**

**Recomendo Híbrido:**
- Pega mais produtos (folder.jpg + fallback)
- Você vê preview antes de confirmar
- Se não gostar, cancela e ajusta

**Use Puro quando:**
- Quer controle total
- Já preparou tudo com `folder.jpg`
- Reimportação de categoria específica

---

### **5. Quanto tempo demora para importar 2000 produtos?**

**Aprox. 30-40 minutos** (~1 segundo por produto):
- Escaneamento: instantâneo
- Análise (IA/fallback): ~0.5s por produto
- Salvar no DB: ~0.5s por produto

Roda em **thread separada**, então a UI não trava!

---

### **6. Preciso ter Pillow instalado?**

**Sim, para preparar pastas:**
```bash
pip install Pillow
```

**Opcional** (para converter SVG → JPG):
```bash
pip install cairosvg
```

Sem Pillow, o script preparador não funciona (mas importação sim).

---

## 🐛 Troubleshooting

### **Problema: "Nenhum produto encontrado"**

**Causas possíveis:**
1. Modo Puro + sem `folder.jpg` nas pastas
2. Pasta base errada
3. Todas subpastas são técnicas (`cdr/`, `svg/`, etc)

**Solução:**
- Use Modo Híbrido
- Rode script preparador antes
- Verifique estrutura de pastas

---

### **Problema: "Importação travou"**

**Roda em thread separada**, não deveria travar. Se travou:
1. Verifique logs: `laserflix_v3.1/logs/`
2. Pode ser erro em produto específico
3. Reinicie app e tente de novo (duplicatas serão puladas)

---

### **Problema: "Script preparador dá erro SVG"**

**Sem cairosvg**, SVG não converte. Duas opções:

1. **Instalar cairosvg:**
   ```bash
   pip install cairosvg
   ```

2. **Ignorar SVGs** (usar apenas .jpg/.png)

---

## 📊 Performance

### **Benchmarks Estimados**

| Operação | 100 Produtos | 1000 Produtos | 2000 Produtos |
|-----------|--------------|---------------|---------------|
| **Escaneamento** | < 1s | 2-3s | 5-10s |
| **Preparar (folder.jpg)** | 10-15s | 2-3 min | 4-6 min |
| **Importação** | 1-2 min | 15-20 min | 30-40 min |

### **Otimizações Futuras**

- [ ] Importação em lote (batch insert no DB)
- [ ] Cache de análises de IA
- [ ] Paralelização com multiprocessing
- [ ] Progress dialog com botão cancelar

---

## 📝 Histórico de Commits

### **Implementação em 6 Etapas**

| # | Commit | Arquivo | Descrição |
|---|--------|---------|-------------|
| 1 | `905e583` | `recursive_scanner.py` | Core - Lógica de escaneamento |
| 2 | `44f35d2` | `import_mode_dialog.py` | Dialog de escolha de modo |
| 3 | `7757691` | `import_preview_dialog.py` | Preview de importação |
| 4 | `34e041c` | `recursive_import_integration.py` | Orquestrador completo |
| 5 | `5880825` | `prepare_folders.py` | Script CLI standalone |
| 6 | `e28c626` | `prepare_folders_dialog.py` | Preparador integrado |

### **Proteção da Estrutura de IA**

- Commit `639eb7d`: `AI_STRUCTURE_LOCK.md` criado
- Versão v741 protegida e documentada
- Sistema de categorias (12 max) preservado

---

## 🔗 Dependências

### **Obrigatórias**
```bash
pip install customtkinter
```

### **Para Preparar Pastas**
```bash
pip install Pillow
```

### **Opcional (conversão SVG)**
```bash
pip install cairosvg
```

---

## 📞 Suporte

**Logs:** `laserflix_v3.1/logs/app.log`

**Documentação de Proteção:** [`AI_STRUCTURE_LOCK.md`](./ai/AI_STRUCTURE_LOCK.md)

**Issues:** Abra issue no repositório com:
- Descrição do problema
- Logs relevantes
- Passos para reproduzir

---

## ✅ Checklist de Integração

- [ ] Importar módulos no `main_window.py`
- [ ] Adicionar botão "Preparar Pastas"
- [ ] Adicionar botão "Importar Pasta Recursiva"
- [ ] Testar com pasta pequena (10-20 produtos)
- [ ] Testar modo Puro
- [ ] Testar modo Híbrido
- [ ] Testar reimportação (duplicatas)
- [ ] Verificar refresh da biblioteca após importar
- [ ] Testar script preparador
- [ ] Importação em massa (2000 produtos)

---

## 🎉 Conclusão

Sistema completo e robusto para importação em massa de produtos, com:

✅ 6 módulos integrados  
✅ Interface gráfica moderna  
✅ Controle total sobre importação  
✅ Proteção contra duplicatas  
✅ Script auxiliar para preparação  
✅ Documentação completa  

**Pronto para processar 2000+ produtos com facilidade!** 🚀

---

**Data de Criação:** 02/03/2026  
**Versão:** 1.0  
**Autor:** Sistema Laserflix v3.1
