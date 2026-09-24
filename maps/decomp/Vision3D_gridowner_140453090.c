// caller FUN_140453090 @ 140453090 body=260


CVitExtReportGridWnd * FUN_140453090(CVitExtReportGridWnd *param_1)

{
  CVitExtReportGridWnd *pCVar1;
  undefined8 uVar2;
  
  CVitExtReportGridWnd::CVitExtReportGridWnd(param_1,(CWnd *)0x0);
  *(undefined ***)param_1 = CAnomaliesGridWnd::vftable;
  *(undefined ***)(param_1 + 0xe8) = CAnomaliesGridWnd::vftable;
  *(undefined ***)(param_1 + 0xf0) = CAnomaliesGridWnd::vftable;
  *(undefined ***)(param_1 + 0x1038) = CAnomaliesGridWnd::vftable;
  *(undefined ***)(param_1 + 0x1218) = CAnomaliesGridWnd::vftable;
  *(undefined ***)(param_1 + 0x18d0) = CAnomaliesGridWnd::vftable;
  pCVar1 = param_1 + 0x1a20;
  *(undefined8 *)pCVar1 = 0;
  *(undefined8 *)(param_1 + 0x1a28) = 0;
  uVar2 = FUN_14045cbd0(pCVar1);
  *(undefined8 *)pCVar1 = uVar2;
  pCVar1 = param_1 + 0x1a30;
  *(undefined8 *)pCVar1 = 0;
  *(undefined8 *)(param_1 + 0x1a38) = 0;
  uVar2 = FUN_14045cd50(pCVar1);
  *(undefined8 *)pCVar1 = uVar2;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)(param_1 + 0x1a40));
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)(param_1 + 0x1a48));
  CImageListErrorProfUIS::CImageListErrorProfUIS((CImageListErrorProfUIS *)(param_1 + 0x1a50));
  *(undefined4 *)(param_1 + 0x1a08) = 1;
  param_1[0x1a1c] = (CVitExtReportGridWnd)0x1;
  return param_1;
}

