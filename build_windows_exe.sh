#!/bin/bash
# Script de Automação de Compilação do DKA Alinhamento para Windows via Wine

set -e

echo "=========================================================="
echo "  Gerador de Executável Windows (DKA Alinhamento)"
echo "=========================================================="

# 1. Verificar/Instalar o Wine se necessário
if ! command -v wine &> /dev/null; then
    echo "📌 Instalação do Wine necessária. Executando sudo apt install -y wine..."
    sudo apt update && sudo apt install -y wine wine64
fi

# 2. Instalar o Python 3.10 para Windows via Wine caso ainda não esteja instalado
PYTHON_WIN="$HOME/.wine/drive_c/users/$USER/AppData/Local/Programs/Python/Python310/python.exe"

if [ ! -f "$PYTHON_WIN" ]; then
    echo "📌 Baixando o instalador do Python 3.10 para Windows..."
    wget -q https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe -O /tmp/python-3.10.11-amd64.exe
    
    echo "📌 Instalando o Python 3.10 no ambiente Wine..."
    wine /tmp/python-3.10.11-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    rm -f /tmp/python-3.10.11-amd64.exe
fi

echo "📌 Instalando dependências (SQLAlchemy, ReportLab, PyInstaller)..."
wine python -m pip install --upgrade pip
wine python -m pip install "sqlalchemy>=2.0.0" "reportlab>=4.0.0" pyinstaller
wine python -m pip install sqlcipher3-binary || true

echo "🚀 Compilando o arquivo DKA_Alinhamento.exe com o PyInstaller..."
wine pyinstaller --noconfirm DKA_Alinhamento.spec

echo "=========================================================="
echo "✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!"
echo "📍 O arquivo executável para Windows está em:"
echo "   dist/DKA_Alinhamento.exe"
echo "=========================================================="
