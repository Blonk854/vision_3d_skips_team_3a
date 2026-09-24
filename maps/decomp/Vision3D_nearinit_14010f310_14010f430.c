// near init 14010f310 : FUN_14010f430 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_14010f430(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_141126f00);
  DAT_141126f18 = 0xf;
  _DAT_141126f10 = 0;
  DAT_141126f00._0_1_ = 0;
  FUN_14045f320(&DAT_141126f00,"ImageCamA",9);
  atexit(FUN_140950960);
  return;
}

