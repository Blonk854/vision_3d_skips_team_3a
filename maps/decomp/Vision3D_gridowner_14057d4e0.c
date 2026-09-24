// caller FUN_14057d4e0 @ 14057d4e0 body=504


CVitExtReportGridWnd * FUN_14057d4e0(CVitExtReportGridWnd *param_1,CWnd *param_2,undefined8 param_3)

{
  CVitExtReportGridWnd *pCVar1;
  undefined8 *puVar2;
  undefined8 *puVar3;
  undefined8 uVar4;
  CVitExtReportGridWnd *pCVar5;
  undefined8 *local_40;
  
  CVitExtReportGridWnd::CVitExtReportGridWnd(param_1,param_2);
  *(undefined ***)param_1 = CMacroEditorGridWnd::vftable;
  *(undefined ***)(param_1 + 0xe8) = CMacroEditorGridWnd::vftable;
  *(undefined ***)(param_1 + 0xf0) = CMacroEditorGridWnd::vftable;
  *(undefined ***)(param_1 + 0x1038) = CMacroEditorGridWnd::vftable;
  *(undefined ***)(param_1 + 0x1218) = CMacroEditorGridWnd::vftable;
  *(undefined ***)(param_1 + 0x18d0) = CMacroEditorGridWnd::vftable;
  CMacroModels::CMacroModels((CMacroModels *)(param_1 + 0x1a20));
  pCVar1 = param_1 + 0x1a40;
  *(undefined8 *)pCVar1 = 0;
  *(undefined8 *)(param_1 + 0x1a48) = 0;
  uVar4 = FUN_1404ca6d0(pCVar1,0);
  *(undefined8 *)pCVar1 = uVar4;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)(param_1 + 0x1a50));
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)(param_1 + 0x1a58));
  pCVar5 = param_1 + 0x1a68;
  *(undefined8 *)pCVar5 = 0;
  *(undefined8 *)(param_1 + 0x1a70) = 0;
  uVar4 = FUN_1404ca6d0(pCVar5,0);
  *(undefined8 *)pCVar5 = uVar4;
  pCVar5 = param_1 + 0x1a78;
  *(undefined8 *)pCVar5 = 0;
  *(undefined8 *)(param_1 + 0x1a80) = 0;
  uVar4 = FUN_140581980(pCVar5);
  *(undefined8 *)pCVar5 = uVar4;
  pCVar5 = (CVitExtReportGridWnd *)
           CMacroModels::GetListModelDisplayNames((CMacroModels *)(param_1 + 0x1a20));
  if (pCVar1 != pCVar5) {
    FUN_1404cbfa0(pCVar1);
    uVar4 = *(undefined8 *)pCVar1;
    *(undefined8 *)pCVar1 = *(undefined8 *)pCVar5;
    *(undefined8 *)pCVar5 = uVar4;
    uVar4 = *(undefined8 *)(param_1 + 0x1a48);
    *(undefined8 *)(param_1 + 0x1a48) = *(undefined8 *)(pCVar5 + 8);
    *(undefined8 *)(pCVar5 + 8) = uVar4;
  }
  puVar2 = (undefined8 *)*local_40;
  *local_40 = local_40;
  local_40[1] = local_40;
  while (puVar2 != local_40) {
    puVar3 = (undefined8 *)*puVar2;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)(puVar2 + 2));
    operator_delete(puVar2);
    puVar2 = puVar3;
  }
  operator_delete(local_40);
  CExtGridBaseWnd::EnableExpanding((CExtGridBaseWnd *)param_1,false,false,false,false,false);
  param_1[0x1a14] = (CVitExtReportGridWnd)0x0;
  *(undefined8 *)(param_1 + 0x1a60) = param_3;
  FUN_14057fc20(param_1);
  FUN_14057f9a0(param_1);
  return param_1;
}

