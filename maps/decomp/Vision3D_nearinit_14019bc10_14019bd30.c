// near init 14019bc10 : FUN_14019bd30 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_14019bd30(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_14114da50);
  DAT_14114da68 = 0xf;
  _DAT_14114da60 = 0;
  DAT_14114da50._0_1_ = 0;
  FUN_14045f320(&DAT_14114da50,"ImageCamA",9);
  atexit(FUN_140a01ed0);
  return;
}

