// PrepareResultsAndAskComThreadToSend @ 0x14068fab0
// function FUN_14068fab0 [14068fab0 ..]


undefined8 FUN_14068fab0(longlong param_1,ulonglong *param_2)

{
  int *piVar1;
  undefined8 *puVar2;
  void *pvVar3;
  code *pcVar4;
  char cVar5;
  bool bVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  CPanel *this;
  __uint64 _Var9;
  CCarteId *pCVar10;
  undefined8 *puVar11;
  ulonglong uVar12;
  undefined8 uVar13;
  CSimpleStringT<char,1> *pCVar14;
  AFX_MODULE_STATE *pAVar15;
  longlong lVar16;
  int iVar17;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *this_00;
  longlong *plVar18;
  __uint64 _Var19;
  CAnomalie *this_01;
  uint uVar20;
  void *pvVar21;
  char *pcVar22;
  ulonglong uVar23;
  longlong lVar24;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res8 [8];
  ulonglong *local_res10;
  int local_res18 [2];
  uint local_res20 [2];
  undefined8 in_stack_fffffffffffffea8;
  ulonglong uVar25;
  ulonglong local_148;
  undefined4 local_140 [2];
  __time64_t local_138;
  __uint64 local_130;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_128 [8];
  longlong local_120;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_118 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_110 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_108 [8];
  CLogManagerFunctionML local_100 [56];
  undefined **local_c8;
  ulonglong local_c0;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_b8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_b0 [8];
  CViUnitAngle local_a8 [40];
  undefined4 local_80;
  undefined4 local_7c;
  uint local_78;
  undefined8 local_68;
  undefined1 local_60 [32];
  
  local_68 = 0xfffffffffffffffe;
  local_res10 = param_2;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_128,"CProductionDoc::PrepareResultsAndAskComThreadToSend");
  uVar25 = CONCAT71((int7)((ulonglong)in_stack_fffffffffffffea8 >> 8),1);
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_100,0x10,local_128,(ulonglong)*(uint *)(param_1 + 0x3924),true);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_128);
  this = CMsgPanel::_Panel_Ptr((CMsgPanel *)(param_1 + 24000),0);
  lVar24 = (longlong)*(int *)(param_1 + 0x5c98) * 0x410 + *(longlong *)(param_1 + 0x5878);
  _Var19 = 0;
  if (this == (CPanel *)0x0) {
    ReleaseSemaphore(*(HANDLE *)(param_1 + 0x3890),1,(LPLONG)0x0);
  }
  else {
    *(undefined4 *)(this + 0x180) = *(undefined4 *)(lVar24 + 0xac);
    _Var9 = CPanel::Carte_GetNumber(this);
    local_130 = _Var9;
    if (0 < (longlong)_Var9) {
      do {
        pCVar10 = CPanel::CarteIndex(this,_Var19);
        if (pCVar10 != (CCarteId *)0x0) {
          uVar7 = FUN_140671710(lVar24,_Var19);
          *(undefined4 *)(pCVar10 + 0x34) = uVar7;
        }
        _Var19 = _Var19 + 1;
      } while ((longlong)_Var19 < (longlong)_Var9);
    }
    uVar20 = *(uint *)(this + 0x180) & 0x400;
    bVar6 = false;
    local_res8[0] = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>)0x0;
    if ((DAT_1410bf544 != 0) && (uVar20 == 0)) {
      piVar1 = (int *)(param_1 + 0x393c);
      *piVar1 = *piVar1 + -1;
      if (*piVar1 == 0) {
        bVar6 = true;
        local_res8[0] = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>)0x1;
        *(int *)(param_1 + 0x393c) = DAT_1410bf544;
      }
    }
    pcVar22 = "true";
    if (!bVar6) {
      pcVar22 = "false";
    }
    local_res20[0] = uVar20;
    CLogManagerFunctionML::Write(local_100,2,"bSendStatsToSupervisor = \'%s\'.\n",pcVar22);
    if ((DAT_1411697f8 == 0) || (local_res18[0] = 1, uVar20 != 0)) {
      local_res18[0] = 0;
    }
    local_148 = (*(longlong *)(lVar24 + 0x20) - *(longlong *)(lVar24 + 0x18)) / 0x370;
    uVar23 = 0;
    if (local_148 != 0) {
      local_120 = 0;
      do {
        if ((ulonglong)((*(longlong *)(lVar24 + 0x20) - *(longlong *)(lVar24 + 0x18)) / 0x370) <=
            uVar23) {
          std::_Xout_of_range("invalid vector<T> subscript");
          pcVar4 = (code *)swi(3);
          uVar13 = (*pcVar4)();
          return uVar13;
        }
        this_01 = (CAnomalie *)(local_120 + *(longlong *)(lVar24 + 0x18));
        if (this_01 != (CAnomalie *)0x0) {
          pCVar10 = CPanel::Carte(this,*(long *)(this_01 + 8));
          iVar17 = *(int *)(pCVar10 + 0x18);
          if (iVar17 < 1) {
            iVar17 = *(int *)(pCVar10 + 0x14);
          }
          *(int *)(pCVar10 + 0x18) = iVar17 + *(int *)(this_01 + 0x36c);
          *(uint *)(this_01 + 0x28) = *(uint *)(this_01 + 0x28) & 0x1ff07df;
          *(undefined4 *)(this_01 + 0x158) = 0;
          if (local_res20[0] == 0) {
            cVar5 = (**(code **)(*(longlong *)this_01 + 0x30))(this_01);
            uVar7 = (undefined4)(uVar25 >> 0x20);
            if (cVar5 == '\x01') {
              CCarteId::TestedObjects_Add(pCVar10,this_01);
              if (((local_res18[0] == 0) || (*(longlong *)(this_01 + 400) == 0)) ||
                 (*(longlong *)(this_01 + 0x198) == 0)) {
                uVar8 = 0;
              }
              else {
                uVar8 = 1;
              }
              *(undefined4 *)(this_01 + 0x158) = uVar8;
              puVar11 = (undefined8 *)(**(code **)(*(longlong *)this_01 + 0xa8))(this_01,local_118);
              uVar25 = CONCAT44(uVar7,*(undefined4 *)(this_01 + 0x2c));
              CLogManagerFunctionML::Write
                        (local_100,2,"IsFaulty = <%s> InspectedCause = %d Error = %d\n",*puVar11,
                         uVar25,*(undefined4 *)(this_01 + 0x28));
              this_00 = local_118;
            }
            else {
              iVar17 = *(int *)(this_01 + 0x2c);
              if (iVar17 < 1) {
                if ((iVar17 != 0) ||
                   (((*(int *)(this_01 + 0x128) != 1 ||
                     (local_res8[0] !=
                      (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>)0x1)) &&
                    (*(char *)(param_1 + 0x3822) != '\x01')))) {
                  if (iVar17 == -1) {
                    uVar12 = FUN_140671710(lVar24);
                    uVar7 = (undefined4)(uVar25 >> 0x20);
                    if ((uVar12 & 0x901) == 0) {
                      puVar11 = (undefined8 *)CAnomalie::_csTopo(this_01);
                      uVar25 = CONCAT44(uVar7,*(undefined4 *)(this_01 + 8));
                      CLogManagerFunctionML::Write
                                (local_100,4,
                                 "TestedObject.NotInspectedCause == nicUNDEFINED for component %s (sub-panel %d) while it has been inspected"
                                 ,*puVar11,uVar25);
                      this_00 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                                &local_138;
                      goto LAB_14068fe89;
                    }
                  }
                  goto LAB_14068fe9d;
                }
                CCarteId::TestedObjects_Add(pCVar10,this_01);
                puVar11 = (undefined8 *)
                          (**(code **)(*(longlong *)this_01 + 0xa8))(this_01,local_108);
                CLogManagerFunctionML::Write(local_100,2,"Statistical = <%s>.\n",*puVar11);
                this_00 = local_108;
              }
              else {
                if (*(char *)(param_1 + 0x382f) != '\x01') goto LAB_14068fe9d;
                CCarteId::TestedObjects_Add(pCVar10,this_01);
                puVar11 = (undefined8 *)
                          (**(code **)(*(longlong *)this_01 + 0xa8))(this_01,local_110);
                uVar25 = CONCAT44(uVar7,*(undefined4 *)(this_01 + 0x2c));
                CLogManagerFunctionML::Write
                          (local_100,2,"tNotInspectedCause = <%s> Cause = %d.\n",*puVar11,uVar25);
                this_00 = local_110;
              }
            }
LAB_14068fe89:
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(this_00);
          }
        }
LAB_14068fe9d:
        uVar23 = uVar23 + 1;
        local_120 = local_120 + 0x370;
        uVar20 = local_res20[0];
      } while (uVar23 < local_148);
    }
    if (uVar20 == 0) {
      FUN_140685e50(param_1,lVar24,this,local_res18[0]);
    }
    _Var19 = local_130;
    _Var9 = 0;
    if (0 < (longlong)local_130) {
      do {
        uVar7 = FUN_140671540(lVar24,_Var9);
        pCVar10 = CPanel::CarteIndex(this,_Var9);
        *(undefined4 *)(pCVar10 + 0x14) = uVar7;
        uVar7 = FUN_140671340(lVar24,_Var9);
        pCVar10 = CPanel::CarteIndex(this,_Var9);
        *(undefined4 *)(pCVar10 + 0x20) = uVar7;
        uVar7 = FUN_1406711b0(lVar24,_Var9);
        pCVar10 = CPanel::CarteIndex(this,_Var9);
        *(undefined4 *)(pCVar10 + 0x1c) = uVar7;
        uVar7 = FUN_140670f70(lVar24,_Var9);
        pCVar10 = CPanel::CarteIndex(this,_Var9);
        *(undefined4 *)(pCVar10 + 0x24) = uVar7;
        uVar7 = FUN_140670fa0(lVar24,_Var9);
        pCVar10 = CPanel::CarteIndex(this,_Var9);
        *(undefined4 *)(pCVar10 + 0x28) = uVar7;
        uVar7 = FUN_140670fd0(lVar24,_Var9);
        pCVar10 = CPanel::CarteIndex(this,_Var9);
        *(undefined4 *)(pCVar10 + 0x2c) = uVar7;
        uVar7 = FUN_140670f40(lVar24,_Var9);
        pCVar10 = CPanel::CarteIndex(this,_Var9);
        *(undefined4 *)(pCVar10 + 0x30) = uVar7;
        _Var9 = _Var9 + 1;
      } while ((longlong)_Var9 < (longlong)_Var19);
    }
    uVar7 = FUN_1406714e0(lVar24);
    *(undefined4 *)(this + 0x188) = uVar7;
    uVar7 = FUN_140671300(lVar24);
    *(undefined4 *)(this + 0x18c) = uVar7;
    uVar7 = FUN_140671150(lVar24);
    *(undefined4 *)(this + 400) = uVar7;
    CPanel::UpdateStatus(this,0);
    local_140[0] = 2;
    uVar23 = *param_2;
    if (uVar23 != param_2[1]) {
      do {
        local_c8 = ViIdentification::CIdentificationProgramResult::vftable;
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_c0,
                   (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                   (uVar23 + 8));
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  (local_b8,(CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                             *)(uVar23 + 0x10));
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  (local_b0,(CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                             *)(uVar23 + 0x18));
        CViUnitAngle::CViUnitAngle(local_a8,(CViUnitAngle *)(uVar23 + 0x20));
        local_80 = *(undefined4 *)(uVar23 + 0x48);
        local_7c = *(undefined4 *)(uVar23 + 0x4c);
        local_78 = *(uint *)(uVar23 + 0x50);
        if (local_78 == 0) {
          CLogManagerFunctionML::Write(local_100,2,"Panel ID code = \'%s\'.\n",local_c0);
          uVar13 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                   CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                             (local_res8,
                              (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                               *)&local_c0);
          CPanel::_csCB(this,uVar13);
          local_140[0] = local_7c;
        }
        else {
          pCVar10 = CPanel::CarteIndex(this,(longlong)(int)(local_78 - 1));
          if (pCVar10 != (CCarteId *)0x0) {
            uVar25 = local_c0;
            CLogManagerFunctionML::Write
                      (local_100,2,"Sub-panel %d ID code = \'%s\'.\n",(ulonglong)local_78,local_c0);
            uVar13 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                     CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                               ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                                local_res18,
                                (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                 *)&local_c0);
            CCarteId::_csCB(pCVar10,uVar13);
          }
        }
        uVar23 = uVar23 + 0x58;
        local_c8 = ViIdentification::CIdentificationProgramResult::vftable;
        CViUnitAngle::_vbase_destructor_(local_a8);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_b0);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_b8);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_c0);
        _Var19 = local_130;
      } while (uVar23 != param_2[1]);
    }
    pCVar14 = (CSimpleStringT<char,1> *)CPanel::_csCB(this);
    bVar6 = ATL::CSimpleStringT<char,1>::IsEmpty(pCVar14);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
    if (bVar6) {
      CLogManagerFunctionML::Write(local_100,4,"BUG: the panel ID code is empty.\n");
      CIniFileAvivion_Parameter::CIniFileAvivion_Parameter((CIniFileAvivion_Parameter *)&local_c8);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_res18,
                 "CB default format");
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8,"Production");
      CIniFileBase::GetValeurIni_cs
                ((CIniFileBase *)&local_c8,
                 (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                 local_res20,
                 (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                 local_res8);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_res18);
      local_138 = _time64((__time64_t *)0x0);
      pcVar22 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64
                          ((CSimpleStringT<char,1> *)local_res20);
      uVar13 = FUN_140493160(&local_138,&local_148,pcVar22);
      CPanel::_csCB(this,uVar13);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_res20);
      CIniFileAvivion_Parameter::~CIniFileAvivion_Parameter((CIniFileAvivion_Parameter *)&local_c8);
    }
    _Var9 = 0;
    if (0 < (longlong)_Var19) {
      do {
        pCVar10 = CPanel::CarteIndex(this,_Var9);
        if (pCVar10 != (CCarteId *)0x0) {
          pCVar14 = (CSimpleStringT<char,1> *)CCarteId::_csCB(pCVar10);
          bVar6 = ATL::CSimpleStringT<char,1>::IsEmpty(pCVar14);
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
          ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                    ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_res18);
          if (bVar6) {
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
            puVar11 = (undefined8 *)CPanel::_csCB(this);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                      (local_res8,"%s_%d",*puVar11,(ulonglong)*(uint *)(pCVar10 + 0x10));
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_res20)
            ;
            uVar13 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                     CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                               ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                                &local_148,
                                (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                 *)local_res8);
            CCarteId::_csCB(pCVar10,uVar13);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
          }
        }
        _Var9 = _Var9 + 1;
        _Var19 = local_130;
      } while ((longlong)_Var9 < (longlong)local_130);
    }
    FUN_1406819a0(param_1,lVar24 + 0x18,_Var19,this);
    *(undefined8 *)(this + 0x158) = *(undefined8 *)(lVar24 + 0x30);
    *(undefined8 *)(this + 0x170) = *(undefined8 *)(lVar24 + 0x38);
    uVar13 = FUN_1405b3d90(lVar24,local_res8);
    CPanel::_csMsgForRepairOperator(this,uVar13);
    if (*(int *)(param_1 + 0x3928) - 3U < 2) {
      *(undefined4 *)(this + 0x50) = 1;
    }
    else {
      *(int *)(this + 0x50) = *(int *)(param_1 + 0x3924) + 1;
    }
    *(undefined4 *)(this + 0x10) = *(undefined4 *)(lVar24 + 0x200);
    uVar13 = FUN_1405b3f70(lVar24,local_res8);
    CPanel::_csFace(this,uVar13);
    bVar6 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)(param_1 + 0x61e0));
    if (!bVar6) {
      uVar13 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
               CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                         (local_res8,
                          (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                           *)(param_1 + 0x61e0));
      CPanel::_csProdInfo(this,uVar13);
    }
    uVar13 = FUN_1405b4180(lVar24,local_res8);
    CPanel::_csPanelInfo(this,uVar13);
    pAVar15 = AfxGetModuleState();
    lVar16 = __RTDynamicCast(*(undefined8 *)(pAVar15 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                             &CAVisionApp::RTTI_Type_Descriptor,uVar25 & 0xffffffff00000000);
    plVar18 = (longlong *)(lVar16 + 0x1b0);
    if (lVar16 == -0x1a8) {
      plVar18 = (longlong *)0x0;
    }
    (**(code **)(*plVar18 + 0x90))(plVar18,*(undefined4 *)(param_1 + 0x3928),this,local_140);
    if (*(longlong *)(param_1 + 0x3860) == 0) {
      CLogManagerFunctionML::Write(local_100,4,"m_pCommunicationThread == 0.");
      CLogManagerFunctionML::~CLogManagerFunctionML(local_100);
      puVar11 = (undefined8 *)*param_2;
      if (puVar11 != (undefined8 *)0x0) {
        puVar2 = (undefined8 *)param_2[1];
        for (; puVar11 != puVar2; puVar11 = puVar11 + 0xb) {
          (**(code **)*puVar11)(puVar11,0);
        }
        pvVar3 = (void *)*param_2;
        uVar25 = (longlong)(param_2[2] - (longlong)pvVar3) / 0x58;
        if (0x2e8ba2e8ba2e8ba < uVar25) {
                    /* WARNING: Subroutine does not return */
          _invalid_parameter_noinfo_noreturn();
        }
        pvVar21 = pvVar3;
        if (0xfff < uVar25 * 0x58) {
          if (((ulonglong)pvVar3 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            _invalid_parameter_noinfo_noreturn();
          }
          pvVar21 = *(void **)((longlong)pvVar3 - 8);
          if (pvVar3 <= pvVar21) {
                    /* WARNING: Subroutine does not return */
            _invalid_parameter_noinfo_noreturn();
          }
          if ((ulonglong)((longlong)pvVar3 - (longlong)pvVar21) < 8) {
                    /* WARNING: Subroutine does not return */
            _invalid_parameter_noinfo_noreturn();
          }
          if (0x27 < (ulonglong)((longlong)pvVar3 - (longlong)pvVar21)) {
                    /* WARNING: Subroutine does not return */
            _invalid_parameter_noinfo_noreturn();
          }
        }
        operator_delete(pvVar21);
        *param_2 = 0;
        param_2[1] = 0;
        param_2[2] = 0;
      }
      return 0;
    }
    FUN_14067c710(param_1 + 24000,*(undefined1 *)(lVar24 + 0x40));
    FUN_14067c5b0(*(undefined8 *)(param_1 + 0x3860));
  }
  uVar13 = FUN_14066d8f0(local_60,param_2);
  FUN_14068ee40(param_1,uVar13);
  CLogManagerFunctionML::~CLogManagerFunctionML(local_100);
  puVar11 = (undefined8 *)*param_2;
  if (puVar11 != (undefined8 *)0x0) {
    puVar2 = (undefined8 *)param_2[1];
    for (; puVar11 != puVar2; puVar11 = puVar11 + 0xb) {
      (**(code **)*puVar11)(puVar11,0);
    }
    pvVar3 = (void *)*param_2;
    uVar25 = (longlong)(param_2[2] - (longlong)pvVar3) / 0x58;
    if (0x2e8ba2e8ba2e8ba < uVar25) {
                    /* WARNING: Subroutine does not return */
      _invalid_parameter_noinfo_noreturn();
    }
    pvVar21 = pvVar3;
    if (0xfff < uVar25 * 0x58) {
      if (((ulonglong)pvVar3 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      pvVar21 = *(void **)((longlong)pvVar3 - 8);
      if (pvVar3 <= pvVar21) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if ((ulonglong)((longlong)pvVar3 - (longlong)pvVar21) < 8) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if (0x27 < (ulonglong)((longlong)pvVar3 - (longlong)pvVar21)) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
    }
    operator_delete(pvVar21);
    *param_2 = 0;
    param_2[1] = 0;
    param_2[2] = 0;
  }
  return 1;
}

