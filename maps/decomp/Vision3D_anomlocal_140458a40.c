// vt off=0x17f0 FUN_140458a40 @ 140458a40


extended_type_info *
FUN_140458a40(extended_type_info *param_1,uint param_2,undefined8 param_3,undefined8 param_4)

{
  undefined8 uVar1;
  
  uVar1 = 0xfffffffffffffffe;
  DAT_1410e51d4 = 1;
  *(undefined ***)param_1 =
       boost::serialization::extended_type_info_typeid<CRoi3dInstruction>::vftable;
  boost::serialization::extended_type_info::key_unregister(param_1);
  boost::serialization::typeid_system::extended_type_info_typeid_0::type_unregister
            ((extended_type_info_typeid_0 *)param_1);
  boost::serialization::typeid_system::extended_type_info_typeid_0::~extended_type_info_typeid_0
            ((extended_type_info_typeid_0 *)param_1);
  if ((param_2 & 1) != 0) {
    FUN_1404556c0(param_1,0x28,param_3,param_4,uVar1);
  }
  return param_1;
}

