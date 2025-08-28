# main.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # Include assets folder
        ('README.md', '.'),    # Include README for users
        ('LICENCE', '.'),      # Include license
        ('ENHANCED_USER_GUIDE.md', '.'),  # Include user guide
    ],
    hiddenimports=[
        'pkg_resources.py2_warn', 
        'pycaw',
        'pycaw.pycaw',
        'psutil',
        'pywin32',
        'win32api',
        'win32gui',
        'win32con',
        'cv2',
        'dlib',
        'numpy',
        'numpy.testing',
        'unittest',
        'unittest.mock',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'app_logic',
        'ui_main_window',
        'camera_detector',
        'safe_gaming_enhancer'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'test', 'IPython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ProjectAURA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # This makes it a windowed app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ProjectAURA',
)