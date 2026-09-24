// vt off=0x510 FUN_14045a5a0 @ 14045a5a0


ISerializable * FUN_14045a5a0(ISerializable *param_1,uint param_2)

{
  CViUnitLength::_vbase_destructor_((CViUnitLength *)(param_1 + -0x30));
  CViUnitLength::_vbase_destructor_((CViUnitLength *)(param_1 + -0x60));
  CViUnitRect::_vbase_destructor_((CViUnitRect *)(param_1 + -0x1c0));
  SharedData::ISerializable::~ISerializable(param_1);
  if ((param_2 & 1) != 0) {
    FUN_1404556c0(param_1 + -0x1d8,0x1e0);
  }
  return param_1 + -0x1d8;
}

