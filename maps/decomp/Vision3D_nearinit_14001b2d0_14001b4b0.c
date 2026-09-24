// near init 14001b2d0 : FUN_14001b4b0 body=86 interesting=True


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_14001b4b0(void)

{
  boost::serialization::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
  ::
  singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
            ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
              *)&DAT_1410e2cb0);
  DAT_1410e2cc8 = 0xf;
  _DAT_1410e2cc0 = 0;
  DAT_1410e2cb0._0_1_ = 0;
  FUN_14045f320(&DAT_1410e2cb0,"ImageMerged",0xb);
  atexit(FUN_140820f80);
  return;
}

