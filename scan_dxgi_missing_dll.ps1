$repoRoot = "g:\dad fucken around\tetris again"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$binPath = Join-Path $repoRoot "vcpkg\installed\x64-windows\bin"

if (-not (Test-Path $venvPython)) {
    throw "Venv python not found at $venvPython"
}

$env:PATH = "$binPath;$env:PATH"

$pythonCode = @"
import os
import sys
import ctypes
import traceback

repo_root = r'''$repoRoot'''
agents_dir = os.path.join(repo_root, "src", "agents")

def parse_imports(module_path):
    import struct

    with open(module_path, 'rb') as f:
        data = f.read()

    if data[:2] != b"MZ":
        raise RuntimeError("Not a PE file")

    pe_offset = struct.unpack_from('<I', data, 0x3C)[0]
    if data[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise RuntimeError("Missing PE signature")

    file_header_offset = pe_offset + 4
    _, number_of_sections, _, _, _, size_of_optional_header, _ = struct.unpack_from('<HHIIIHH', data, file_header_offset)
    optional_header_offset = file_header_offset + 20

    magic = struct.unpack_from('<H', data, optional_header_offset)[0]
    if magic == 0x10B:
        standard_size = 28
        windows_size = 68
    elif magic == 0x20B:
        standard_size = 24
        windows_size = 88
    else:
        raise RuntimeError(f"Unexpected optional header magic: {hex(magic)}")

    data_directories_offset = optional_header_offset + standard_size + windows_size
    import_dir_index = 1  # second entry
    import_rva, import_size = struct.unpack_from('<II', data, data_directories_offset + import_dir_index * 8)

    sections_offset = optional_header_offset + size_of_optional_header
    sections = []
    for i in range(number_of_sections):
        sec_offset = sections_offset + i * 40
        name = data[sec_offset:sec_offset + 8].split(b'\x00', 1)[0].decode('ascii', errors='ignore')
        virtual_size, virtual_address, size_of_raw_data, pointer_to_raw_data = struct.unpack_from('<IIII', data, sec_offset + 8)
        sections.append({
            'name': name,
            'virtual_address': virtual_address,
            'virtual_size': virtual_size,
            'size_of_raw': size_of_raw_data,
            'pointer_to_raw': pointer_to_raw_data,
        })

    def rva_to_offset(rva):
        for sec in sections:
            start = sec['virtual_address']
            size = max(sec['virtual_size'], sec['size_of_raw'])
            if start <= rva < start + size:
                return sec['pointer_to_raw'] + (rva - start)
        return None

    if import_rva == 0:
        return []

    import_offset = rva_to_offset(import_rva)
    if import_offset is None:
        raise RuntimeError("Unable to map import table RVA")

    imports = []
    while True:
        orig_first, time_stamp, forward_chain, name_rva, first_thunk = struct.unpack_from('<IIIII', data, import_offset)
        if orig_first == 0 and name_rva == 0 and first_thunk == 0:
            break
        name_offset = rva_to_offset(name_rva)
        if name_offset is None:
            break
        dll_name = []
        idx = name_offset
        while data[idx] != 0:
            dll_name.append(data[idx])
            idx += 1
        imports.append(bytes(dll_name).decode('ascii', errors='ignore'))
        import_offset += 20
    return imports

def find_pyd():
    for entry in sorted(os.listdir(agents_dir)):
        if entry.startswith("dxgi_capture") and entry.endswith(".pyd"):
            return os.path.join(agents_dir, entry)
    return None

def missing_dlls(module_path):
    LOAD_LIBRARY_AS_DATAFILE = 0x00000008  # Per instructions
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.LoadLibraryExW(module_path, None, LOAD_LIBRARY_AS_DATAFILE)
    if not handle:
        print("[warn] Could not open module for inspection:", ctypes.WinError())
        return

    try:
        buf = ctypes.create_unicode_buffer(32768)
        copied = kernel32.GetModuleFileNameW(handle, buf, len(buf))
        if copied:
            print("[ok] Module opened as datafile:", buf.value)
        else:
            print("[warn] GetModuleFileNameW failed:", ctypes.WinError())
    finally:
        kernel32.FreeLibrary(handle)

    print("[info] Rely on the ImportError above for the missing DLL name; extend this helper to enumerate dependencies if needed.")

pyd_path = find_pyd()
if not pyd_path:
    print("[error] No dxgi_capture*.pyd found under", agents_dir)
    sys.exit(1)

print("[info] dxgi_capture module path:", pyd_path)

try:
    sys.path.insert(0, agents_dir)
    import dxgi_capture
    print("[ok] dxgi_capture imported successfully – no missing DLLs")
except Exception as exc:
    print("[error] ImportError:", exc)
    print(traceback.format_exc())
    try:
        deps = parse_imports(pyd_path)
    except Exception as pe_err:
        print("[warn] Could not parse import table:", pe_err)
        deps = []

    if deps:
        print("[info] Declared dependencies:")
        for dep in deps:
            print("   -", dep)

        missing = []
        kernel32 = ctypes.windll.kernel32
        for dep in deps:
            handle = kernel32.LoadLibraryExW(dep, None, 0x00001100)  # LOAD_LIBRARY_SEARCH_DEFAULT_DIRS
            if handle:
                kernel32.FreeLibrary(handle)
            else:
                missing.append((dep, ctypes.WinError()))

        if missing:
            print("[error] Missing DLLs detected:")
            for dep, err in missing:
                print(f"   - {dep}: {err}")
        else:
            print("[ok] All declared dependencies loaded successfully")
    missing_dlls(pyd_path)
"@

$tmpPy = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "scan_dxgi_missing_dll_" + [System.IO.Path]::GetRandomFileName() + ".py")
Set-Content -Path $tmpPy -Value $pythonCode -Encoding UTF8
try {
    & $venvPython $tmpPy
}
finally {
    if (Test-Path $tmpPy) { Remove-Item $tmpPy -Force }
}
