// near init 1400a4600 : FUN_1400a47e0 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1400a47e0(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_1411098e0);
  DAT_1411098f8 = 0xf;
  _DAT_1411098f0 = 0;
  DAT_1411098e0._0_1_ = 0;
  FUN_14045f320(&DAT_1411098e0,"ImageMerged",0xb);
  atexit(FUN_1408ca360);
  return;
}

