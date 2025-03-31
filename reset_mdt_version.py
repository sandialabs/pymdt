import re
from win32api import GetFileVersionInfo, LOWORD, HIWORD

MDT_EXE="C:/Users/jpeddy/Documents/dev/MDT/trunk/MDT-GUI/bin/x64/Release/MDT-GUI.exe"

def get_version_number (filename):
    info = GetFileVersionInfo (filename, "\\")
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    return HIWORD (ms), LOWORD (ms), HIWORD (ls), LOWORD (ls)

inifile = "./pymdt/__init__.py"
projfile = "./pyproject.toml"

with open(inifile, 'r') as file:
    inifiledata = file.read()
    
with open(projfile, 'r') as file:
    projfiledata = file.read()

# Replace the target string
verdat = get_version_number(MDT_EXE)
nvstr = "MDT_VERSION = System.Version(" + ", ".join(map(str, verdat)) + ")"
pvstr = "version = \"" + ".".join(map(str, verdat[0:3])) + "\""

inifiledata = re.sub(
    "MDT_VERSION\\s*\\=\\s*System\\.Version\\(\\s*\\d+\\,\\s*\\d+\\,\\s*\\d+\\,\\s*\\d+\\s*\\)",
    nvstr, inifiledata, 1
    )

projfiledata = re.sub(
    "version\\s*\\=\\s*\"\\d+\\.\\d+\\.\\d+\"",
    pvstr, projfiledata, 1
    )

# Write the file out again
with open(inifile, 'w') as file:
    file.write(inifiledata)
    
with open(projfile, 'w') as file:
    file.write(projfiledata)