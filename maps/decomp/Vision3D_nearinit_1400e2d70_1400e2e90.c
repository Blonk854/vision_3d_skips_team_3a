// near init 1400e2d70 : FUN_1400e2e90 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1400e2e90(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_14111aa68);
  DAT_14111aa80 = 0xf;
  _DAT_14111aa78 = 0;
  DAT_14111aa68._0_1_ = 0;
  FUN_14045f320(&DAT_14111aa68,"ImageCamA",9);
  atexit(FUN_1409179e0);
  return;
}

