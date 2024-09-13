# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ERTC.py'],
    pathex=[],
    binaries=[],
	datas=[
		('ERTC_Database.db', '.'),
		('typeProduit.db', '.'),
		('Export_Excel', 'Export_Excel'),
	],
	hiddenimports=[
        'babel.numbers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
	onefile=True,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ERTC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
