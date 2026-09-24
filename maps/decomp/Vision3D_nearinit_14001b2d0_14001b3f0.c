// near init 14001b2d0 : FUN_14001b3f0 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_14001b3f0(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_1410e2c70);
  DAT_1410e2c88 = 0xf;
  _DAT_1410e2c80 = 0;
  DAT_1410e2c70._0_1_ = 0;
  FUN_14045f320(&DAT_1410e2c70,"ImageCamA",9);
  atexit(FUN_140820e20);
  return;
}

