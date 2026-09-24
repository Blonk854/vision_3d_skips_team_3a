// Zone_SaveOIS_callsite @ 0x140737b20
// function FUN_140737b20 [140737b20 ..]


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */

void FUN_140737b20(undefined8 *param_1,CAnomalieProd *param_2,CCAD_ZoneMatriciel *param_3,
                  undefined8 param_4,CCAD_BaseContainer *param_5,undefined8 param_6,
                  CZoneStorage *param_7)

{
  CTest *this;
  CLibraryUsingContext *this_00;
  CAnomalieProd *pCVar1;
  longlong lVar2;
  char cVar3;
  bool bVar4;
  ushort uVar5;
  LONG LVar6;
  CImagesDefinitions *pCVar7;
  __int64 _Var8;
  CCAD_Base *pCVar9;
  undefined8 *puVar10;
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *pCVar11;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *this_01;
  undefined4 *puVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  undefined8 uVar16;
  int iVar17;
  uint uVar18;
  uint uVar19;
  longlong lVar20;
  longlong lVar21;
  longlong lVar22;
  int iVar23;
  double dVar24;
  double dVar25;
  uint uVar26;
  double dVar27;
  double dVar28;
  undefined ***local_res8;
  CAnomalieProd *local_res10;
  CCAD_ZoneMatriciel *local_res18;
  undefined8 local_res20;
  ulonglong in_stack_ffffffffffffef40;
  ulonglong in_stack_ffffffffffffef48;
  undefined8 in_stack_ffffffffffffef50;
  undefined4 uVar29;
  ulonglong uVar30;
  undefined8 local_1098;
  undefined8 local_1090;
  RECT local_1088;
  __int64 local_1078;
  RECT local_1070;
  RECT local_1060;
  RECT local_1050;
  uint local_1040;
  tagRECT local_1038;
  int local_1028;
  int local_1024;
  undefined8 local_1020;
  double dStack_1018;
  double local_1010;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1008 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1000 [8];
  code *local_ff8;
  double local_ff0;
  double local_fe8;
  undefined1 local_fe0 [8];
  undefined **local_fd8;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_fd0 [8];
  undefined8 local_fc8;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_fc0 [8];
  undefined8 local_fb8;
  undefined1 local_fb0 [8];
  longlong local_fa8;
  longlong local_fa0;
  double local_f88;
  double local_f80;
  double local_f78;
  double local_f70;
  double local_f68;
  double local_f60;
  double local_f58;
  double local_f50;
  int local_f48 [4];
  double local_f38 [6];
  CDPoint local_f08 [16];
  double local_ef8;
  double local_ef0;
  undefined **local_ee0;
  CDPoint local_ed8 [48];
  undefined8 local_ea8;
  CDPoint local_ea0 [16];
  double local_e90;
  double local_e88;
  CDPoint local_e78 [16];
  double local_e68;
  double local_e60;
  CZConvert local_e50 [40];
  vitXform local_e28 [8];
  ccXform<2> local_e20 [56];
  CDPoint local_de8 [40];
  CLogManagerFunctionML local_dc0 [56];
  undefined8 local_d88;
  undefined8 local_d80;
  undefined4 local_d78;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_d70 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_d68 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_d60 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_d58 [8];
  uint local_d50;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_d48 [8];
  CSimpleStringT<char,1> local_d40 [8];
  undefined1 local_d38;
  tagRECT local_d30;
  undefined4 local_d20;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_c90 [32];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_c70 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_c68 [88];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_c10 [24];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_bf8 [8];
  undefined4 local_bf0;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_be8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_be0 [32];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_bc0 [33];
  undefined1 local_b9f;
  undefined1 local_ab8 [56];
  CViUnitPoint local_a80 [168];
  CcPelBuffer local_9d8 [224];
  undefined8 local_8f8;
  CFontParam_OCV local_8d8 [224];
  CRunContextModel_Font local_7f8 [16];
  CZoneStorage *local_7e8;
  undefined1 local_720;
  CImagesDefinitions local_648 [736];
  CImagesDefinitions local_368 [800];
  undefined8 uStack_48;
  
  uStack_48 = 0x140737b4d;
  local_ea8 = 0xfffffffffffffffe;
  uVar19 = 0;
  local_res8 = (undefined ***)((ulonglong)local_res8 & 0xffffffff00000000);
  local_res10 = param_2;
  local_res18 = param_3;
  local_res20 = param_4;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1090,
             "CZoneAnalysis::PictureSave");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_dc0,0x10,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1090,
             (ulonglong)*(uint *)(param_1[2] + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1090);
  cVar3 = FUN_14068bd70(param_1[2]);
  local_1040 = -(uint)(cVar3 != '\0') & 4;
  if ((local_1040 != 0) &&
     ((*(longlong *)(param_2 + 400) == 0 || (*(longlong *)(param_2 + 0x198) == 0)))) {
    CCAD_ZoneMatriciel::GetImagesDefinitions(param_3);
    pCVar7 = (CImagesDefinitions *)CTest::GetZMapScanParams((CTest *)(param_1[2] + 0x188));
    CImagesDefinitions::SetZmapScanParam(local_648,pCVar7);
    CImagesDefinitions::_vbase_destructor_(local_368);
    uVar18 = 1;
    do {
      if ((*(short *)(param_1[2] + 0x3820) != 0) ||
         (bVar4 = CRequiredImages::Has2DLevel((CRequiredImages *)(param_3 + 0x430),uVar18), bVar4))
      {
        if (uVar19 == 0) {
          uVar19 = uVar18;
        }
      }
      else {
        CImagesDefinitions::RemoveGrayImageFlag(local_648,uVar18);
      }
      uVar18 = uVar18 + 1;
    } while (uVar18 < 6);
    _Var8 = CCAD_BaseContainer::GetOjectCAOCount(param_5);
    dVar27 = DAT_140de2128;
    uVar29 = (undefined4)((ulonglong)in_stack_ffffffffffffef50 >> 0x20);
    local_1070.left = 0;
    local_1070.top = 0;
    local_1070.right = 0;
    local_1070.bottom = 0;
    local_1060.left = 0;
    local_1060.top = 0;
    local_1060.right = 0;
    local_1060.bottom = 0;
    local_1078 = 0;
    local_1098 = (undefined ****)_Var8;
    if (0 < _Var8) {
      do {
        lVar22 = 0;
        pCVar9 = CCAD_BaseContainer::GetOjectCAO(param_5,&local_1078);
        local_fd8 = CString_Result::vftable;
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_fd0);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_fc0);
        FUN_14051d5a0(local_fb0);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_fd0,"");
        local_fc8 = 0;
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_fc0,"");
        FUN_1405404a0(local_fb0,0,0xffffffffffffffff);
        local_fb8 = 0xffffffffffffffff;
        cVar3 = FUN_140527f50(param_6,local_1078);
        if (cVar3 == '\x01') {
          (**(code **)(*(longlong *)pCVar9 + 0x118))(pCVar9,&local_1020);
          lVar2 = local_fa0;
          if (0 < local_fa0) {
            lVar21 = 0;
            do {
              if ((lVar21 < 0) || (local_fa0 <= lVar22)) {
                    /* WARNING: Subroutine does not return */
                AfxThrowInvalidArgException();
              }
              lVar20 = local_fa8 + lVar21;
              local_ee0 = CString_Pos::vftable;
              CDPoint::CDPoint(local_ed8);
              (*(code *)local_ee0[5])(&local_ee0,lVar20);
              FUN_140544120(&local_ee0,local_f08);
              iVar17 = (int)local_1010;
              if ((int)local_1010 < (int)dStack_1018) {
                iVar17 = (int)dStack_1018;
              }
              dVar28 = (double)iVar17 * dVar27;
              iVar23 = (int)(local_ef8 - dVar28);
              iVar17 = (int)(local_ef0 - dVar28);
              local_1060.right = (LONG)(dVar28 + local_ef8);
              local_1060.bottom = (LONG)(dVar28 + local_ef0);
              local_1060.left = iVar23;
              if (local_1060.right < iVar23) {
                local_1060.left = local_1060.right;
                local_1060.right = iVar23;
              }
              local_1060.top = iVar17;
              if (local_1060.bottom < iVar17) {
                local_1060.top = local_1060.bottom;
                local_1060.bottom = iVar17;
              }
              UnionRect(&local_1070,&local_1060,&local_1070);
              CDPoint::_vbase_destructor_(local_f08);
              CDPoint::_vbase_destructor_(local_ed8);
              lVar22 = lVar22 + 1;
              lVar21 = lVar21 + 0x38;
              _Var8 = (__int64)local_1098;
            } while (lVar22 < lVar2);
          }
          CDSize::~CDSize((CDSize *)&local_1020);
        }
        local_1078 = local_1078 + 1;
        FUN_140520010(&local_fd8);
        uVar29 = (undefined4)((ulonglong)in_stack_ffffffffffffef50 >> 0x20);
        param_3 = local_res18;
      } while (local_1078 < _Var8);
    }
    local_ff8 = _vftable__exref;
    local_ff0 = (double)(local_1070.bottom - local_1070.top);
    local_fe8 = (double)(local_1070.right - local_1070.left);
    puVar10 = (undefined8 *)CDSize::cSize((CDSize *)&local_ff8);
    InflateRect(&local_1070,(int)*puVar10,(int)((ulonglong)*puVar10 >> 0x20));
    local_1090 = (CDPoint *)
                 CONCAT44((local_1070.bottom + local_1070.top) / 2,
                          (local_1070.right + local_1070.left) / 2);
    CDPoint::CDPoint(local_e78,(CPoint *)&local_1090);
    dVar28 = local_e60 * DAT_140e44658;
    local_e60 = dVar28;
    dVar24 = cos(0.0);
    dVar25 = sin(0.0);
    uVar18 = (uint)DAT_140de2140;
    uVar26 = (uint)((ulonglong)DAT_140de2140 >> 0x20);
    iVar23 = (int)((double)*(int *)(param_1[2] + 0x3948) *
                  ((double)CONCAT44((uint)((ulonglong)(local_fe8 * dVar25) >> 0x20) & uVar26,
                                    SUB84(local_fe8 * dVar25,0) & uVar18) +
                  (double)CONCAT44((uint)((ulonglong)(local_ff0 * dVar24) >> 0x20) & uVar26,
                                   SUB84(local_ff0 * dVar24,0) & uVar18)));
    iVar17 = (int)((double)*(int *)(param_1[2] + 0x3948) *
                  ((double)CONCAT44((uint)((ulonglong)(local_fe8 * dVar24) >> 0x20) & uVar26,
                                    SUB84(local_fe8 * dVar24,0) & uVar18) +
                  (double)CONCAT44((uint)((ulonglong)(local_ff0 * dVar25) >> 0x20) & uVar26,
                                   SUB84(local_ff0 * dVar25,0) & uVar18)));
    if (iVar17 < iVar23) {
      iVar17 = iVar23;
    }
    dVar27 = (double)iVar17 * dVar27;
    iVar23 = (int)(local_e68 - dVar27);
    iVar17 = (int)(dVar28 - dVar27);
    local_1088.right = (LONG)(local_e68 + dVar27);
    local_1088.bottom = (LONG)(dVar28 + dVar27);
    local_1088.left = iVar23;
    if (local_1088.right < iVar23) {
      local_1088.left = local_1088.right;
      local_1088.right = iVar23;
    }
    local_1088.top = iVar17;
    if (local_1088.bottom < iVar17) {
      local_1088.top = local_1088.bottom;
      local_1088.bottom = iVar17;
    }
    local_f80 = (double)local_1088.top;
    local_f88 = (double)local_1088.left;
    local_f70 = (double)local_1088.bottom;
    local_f78 = (double)local_1088.right;
    CcPelBuffer::CcPelBuffer
              (local_9d8,(CcPelBuffer *)(param_7 + (ulonglong)(uVar19 - 1) * 0xf8 + 0x68));
    CcPelBuffer::GetXform(local_9d8);
    ccXform<2>::invMapPoint(local_e20,(ccVector<2> *)&local_f68);
    ccXform<2>::invMapPoint(local_e20,(ccVector<2> *)&local_f58);
    iVar23 = (int)local_f68;
    iVar17 = (int)local_f60;
    local_1088.right = (LONG)local_f58;
    local_1088.bottom = (LONG)local_f50;
    local_1088.left = iVar23;
    if (local_1088.right < iVar23) {
      local_1088.left = local_1088.right;
      local_1088.right = iVar23;
    }
    local_1088.top = iVar17;
    if (local_1088.bottom < iVar17) {
      local_1088.top = local_1088.bottom;
      local_1088.bottom = iVar17;
    }
    (**(code **)(*(longlong *)param_1[6] + 0x1c0))((longlong *)param_1[6],&local_1028,1);
    local_1024 = local_1024 + -2;
    local_1028 = local_1028 + -2;
    local_1098 = (undefined ****)CONCAT44(local_1024,local_1028);
    local_1090 = (CDPoint *)0x0;
    local_1050.left = 0;
    local_1050.right = local_1028;
    if (local_1028 < 0) {
      local_1050.right = 0;
      local_1050.left = local_1028;
    }
    local_1050.top = 0;
    local_1050.bottom = local_1024;
    if (local_1024 < 0) {
      local_1050.bottom = 0;
      local_1050.top = local_1024;
    }
    local_1038.left = 0;
    local_1038.top = 0;
    local_1038.right = 0;
    local_1038.bottom = 0;
    IntersectRect(&local_1038,&local_1088,&local_1050);
    uVar19 = 2;
    LVar6 = local_1038.top;
    if (local_1038.top == 0) {
      LVar6 = 2;
    }
    if (local_1038.left == 0) {
      local_1038.left = 2;
    }
    local_1038.top = LVar6;
    local_f38[0] = 0.0;
    local_f38[1] = 0.0;
    local_f38[2] = 0.0;
    local_f38[3] = 0.0;
    local_f38[4] = 0.0;
    local_f38[5] = 0.0;
    vitXform::GetDoubleTab(local_e28,local_f38);
    CZConvert::CZConvert(local_e50);
    CZConvert::GetParamIntTab(local_e50,local_f48);
    uVar30 = 0;
    FUN_140764f30(local_ab8,local_648,local_f38,local_f48,local_8f8,
                  in_stack_ffffffffffffef40 & 0xffffffffffffff00,
                  in_stack_ffffffffffffef48 & 0xffffffffffffff00,CONCAT44(uVar29,0xd),0);
    this = (CTest *)(param_1[2] + 0x188);
    this_00 = (CLibraryUsingContext *)(param_1[2] + 0x1200);
    FUN_1404e2dc0(&local_d88);
    FUN_1407654a0(&local_d88);
    iVar17 = CCAD_Zone::IsJokerZone((CCAD_Zone *)param_3);
    local_b9f = iVar17 != 0;
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              (**(code **)(*(longlong *)param_1[6] + 0x20))((longlong *)param_1[6],&local_1098);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_c68,pCVar11)
    ;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1098);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              (**(code **)(*(longlong *)param_5 + 0x60))(param_5,&local_1098);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_c90,pCVar11)
    ;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1098);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              (**(code **)(*(longlong *)param_5 + 0x78))(param_5,&local_1098);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_c70,pCVar11)
    ;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1098);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              CBibliotheque::GetCompleteLibName((CBibliotheque *)(param_1[2] + 0x11f8));
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_be8,pCVar11)
    ;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1098);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              CTest::GetProductName(this);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_c10,pCVar11)
    ;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1098);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_be0,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               (param_1[2] + 0x48));
    if (this_00 == (CLibraryUsingContext *)0x0) {
      pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                          ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                           &local_1098,"");
    }
    else {
      pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                CLibraryUsingContext::GetSystemName(this_00);
      uVar19 = 1;
    }
    local_res8 = (undefined ***)CONCAT44(local_res8._4_4_,uVar19);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_bc0,pCVar11)
    ;
    if ((uVar19 & 2) != 0) {
      uVar19 = uVar19 & 0xfffffffd;
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1098);
    }
    if ((uVar19 & 1) != 0) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1090);
    }
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              (**(code **)(*(longlong *)param_5 + 0x48))(param_5,&local_res8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_bf8,pCVar11)
    ;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8);
    local_bf0 = *(undefined4 *)(param_5 + 0x14);
    local_d20 = *(undefined4 *)(param_5 + 8);
    local_d80 = 0;
    local_d88 = 0;
    local_d30.left = local_1038.left;
    local_d30.top = local_1038.top;
    local_d30.right = local_1038.right;
    local_d30.bottom = local_1038.bottom;
    local_1098 = &local_res8;
    this_01 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
              CTest::GetOIS_ProdFileDirectory(this);
    local_1090 = (CDPoint *)this_01;
    puVar12 = (undefined4 *)CTest::GetRecordPanelTypeInfo(this);
    local_d78 = *puVar12;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_d70,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               (puVar12 + 2));
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_d68,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               (puVar12 + 4));
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_d60,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               (puVar12 + 6));
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_d58,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               (puVar12 + 8));
    local_d50 = 0;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_d48,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)this_01)
    ;
    ATL::CSimpleStringT<char,1>::Empty(local_d40);
    local_d38 = 0;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(this_01);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1000);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1008);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1010);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&dStack_1018);
    if (*(short *)(param_1[2] + 0x3820) == 0) {
      uVar5 = CImagesDefinitions::GetGrayImageFlag(local_648);
      local_d50 = (uint)uVar5;
    }
    else {
      local_d50 = 0x1f;
    }
    CFontParam_OCV::CFontParam_OCV(local_8d8);
    local_res8 = &local_fd8;
    local_1098 = (undefined ****)&local_ee0;
    local_1090 = local_f08;
    uVar13 = CViUnitLength::CViUnitLength((CViUnitLength *)&local_fd8,0.0);
    uVar14 = CViUnitLength::CViUnitLength((CViUnitLength *)&local_ee0,0.0);
    uVar15 = CViUnitAngle::CViUnitAngle((CViUnitAngle *)local_f08,0.0);
    uVar16 = CViUnitPoint::CViUnitPoint(local_a80,0.0,0.0);
    CRunContextModel_Font::CRunContextModel_Font
              (local_7f8,param_7,*param_1,uVar16,uVar15,uVar14,uVar13,local_8d8,
               uVar30 & 0xffffffffffffff00);
    local_720 = 1;
    CZoneStorage::CopyRefence(local_7e8,param_7);
    FUN_1404aab30(local_fe0,param_1[2]);
    pCVar1 = local_res10;
    local_1020 = 0;
    dStack_1018 = 0.0;
    cVar3 = FUN_1406e79c0(local_fe0,6,local_1040,local_7f8,local_ab8,&local_d88,local_res10,
                          &local_1020);
    if (cVar3 == '\0') {
      CLogManagerFunctionML::Write(local_dc0,4,"oVitImgFileRecorderHelper.SaveOIS() failed.");
    }
    CDPoint::CDPoint(local_ea0);
    CDPoint::CDPoint(local_de8);
    CDataCaoTraitement::ComputeZonePosition
              ((CDataCaoTraitement *)param_1[2],local_ea0,local_de8,param_3);
    uVar13 = CViUnitPoint::CViUnitPoint(local_a80,local_e90,local_e88);
    CAnomalieProd::SetColorImgInfo(pCVar1,local_res20,uVar13);
    CDPoint::_vbase_destructor_(local_de8);
    CDPoint::_vbase_destructor_(local_ea0);
    CRunContextModel_Font::~CRunContextModel_Font(local_7f8);
    CFontParam_OCV::~CFontParam_OCV(local_8d8);
    FUN_1404e33f0(&local_d88);
    CZConvert::~CZConvert(local_e50);
    vitXform::~vitXform(local_e28);
    CcPelBuffer::~CcPelBuffer(local_9d8);
    CDPoint::_vbase_destructor_(local_e78);
    CDSize::~CDSize((CDSize *)&local_ff8);
    CImagesDefinitions::_vbase_destructor_(local_648);
  }
  CLogManagerFunctionML::~CLogManagerFunctionML(local_dc0);
  return;
}

