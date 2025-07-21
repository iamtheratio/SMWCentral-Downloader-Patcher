"""
Dynamic version.txt generator for Windows executables
Generates version.txt from the centralized version in main.py
"""

from version_manager import get_version_tuple, get_version_string, get_version
import os

def generate_version_txt():
    """Generate version.txt with current version information"""
    version_tuple = get_version_tuple()
    version_string = get_version_string()
    version_full = get_version()
    
    version_content = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers={version_tuple},
    prodvers={version_tuple},
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'iamtheratio'),
        StringStruct(u'FileDescription', u'SMWCentral Downloader & Patcher'),
        StringStruct(u'FileVersion', u'{version_string}'),
        StringStruct(u'InternalName', u'SMWC Downloader'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 iamtheratio'),
        StringStruct(u'OriginalFilename', u'SMWC Downloader.exe'),
        StringStruct(u'ProductName', u'SMWCentral Downloader & Patcher'),
        StringStruct(u'ProductVersion', u'{version_string}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print(f"✅ Generated version.txt for {version_full} ({version_string})")

if __name__ == "__main__":
    generate_version_txt()
