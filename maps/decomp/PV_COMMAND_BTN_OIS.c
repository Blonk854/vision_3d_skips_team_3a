// PV_COMMAND_BTN_OIS @ 0x1406b0c00
// function FUN_1406b0c00 [1406b0c00 ..]


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */

undefined8 FUN_1406b0c00(CWnd *param_1,undefined8 param_2)

{
  bool bVar1;
  char cVar2;
  BOOL BVar3;
  int iVar4;
  AFX_MODULE_STATE *pAVar5;
  longlong lVar6;
  __int64 _Var7;
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *pCVar8;
  CImagesDefinitions *pCVar9;
  IVMachineController *pIVar10;
  undefined8 uVar11;
  CWinThread *pCVar12;
  longlong *plVar13;
  longlong *plVar14;
  ELogManagerStateLevel EVar15;
  char *pcVar16;
  __time64_t local_res8;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res10 [16];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res20 [8];
  CLogManagerFunctionML local_77d8 [48];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_77a8 [8];
  undefined8 local_77a0;
  CExtResDlg local_7798 [2624];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_6d58 [16];
  CImagesDefinitions local_6d48 [736];
  CDlgMaintenanceIO local_6a68 [15744];
  longlong *local_2ce8;
  undefined8 uStack_30;
  
  uStack_30 = 0x1406b0c19;
  local_77a0 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
             "CProductionView::OnProdViewCommand");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_77d8,0x10,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
             (ulonglong)*(uint *)(*(longlong *)(param_1 + 0xe8) + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_77a8);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res10);
  CWnd::SetFocus(param_1);
  pAVar5 = AfxGetModuleState();
  plVar13 = (longlong *)0x0;
  lVar6 = __RTDynamicCast(*(undefined8 *)(pAVar5 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                          &CAVisionApp::RTTI_Type_Descriptor,0);
  plVar14 = (longlong *)(lVar6 + 0x1b0);
  if (lVar6 == -0x1a8) {
    plVar14 = plVar13;
  }
  switch(param_2) {
  case 1:
    CLogManagerFunctionML::Write(local_77d8,2,"PV_COMMAND_BTN_START.\n");
    cVar2 = FUN_140680b40(*(undefined8 *)(param_1 + 0xe8));
    if (cVar2 == '\0') {
      pcVar16 = "Start production not allowed by external system.\n";
      EVar15 = 2;
    }
    else {
      if (*(char *)(*(longlong *)(param_1 + 0xe8) + 0x3880) == '\0') {
        if (param_1[0x7004] != (CWnd)0x0) {
          pAVar5 = AfxGetModuleState();
          uVar11 = __RTDynamicCast(*(undefined8 *)(pAVar5 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                                   &CAVisionApp::RTTI_Type_Descriptor,0);
          iVar4 = FUN_1404e0b60(uVar11,0);
          if (iVar4 == 0) {
            CLogManagerFunctionML::Write
                      (local_77d8,2,"Start production cancelled : wrong password.\n");
            FUN_140677ba0(param_1 + 0x9c8,1);
            break;
          }
        }
        param_1[0x7004] = (CWnd)0x0;
        *(undefined4 *)(param_1 + 0x6f10) = 0;
        if ((*(char *)(*(longlong *)(param_1 + 0xe8) + 0x61e8) != '\0') &&
           (*(char *)(*(longlong *)(param_1 + 0xe8) + 0x382d) == '\0')) {
          FUN_1405bb940(local_7798,param_1);
          _Var7 = CExtResDlg::DoModal(local_7798);
          if (_Var7 == 1) {
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                      (local_res10,
                       (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                       local_6d58);
            bVar1 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)local_res10);
            if (!bVar1) {
              uVar11 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                       CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                                 ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                                  &local_res8,
                                  (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                   *)local_res10);
              FUN_1406b3720(param_1 + 0x870,uVar11);
              FUN_140675f90(param_1 + 0x870);
              ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_6d58);
              CExtNCW<CExtResizableDialog>::~CExtNCW<CExtResizableDialog>
                        ((CExtNCW<CExtResizableDialog> *)local_7798);
              goto LAB_1406b0f35;
            }
            pcVar16 = "No lot number entered : cancel production start.\n";
          }
          else {
            pcVar16 = "Lot number input cancelled : cancel production start.\n";
          }
          CLogManagerFunctionML::Write(local_77d8,2,pcVar16);
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
          ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_6d58);
          CExtNCW<CExtResizableDialog>::~CExtNCW<CExtResizableDialog>
                    ((CExtNCW<CExtResizableDialog> *)local_7798);
          break;
        }
LAB_1406b0f35:
        bVar1 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)local_res10);
        if (bVar1) {
          local_res8 = _time64((__time64_t *)0x0);
          pCVar8 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                   FUN_140493160(&local_res8,local_res20,"%Y%m/%d %H:%M:%S");
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                    (local_res10,pCVar8);
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
          ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res20);
        }
        uVar11 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                 CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                           ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                            &local_res8,
                            (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                             *)local_res10);
        (**(code **)(*plVar14 + 0x150))
                  (plVar14,*(undefined4 *)(*(longlong *)(param_1 + 0xe8) + 0x3928),uVar11);
        cVar2 = FUN_140691c80(*(undefined8 *)(param_1 + 0xe8));
        if (cVar2 != '\0') {
          FUN_140676ff0(param_1 + 0x9c8);
          break;
        }
        pcVar16 = "GetDocument()->ProductionStart() failed.\n";
        goto LAB_1406b12fb;
      }
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res20,"");
      local_res8 = CONCAT44(local_res8._4_4_,0x1d);
      pAVar5 = AfxGetModuleState();
      lVar6 = __RTDynamicCast(*(undefined8 *)(pAVar5 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                              &CAVisionApp::RTTI_Type_Descriptor,0);
      plVar14 = (longlong *)(lVar6 + 0x1b0);
      if (lVar6 == -0x1a8) {
        plVar14 = plVar13;
      }
      (**(code **)(*plVar14 + 400))
                (plVar14,*(undefined4 *)(*(longlong *)(param_1 + 0xe8) + 0x3924),&local_res8,
                 local_res20);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res20);
      pcVar16 = "Start production not allowed TST not compatible.\n";
      EVar15 = 2;
    }
    goto LAB_1406b1300;
  case 2:
    CLogManagerFunctionML::Write(local_77d8,2,"PV_COMMAND_BTN_STOP.\n");
    cVar2 = FUN_140680ba0(*(undefined8 *)(param_1 + 0xe8));
    if (cVar2 != '\0') {
      *(undefined4 *)(param_1 + 0x6f10) = 0;
      FUN_1406b3c50(param_1);
      (**(code **)(*(longlong *)(*(longlong *)(param_1 + 0xe8) + 0x2548) + 8))();
      FUN_1406af4d0(param_1);
      break;
    }
    pcVar16 = "Stop production not allowed by external system.\n";
    EVar15 = 2;
    goto LAB_1406b1300;
  case 3:
    pCVar9 = (CImagesDefinitions *)FUN_1405567f0(&DAT_141169870,local_6d48);
    pIVar10 = (IVMachineController *)(**(code **)(**(longlong **)(param_1 + 0xe8) + 0x230))();
    bVar1 = (bool)(**(code **)(*plVar14 + 0x160))(plVar14);
    CDlgMaintenanceIO::CDlgMaintenanceIO
              (local_6a68,pIVar10,(CConsoleDisplay *)DAT_1410f5ad0,pCVar9,bVar1,param_1);
    CImagesDefinitions::_vbase_destructor_(local_6d48);
    local_2ce8 = plVar14;
    CExtResDlg::DoModal((CExtResDlg *)local_6a68);
    CDlgMaintenanceIO::~CDlgMaintenanceIO(local_6a68);
    break;
  case 4:
    CLogManagerFunctionML::Write(local_77d8,2,"PV_COMMAND_BTN_VIDEO.\n");
    BVar3 = IsWindowVisible(*(HWND *)(DAT_1410f5ad0 + 0x40));
    if (BVar3 == 1) {
      CConsoleDisplay::Hide((CConsoleDisplay *)DAT_1410f5ad0);
    }
    else {
      CConsoleDisplay::Show((CConsoleDisplay *)DAT_1410f5ad0);
    }
    BVar3 = IsIconic(*(HWND *)(DAT_1410f5ad0 + 0x40));
    if (BVar3 == 1) {
      OpenIcon(*(HWND *)(DAT_1410f5ad0 + 0x40));
    }
    break;
  case 5:
    CLogManagerFunctionML::Write(local_77d8,2,"PV_COMMAND_BTN_PASSTHROUGH.\n");
    if ((*(char *)(*(longlong *)(param_1 + 0xe8) + 0x382d) == '\0') &&
       (iVar4 = AfxMessageBox(0xd31,4,0xffffffff), iVar4 == 7)) {
      pcVar16 = "Passthrough cancelled : user cancel.\n";
LAB_1406b1198:
      CLogManagerFunctionML::Write(local_77d8,2,pcVar16);
      FUN_140677ba0(param_1 + 0x9c8,5,1);
    }
    else {
      if (*(char *)(*(longlong *)(param_1 + 0xe8) + 0x382d) == '\0') {
        pAVar5 = AfxGetModuleState();
        uVar11 = __RTDynamicCast(*(undefined8 *)(pAVar5 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                                 &CAVisionApp::RTTI_Type_Descriptor,0);
        iVar4 = FUN_1404e0b60(uVar11,1);
        if (iVar4 == 0) {
          pcVar16 = "Passthrough cancelled : wrong password.\n";
          goto LAB_1406b1198;
        }
      }
      *(undefined4 *)(param_1 + 0x6f10) = 0;
      (**(code **)(*plVar14 + 0x148))
                (plVar14,*(undefined4 *)(*(longlong *)(param_1 + 0xe8) + 0x3928));
    }
    break;
  case 6:
    CLogManagerFunctionML::Write(local_77d8,2,"PV_COMMAND_BTN_EXIT.\n");
    cVar2 = FUN_140697ce0(*(undefined8 *)(param_1 + 0xe8));
    if (cVar2 != '\0') {
      if (*(char *)(*(longlong *)(param_1 + 0xe8) + 0x382d) == '\0') {
        FUN_1406b3100(param_1);
      }
      pCVar12 = AfxGetThread();
      if (pCVar12 != (CWinThread *)0x0) {
        plVar13 = (longlong *)(**(code **)(*(longlong *)pCVar12 + 0xf8))(pCVar12);
      }
      FUN_1406319f0(plVar13,0);
      SendMessageA(*(HWND *)(param_1 + 0x40),0x111,0xe102,0);
    }
    break;
  case 7:
    CLogManagerFunctionML::Write(local_77d8,2,"PV_COMMAND_BTN_OIS.\n");
    FUN_1406ae120(param_1);
    break;
  case 8:
    CLogManagerFunctionML::Write(local_77d8,2,"PV_COMMAND_BTN_OTR.\n");
    FUN_1406ae950(param_1);
    break;
  default:
    pcVar16 = "UNKNOWN.\n";
LAB_1406b12fb:
    EVar15 = 4;
LAB_1406b1300:
    CLogManagerFunctionML::Write(local_77d8,EVar15,pcVar16);
  }
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res10);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_77a8);
  CLogManagerFunctionML::~CLogManagerFunctionML(local_77d8);
  return 0;
}

