// near init 14005da40 : FUN_14005db60 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_14005db60(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_1410f5eb8);
  DAT_1410f5ed0 = 0xf;
  _DAT_1410f5ec8 = 0;
  DAT_1410f5eb8._0_1_ = 0;
  FUN_14045f320(&DAT_1410f5eb8,"ImageCamA",9);
  atexit(FUN_140873ce0);
  return;
}

