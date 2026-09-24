// vt off=0x1588 FUN_1405754f0 @ 1405754f0


undefined8 * FUN_1405754f0(undefined8 *param_1,ulonglong param_2)

{
  *param_1 = boost::system::system_error::vftable;
  FUN_1404546f0(param_1 + 5);
  *param_1 = std::exception::vftable;
  __std_exception_destroy(param_1 + 1);
  if ((param_2 & 1) != 0) {
    FUN_1404556c0(param_1,0x48);
  }
  return param_1;
}

