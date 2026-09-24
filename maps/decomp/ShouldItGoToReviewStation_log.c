// ShouldItGoToReviewStation_log @ 0x140674820
// function FUN_140674820 [140674820 ..]


undefined1 FUN_140674820(longlong param_1)

{
  undefined1 uVar1;
  longlong lVar2;
  undefined *puVar3;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res10 [8];
  CLogManagerFunction local_30 [40];
  
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res10,"ShouldItGoToReviewStation");
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8,"CProdCarte");
  lVar2 = 0;
  CLogManagerFunction::CLogManagerFunction(local_30,0x10,local_res8,local_res10,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res10);
  if (*(int *)(param_1 + 0xac) == 0) {
    if (0 < *(longlong *)(param_1 + 0x1f8)) {
      do {
        if ((lVar2 < 0) || (*(longlong *)(param_1 + 0xc0) <= lVar2)) {
                    /* WARNING: Subroutine does not return */
          AfxThrowInvalidArgException();
        }
        if ((*(uint *)(*(longlong *)(param_1 + 0xb8) + lVar2 * 4) & 0xfffffeff) != 0)
        goto LAB_1406748d8;
        lVar2 = lVar2 + 1;
      } while (lVar2 < *(longlong *)(param_1 + 0x1f8));
    }
  }
  else {
LAB_1406748d8:
    *(undefined1 *)(param_1 + 0x40) = 1;
  }
  puVar3 = &DAT_140e9e944;
  if (*(char *)(param_1 + 0x40) != '\0') {
    puVar3 = &DAT_140e96018;
  }
  CLogManagerFunction::Write(local_30,2,"Send panel result to review station = \'%s\'.\n",puVar3);
  uVar1 = *(undefined1 *)(param_1 + 0x40);
  CLogManagerFunction::~CLogManagerFunction(local_30);
  return uVar1;
}

