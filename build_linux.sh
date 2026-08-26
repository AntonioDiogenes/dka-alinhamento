#!/bin/bash
# Script de Automação de Compilação do DKA Alinhamento para Linux

set -e

echo "=========================================================="
echo "  Gerador de Executável Linux (DKA Alinhamento)"
echo "=========================================================="

echo "📌 Verificando dependências (SQLAlchemy, ReportLab, PyInstaller)..."
python3 -m pip install -r requirements.txt pyinstaller

echo "🚀 Compilando o executável com PyInstaller..."
pyinstaller --noconfirm DKA_Alinhamento.spec

echo "📦 Copiando executável para ~/Downloads..."
mkdir -p ~/Downloads
cp -f dist/DKA_Alinhamento ~/Downloads/dka_alinhamento_linux_v1
chmod +x ~/Downloads/dka_alinhamento_linux_v1
cp -f dist/DKA_Alinhamento ~/Downloads/dka-tkinter_linux_v1
chmod +x ~/Downloads/dka-tkinter_linux_v1

echo "=========================================================="
echo "✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!"
echo "📍 Executável disponível em:"
echo "   ~/Downloads/dka_alinhamento_linux_v1"
echo "   ~/Downloads/dka-tkinter_linux_v1"
echo "=========================================================="
