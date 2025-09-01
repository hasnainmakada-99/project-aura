# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Project AURA
# Built to work flawlessly on first try in GitHub Actions

import os
import sys

# Get the project directory
project_dir = os.path.abspath('.')

# Data files to include - only include files that actually exist
data_files = []

# Assets directory (critical for the app)
assets_dir = os.path.join(project_dir, 'assets')
if os.path.exists(assets_dir):
    # Include each asset file individually to avoid directory creation
    asset_files = [
        'demo_sound.mp3',
        'haarcascade_frontalface_default.xml', 
        'shape_predictor_68_face_landmarks.dat',
        'toggle_off.png',
        'toggle_on.png'
    ]
    for asset_file in asset_files:
        asset_path = os.path.join(assets_dir, asset_file)
        if os.path.exists(asset_path):
            data_files.append((asset_path, os.path.join('assets', asset_file)))

# License file - check multiple possible names
license_candidates = ['LICENCE', 'LICENSE', 'License', 'license', 'LICENSE.txt', 'license.txt']
for license_file in license_candidates:
    if os.path.exists(os.path.join(project_dir, license_file)):
        data_files.append((license_file, license_file))
        print(f"Found license file: {license_file}")
        break

# README file
if os.path.exists(os.path.join(project_dir, 'README.md')):
    data_files.append(('README.md', 'README.md'))

# Requirements file
if os.path.exists(os.path.join(project_dir, 'requirements.txt')):
    data_files.append(('requirements.txt', 'requirements.txt'))

print(f"Data files to include: {data_files}")

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        # Core PyQt6 modules
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.QtNetwork',
        
        # OpenCV modules
        'cv2',
        'cv2.data',
        
        # NumPy and scientific computing
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.lib.format',
        
        # Audio libraries
        'sounddevice',
        'pycaw',
        'pycaw.pycaw',
        'comtypes',
        'comtypes.client',
        'psutil',
        
        # Project modules
        'app_logic',
        'ui_main_window',
        'emotion_detection',
        'emotion_action_system',
        'audio_device_manager',
        'safe_gaming_enhancer',
        'game_audio_analyzer',
        
        # System modules
        'threading',
        'queue',
        'time',
        'datetime',
        'json',
        'os',
        'sys',
        'logging',
        'traceback',
        
        # Windows specific
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'pythoncom',
        'pywintypes',
        
        # Machine learning
        'dlib',
        'scipy',
        'scipy.spatial',
        'scipy.spatial.distance',
        
        # Additional utilities
        'pkg_resources',
        'pkg_resources.extern',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
        'unittest.mock'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Only exclude truly unnecessary modules
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'pydoc'
    ],
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
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
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