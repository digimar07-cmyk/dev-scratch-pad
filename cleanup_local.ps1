# LASERFLIX - Script de Limpeza Local
# Remove arquivos antigos que causam conflito

Write-Host "" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "LASERFLIX - Limpeza Local" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Remove pasta ui/ antiga (se existir)
if (Test-Path "ui") {
    Write-Host "[1/4] Removendo pasta ui/ antiga..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "ui" -ErrorAction SilentlyContinue
    Write-Host "      ✓ Pasta ui/ removida" -ForegroundColor Green
} else {
    Write-Host "[1/4] Pasta ui/ antiga não encontrada (OK)" -ForegroundColor Green
}

# Remove __pycache__
if (Test-Path "__pycache__") {
    Write-Host "[2/4] Limpando __pycache__..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "__pycache__" -ErrorAction SilentlyContinue
    Write-Host "      ✓ __pycache__ limpo" -ForegroundColor Green
} else {
    Write-Host "[2/4] __pycache__ não encontrado (OK)" -ForegroundColor Green
}

# Remove arquivos .pyc
Write-Host "[3/4] Removendo arquivos .pyc..." -ForegroundColor Yellow
$pycFiles = Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
if ($pycFiles) {
    $pycFiles | Remove-Item -Force
    Write-Host "      ✓ $($pycFiles.Count) arquivos .pyc removidos" -ForegroundColor Green
} else {
    Write-Host "      ✓ Nenhum arquivo .pyc encontrado" -ForegroundColor Green
}

# Limpa cache do Git
Write-Host "[4/4] Limpando cache do Git..." -ForegroundColor Yellow
git clean -fd
Write-Host "      ✓ Cache limpo" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "✓ LIMPEZA CONCLUÍDA!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. git pull origin modularizacao" -ForegroundColor White
Write-Host "2. python test_imports.py" -ForegroundColor White
Write-Host "3. python main.py" -ForegroundColor White
Write-Host ""
