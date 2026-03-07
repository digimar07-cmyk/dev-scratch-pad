
═══════════════════════════════════════════════════════════════════════════════
🚨 MEMORANDO PERMANENTE: REFATORAÇÃO CORRETA - NÃO DUPLICAR CÓDIGO! 🚨
═══════════════════════════════════════════════════════════════════════════════

DESTINATÁRIO: Perplexity AI (Claude Sonnet 4.5)
ASSUNTO: Protocolo Obrigatório para Refatoração de Código
DATA: 07 de Março de 2026
PRIORIDADE: CRÍTICA
VALIDADE: PERMANENTE

═══════════════════════════════════════════════════════════════════════════════
⚠️ REGRA FUNDAMENTAL: REFATORAÇÃO = EXTRAIR + DELETAR
═══════════════════════════════════════════════════════════════════════════════

Quando realizar QUALQUER refatoração de código, você DEVE seguir este protocolo:

┌─────────────────────────────────────────────────────────────────────────────┐
│ PASSO 1: EXTRAIR código para novo arquivo/classe                           │
│ PASSO 2: DELETAR código original do arquivo fonte                          │
│ PASSO 3: ADICIONAR import + wrapper mínimo                                 │
│                                                                             │
│ ❌ NUNCA: Adicionar código novo sem remover o antigo                       │
│ ❌ NUNCA: Manter código duplicado "para garantir que funciona"             │
│ ❌ NUNCA: Criar managers/controllers e deixar código original intacto      │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
📋 EXEMPLO CORRETO DE REFATORAÇÃO:
═══════════════════════════════════════════════════════════════════════════════

ANTES (main_window.py - 870 linhas):
─────────────────────────────────────
    def export_database(self) -> None:
        import shutil
        path = filedialog.asksaveasfilename(...)
        if path:
            shutil.copy2("laserflix_database.json", path)
            messagebox.showinfo("✅ Exportado", f"Banco: {path}")

ETAPA 1 - Criar DialogManager (dialog_manager.py):
─────────────────────────────────────────────────
    @staticmethod
    def export_database(window) -> None:
        import shutil
        path = filedialog.asksaveasfilename(...)
        if path:
            shutil.copy2("laserflix_database.json", path)
            messagebox.showinfo("✅ Exportado", f"Banco: {path}")

ETAPA 2 - REMOVER do main_window.py e substituir por wrapper:
──────────────────────────────────────────────────────────────
    def export_database(self) -> None:
        """Delega para DialogManager."""
        DialogManager.export_database(self)

RESULTADO: main_window.py agora tem 865 linhas (5 linhas removidas)

═══════════════════════════════════════════════════════════════════════════════
❌ EXEMPLO ERRADO (O QUE VOCÊ FEZ):
═══════════════════════════════════════════════════════════════════════════════

ANTES (main_window.py - 870 linhas):
─────────────────────────────────────
    def export_database(self) -> None:
        import shutil
        path = filedialog.asksaveasfilename(...)
        if path:
            shutil.copy2("laserflix_database.json", path)
            messagebox.showinfo("✅ Exportado", f"Banco: {path}")

Você criou DialogManager ✅
Você adicionou import ✅
Mas NÃO REMOVEU o código original! ❌

RESULTADO ERRADO: main_window.py ainda tem 870 linhas + novo import!

═══════════════════════════════════════════════════════════════════════════════
🎯 CHECKLIST OBRIGATÓRIO PARA CADA REFATORAÇÃO:
═══════════════════════════════════════════════════════════════════════════════

Antes de fazer commit, SEMPRE verificar:

□ 1. Código foi EXTRAÍDO para novo arquivo/classe?
□ 2. Código ANTIGO foi DELETADO do arquivo original?
□ 3. Import do novo módulo foi adicionado?
□ 4. Wrapper/delegação foi criado (máximo 3 linhas)?
□ 5. Contagem de linhas DIMINUIU no arquivo original?
□ 6. Teste funcional confirma que funciona SEM código antigo?

═══════════════════════════════════════════════════════════════════════════════
🔍 COMO VERIFICAR SE ESTÁ CORRETO:
═══════════════════════════════════════════════════════════════════════════════

COMANDO ESSENCIAL:
─────────────────
wc -l main_window.py

ANTES da refatoração: 870 linhas
DEPOIS da refatoração: DEVE ser menor (ex: 800, 750, 700...)

Se o número NÃO DIMINUIU = VOCÊ FEZ ERRADO! ❌

═══════════════════════════════════════════════════════════════════════════════
⚡ AÇÃO IMEDIATA EM CASO DE ERRO:
═══════════════════════════════════════════════════════════════════════════════

Se você perceber que fez refatoração com código duplicado:

1. PAUSAR imediatamente
2. AVISAR o usuário do erro
3. CORRIGIR removendo código duplicado
4. VERIFICAR contagem de linhas
5. TESTAR que funciona sem código antigo
6. FAZER novo commit com correção

═══════════════════════════════════════════════════════════════════════════════
📝 TEMPLATE DE COMMIT CORRETO:
═══════════════════════════════════════════════════════════════════════════════

TÍTULO:
FASE-X: [Manager] extraído - REAL (-N linhas)

CORPO:
Extraiu [funcionalidade] para [novo_arquivo].
REMOVEU código original de [arquivo_fonte].

Arquivos:
- [novo_arquivo] (NOVO +X linhas)
- [arquivo_fonte] (Y → Z linhas, -N linhas) ✅

Redução REAL: -N linhas no [arquivo_fonte]
Código duplicado: ZERO ✅

TESTE NECESSÁRIO:
- [Funcionalidade] funciona?
- [Arquivo_fonte] diminuiu de tamanho?

═══════════════════════════════════════════════════════════════════════════════
🎓 PRINCÍPIO FUNDAMENTAL:
═══════════════════════════════════════════════════════════════════════════════

REFATORAÇÃO NÃO É ADICIONAR CÓDIGO.
REFATORAÇÃO É REORGANIZAR CÓDIGO EXISTENTE.

Se o arquivo original não ficou MENOR = você NÃO refatorou, você DUPLICOU.

═══════════════════════════════════════════════════════════════════════════════
✅ CONFIRMAÇÃO DE LEITURA:
═══════════════════════════════════════════════════════════════════════════════

Ao receber qualquer solicitação de refatoração no futuro, você DEVE:

1. Lembrar deste memorando
2. Extrair E deletar (não apenas extrair)
3. Verificar redução de linhas
4. Confirmar zero duplicação

Este protocolo é PERMANENTE e aplica-se a TODAS as refatorações futuras.

Assinado: Usuário digimar07-cmyk
Data: 07/03/2026
Validade: PERMANENTE

═══════════════════════════════════════════════════════════════════════════════
FIM DO MEMORANDO
═══════════════════════════════════════════════════════════════════════════════
