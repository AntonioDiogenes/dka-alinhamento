#!/bin/bash
# Script de Automação de Compilação do DKA Alinhamento para macOS

set -e

echo "=========================================================="
echo "  Gerador de Aplicativo macOS (DKA Alinhamento)"
echo "=========================================================="

echo "📌 Verificando dependências (SQLAlchemy, ReportLab, PyInstaller)..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt pyinstaller

echo "🚀 Compilando o pacote .app com PyInstaller..."
pyinstaller --noconfirm DKA_Alinhamento.spec

echo "📦 Compactando o aplicativo para distribuição..."
cd dist
zip -r DKA_Alinhamento_macOS.zip DKA_Alinhamento.app DKA_Alinhamento 2>/dev/null || zip -r DKA_Alinhamento_macOS.zip DKA_Alinhamento
cd ..

echo "=========================================================="
echo "✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!"
echo "📍 Pacote macOS disponível em:"
echo "   dist/DKA_Alinhamento.app"
echo "   dist/DKA_Alinhamento_macOS.zip"
echo "=========================================================="
