// CAPM_SetInspectionStatus @ 0x14069b2a0
// function FUN_14069b2a0 [14069b2a0 ..]


undefined8 FUN_14069b2a0(longlong param_1)

{
  longlong *plVar1;
  undefined4 uVar2;
  int iVar3;
  uint dwMilliseconds;
  char cVar4;
  DWORD DVar5;
  longlong lVar6;
  undefined8 uVar7;
  AFX_MODULE_STATE *pAVar8;
  undefined8 uVar9;
  undefined8 *puVar10;
  ELogManagerStateLevel EVar11;
  longlong lVar12;
  char *pcVar13;
  longlong *plVar14;
  char local_res8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *local_res10;
  undefined4 local_res18 [2];
  undefined4 local_res20 [2];
  undefined8 in_stack_fffffffffffffe48;
  ulonglong uVar15;
  undefined4 local_1a8 [2];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1a0 [12];
  uint local_194;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *local_188;
  undefined8 local_180;
  CLogManagerFunctionML local_178 [48];
  undefined **local_148;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_140 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_138 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_130 [8];
  CViUnitAngle local_128 [40];
  undefined8 local_100;
  undefined4 local_f8;
  CViUnitTime local_e8 [24];
  double local_d0;
  undefined8 local_c0;
  undefined **local_b8;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_b0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_a8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_a0 [8];
  CViUnitAngle local_98 [88];
  
  local_c0 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res10,
             "CProductionThread::CAPM_SetInspectionStatus");
  lVar6 = FUN_1406a15d0(param_1);
  uVar15 = CONCAT71((int7)((ulonglong)in_stack_fffffffffffffe48 >> 8),1);
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_178,0x10,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res10,
             (ulonglong)*(uint *)(lVar6 + 0x3924),true);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res10);
  ResetEvent(*(HANDLE *)(param_1 + 0x1b8));
  uVar7 = FUN_1406a15d0(param_1);
  FUN_140685620(uVar7);
  pAVar8 = AfxGetModuleState();
  uVar15 = uVar15 & 0xffffffff00000000;
  lVar6 = __RTDynamicCast(*(undefined8 *)(pAVar8 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                          &CAVisionApp::RTTI_Type_Descriptor,uVar15);
  plVar14 = (longlong *)(lVar6 + 0x1b0);
  if (lVar6 == -0x1a8) {
    plVar14 = (longlong *)0x0;
  }
  lVar6 = *plVar14;
  plVar1 = (longlong *)(param_1 + 0xe50);
  uVar7 = FUN_1406a15d0(param_1);
  (**(code **)(lVar6 + 0xb0))(plVar14,uVar7,plVar1,param_1 + 0x32);
  local_148 = ViIdentification::CIdentificationProgramResult::vftable;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_140,"");
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_138,"");
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_130,"");
  CViUnitAngle::CViUnitAngle(local_128,0.0);
  local_100 = 0;
  local_f8 = 0xffffffff;
  lVar6 = *(longlong *)(param_1 + 0xe58);
  lVar12 = *plVar1;
  if (lVar12 != lVar6) {
    do {
      if (*(int *)(lVar12 + 0x50) == 0) break;
      lVar12 = lVar12 + 0x58;
    } while (lVar12 != lVar6);
    if ((lVar12 != lVar6) && (lVar12 != 0)) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                (local_140,
                 (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                 (lVar12 + 8));
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                (local_138,
                 (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                 (lVar12 + 0x10));
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                (local_130,
                 (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                 (lVar12 + 0x18));
      CViUnitAngle::operator=(local_128,(CViUnitAngle *)(lVar12 + 0x20));
      local_100 = *(undefined8 *)(lVar12 + 0x48);
      local_f8 = *(undefined4 *)(lVar12 + 0x50);
    }
  }
  lVar6 = FUN_1406a15d0(param_1);
  uVar2 = *(undefined4 *)(lVar6 + 0x3928);
  lVar6 = *plVar14;
  lVar12 = FUN_1406a15d0(param_1);
  iVar3 = *(int *)(lVar12 + 0x5c98);
  lVar12 = FUN_1406a15d0(param_1);
  (**(code **)(lVar6 + 0x88))
            (plVar14,uVar2,*(longlong *)(lVar12 + 0x5878) + (longlong)iVar3 * 0x410,&local_148);
  lVar6 = FUN_1406a15d0(param_1);
  iVar3 = *(int *)(lVar6 + 0x5c98);
  lVar6 = FUN_1406a15d0(param_1);
  local_res8[0] = FUN_140674820(*(longlong *)(lVar6 + 0x5878) + (longlong)iVar3 * 0x410);
  local_res18[0] = 1;
  uVar7 = FUN_1406a15d0(param_1);
  FUN_1406852f0(uVar7,local_res18,local_res8);
  uVar7 = FUN_1406a15d0(param_1);
  FUN_1406855e0(uVar7,local_res18,local_res8);
  local_res20[0] = 0;
  uVar7 = FUN_1406a15d0(param_1);
  FUN_14068d730(uVar7,local_res18,local_res8,local_res20);
  local_1a8[0] = 0;
  uVar7 = FUN_1406a15d0(param_1);
  FUN_140685fd0(uVar7);
  lVar6 = FUN_1406a15d0(param_1);
  if ((*(char *)(lVar6 + 0x61e9) == '\0') || (local_res8[0] != '\x01')) {
    uVar7 = FUN_1406a15d0(param_1);
    cVar4 = FUN_140694410(uVar7);
    if ((cVar4 == '\x01') && ((local_res8[0] == '\x01' || (DAT_1411697f0 == 0)))) {
      uVar7 = FUN_1406a15d0(param_1);
      FUN_140694450(uVar7);
    }
    uVar7 = FUN_1406a15d0(param_1);
    cVar4 = FUN_140694410(uVar7);
    if ((cVar4 == '\x01') && (local_res8[0] == '\x01')) {
      lVar6 = FUN_1406a15d0(param_1);
      if (*(char *)(lVar6 + 0x3834) != '\0') goto LAB_14069baa2;
      lVar6 = *plVar14;
      uVar7 = FUN_1406a15d0(param_1);
      (**(code **)(lVar6 + 0x98))(plVar14,uVar7,0,local_res18[0],local_res8,local_1a8);
      if (*(char *)(param_1 + 0x31) == '\0') {
        (**(code **)(**(longlong **)(param_1 + 0xeb8) + 0x188))
                  (*(longlong **)(param_1 + 0xeb8),local_res8[0] == '\0',local_res20[0]);
        puVar10 = (undefined8 *)FUN_1406a1480(&local_res10,local_res20[0]);
        pcVar13 = "true";
        if (local_res8[0] != '\0') {
          pcVar13 = "false";
        }
        CLogManagerFunctionML::Write
                  (local_178,2,"GetVMC()->SetInspectionStatus(\'%s\', \'%s\') called.",pcVar13,
                   *puVar10);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res10);
      }
      uVar7 = FUN_1406a15d0(param_1);
      cVar4 = FUN_140694410(uVar7);
      if (cVar4 == '\x01') {
        local_188 = *(CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> **)
                     (param_1 + 0x1b8);
        local_180 = *(undefined8 *)(param_1 + 0x1a8);
        CLogManagerFunctionML::Write(local_178,2,"Waiting panel ejection.\n");
        DVar5 = WaitForMultipleObjects(2,&local_188,0,0xffffffff);
        if (DVar5 == 0) {
          pcVar13 = "Panel ejected.\n";
          EVar11 = 2;
        }
        else {
          if (DVar5 == 1) {
            (**(code **)(**(longlong **)(param_1 + 0xeb8) + 0x1f0))
                      (*(longlong **)(param_1 + 0xeb8),local_1a0);
            CLogManagerFunctionML::Write
                      (local_178,2,"VMC error %d event received.\n",(ulonglong)local_194);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1a0);
            goto LAB_14069b9ff;
          }
          pcVar13 = "WaitForMultipleObjects() failed.\n";
          EVar11 = 4;
        }
        CLogManagerFunctionML::Write(local_178,EVar11,pcVar13);
      }
LAB_14069b9ff:
      lVar6 = FUN_1406a15d0(param_1);
      WaitForSingleObject(*(HANDLE *)(lVar6 + 0x3890),0xffffffff);
      DVar5 = GetTickCount();
      CViUnitTime::CViUnitTime(local_e8,(double)DVar5);
      local_res10 = local_1a0;
      uVar7 = FUN_14066d8f0(local_1a0,plVar1);
      uVar9 = FUN_1406a15d0(param_1);
      FUN_14068fab0(uVar9,uVar7);
      DVar5 = GetTickCount();
      CLogManagerFunctionML::Write
                (local_178,2,"Time to prepare results: %d ms. Results sent.\n",
                 (double)DVar5 - local_d0);
    }
    else {
LAB_14069baa2:
      lVar6 = FUN_1406a15d0(param_1);
      WaitForSingleObject(*(HANDLE *)(lVar6 + 0x3890),0xffffffff);
      pAVar8 = AfxGetModuleState();
      lVar6 = __RTDynamicCast(*(undefined8 *)(pAVar8 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                              &CAVisionApp::RTTI_Type_Descriptor,uVar15 & 0xffffffff00000000);
      if ((*(int *)(lVar6 + 0x834) == 1) && (DAT_1411697f0 == 3)) {
        cVar4 = FUN_14069c6f0(param_1);
        if (cVar4 == '\0') {
          *(undefined1 *)(param_1 + 0xec4) = 1;
          local_res10 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                        CONCAT44(local_res10._4_4_,1);
          local_188 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                      ((ulonglong)local_188 & 0xffffffff00000000);
          (**(code **)(*plVar14 + 0x188))
                    (plVar14,*(undefined4 *)(param_1 + 0xec0),&local_188,&local_res10);
          *(undefined1 *)(param_1 + 0xec4) = 0;
          uVar7 = 0;
          goto LAB_14069bcd3;
        }
      }
      DVar5 = GetTickCount();
      CViUnitTime::CViUnitTime(local_e8,(double)DVar5);
      local_res10 = local_1a0;
      uVar7 = FUN_14066d8f0(local_1a0,plVar1);
      uVar9 = FUN_1406a15d0(param_1);
      FUN_14068fab0(uVar9,uVar7);
      DVar5 = GetTickCount();
      CLogManagerFunctionML::Write
                (local_178,2,"Time to prepare results: %d ms. Results sent.\n",
                 (ulonglong)(DVar5 - (int)(longlong)local_d0));
      lVar6 = *plVar14;
      uVar7 = FUN_1406a15d0(param_1);
      (**(code **)(lVar6 + 0x98))(plVar14,uVar7,1,local_res18[0],local_res8,local_1a8);
      if (*(char *)(param_1 + 0x31) == '\0') {
        if (local_res8[0] == '\x01') {
          local_res10 = local_1a0;
          uVar7 = FUN_14066d8f0(local_1a0,plVar1);
          uVar9 = FUN_1406a15d0(param_1);
          FUN_140689e80(uVar9,uVar7);
        }
        (**(code **)(**(longlong **)(param_1 + 0xeb8) + 0x188))
                  (*(longlong **)(param_1 + 0xeb8),local_res8[0] == '\0',local_res20[0]);
        puVar10 = (undefined8 *)FUN_1406a1480(&local_res10,local_res20[0]);
        pcVar13 = "true";
        if (local_res8[0] != '\0') {
          pcVar13 = "false";
        }
        CLogManagerFunctionML::Write
                  (local_178,2,"GetVMC()->SetInspectionStatus(\'%s\', \'%s\') called.",pcVar13,
                   *puVar10);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res10);
      }
    }
    CViUnitTime::_vbase_destructor_(local_e8);
  }
  else {
    uVar7 = FUN_1406a15d0(param_1);
    lVar6 = FUN_1404c01f0(uVar7,&local_b8);
    CLogManagerFunctionML::Write
              (local_178,2,"Send panel <%s> to INSIDE repair.\n",*(undefined8 *)(lVar6 + 8));
    local_b8 = ViIdentification::CIdentificationProgramResult::vftable;
    CViUnitAngle::_vbase_destructor_(local_98);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_a0);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_a8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_b0);
    lVar6 = FUN_1406a15d0(param_1);
    WaitForSingleObject(*(HANDLE *)(lVar6 + 0x3890),0xffffffff);
    DVar5 = GetTickCount();
    CViUnitTime::CViUnitTime(local_e8,(double)DVar5);
    local_188 = local_1a0;
    uVar7 = FUN_14066d8f0(local_1a0,plVar1);
    uVar9 = FUN_1406a15d0(param_1);
    FUN_14068fab0(uVar9,uVar7);
    DVar5 = GetTickCount();
    CLogManagerFunctionML::Write
              (local_178,2,"Time to prepare results: %d ms. Results sent.\n",
               (double)DVar5 - local_d0);
    lVar6 = FUN_1406a15d0(param_1);
    dwMilliseconds = *(uint *)(lVar6 + 0x61ec);
    CLogManagerFunctionML::Write
              (local_178,2,"Wait <%d> (ms) review station receive data.\n",(ulonglong)dwMilliseconds
              );
    Sleep(dwMilliseconds);
    CLogManagerFunctionML::Write(local_178,2,"Wait review station free.\n");
    uVar7 = FUN_1406a15d0(param_1);
    FUN_140694450(uVar7);
    CLogManagerFunctionML::Write(local_178,2,"Review station is now free.\n");
    local_res10 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                  ((ulonglong)local_res10 & 0xffffffffffffff00);
    uVar7 = FUN_1406a15d0(param_1);
    FUN_140692480(uVar7,&local_res10);
    local_res8[0] =
         local_res10._0_1_ == (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>)0x0;
    local_res18[0] = 2;
    pcVar13 = "Defect panel";
    if (local_res10._0_1_ != (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>)0x0) {
      pcVar13 = "Panel OK";
    }
    CLogManagerFunctionML::Write(local_178,2,"Operator sanction received <%s>.\n",pcVar13);
    lVar6 = *plVar14;
    uVar7 = FUN_1406a15d0(param_1);
    (**(code **)(lVar6 + 0x98))(plVar14,uVar7,1,local_res18[0],local_res8,local_1a8);
    CLogManagerFunctionML::Write(local_178,2,"Now we can unload the panel.\n");
    if (*(char *)(param_1 + 0x31) == '\0') {
      (**(code **)(**(longlong **)(param_1 + 0xeb8) + 0x188))
                (*(longlong **)(param_1 + 0xeb8),(ulonglong)local_res10 & 0xff,0);
      pcVar13 = "true";
      if (local_res10._0_1_ == (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>)0x0) {
        pcVar13 = "false";
      }
      CLogManagerFunctionML::Write
                (local_178,2,
                 "Repair station inside AOI mode: GetVMC()->SetInspectionStatus(\'%s\') called.\n",
                 pcVar13);
    }
    CViUnitTime::_vbase_destructor_(local_e8);
  }
  uVar7 = 1;
LAB_14069bcd3:
  local_148 = ViIdentification::CIdentificationProgramResult::vftable;
  CViUnitAngle::_vbase_destructor_(local_128);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_130);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_138);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_140);
  CLogManagerFunctionML::~CLogManagerFunctionML(local_178);
  return uVar7;
}

