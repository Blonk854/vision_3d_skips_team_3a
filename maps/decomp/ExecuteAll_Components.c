// ExecuteAll_Components @ 0x1407354b0
// function ExecuteAll_Components [1407354b0 ..]


undefined1
ExecuteAll_Components
          (longlong param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,
          undefined8 param_5,undefined8 param_6)

{
  longlong *plVar1;
  double dVar2;
  longlong lVar3;
  longlong *plVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  undefined4 uVar8;
  undefined8 *puVar9;
  undefined8 *puVar10;
  ulonglong *puVar11;
  void *pvVar12;
  undefined1 uVar13;
  ulonglong uVar14;
  ulonglong in_stack_fffffffffffffec8;
  undefined4 uVar16;
  undefined8 uVar15;
  undefined4 uVar17;
  undefined8 in_stack_fffffffffffffed0;
  undefined8 uVar18;
  undefined1 local_f8;
  longlong *local_f0;
  void *local_e8;
  longlong lStack_e0;
  longlong local_d8;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_d0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_c8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_c0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_b8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_b0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_a8 [8];
  undefined8 local_a0;
  ccTimer local_98 [32];
  CLogManagerFunctionML local_78 [64];
  
  local_a0 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_f0,
             "CZoneAnalysis::ExecuteAll_Components");
  in_stack_fffffffffffffec8 = in_stack_fffffffffffffec8 & 0xffffffffffffff00;
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_78,0x10,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_f0,
             (ulonglong)*(uint *)(*(longlong *)(param_1 + 0x10) + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_f0);
  uVar13 = 1;
  local_f8 = 1;
  FUN_14052b260(param_2,&local_e8,1);
  uVar14 = 0;
  if (lStack_e0 - (longlong)local_e8 >> 3 != 0) {
    do {
      iVar5 = (**(code **)(**(longlong **)((longlong)local_e8 + uVar14 * 8) + 200))();
      uVar16 = (undefined4)((ulonglong)in_stack_fffffffffffffed0 >> 0x20);
      if (iVar5 == 0) {
        local_f0 = (longlong *)0x0;
        plVar1 = *(longlong **)((longlong)local_e8 + uVar14 * 8);
        if ((int)plVar1[2] != -1) {
          local_f0 = (longlong *)
                     ((longlong)(int)plVar1[2] * 0x370 +
                     *(longlong *)
                      ((longlong)*(int *)(*(longlong *)(param_1 + 0x10) + 0x5c9c) * 0x410 + 0x18 +
                      *(longlong *)(*(longlong *)(param_1 + 0x10) + 0x5878)));
        }
        plVar4 = local_f0;
        iVar5 = (**(code **)(*plVar1 + 0xe8))(plVar1);
        uVar16 = (undefined4)(in_stack_fffffffffffffec8 >> 0x20);
        uVar8 = (undefined4)((ulonglong)in_stack_fffffffffffffed0 >> 0x20);
        if (iVar5 == 0) {
          if (plVar4 != (longlong *)0x0) {
            ccTimer::ccTimer(local_98,false);
            ccTimer::start(local_98);
            puVar9 = (undefined8 *)(**(code **)(*plVar1 + 0x60))(plVar1,local_c8);
            puVar10 = (undefined8 *)(**(code **)(*plVar1 + 0x48))(plVar1,local_d0);
            uVar17 = *(undefined4 *)((longlong)plVar1 + 0x14);
            uVar6 = (**(code **)(*plVar1 + 0x98))(plVar1);
            CLogManagerFunctionML::Write
                      (local_78,2,
                       "Index %03Id Zone %03d Sub-panel %02d Component %s JEDEC %s Tri 0\n",param_4,
                       CONCAT44(uVar16,uVar6),CONCAT44(uVar8,uVar17),*puVar10,*puVar9);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_d0);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_c8);
            uVar15 = param_6;
            uVar18 = param_4;
            uVar7 = ExecuteOne_Component(param_1,param_3,param_5,plVar4,param_6,param_4,plVar1);
            uVar17 = (undefined4)((ulonglong)uVar15 >> 0x20);
            uVar6 = (undefined4)((ulonglong)uVar18 >> 0x20);
            ccTimer::stop(local_98);
            puVar9 = (undefined8 *)(**(code **)(*plVar1 + 0x60))(plVar1,local_b8);
            puVar10 = (undefined8 *)(**(code **)(*plVar1 + 0x48))(plVar1,local_c0);
            lVar3 = local_f0[0x58];
            uVar16 = *(undefined4 *)((longlong)plVar1 + 0x14);
            dVar2 = ccTimer::msec(local_98);
            uVar8 = (**(code **)(*plVar1 + 0x98))(plVar1);
            in_stack_fffffffffffffed0 = CONCAT44(uVar6,uVar16);
            in_stack_fffffffffffffec8 = CONCAT44(uVar17,uVar8);
            CLogManagerFunctionML::Write
                      (local_78,2,
                       "Index %03Id Zone %03d Sub-panel %02d Component %s JEDEC %s Tri 1 Returned 0x%08X ModelCount %d Time_ms %.2lf\n"
                       ,param_4,in_stack_fffffffffffffec8,in_stack_fffffffffffffed0,*puVar10,*puVar9
                       ,uVar7,(int)lVar3,dVar2);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_c0);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_b8);
            uVar13 = local_f8;
            if ((uVar7 & 0x1ff07df) != 0) {
              local_f8 = 0;
              uVar13 = 0;
            }
          }
        }
        else {
          puVar11 = (ulonglong *)(**(code **)(*plVar1 + 0x48))(plVar1,local_b0);
          in_stack_fffffffffffffed0 = CONCAT44(uVar8,*(undefined4 *)((longlong)plVar1 + 0x14));
          in_stack_fffffffffffffec8 = *puVar11;
          CLogManagerFunctionML::Write
                    (local_78,2,
                     "Zone index %Id, Component \'%s\' on sub-panel #%d has been skipped by operator (index comp %Id)\n"
                     ,param_4,in_stack_fffffffffffffec8,in_stack_fffffffffffffed0,uVar14);
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
          ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_b0);
          (**(code **)(*plVar4 + 0x48))(plVar4);
          *(undefined4 *)((longlong)plVar4 + 0x2c) = 1;
        }
      }
      else {
        plVar1 = *(longlong **)((longlong)local_e8 + uVar14 * 8);
        puVar11 = (ulonglong *)(**(code **)(*plVar1 + 0x48))(plVar1,local_a8);
        in_stack_fffffffffffffed0 =
             CONCAT44(uVar16,*(undefined4 *)(*(longlong *)((longlong)local_e8 + uVar14 * 8) + 0x14))
        ;
        in_stack_fffffffffffffec8 = *puVar11;
        CLogManagerFunctionML::Write
                  (local_78,2,
                   "Zone index %Id, Component \'%s\' on sub-panel #%d is skipped (index comp %Id)\n"
                   ,param_4,in_stack_fffffffffffffec8,in_stack_fffffffffffffed0,uVar14);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_a8);
      }
      uVar14 = uVar14 + 1;
    } while (uVar14 < (ulonglong)(lStack_e0 - (longlong)local_e8 >> 3));
  }
  if (local_e8 != (void *)0x0) {
    uVar14 = local_d8 - (longlong)local_e8 >> 3;
    if (0x1fffffffffffffff < uVar14) {
                    /* WARNING: Subroutine does not return */
      _invalid_parameter_noinfo_noreturn();
    }
    pvVar12 = local_e8;
    if (0xfff < uVar14 * 8) {
      if (((ulonglong)local_e8 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      pvVar12 = *(void **)((longlong)local_e8 + -8);
      if (local_e8 <= pvVar12) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if ((ulonglong)((longlong)local_e8 - (longlong)pvVar12) < 8) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if (0x27 < (ulonglong)((longlong)local_e8 - (longlong)pvVar12)) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
    }
    operator_delete(pvVar12);
    local_e8 = (void *)0x0;
    lStack_e0 = 0;
    local_d8 = 0;
  }
  CLogManagerFunctionML::~CLogManagerFunctionML(local_78);
  return uVar13;
}

