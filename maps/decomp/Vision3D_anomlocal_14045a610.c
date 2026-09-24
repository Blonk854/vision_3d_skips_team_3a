// vt off=0x15d8 FUN_14045a610 @ 14045a610


CAnomalieProd * FUN_14045a610(CAnomalieProd *param_1,uint param_2)

{
  CAnomalieProd::~CAnomalieProd(param_1);
  if ((param_2 & 1) != 0) {
    if ((param_2 & 4) == 0) {
      operator_delete(param_1);
      return param_1;
    }
    thunk_FUN_1404556c0(param_1,0x370);
  }
  return param_1;
}

