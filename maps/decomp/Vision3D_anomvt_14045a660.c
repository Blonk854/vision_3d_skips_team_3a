// FUN_14045a660 @ 14045a660


void * FUN_14045a660(void *param_1,ulonglong param_2)

{
  FUN_140454fd0();
  if ((param_2 & 1) != 0) {
    if ((param_2 & 4) == 0) {
      operator_delete(param_1);
      return param_1;
    }
    thunk_FUN_1404556c0(param_1,0x1b80);
  }
  return param_1;
}

