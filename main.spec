# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['jarvix/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('jarvix/XCHATBOT/wake_word.ppn', 'XCHATBOT'),
        ('jarvix/XCHATBOT/wake_word_linux.ppn', 'XCHATBOT'),
        ('jarvix/XCHATBOT/wake_word_win.ppn', 'XCHATBOT'),
        ('jarvix/XCHATBOT/wake_word_pi.ppn', 'XCHATBOT'),
        ('/Users/sergemugisha/serge/code/jarvix/venv/lib/python3.12/site-packages/pvporcupine/resources', 'pvporcupine/resources'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,  # Avoid using a single archive to prevent high memory usage
    optimize=1,  # Apply bytecode optimizations to reduce memory footprint
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Do not include binaries here, they will be included by COLLECT
    name='Jarvix',
    debug=False,  # Enable debug to get more detailed logs to troubleshoot memory issues
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir="./temp",  # Set runtime temporary directory to avoid memory issues with extraction
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='Jarvix',  # This should be the directory name, not an existing resource
)
