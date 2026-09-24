// ExecuteOne_Component @ 0x1407368d0
// function ExecuteOne_Component [1407368d0 ..]


CRunContextExtraWork *
ExecuteOne_Component
          (CResult *param_1,undefined8 param_2,CDPoint *param_3,CAnomalie *param_4,
          undefined8 param_5,undefined8 param_6,undefined8 param_7)

{
  double dVar1;
  double dVar2;
  double dVar3;
  int iVar4;
  double dVar5;
  double dVar6;
  bool bVar7;
  CResult *pCVar8;
  CResult *this;
  char cVar9;
  bool bVar10;
  CAnomalie CVar11;
  int iVar12;
  int iVar13;
  ulong uVar14;
  int iVar15;
  undefined4 uVar16;
  undefined8 uVar17;
  CComposant *pCVar18;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *pCVar19;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *pCVar20;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *pCVar21;
  undefined8 uVar22;
  undefined8 uVar23;
  undefined8 uVar24;
  undefined8 uVar25;
  longlong lVar26;
  CRunContextExtraWork *pCVar27;
  CLibraryHelperExportThread *this_00;
  longlong lVar28;
  CResult *this_01;
  ushort uVar29;
  CCAD_Base *pCVar30;
  CRunContextExtraWork *pCVar31;
  undefined4 uVar32;
  CResult *local_res8;
  undefined8 local_res10;
  CDPoint *local_res18;
  ulonglong in_stack_fffffffffffff828;
  CRect *pCVar33;
  ulong local_780 [2];
  CModelFamily *local_778;
  undefined8 local_770;
  int local_768;
  ulong local_764;
  CRunContextExtraWork_ExportJointRes *local_760;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_758 [8];
  undefined8 local_750;
  CViUnitLength local_748 [8];
  undefined8 local_740;
  undefined8 uStack_738;
  undefined8 local_730;
  undefined8 uStack_728;
  undefined8 local_720;
  undefined8 uStack_718;
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> local_710 [8];
  undefined1 local_708 [8];
  undefined8 local_700;
  undefined8 local_6f8;
  CModelResult local_6f0 [32];
  CViUnitLength *local_6d0;
  CViUnitLength *local_6c8;
  CViUnitAngle *local_6c0;
  CViUnitAngle *local_6b8;
  CViUnitAngle local_6b0 [40];
  undefined8 local_688;
  undefined1 *local_680;
  CComponentPinResults local_678 [40];
  longlong local_650 [5];
  CViUnitAngle *local_628;
  CDPoint local_620 [16];
  double local_610;
  double local_608;
  CInputIdentity local_5f8 [48];
  CStringListe local_5c8 [40];
  CLogManagerFunctionML local_5a0 [48];
  undefined **local_570;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_568 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_560 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_558 [8];
  CViUnitAngle local_550 [104];
  CRunContextModelFamily local_4e8 [8];
  CRunContextModel_Component *local_4e0;
  CRunContextPads local_498 [80];
  CViUnitAngle local_448 [40];
  CViUnitAngle local_420 [40];
  CViUnitLength local_3f8 [48];
  CViUnitPoint local_3c8 [160];
  CRunContextModel_Component local_328 [752];
  
  local_688 = 0xfffffffffffffffe;
  pCVar31 = (CRunContextExtraWork *)0x0;
  iVar12 = 0;
  local_780[0] = 0;
  local_res8 = param_1;
  local_res10 = param_2;
  local_res18 = param_3;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_778,
             "CZoneAnalysis::ExecuteOne_Component");
  in_stack_fffffffffffff828 = in_stack_fffffffffffff828 & 0xffffffffffffff00;
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_5a0,0x10,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_778,
             (ulonglong)*(uint *)(*(longlong *)(param_1 + 0x10) + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_778);
  pCVar30 = (CCAD_Base *)CONCAT44(param_7._4_4_,CONCAT22(param_7._2_2_,(ushort)param_7));
  (**(code **)(*(longlong *)pCVar30 + 0x48))(pCVar30,local_710);
  uVar14 = *(ulong *)(pCVar30 + 0x14);
  local_764 = uVar14;
  CCAD_Base::_dptPos_um(pCVar30);
  dVar1 = *(double *)(pCVar30 + 0x90);
  FUN_1406492e0(*(longlong *)(param_1 + 0x10) + 0x1a58,local_650,uVar14);
  (**(code **)(local_650[0] + 0x28))(local_650,local_620,param_3);
  dVar5 = (double)FUN_14064a230(*(longlong *)(param_1 + 0x10) + 0x1a58,uVar14);
  dVar6 = ModuloAngleDg(dVar1 - dVar5);
  iVar15 = *(int *)(pCVar30 + 0x130);
  dVar5 = *(double *)(pCVar30 + 0x100);
  dVar2 = *(double *)(pCVar30 + 0x108);
  dVar3 = *(double *)(pCVar30 + 0x110);
  local_778 = (CModelFamily *)0x0;
  uVar17 = (**(code **)(*(longlong *)pCVar30 + 0x60))(pCVar30,local_780);
  cVar9 = FUN_1407378a0(param_1,uVar17,param_6,&local_778);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_780);
  if (cVar9 == '\0') {
    pCVar31 = (CRunContextExtraWork *)0x20;
    goto LAB_14073747e;
  }
  CRunContextPads::CRunContextPads(local_498);
  pCVar18 = (CComposant *)
            __RTDynamicCast(pCVar30,0,&CCAD_Base::RTTI_Type_Descriptor,
                            &CComposant::RTTI_Type_Descriptor,
                            in_stack_fffffffffffff828 & 0xffffffff00000000);
  local_780[0] = uVar14;
  CDataCaoTraitement::InitialyseRunContextPads
            (*(CDataCaoTraitement **)(param_1 + 0x10),local_498,pCVar18,local_res18,(int *)local_780
             ,false);
  pCVar19 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
            (**(code **)(*(longlong *)pCVar18 + 0x60))(pCVar18,local_758);
  pCVar20 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
            (**(code **)(*(longlong *)pCVar18 + 0x78))(pCVar18,&local_760);
  pCVar21 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
            (**(code **)(*(longlong *)pCVar18 + 0x48))(pCVar18,local_780);
  iVar4 = *(int *)(pCVar18 + 0x14);
  iVar13 = (**(code **)(*(longlong *)pCVar18 + 0x98))(pCVar18);
  CInputIdentity::CInputIdentity(local_5f8,pCVar21,iVar4,pCVar20,pCVar19,iVar13);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_780);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_760);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_758);
  local_680 = local_708;
  local_628 = local_448;
  local_6d0 = local_3f8;
  local_6c8 = local_748;
  local_6c0 = local_420;
  local_6b8 = local_6b0;
  uVar17 = (**(code **)(*(longlong *)pCVar18 + 0x78))(pCVar18,local_708);
  uVar22 = CViUnitAngle::CViUnitAngle(local_448,dVar3);
  uVar23 = CViUnitLength::CViUnitLength(local_3f8,dVar2 * DAT_140ddd0f0);
  uVar24 = CViUnitLength::CViUnitLength(local_748,dVar5 * DAT_140ddd0f0);
  local_750 = CViUnitAngle::CViUnitAngle(local_420,dVar1);
  local_770 = CViUnitAngle::CViUnitAngle(local_6b0,dVar6);
  uVar25 = CViUnitPoint::CViUnitPoint(local_3c8,local_610,local_608);
  pCVar8 = local_res8;
  pCVar30 = (CCAD_Base *)CONCAT44(param_7._4_4_,CONCAT22(param_7._2_2_,(ushort)param_7));
  if (*(int *)(pCVar30 + 0xc4) != 0) {
    iVar12 = *(int *)(pCVar30 + 0xe8);
  }
  CRunContextModel_Component::CRunContextModel_Component
            (local_328,local_res10,*(undefined8 *)local_res8,uVar25,iVar12 != 1,local_5f8,local_770,
             local_750,uVar24,uVar23,uVar22,uVar17,local_498);
  if (*(char *)(*(longlong *)(pCVar8 + 0x10) + 0x38a0) != '\0') {
    local_760 = (CRunContextExtraWork_ExportJointRes *)FUN_14076d550(0x30);
    pCVar27 = pCVar31;
    if (local_760 != (CRunContextExtraWork_ExportJointRes *)0x0) {
      local_6b8 = (CViUnitAngle *)&local_res8;
      local_6c0 = (CViUnitAngle *)&local_770;
      local_6c8 = (CViUnitLength *)&local_750;
      uVar17 = (**(code **)(*(longlong *)pCVar30 + 0x48))(pCVar30,&local_res8);
      lVar26 = FUN_1404c01f0(*(undefined8 *)(pCVar8 + 0x10),&local_570);
      local_780[0] = 1;
      uVar22 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
               CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                         ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                          &local_770,
                          (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                           *)(lVar26 + 8));
      uVar23 = CDataCao::GetFileNameWithoutExt((CDataCao *)(*(longlong *)(pCVar8 + 0x10) + 0x180));
      uVar24 = FUN_140737af0(*(undefined8 *)(pCVar8 + 0x10),local_758);
      pCVar27 = (CRunContextExtraWork *)
                CRunContextExtraWork_ExportJointRes::CRunContextExtraWork_ExportJointRes
                          (local_760,uVar24,uVar23,uVar22,uVar17);
      pCVar30 = (CCAD_Base *)CONCAT44(param_7._4_4_,CONCAT22(param_7._2_2_,(ushort)param_7));
      local_570 = ViIdentification::CIdentificationProgramResult::vftable;
      CViUnitAngle::_vbase_destructor_(local_550);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_558);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_560);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_568);
    }
    CRunContextModel::AddExtraWork((CRunContextModel *)local_328,pCVar27);
  }
  bVar7 = false;
  CStringListe::CStringListe(local_5c8);
  CRunContextModelFamily::CRunContextModelFamily
            (local_4e8,(CRunContextModel *)local_328,
             *(double *)(*(longlong *)(pCVar8 + 0x10) + 0x3918),local_5c8,iVar15 != 0,false);
  CModelResult::CModelResult(local_6f0);
  local_700 = 0;
  local_6f8 = 0;
  local_768 = 0;
  pCVar33 = (CRect *)&local_700;
  bVar10 = CModelFamily::ImagesAnalysis(local_778,local_4e8,local_6f0,&local_768,pCVar33);
  uVar16 = (undefined4)((ulonglong)pCVar33 >> 0x20);
  if (bVar10) {
    this_00 = CLibraryHelperExportThread::GetInstance();
    local_748[0] = (CViUnitLength)0x0;
    local_740 = 0;
    uStack_738 = 0;
    local_730 = 0;
    uStack_728 = 0;
    local_720 = 0;
    uStack_718 = 0;
    CLibraryHelperExportThread::PushResult
              (this_00,local_5f8,local_6f0,(SCertifiedResults *)local_748);
    FUN_14056d860(&uStack_728);
    FUN_14056d860(&local_740);
    local_res8 = CModelResult::GetResult(local_6f0);
    uVar14 = CResult::GetBinaryFieldDefects(local_res8);
    uVar17 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
             CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                       ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_770,
                        local_710);
    lVar26 = FUN_140667dc0(*(longlong *)(pCVar8 + 0x10) + 0x5ca0,(undefined2)local_764,uVar17);
    if (lVar26 != 0) {
      uVar14 = uVar14 + *(int *)(lVar26 + 0x10);
    }
    (**(code **)(*(longlong *)param_4 + 0x48))(param_4);
    if (*(char *)(*(longlong *)(pCVar8 + 0x10) + 0x3835) == '\x01') {
      pCVar19 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                (**(code **)(*(longlong *)pCVar30 + 0x48))(pCVar30,&param_7);
      iVar15 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::CompareNoCase
                         (pCVar19,"SKIP");
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&param_7);
      if (iVar15 == 0) {
        if ((uVar14 & 0x800001) == 0) {
          CLogManagerFunctionML::Write
                    (local_5a0,5,
                     "Zone index %Id, Found a SKIP component on sub-panel #%d -> skip it\n",param_6,
                     CONCAT44(uVar16,*(undefined4 *)(pCVar30 + 0x14)));
          CDataCaoTraitement::SkipSubPanel
                    (*(CDataCaoTraitement **)(pCVar8 + 0x10),*(long *)(pCVar30 + 0x14));
          PostMessageA(*(HWND *)(*(longlong *)(*(longlong *)(pCVar8 + 0x10) + 0x5838) + 0x40),
                       DAT_1411dcb30,0,0);
        }
        goto LAB_14073742d;
      }
    }
    uVar17 = CCAD_Base::GetSize(pCVar30);
    uVar16 = FUN_14068b960(*(undefined8 *)(pCVar8 + 0x10),pCVar30,*(undefined4 *)(pCVar30 + 8),
                           uVar17,CONCAT44(uVar16,uVar14));
    param_7._0_2_ = (ushort)uVar16;
    param_7._2_2_ = (undefined2)((uint)uVar16 >> 0x10);
    CViUnitSize::_vbase_destructor_((CViUnitSize *)&local_570);
    if (0 < CONCAT22(param_7._2_2_,(ushort)param_7)) {
      FUN_1407388a0(pCVar8,param_4,param_5,param_6,pCVar30,local_res10,local_328,
                    CONCAT22(param_7._2_2_,(ushort)param_7),local_778,&local_700,local_6f0);
    }
    *(ulong *)(param_4 + 0x28) = uVar14;
    *(undefined4 *)(param_4 + 0x2c) = 0;
    uVar17 = CModelResult::GetModelName(local_6f0);
    CAnomalie::_csWinnerModel(param_4,uVar17);
    this = local_res8;
    uVar17 = CResult_Component::GetReadText((CResult_Component *)local_res8);
    CAnomalie::SetReadText(param_4,uVar17);
    uVar17 = CResult_Component::GetMeasure((CResult_Component *)this);
    CAnomalie::SetMeasure(param_4,uVar17);
    *(undefined8 *)(param_4 + 0x290) = 0;
    *(undefined8 *)(param_4 + 0x298) = 0;
    *(undefined8 *)(param_4 + 0x2a0) = 0;
    lVar28 = CResult_Component::GetDeltaTheta((CResult_Component *)this);
    *(undefined8 *)(param_4 + 0x70) = *(undefined8 *)(lVar28 + 0x18);
    CViUnitAngle::_vbase_destructor_(local_6b0);
    lVar28 = CResult_Component::GetDeltaThickness((CResult_Component *)this);
    *(undefined8 *)(param_4 + 0x78) = *(undefined8 *)(lVar28 + 0x20);
    CViUnitLength::_vbase_destructor_(local_748);
    lVar28 = CResult_Component::GetExpectedThickness((CResult_Component *)this);
    *(undefined8 *)(param_4 + 0xa8) = *(undefined8 *)(lVar28 + 0x20);
    CViUnitLength::_vbase_destructor_(local_748);
    lVar28 = CResult_Component::GetTilt((CResult_Component *)this);
    *(undefined8 *)(param_4 + 0x80) = *(undefined8 *)(lVar28 + 0x20);
    CViUnitLength::_vbase_destructor_(local_748);
    lVar28 = CResult_Component::GetDeltaX((CResult_Component *)this);
    *(undefined8 *)(param_4 + 0x60) = *(undefined8 *)(lVar28 + 0x20);
    CViUnitLength::_vbase_destructor_(local_748);
    lVar28 = CResult_Component::GetDeltaY((CResult_Component *)this);
    *(undefined8 *)(param_4 + 0x68) = *(undefined8 *)(lVar28 + 0x20);
    CViUnitLength::_vbase_destructor_(local_748);
    *(undefined8 *)(param_4 + 0x30) = *(undefined8 *)(this + 0x10);
    *(double *)(param_4 + 0xa0) = dVar1;
    *(int *)(param_4 + 0x2c0) = local_768;
    this_01 = CModelResult::GetResult(local_6f0);
    CVar11 = (CAnomalie)CResult::Has3DMeasureBeenReplacedBy2D(this_01);
    param_4[0x2c4] = CVar11;
    CComponentPinResults::CComponentPinResults(local_678);
    CResult::GetPinResults(this,local_678,(ulong *)(*(longlong *)(pCVar8 + 0x10) + 0x3840));
    if (lVar26 != 0) {
      lVar28 = *(longlong *)(lVar26 + 0x28);
      uVar29 = 0;
      param_7._0_2_ = 0;
      local_res8 = (CResult *)((ulonglong)local_res8 & 0xffffffffffff0000);
      local_780[0] = 0;
      if (0 < lVar28) {
        do {
          FUN_140667d20(lVar26,uVar29,&param_7,&local_res8,local_780);
          CComponentPinResults::AddDefectsToPin
                    (local_678,(int)(short)local_res8,(uint)(ushort)param_7,0,local_780[0],0,0);
          uVar29 = uVar29 + 1;
        } while ((longlong)(ulonglong)uVar29 < lVar28);
      }
    }
    CComponentPinResults::SetPinResults((CComponentPinResults *)(param_4 + 0x38),local_678);
    if (local_4e0 == (CRunContextModel_Component *)0x0) {
      uVar16 = CONCAT22(param_7._2_2_,(ushort)param_7);
LAB_14073731a:
      bVar10 = false;
      uVar32 = param_7._4_4_;
    }
    else {
      lVar26 = CRunContextModel_Component::GetTolerance_X(local_4e0);
      bVar7 = true;
      dVar1 = *(double *)(lVar26 + 0x20);
      uVar16 = SUB84(dVar1,0);
      param_7._4_4_ = (undefined4)((ulonglong)dVar1 >> 0x20);
      if (dVar1 == 0.0) goto LAB_14073731a;
      bVar10 = true;
      uVar32 = param_7._4_4_;
    }
    if (bVar7) {
      CViUnitLength::_vbase_destructor_(local_748);
    }
    bVar7 = false;
    if (bVar10) {
      *(double *)(param_4 + 0x298) = *(double *)(param_4 + 0x60) / (double)CONCAT44(uVar32,uVar16);
    }
    if (local_4e0 == (CRunContextModel_Component *)0x0) {
LAB_140737371:
      bVar10 = false;
    }
    else {
      lVar26 = CRunContextModel_Component::GetTolerance_Y(local_4e0);
      bVar7 = true;
      dVar1 = *(double *)(lVar26 + 0x20);
      uVar16 = SUB84(dVar1,0);
      uVar32 = (undefined4)((ulonglong)dVar1 >> 0x20);
      if (dVar1 == 0.0) goto LAB_140737371;
      bVar10 = true;
    }
    if (bVar7) {
      CViUnitLength::_vbase_destructor_(local_748);
    }
    bVar7 = false;
    if (bVar10) {
      *(double *)(param_4 + 0x2a0) = *(double *)(param_4 + 0x68) / (double)CONCAT44(uVar32,uVar16);
    }
    if (local_4e0 == (CRunContextModel_Component *)0x0) {
LAB_1407373c7:
      bVar10 = false;
    }
    else {
      lVar26 = CRunContextModel_Component::GetTolerance_Theta(local_4e0);
      bVar7 = true;
      dVar1 = *(double *)(lVar26 + 0x18);
      uVar16 = SUB84(dVar1,0);
      uVar32 = (undefined4)((ulonglong)dVar1 >> 0x20);
      if (dVar1 == 0.0) goto LAB_1407373c7;
      bVar10 = true;
    }
    if (bVar7) {
      CViUnitAngle::_vbase_destructor_(local_6b0);
    }
    if (bVar10) {
      *(double *)(param_4 + 0x290) = *(double *)(param_4 + 0x70) / (double)CONCAT44(uVar32,uVar16);
    }
    *(double *)(param_4 + 0x2b0) = *(double *)(param_4 + 0x60) / *(double *)(pCVar8 + 0x38);
    *(double *)(param_4 + 0x2b8) = *(double *)(param_4 + 0x68) / *(double *)(pCVar8 + 0x38);
    pCVar31 = (CRunContextExtraWork *)(ulonglong)uVar14;
    CComponentPinResults::~CComponentPinResults(local_678);
  }
  else {
    pCVar31 = (CRunContextExtraWork *)0x20;
  }
LAB_14073742d:
  CModelResult::~CModelResult(local_6f0);
  CRunContextModelFamily::~CRunContextModelFamily(local_4e8);
  CStringListe::~CStringListe(local_5c8);
  CRunContextModel_Component::~CRunContextModel_Component(local_328);
  CInputIdentity::~CInputIdentity(local_5f8);
  CRunContextPads::~CRunContextPads(local_498);
LAB_14073747e:
  CDPoint::_vbase_destructor_(local_620);
  CDPoint::_vbase_destructor_((CDPoint *)local_650);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_710);
  CLogManagerFunctionML::~CLogManagerFunctionML(local_5a0);
  return pCVar31;
}

