# Class index — product core

Generated from Ghidra named symbols + string-named production anchors.  
Raw: [`Vision3D_exe_atlas_extract.json`](Vision3D_exe_atlas_extract.json), [`AvVTraitLib_dll_atlas_extract.json`](AvVTraitLib_dll_atlas_extract.json), [`vision3d_product_index.json`](vision3d_product_index.json).

## Vision3D.exe — keep / investigate

| Class | Named methods (approx) | Mode | Notes |
| --- | --- | --- | --- |
| `CDataCaoTraitement` | 142 | production | Skip list owner; `SkipSubPanel`, `IsSkippedSubPanel`, OIS save helpers |
| `CVitExtReportGridWnd` | DYTOOLS0 (imported) | review / UI | Base report grid; posts `ID_VITREPORTGRID_CLICK_*` + `OnClick*` virtuals |
| `CAnomaliesGridWnd` / `CAnomaliesGridView` | Vision3D local | review | Failure-mode table; left-double → `FUN_14045c740` → `ExecOneComp` / FM console |
| `CExtReportGridWnd` / `CExtGridWnd` / `CExtTreeGridWnd` | PROFUISM (imported) | UI | Generic grid framework; base click is not image-open |
| `CAnomalie` / `CAnomalieProd` | 9 / 10 (IAT StructSupport) | production / review | Defect + skip cause fields |
| `CModel_Shape` / `CModelShape_Component` | 19 / 12 | library / production | Shape-side analysis entry |
| `CSkip_bloc` | 11 | production | Skip-mark block objects |

### String-named (often still `FUN_*` until renamed)

| Class / method | Evidence VA | Status |
| --- | --- | --- |
| `CZoneAnalysis::ExecuteAll_Components` | `0x1407354b0` | Renamed |
| `CZoneAnalysis::ExecuteOne_Component` | `0x1407368d0` | Renamed |
| `CProductionThread::ExecuteSkip` | `0x1406a06b0` | Renamed |
| `CProdCarte::ShouldItGoToReviewStation` | `0x140674820` | Log-string named; still `FUN_140674820` |
| `CProductionDoc::PrepareResultsAndAskComThreadToSend` | `0x14068fab0` | Builds `CMsgPanelProd`, then signals communication thread |
| `CMsgPanelProd::SendPanelToReviewStation` | `0x14067c710` | Sets inverted field at `+0x0c`; no transport |
| `CProductionCommunication::SendResults` | `0x14067c7b0` | Sends anomaly-memory `CMsgImage`s, then panel |
| `CNetworkDataManagement::Send` | `0x14064e110` | Calls imported `CTalkToSuperviseur::Send` |
| `CVitImgFileRecorderHelper::Save` | `0x1406e79c0` | Dispatches memory/OIS/OTR outputs by mask |
| `CVitImgFileRecorderHelper::SaveOIS` / `SaveOTR` | `0x1406e7d90` / `0x1406e8220` | Parallel filesystem recorders, not review transfer |
| `CProductionDoc::ReadCurrentPanelStatusFromReview` | xref `0x140692480` | Log-string named |

## AvVTraitLib.dll — keep / investigate

| Class | Named methods (approx) | Notes |
| --- | --- | --- |
| `CModelFamily` | 170 | `ImagesAnalysis` overloads |
| `CVTrait_Chip` | 132 | Presence 2D/3D |
| `CVTrait_CustomComponent` | 111 | Custom body tools |
| `CVTrait_Profile` / `Blob` / `Edge` | 98 / 87 / 72 | Other traits |
| `CModelFamilyComponent` | 82 | Per-component family |
| `CBibliotheque` | 141 | Library editor side |

Ignore for Feature 1 unless a defect path requires it: `CExt*` paint/grid classes mirrored into this DLL.

## StructSupport.dll — known anchors

From [`../version.md`](../version.md):

| Symbol | VA |
| --- | --- |
| `CAnomalie::IsOk` | `0x1800900a0` |
| `CAnomalie::RazRes` | `0x180090840` |
| `CAnomalieProd::RazRes` | `0x1800908c0` |
| `CAnomalie` vtable | `0x1801274b0` |
| `CAnomalieProd` vtable | `0x180127548` |

Import into `V3D_SKIP` before deep defect-bit work.

## Filter rules for future catalog passes

**Include:** names starting with `C` / `CV` that match production, zone, CAO, anomalie, review, OIS, trait, model family.

**Exclude by default:** `CExtPaint*`, `CExtPopup*`, `CExtControlBar*`, `ATL::`, `std::`, `boost::`, OLE/COM error strings, TPM/NDIS system strings.
