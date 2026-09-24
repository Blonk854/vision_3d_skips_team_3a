// vt off=0x17b0 FUN_14045a810 @ 14045a810


ISerializable * FUN_14045a810(ISerializable *param_1,ulonglong param_2)

{
  FUN_140455110();
  SharedData::ISerializable::~ISerializable(param_1);
  if ((param_2 & 1) != 0) {
    FUN_1404556c0(param_1 + -0x1c8,0x1d0);
  }
  return param_1 + -0x1c8;
}

