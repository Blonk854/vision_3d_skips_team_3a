# Rev7 maintenance-window checklist

Controlled trial only (authorized 2026-10-18). Not production release.
Full scope: `plans/rev6_native_install_authorization.md`.

Station ID: **L3PSTAOI** (pinned 2026-10-18). Confirm single-lane on the run
sheet before copy. Set install path once at the window:

```powershell
$Repo = "C:\Users\s_sme\Documents\VS_Project_LapTop\vision_3d_skips - team 3a"
$StationId = "L3PSTAOI"
$StationExe = "C:\PATH\TO\INSTALL\Vision3D.exe"   # operator: real path on L3PSTAOI
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
```

Record on `plans/rev6_station_run_sheet.md`: operator, single-lane ☑, hashes.

## 1. Rebuild + offline verify (build host)

```powershell
cd $Repo
& $Py tools\patch_f1_missing_n_rev7.py
& $Py maps\vector_ownership\team2_progress_check.py
& $Py tools\verify_hardened_patch.py --revision rev7
```

All must PASS. Note candidate hash (must match installed hash later):

```powershell
Get-FileHash (Join-Path $Repo "Updated\Vision3D_concurrency_fix_rev7.exe") -Algorithm SHA256
```

Expected size: `28754432`. If SHA-256 ≠ prior note, write the new hash on the run sheet and use that value below.

## 2. Quiesce station

- Production stopped; no panel in flight; pending results drained.
- Single-lane confirmed.
- Vision3D process not running.

## 3. Hash stock, retain copy

```powershell
Get-FileHash $StationExe -Algorithm SHA256
Copy-Item $StationExe "$StationExe.stock_pre_rev7" -Force
Get-FileHash "$StationExe.stock_pre_rev7" -Algorithm SHA256
```

Stock hash should equal source  
`ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`  
or be recorded as an explicit baseline on the run sheet. Retain hashes of
`AvVTraitLib.dll` / `StructSupport.dll` (do not replace them).

## 4. Install candidate only

```powershell
$Cand = Join-Path $Repo "Updated\Vision3D_concurrency_fix_rev7.exe"
Copy-Item $Cand $StationExe -Force
Get-FileHash $StationExe -Algorithm SHA256
```

Installed SHA-256 must equal the candidate hash from step 1. If not: stop, restore stock (step 6), do not restart on the bad copy.

## 5. Restart + smoke

- Start Vision3D.
- Run CP-1…CP-5 and applicable F1 rows on the run sheet.
- On any stop trigger: preserve logs, go to step 6.

## 6. Rollback (process stopped)

```powershell
Stop-Process -Name Vision3D -ErrorAction SilentlyContinue   # or station stop procedure
Copy-Item "$StationExe.stock_pre_rev7" $StationExe -Force
Get-FileHash $StationExe -Algorithm SHA256   # must match retained stock
```

Confirm companion DLL hashes unchanged; restart; smoke normal + mixed-defect panels.
Record restore minutes on the run sheet.
