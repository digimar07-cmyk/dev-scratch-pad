#!/bin/bash
# Script para mover documentação obsoleta para archive
# Execute este script na pasta laserflix_v3.4.2.6_Stable

echo "🧹 Limpando documentação obsoleta..."
echo ""

# Criar pasta archive se não existir
mkdir -p docs/archive

# Mover arquivos para archive
echo "Movendo arquivos..."
git mv ARCHITECTURAL_REFACTORING_PLAN.md docs/archive/
git mv PLANO_EXPANDIDO_7C_7F.md docs/archive/
git mv FASE_7_ANALISE_COMPLETA.md docs/archive/
git mv MEMORANDO_REFATORACAO_PERMANENTE.md docs/archive/
git mv WHY_REFACTORING.md docs/archive/
git mv AUDIT_REPORT.md docs/archive/
git mv CONSOLIDATED_AUDIT.md docs/archive/
git mv TECHNICAL_ASSESSMENT.md docs/archive/
git mv IMPLEMENTATION_SUMMARY.md docs/archive/
git mv LAYOUT_CHECKLIST.md docs/archive/
git mv LAYOUT_COMPARISON.md docs/archive/
git mv MIGRATION_GUIDE.md docs/archive/

echo ""
echo "✅ Arquivos movidos!"
echo ""
echo "Execute: git commit -m 'docs: move obsolete documentation to archive'"
echo "Depois: git push origin main"
