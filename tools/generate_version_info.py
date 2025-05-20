import os
import re

VERSION_PY = os.path.join(os.path.dirname(__file__), '..', 'src', 'common', 'version.py')
VERSION_TXT = os.path.join(os.path.dirname(__file__), '..', 'version_info.txt')

# Read version from src/common/version.py
with open(VERSION_PY, encoding='utf-8') as f:
    content = f.read()
match = re.search(r'__version__\s*=\s*"([0-9.]+)"', content)
if not match:
    raise RuntimeError("Could not find __version__ in version.py")
version = match.group(1)
version_tuple = tuple(map(int, version.split('.'))) + (0,) * (4 - len(version.split('.')))

# Write version_info.txt
with open(VERSION_TXT, 'w', encoding='utf-8') as f:
    f.write(f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'Samuel Vannier'),
        StringStruct('FileDescription', 'GetReadyToWork lets you launch your favorite apps in one click, with multi-language and cross-platform support.'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', 'GetReadyToWork'),
        StringStruct('OriginalFilename', 'GetReadyToWork.exe'),
        StringStruct('ProductName', 'Get Ready To Work'),
        StringStruct('ProductVersion', '{version}'),
        StringStruct('Author', 'Samuel Vannier')])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""")
print(f"version_info.txt generated with version {version}")
