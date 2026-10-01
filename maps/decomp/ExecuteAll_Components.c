// ExecuteAll_Components @ 0x1407354b0
// function FUN_1407354b0 [1407354b0 ..]


ulonglong FUN_1407354b0(longlong param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,
                       undefined8 param_5,undefined8 param_6)

{
  longlong *plVar1;
  code *pcVar2;
  longlong lVar3;
  longlong *plVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  undefined4 uVar8;
  undefined8 *puVar9;
  undefined8 *puVar10;
  ulonglong *puVar11;
  ulonglong uVar12;
  byte bVar13;
  ulonglong uVar14;
  ulonglong in_stack_fffffffffffffec8;
  undefined4 uVar16;
  undefined8 uVar15;
  undefined4 uVar17;
  undefined8 in_stack_fffffffffffffed0;
  undefined8 uVar18;
  byte bStack_f8;
  longlong *plStack_f0;
  ulonglong uStack_e8;
  longlong lStack_e0;
  longlong lStack_d8;
  undefined1 auStack_d0 [8];
  undefined1 auStack_c8 [8];
  undefined1 auStack_c0 [8];
  undefined1 auStack_b8 [8];
  undefined1 auStack_b0 [8];
  undefined1 auStack_a8 [8];
  undefined8 uStack_a0;
  undefined1 auStack_98 [32];
  undefined1 auStack_78 [64];
  
  uStack_a0 = 0xfffffffffffffffe;
  __0__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL__QEAA_PEBD_Z
            (&plStack_f0,&UNK_140ecfbc0);
  in_stack_fffffffffffffec8 = in_stack_fffffffffffffec8 & 0xffffffffffffff00;
  __0CLogManagerFunctionML__QEAA_W4ELogManagerStateModule__AEBV__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL___K_N_Z
            (auStack_78,0x10,&plStack_f0,*(undefined4 *)(*(longlong *)(param_1 + 0x10) + 0x3924),
             in_stack_fffffffffffffec8);
  __1__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL__QEAA_XZ(&plStack_f0);
  bVar13 = 1;
  bStack_f8 = 1;
  FUN_14052b260(param_2,&uStack_e8,1);
  uVar14 = 0;
  if ((longlong)(lStack_e0 - uStack_e8) >> 3 != 0) {
    do {
      iVar5 = (**(code **)(**(longlong **)(uStack_e8 + uVar14 * 8) + 200))();
      uVar16 = (undefined4)((ulonglong)in_stack_fffffffffffffed0 >> 0x20);
      if (iVar5 == 0) {
        plStack_f0 = (longlong *)0x0;
        plVar1 = *(longlong **)(uStack_e8 + uVar14 * 8);
        if ((int)plVar1[2] != -1) {
          plStack_f0 = (longlong *)
                       ((longlong)(int)plVar1[2] * 0x370 +
                       *(longlong *)
                        ((longlong)*(int *)(*(longlong *)(param_1 + 0x10) + 0x5c9c) * 0x410 + 0x18 +
                        *(longlong *)(*(longlong *)(param_1 + 0x10) + 0x5878)));
        }
        plVar4 = plStack_f0;
        iVar5 = (**(code **)(*plVar1 + 0xe8))(plVar1);
        uVar16 = (undefined4)(in_stack_fffffffffffffec8 >> 0x20);
        uVar8 = (undefined4)((ulonglong)in_stack_fffffffffffffed0 >> 0x20);
        if (iVar5 == 0) {
          if (plVar4 != (longlong *)0x0) {
            __0ccTimer__QEAA__N_Z(auStack_98,0);
            _start_ccTimer__QEAAXXZ(auStack_98);
            puVar9 = (undefined8 *)(**(code **)(*plVar1 + 0x60))(plVar1,auStack_c8);
            puVar10 = (undefined8 *)(**(code **)(*plVar1 + 0x48))(plVar1,auStack_d0);
            uVar17 = *(undefined4 *)((longlong)plVar1 + 0x14);
            uVar6 = (**(code **)(*plVar1 + 0x98))(plVar1);
            _Write_CLogManagerFunctionML__UEAA_NW4ELogManagerStateLevel__PEBDZZ
                      (auStack_78,2,&UNK_140ecfa60,param_4,CONCAT44(uVar16,uVar6),
                       CONCAT44(uVar8,uVar17),*puVar10,*puVar9);
            __1__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL__QEAA_XZ(auStack_d0);
            __1__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL__QEAA_XZ(auStack_c8);
            uVar15 = param_6;
            uVar18 = param_4;
            uVar7 = FUN_1407368d0(param_1,param_3,param_5,plVar4,param_6,param_4,plVar1);
            uVar17 = (undefined4)((ulonglong)uVar15 >> 0x20);
            uVar6 = (undefined4)((ulonglong)uVar18 >> 0x20);
            _stop_ccTimer__QEAAXXZ(auStack_98);
            puVar9 = (undefined8 *)(**(code **)(*plVar1 + 0x60))(plVar1,auStack_b8);
            puVar10 = (undefined8 *)(**(code **)(*plVar1 + 0x48))(plVar1,auStack_c0);
            lVar3 = plStack_f0[0x58];
            uVar16 = *(undefined4 *)((longlong)plVar1 + 0x14);
            uVar15 = _msec_ccTimer__QEBANXZ(auStack_98);
            uVar8 = (**(code **)(*plVar1 + 0x98))(plVar1);
            in_stack_fffffffffffffed0 = CONCAT44(uVar6,uVar16);
            in_stack_fffffffffffffec8 = CONCAT44(uVar17,uVar8);
            _Write_CLogManagerFunctionML__UEAA_NW4ELogManagerStateLevel__PEBDZZ
                      (auStack_78,2,&UNK_140ecfbf0,param_4,in_stack_fffffffffffffec8,
                       in_stack_fffffffffffffed0,*puVar10,*puVar9,uVar7,(int)lVar3,uVar15);
            __1__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL__QEAA_XZ(auStack_c0);
            __1__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL__QEAA_XZ(auStack_b8);
            bVar13 = bStack_f8;
            if ((uVar7 & 0x1ff07df) != 0) {
              bStack_f8 = 0;
              bVar13 = 0;
            }
          }
        }
        else {
          puVar11 = (ulonglong *)(**(code **)(*plVar1 + 0x48))(plVar1,auStack_b0);
          in_stack_fffffffffffffed0 = CONCAT44(uVar8,*(undefined4 *)((longlong)plVar1 + 0x14));
          in_stack_fffffffffffffec8 = *puVar11;
          _Write_CLogManagerFunctionML__UEAA_NW4ELogManagerStateLevel__PEBDZZ
                    (auStack_78,2,&UNK_140ecfc60,param_4,in_stack_fffffffffffffec8,
                     in_stack_fffffffffffffed0,uVar14);
          __1__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL__QEAA_XZ(auStack_b0);
          (**(code **)(*plVar4 + 0x48))(plVar4);
          *(undefined4 *)((longlong)plVar4 + 0x2c) = 1;
        }
      }
      else {
        plVar1 = *(longlong **)(uStack_e8 + uVar14 * 8);
        puVar11 = (ulonglong *)(**(code **)(*plVar1 + 0x48))(plVar1,auStack_a8);
        in_stack_fffffffffffffed0 =
             CONCAT44(uVar16,*(undefined4 *)(*(longlong *)(uStack_e8 + uVar14 * 8) + 0x14));
        in_stack_fffffffffffffec8 = *puVar11;
        _Write_CLogManagerFunctionML__UEAA_NW4ELogManagerStateLevel__PEBDZZ
                  (auStack_78,2,&UNK_140ecfcc0,param_4,in_stack_fffffffffffffec8,
                   in_stack_fffffffffffffed0,uVar14);
        __1__CStringT_DV__StrTraitMFC_DLL_DV__ChTraitsCRT_D_ATL_____ATL__QEAA_XZ(auStack_a8);
      }
      uVar14 = uVar14 + 1;
    } while (uVar14 < (ulonglong)((longlong)(lStack_e0 - uStack_e8) >> 3));
  }
  if (uStack_e8 != 0) {
    uVar14 = (longlong)(lStack_d8 - uStack_e8) >> 3;
    if (0x1fffffffffffffff < uVar14) {
      _invalid_parameter_noinfo_noreturn();
      pcVar2 = (code *)swi(3);
      uVar14 = (*pcVar2)();
      return uVar14;
    }
    uVar12 = uStack_e8;
    if (0xfff < uVar14 * 8) {
      if ((uStack_e8 & 0x1f) != 0) {
        _invalid_parameter_noinfo_noreturn();
        pcVar2 = (code *)swi(3);
        uVar14 = (*pcVar2)();
        return uVar14;
      }
      uVar12 = *(ulonglong *)(uStack_e8 - 8);
      if (uStack_e8 <= uVar12) {
        _invalid_parameter_noinfo_noreturn();
        pcVar2 = (code *)swi(3);
        uVar14 = (*pcVar2)();
        return uVar14;
      }
      if (uStack_e8 - uVar12 < 8) {
        _invalid_parameter_noinfo_noreturn();
        pcVar2 = (code *)swi(3);
        uVar14 = (*pcVar2)();
        return uVar14;
      }
      if (0x27 < uStack_e8 - uVar12) {
        _invalid_parameter_noinfo_noreturn();
        pcVar2 = (code *)swi(3);
        uVar14 = (*pcVar2)();
        return uVar14;
      }
    }
    func_0x00014077f4ae(uVar12);
    uStack_e8 = 0;
    lStack_e0 = 0;
    lStack_d8 = 0;
  }
  __1CLogManagerFunctionML__UEAA_XZ(auStack_78);
  return (ulonglong)bVar13;
}

