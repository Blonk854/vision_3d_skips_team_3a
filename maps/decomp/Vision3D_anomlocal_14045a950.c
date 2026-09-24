// vt off=0x560 FUN_14045a950 @ 14045a950


ISerializable * FUN_14045a950(ISerializable *param_1,ulonglong param_2)

{
  FUN_140455220();
  SharedData::ISerializable::~ISerializable(param_1);
  if ((param_2 & 1) != 0) {
    FUN_1404556c0(param_1 + -0x1b0,0x1b8);
  }
  return param_1 + -0x1b0;
}

