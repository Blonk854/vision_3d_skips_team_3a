// vt off=0x1590 FUN_140467c50 @ 140467c50


longlong * FUN_140467c50(longlong param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  undefined8 uVar1;
  longlong *plVar2;
  void *pvVar3;
  char *pcVar4;
  longlong lVar5;
  void *local_30 [3];
  ulonglong local_18;
  
  if (*(longlong *)(param_1 + 0x38) != 0) goto LAB_140467d4f;
  pcVar4 = *(char **)(param_1 + 8);
  if (pcVar4 == (char *)0x0) {
    pcVar4 = "Unknown exception";
LAB_140467c90:
    lVar5 = -1;
    do {
      lVar5 = lVar5 + 1;
    } while (pcVar4[lVar5] != '\0');
  }
  else {
    if (*pcVar4 != '\0') goto LAB_140467c90;
    lVar5 = 0;
  }
  FUN_14045f320(param_1 + 0x28,pcVar4,lVar5,param_4,0xfffffffffffffffe);
  if (*(longlong *)(param_1 + 0x38) != 0) {
    FUN_14045f0a0(param_1 + 0x28,&DAT_140dd881c,2);
  }
  uVar1 = FUN_1404661c0(param_1 + 0x18,local_30);
  FUN_14045ef80(param_1 + 0x28,uVar1,0,0xffffffffffffffff);
  if (0xf < local_18) {
    pvVar3 = local_30[0];
    if (0xfff < local_18 + 1) {
      if (((ulonglong)local_30[0] & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      pvVar3 = *(void **)((longlong)local_30[0] + -8);
      if (local_30[0] <= pvVar3) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if ((ulonglong)((longlong)local_30[0] - (longlong)pvVar3) < 8) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
      if (0x27 < (ulonglong)((longlong)local_30[0] - (longlong)pvVar3)) {
                    /* WARNING: Subroutine does not return */
        _invalid_parameter_noinfo_noreturn();
      }
    }
    operator_delete(pvVar3);
  }
LAB_140467d4f:
  plVar2 = (longlong *)(param_1 + 0x28);
  if (0xf < *(ulonglong *)(param_1 + 0x40)) {
    plVar2 = (longlong *)*plVar2;
  }
  return plVar2;
}

