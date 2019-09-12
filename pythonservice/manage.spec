# -*- mode: python -*-

block_cipher = None


a = Analysis(['manage.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=['rest_framework.apps', 'rest_framework.authentication', 'rest_framework.permissions',
                            'rest_framework.parsers', 'rest_framework.negotiation',
                            'rest_framework.metadata', 'rest_framework.urls'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt5', 'PyQt5-sip', 'Pillow'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='python_service',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='python_service')
