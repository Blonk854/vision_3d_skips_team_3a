from pathlib import Path

try:
    import win32api  # type: ignore
except Exception:
    win32api = None

root = Path(r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\v3d_files_")
for name in ("DyTools0.dll", "ProfUISm.dll", "Vision3D.exe", "AvVTraitLib.dll", "StructSupport.dll"):
    p = root / name
    if not p.exists():
        print(name, "MISSING")
        continue
    if win32api:
        info = win32api.GetFileVersionInfo(str(p), "\\")
        ms = info["FileVersionMS"]
        ls = info["FileVersionLS"]
        fv = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        print(name, "FileVersion", fv)
    else:
        # Fallback via ctypes
        import ctypes
        from ctypes import wintypes

        GetFileVersionInfoSizeW = ctypes.windll.version.GetFileVersionInfoSizeW
        GetFileVersionInfoW = ctypes.windll.version.GetFileVersionInfoW
        VerQueryValueW = ctypes.windll.version.VerQueryValueW
        size = GetFileVersionInfoSizeW(str(p), None)
        if not size:
            print(name, "no version resource")
            continue
        buf = ctypes.create_string_buffer(size)
        GetFileVersionInfoW(str(p), 0, size, buf)
        ptr = ctypes.c_void_p()
        length = wintypes.UINT()
        if VerQueryValueW(buf, "\\", ctypes.byref(ptr), ctypes.byref(length)):
            class VS_FIXEDFILEINFO(ctypes.Structure):
                _fields_ = [
                    ("dwSignature", wintypes.DWORD),
                    ("dwStrucVersion", wintypes.DWORD),
                    ("dwFileVersionMS", wintypes.DWORD),
                    ("dwFileVersionLS", wintypes.DWORD),
                    ("dwProductVersionMS", wintypes.DWORD),
                    ("dwProductVersionLS", wintypes.DWORD),
                    ("dwFileFlagsMask", wintypes.DWORD),
                    ("dwFileFlags", wintypes.DWORD),
                    ("dwFileOS", wintypes.DWORD),
                    ("dwFileType", wintypes.DWORD),
                    ("dwFileSubtype", wintypes.DWORD),
                    ("dwFileDateMS", wintypes.DWORD),
                    ("dwFileDateLS", wintypes.DWORD),
                ]

            fi = ctypes.cast(ptr, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
            def v(ms, ls):
                return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
            print(name, "File", v(fi.dwFileVersionMS, fi.dwFileVersionLS), "Product", v(fi.dwProductVersionMS, fi.dwProductVersionLS))
