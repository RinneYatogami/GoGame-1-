# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['startgame.py'],
    pathex=[],
    binaries=[],
    datas=[('Re2.wav', 'game'), ('startwindow.jpg', 'game'), ('Re.wav', 'game'), ('..\\\\lang\\\\language.json', 'lang'), ('icongame.ico', 'game')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='startgame',
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
    icon=['icongame.ico'],
)
