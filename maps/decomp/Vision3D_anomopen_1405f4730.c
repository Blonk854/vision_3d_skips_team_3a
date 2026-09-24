// FUN_1405f4730 @ 1405f4730 body=3461


undefined8
FUN_1405f4730(CDataCaoTraitement *param_1,
             CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *param_2,int param_3)

{
  char cVar1;
  bool bVar2;
  int iVar3;
  ulong uVar4;
  int iVar5;
  __int64 _Var6;
  CCAD_Base *this;
  CSimpleStringT<char,1> *pCVar7;
  char *pcVar8;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *pCVar9;
  undefined8 uVar10;
  CCAD_Base *pCVar11;
  ulonglong uVar12;
  ulonglong uVar13;
  AFX_MODULE_STATE *pAVar14;
  undefined8 uVar15;
  ulonglong uVar16;
  void *pvVar17;
  longlong lVar18;
  __int64 _Var19;
  CDataCaoTraitement *pCVar20;
  char local_res20 [8];
  CSimpleStringT<char,1> *local_148;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *local_140;
  void *local_138;
  longlong lStack_130;
  longlong local_128;
  undefined4 local_120 [2];
  longlong local_118;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *local_110;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *local_108;
  longlong local_100;
  void *local_f8;
  undefined8 uStack_f0;
  longlong local_e8;
  undefined **local_d8;
  CStringListe local_c8 [40];
  CStringListe local_a0 [40];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_78 [8];
  CLogManagerFunction local_70 [40];
  undefined8 local_48;
  
  local_48 = 0xfffffffffffffffe;
  local_120[0] = 0;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_78,"CDocCompose::ExecOneComp")
  ;
  CLogManagerFunction::CLogManagerFunction(local_70,0x16,local_78,1);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_78);
  cVar1 = FUN_1405ddc30(param_1);
  if (cVar1 == '\x01') {
    CLogManagerFunction::~CLogManagerFunction(local_70);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(param_2);
    return 1;
  }
  local_148 = (CSimpleStringT<char,1> *)(param_1 + 0x1a78);
  ATL::CSimpleStringT<char,1>::Empty(local_148);
  pCVar11 = (CCAD_Base *)0x0;
  lVar18 = 0;
  _Var6 = CDataCao::GetSizeCadTab((CDataCao *)(param_1 + 0x180));
  if (0 < _Var6) {
    do {
      this = CDataCao::GetLineCAD((CDataCao *)(param_1 + 0x180),lVar18);
      pCVar7 = (CSimpleStringT<char,1> *)(**(code **)(*(longlong *)this + 0x48))(this,&local_118);
      local_120[0] = 1;
      pcVar8 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64(pCVar7);
      iVar3 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::CompareNoCase
                        (param_2,pcVar8);
      if ((iVar3 == 0) && (param_3 == *(int *)(this + 0x14))) {
        bVar2 = true;
      }
      else {
        bVar2 = false;
      }
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_118);
      if (bVar2) {
        if ((*(uint *)(this + 8) & 0x3041e0) != 0) {
          (**(code **)(*(longlong *)this + 0x48))(this,&local_118);
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                    ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_148,
                     0xb7b);
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
          ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                    ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_118);
          pcVar8 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64(local_148);
          AfxMessageBox(pcVar8,0x10,0);
          CLogManagerFunction::~CLogManagerFunction(local_70);
          goto LAB_1405f54ab;
        }
        if (DAT_1410f5ad0 != 0) {
          CVitCognexConsoleDispatcher::PanAndFit_SetAllowPanInClientCoord
                    ((CVitCognexConsoleDispatcher *)(DAT_1410f5ad0 + 0xa40),true);
        }
        FUN_1405ea870(param_1,1);
        FUN_140616280(param_1 + 0x3220,1);
        pCVar9 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                 ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                 CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                           ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                            &local_148,
                            (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                             *)param_2);
        *(undefined4 *)(param_1 + 0x3c68) = 0;
        local_140 = pCVar9;
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                   (param_1 + 0x3c88),
                   (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                   pCVar9);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(pCVar9);
        *(undefined4 *)(param_1 + 0x3c68) = 0;
        *(int *)(param_1 + 0x3ca8) = param_3;
        FUN_1405ea2c0(param_1);
        if ((*(uint *)(this + 8) & 0x200008) == 0) {
          uVar10 = (**(code **)(*(longlong *)this + 0x48))(this,&local_148);
          uVar10 = FUN_1405cf760(&local_110,uVar10,*(undefined4 *)(this + 0x14));
          FUN_1405ccdf0(param_1 + 0x5128,uVar10);
          local_d8 = CRecordComponents::vftable;
          CStringListe::~CStringListe(local_a0);
          CStringListe::~CStringListe(local_c8);
          if (local_f8 != (void *)0x0) {
            FUN_14057be20(&local_f8,local_f8,local_e8 - (longlong)local_f8 >> 2);
            local_f8 = (void *)0x0;
            uStack_f0 = 0;
            local_e8 = 0;
          }
          FUN_14056d6d0(&local_110);
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
          ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                    ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_148);
          goto LAB_1405f4cc0;
        }
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_120,"");
        uVar10 = (**(code **)(*(longlong *)this + 0x48))(this,&local_148);
        uVar10 = FUN_1405cfbf0(&local_110,uVar10,local_120,*(undefined4 *)(this + 0x14));
        FUN_1405ccdf0(param_1 + 0x5128,uVar10);
        local_d8 = CRecordComponents::vftable;
        CStringListe::~CStringListe(local_a0);
        CStringListe::~CStringListe(local_c8);
        if (local_f8 != (void *)0x0) {
          FUN_14057be20(&local_f8,local_f8,local_e8 - (longlong)local_f8 >> 2);
          local_f8 = (void *)0x0;
          uStack_f0 = 0;
          local_e8 = 0;
        }
        FUN_14056d6d0(&local_110);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_148);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_120);
        pCVar7 = (CSimpleStringT<char,1> *)(**(code **)(*(longlong *)this + 0x88))(this,&local_148);
        bVar2 = ATL::CSimpleStringT<char,1>::IsEmpty(pCVar7);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_148);
        if (bVar2) goto LAB_1405f4cc0;
        _Var19 = 0;
        local_118 = 0;
        _Var6 = CDataCao::GetSizeCadTab((CDataCao *)(param_1 + 0x180));
        if (0 < _Var6) goto LAB_1405f4b32;
        goto LAB_1405f4cc0;
      }
      lVar18 = lVar18 + 1;
      _Var6 = CDataCao::GetSizeCadTab((CDataCao *)(param_1 + 0x180));
    } while (lVar18 < _Var6);
  }
  AfxMessageBox(0xd1b,0x10,0xffffffff);
  CLogManagerFunction::~CLogManagerFunction(local_70);
  goto LAB_1405f54ab;
  while( true ) {
    _Var19 = local_118 + 1;
    local_118 = _Var19;
    _Var6 = CDataCao::GetSizeCadTab((CDataCao *)(param_1 + 0x180));
    if (_Var6 <= _Var19) break;
LAB_1405f4b32:
    pCVar11 = CDataCao::GetLineCAD((CDataCao *)(param_1 + 0x180),_Var19);
    pCVar7 = (CSimpleStringT<char,1> *)(**(code **)(*(longlong *)this + 0x88))(this,&local_140);
    local_120[0] = 2;
    pCVar9 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
             (**(code **)(*(longlong *)pCVar11 + 0x48))(pCVar11,&local_148);
    local_120[0] = 6;
    pcVar8 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64(pCVar7);
    iVar3 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::CompareNoCase
                      (pCVar9,pcVar8);
    if ((iVar3 == 0) && (*(int *)(pCVar11 + 0x14) == *(int *)(this + 0x14))) {
      bVar2 = true;
    }
    else {
      bVar2 = false;
    }
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_148);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_140);
    if (bVar2) {
      uVar10 = (**(code **)(*(longlong *)pCVar11 + 0x48))(pCVar11,&local_148);
      uVar15 = (**(code **)(*(longlong *)this + 0x48))(this,&local_140);
      uVar10 = FUN_1405cfbf0(&local_110,uVar15,uVar10,*(undefined4 *)(this + 0x14));
      FUN_1405ccdf0(param_1 + 0x5128,uVar10);
      local_d8 = CRecordComponents::vftable;
      CStringListe::~CStringListe(local_a0);
      CStringListe::~CStringListe(local_c8);
      if (local_f8 != (void *)0x0) {
        FUN_14057be20(&local_f8,local_f8,local_e8 - (longlong)local_f8 >> 2);
        local_f8 = (void *)0x0;
        uStack_f0 = 0;
        local_e8 = 0;
      }
      FUN_14056d6d0(&local_110);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_140);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_148);
      break;
    }
  }
LAB_1405f4cc0:
  pCVar20 = param_1 + 0x5128;
  iVar3 = *(int *)(param_1 + 0x50e8);
  uVar4 = CDataCaoTraitement::GetCurrentSection(param_1);
  iVar3 = FUN_1405e8850(param_1,param_1 + 0x4b98,param_1 + 0x11f8,0,uVar4,iVar3 != 0,0,0);
  if (iVar3 < 0) {
    bVar2 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)(param_1 + 0x1a78));
    if (bVar2) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::LoadStringA
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)(param_1 + 0x1a78)
                 ,0xd1b);
    }
    pcVar8 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64
                       ((CSimpleStringT<char,1> *)(param_1 + 0x1a78));
    AfxMessageBox(pcVar8,0x10,0);
    uVar10 = FUN_1405e04b0(&local_110);
    FUN_1405ccdf0(pCVar20,uVar10);
    local_d8 = CRecordComponents::vftable;
    CStringListe::~CStringListe(local_a0);
    CStringListe::~CStringListe(local_c8);
    if (local_f8 != (void *)0x0) {
      FUN_14057be20(&local_f8,local_f8,local_e8 - (longlong)local_f8 >> 2);
      local_f8 = (void *)0x0;
      uStack_f0 = 0;
      local_e8 = 0;
    }
    pCVar9 = local_110;
    if (local_110 != (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)0x0) {
      for (; pCVar9 != local_108; pCVar9 = pCVar9 + 8) {
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(pCVar9);
      }
      FUN_140579780(&local_110,local_110,local_100 - (longlong)local_110 >> 3);
    }
    FUN_1405ea870(param_1,0);
    CLogManagerFunction::~CLogManagerFunction(local_70);
    goto LAB_1405f54ab;
  }
  param_1[0x3cb8] = (CDataCaoTraitement)0x1;
  if ((*(uint *)(this + 8) & 0x200008) == 0) {
    if (*(int *)(this + 0xc4) == 0) {
LAB_1405f4e44:
      iVar5 = 0;
    }
    else {
      iVar5 = *(int *)(this + 0xe8);
    }
LAB_1405f4e46:
    param_1[0x3cb8] = (CDataCaoTraitement)(iVar5 == 1);
  }
  else if (pCVar11 != (CCAD_Base *)0x0) {
    if (*(int *)(pCVar11 + 0xc4) == 0) goto LAB_1405f4e44;
    iVar5 = *(int *)(pCVar11 + 0xe8);
    goto LAB_1405f4e46;
  }
  CDataCaoTraitement::GetAllInspectedElmt(param_1);
  uVar13 = 0;
  uVar16 = lStack_130 - (longlong)local_138 >> 3;
  uVar12 = uVar13;
  if (uVar16 != 0) {
    do {
      if (this == *(CCAD_Base **)((longlong)local_138 + uVar12 * 8)) {
        if (pCVar11 == (CCAD_Base *)0x0) goto LAB_1405f50a0;
        if (uVar16 != 0) goto LAB_1405f4ea4;
        goto LAB_1405f4eb6;
      }
      uVar12 = uVar12 + 1;
    } while (uVar12 < uVar16);
  }
  AfxMessageBox(0xd1b,0x10,0xffffffff);
  uVar10 = FUN_1405e04b0(&local_110);
  FUN_1405ccdf0(pCVar20,uVar10);
  local_d8 = CRecordComponents::vftable;
  CStringListe::~CStringListe(local_a0);
  CStringListe::~CStringListe(local_c8);
  if (local_f8 != (void *)0x0) {
    uVar12 = local_e8 - (longlong)local_f8 >> 2;
    if (0x3fffffffffffffff < uVar12) {
                    /* WARNING: Subroutine does not return */
      _invalid_parameter_noinfo_noreturn();
    }
    pvVar17 = local_f8;
    if (0xfff < uVar12 * 4) {
      if (((ulonglong)local_f8 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      pvVar17 = *(void **)((longlong)local_f8 + -8);
      if (local_f8 <= pvVar17) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if ((ulonglong)((longlong)local_f8 - (longlong)pvVar17) < 8) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if (0x27 < (ulonglong)((longlong)local_f8 - (longlong)pvVar17)) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
    }
    operator_delete(pvVar17);
    local_f8 = (void *)0x0;
    uStack_f0 = 0;
    local_e8 = 0;
  }
  pCVar9 = local_110;
  if (local_110 != (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)0x0) {
    for (; pCVar9 != local_108; pCVar9 = pCVar9 + 8) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(pCVar9);
    }
    uVar12 = local_100 - (longlong)local_110 >> 3;
    if (0x1fffffffffffffff < uVar12) {
                    /* WARNING: Subroutine does not return */
      _invalid_parameter_noinfo_noreturn();
    }
    pCVar9 = local_110;
    if (0xfff < uVar12 * 8) {
      if (((ulonglong)local_110 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      pCVar9 = *(CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> **)(local_110 + -8);
      if (local_110 <= pCVar9) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if ((ulonglong)((longlong)local_110 - (longlong)pCVar9) < 8) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if (0x27 < (ulonglong)((longlong)local_110 - (longlong)pCVar9)) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
    }
    operator_delete(pCVar9);
  }
  FUN_1405ea870(param_1,0);
  if (local_138 != (void *)0x0) {
    uVar12 = local_128 - (longlong)local_138 >> 3;
    if (0x1fffffffffffffff < uVar12) {
                    /* WARNING: Subroutine does not return */
      _invalid_parameter_noinfo_noreturn();
    }
    pvVar17 = local_138;
    if (0xfff < uVar12 * 8) {
      if (((ulonglong)local_138 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      pvVar17 = *(void **)((longlong)local_138 + -8);
      if (local_138 <= pvVar17) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if ((ulonglong)((longlong)local_138 - (longlong)pvVar17) < 8) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if (0x27 < (ulonglong)((longlong)local_138 - (longlong)pvVar17)) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
    }
    operator_delete(pvVar17);
    goto LAB_1405f5077;
  }
  goto LAB_1405f5089;
LAB_1405f50a0:
  local_res20[0] = '\0';
  local_148 = (CSimpleStringT<char,1> *)&local_140;
  uVar10 = CTest::GetCompleteLibName((CTest *)(param_1 + 0x188));
  pAVar14 = AfxGetModuleState();
  uVar15 = __RTDynamicCast(*(undefined8 *)(pAVar14 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                           &CAVisionApp::RTTI_Type_Descriptor,0);
  FUN_1404d21e0(uVar15,uVar10,1,local_res20);
  if (local_res20[0] == '\0') {
    FUN_1405ea2c0(param_1);
  }
  cVar1 = FUN_1405febf0(param_1);
  if (((cVar1 != '\0') && (cVar1 = FUN_1405fed00(param_1,this), cVar1 != '\0')) &&
     ((pCVar11 == (CCAD_Base *)0x0 || (cVar1 = FUN_1405fed00(param_1,pCVar11), cVar1 != '\0')))) {
    FUN_1405f5660(param_1,0,iVar3,pCVar11 == (CCAD_Base *)0x0);
  }
  FUN_1405ff160(param_1);
  uVar10 = FUN_1405e04b0(&local_110);
  FUN_1405ccdf0(pCVar20,uVar10);
  local_d8 = CRecordComponents::vftable;
  CStringListe::~CStringListe(local_a0);
  CStringListe::~CStringListe(local_c8);
  if (local_f8 != (void *)0x0) {
    FUN_14057be20(&local_f8);
    local_f8 = (void *)0x0;
    uStack_f0 = 0;
    local_e8 = 0;
  }
  FUN_14056d6d0(&local_110);
  FUN_1405ea870(param_1);
  if (DAT_1410f5ad0 != 0) {
    CVitCognexConsoleDispatcher::PanAndFit_SetAllowPanInClientCoord
              ((CVitCognexConsoleDispatcher *)(DAT_1410f5ad0 + 0xa40),false);
  }
  if (0 < iVar3) {
    if (local_138 != (void *)0x0) {
      FUN_140579780(&local_138,local_138,local_128 - (longlong)local_138 >> 3);
      local_138 = (void *)0x0;
      lStack_130 = 0;
      local_128 = 0;
    }
    CLogManagerFunction::~CLogManagerFunction(local_70);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(param_2);
    return 1;
  }
  AfxMessageBox(0xd1b,0x10,0xffffffff);
  if (local_138 != (void *)0x0) {
    FUN_140579780(&local_138,local_138,local_128 - (longlong)local_138 >> 3);
    local_138 = (void *)0x0;
    lStack_130 = 0;
    local_128 = 0;
  }
  CLogManagerFunction::~CLogManagerFunction(local_70);
  goto LAB_1405f54ab;
  while (uVar13 = uVar13 + 1, uVar13 < uVar16) {
LAB_1405f4ea4:
    if (pCVar11 == *(CCAD_Base **)((longlong)local_138 + uVar13 * 8)) goto LAB_1405f50a0;
  }
LAB_1405f4eb6:
  pCVar7 = (CSimpleStringT<char,1> *)CCAD_Base::MsgSupportNotExecutable(this);
  pcVar8 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64(pCVar7);
  AfxMessageBox(pcVar8,0x10,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_140);
  uVar10 = FUN_1405e04b0(&local_110);
  FUN_1405ccdf0(pCVar20,uVar10);
  local_d8 = CRecordComponents::vftable;
  CStringListe::~CStringListe(local_a0);
  CStringListe::~CStringListe(local_c8);
  if (local_f8 != (void *)0x0) {
    uVar12 = local_e8 - (longlong)local_f8 >> 2;
    if (0x3fffffffffffffff < uVar12) {
                    /* WARNING: Subroutine does not return */
      _invalid_parameter_noinfo_noreturn();
    }
    pvVar17 = local_f8;
    if (0xfff < uVar12 * 4) {
      if (((ulonglong)local_f8 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      pvVar17 = *(void **)((longlong)local_f8 + -8);
      if (local_f8 <= pvVar17) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if ((ulonglong)((longlong)local_f8 - (longlong)pvVar17) < 8) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if (0x27 < (ulonglong)((longlong)local_f8 - (longlong)pvVar17)) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
    }
    operator_delete(pvVar17);
    local_f8 = (void *)0x0;
    uStack_f0 = 0;
    local_e8 = 0;
  }
  pCVar9 = local_110;
  if (local_110 != (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)0x0) {
    for (; pCVar9 != local_108; pCVar9 = pCVar9 + 8) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(pCVar9);
    }
    uVar12 = local_100 - (longlong)local_110 >> 3;
    if (0x1fffffffffffffff < uVar12) {
                    /* WARNING: Subroutine does not return */
      _invalid_parameter_noinfo_noreturn();
    }
    pCVar9 = local_110;
    if (0xfff < uVar12 * 8) {
      if (((ulonglong)local_110 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      pCVar9 = *(CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> **)(local_110 + -8);
      if (local_110 <= pCVar9) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if ((ulonglong)((longlong)local_110 - (longlong)pCVar9) < 8) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if (0x27 < (ulonglong)((longlong)local_110 - (longlong)pCVar9)) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
    }
    operator_delete(pCVar9);
  }
  FUN_1405ea870(param_1,0);
  if (local_138 != (void *)0x0) {
    FUN_140579780(&local_138,local_138,local_128 - (longlong)local_138 >> 3);
LAB_1405f5077:
    local_138 = (void *)0x0;
    lStack_130 = 0;
    local_128 = 0;
  }
LAB_1405f5089:
  CLogManagerFunction::~CLogManagerFunction(local_70);
LAB_1405f54ab:
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(param_2);
  return 0;
}

