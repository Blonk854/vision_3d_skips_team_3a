// vt off=0x820 boost::archive::detail::oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<CZone2DInfo,std::allocator<CZone2DInfo>_>_>::save_object_data @ 1404674d0


/* public: virtual void __cdecl boost::archive::detail::oserializer<struct
   basictools::serialization::archive::Vit_xml_oarchive,class std::vector<class CZone2DInfo,class
   std::allocator<class CZone2DInfo> > >::save_object_data(class
   boost::archive::detail::basic_oarchive & __ptr64,void const * __ptr64)const __ptr64 */

void __thiscall
boost::archive::detail::
oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<CZone2DInfo,std::allocator<CZone2DInfo>_>_>
::save_object_data(oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<CZone2DInfo,std::allocator<CZone2DInfo>_>_>
                   *this,basic_oarchive *param_1,void *param_2)

{
  undefined8 uVar1;
  undefined1 local_res8 [8];
  longlong local_res18 [2];
  
                    /* 0x4674d0  413
                       ?save_object_data@?$oserializer@UVit_xml_oarchive@archive@serialization@basictools@@V?$vector@VCZone2DInfo@@V?$allocator@VCZone2DInfo@@@std@@@std@@@detail@archive@boost@@UEBAXAEAVbasic_oarchive@234@PEBX@Z
                        */
  (**(code **)(*(longlong *)this + 0x20))(this,local_res8);
  local_res18[0] = (*(longlong *)((longlong)param_2 + 8) - *(longlong *)param_2) / 0x178;
  uVar1 = serialization::
          singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
          ::
          singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
                    ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
                      *)param_1);
  FUN_14044ec60(uVar1,param_2,local_res18);
  return;
}

