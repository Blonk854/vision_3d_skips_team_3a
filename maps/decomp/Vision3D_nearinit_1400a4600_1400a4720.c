// near init 1400a4600 : FUN_1400a4720 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1400a4720(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_1411098a0);
  DAT_1411098b8 = 0xf;
  _DAT_1411098b0 = 0;
  DAT_1411098a0._0_1_ = 0;
  FUN_14045f320(&DAT_1411098a0,"ImageCamA",9);
  atexit(FUN_1408ca200);
  return;
}

