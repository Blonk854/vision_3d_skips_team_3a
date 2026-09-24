// vt off=0x1788 FUN_14045a860 @ 14045a860


ISerializable * FUN_14045a860(ISerializable *param_1,uint param_2)

{
  *(undefined ***)(param_1 + (longlong)*(int *)(*(longlong *)(param_1 + -0x68) + 4) + -0x68) =
       CZWindow::vftable;
  CViUnitLength::_vbase_destructor_((CViUnitLength *)(param_1 + -0x30));
  CViUnitLength::_vbase_destructor_((CViUnitLength *)(param_1 + -0x60));
  SharedData::ISerializable::~ISerializable(param_1);
  if ((param_2 & 1) != 0) {
    FUN_1404556c0(param_1 + -0x68,0x70);
  }
  return param_1 + -0x68;
}

