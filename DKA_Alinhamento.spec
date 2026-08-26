# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Mapeamento de pastas do projeto para inclusão no bundle
datas = [
    ('app', 'app'),
    ('database', 'database'),
]

# Incluir arquivo de banco de dados se existir no diretório raiz
if os.path.exists('dka_ferramentas.db'):
    datas.append(('dka_ferramentas.db', '.'))

# Coletar submódulos e dados necessários
hiddenimports = [
    'sqlite3',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'reportlab',
    'reportlab.lib',
    'reportlab.platypus',
    'reportlab.pdfgen.canvas',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'app.services.sensor_service',
]

try:
    import sqlcipher3
    hiddenimports.extend(['sqlcipher3', 'sqlcipher3.dbapi2'])
except ImportError:
    pass

a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DKA_Alinhamento',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='DKA_Alinhamento.app',
        icon=None,
        bundle_identifier='com.dka.alinhamento',
    )
