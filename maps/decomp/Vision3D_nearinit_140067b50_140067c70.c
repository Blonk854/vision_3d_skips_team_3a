// near init 140067b50 : FUN_140067c70 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_140067c70(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_1410f8ef8);
  DAT_1410f8f10 = 0xf;
  _DAT_1410f8f08 = 0;
  DAT_1410f8ef8._0_1_ = 0;
  FUN_14045f320(&DAT_1410f8ef8,"ImageCamA",9);
  atexit(FUN_14087e6b0);
  return;
}

