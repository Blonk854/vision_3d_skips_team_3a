// vt off=0x858 boost::archive::detail::oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<algo::CJEDECPathProperties,std::allocator<algo::CJEDECPathProperties>_>_>::save_object_data @ 140467380


/* public: virtual void __cdecl boost::archive::detail::oserializer<struct
   basictools::serialization::archive::Vit_xml_oarchive,class std::vector<class
   algo::CJEDECPathProperties,class std::allocator<class algo::CJEDECPathProperties> >
   >::save_object_data(class boost::archive::detail::basic_oarchive & __ptr64,void const *
   __ptr64)const __ptr64 */

void __thiscall
boost::archive::detail::
oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<algo::CJEDECPathProperties,std::allocator<algo::CJEDECPathProperties>_>_>
::save_object_data(oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<algo::CJEDECPathProperties,std::allocator<algo::CJEDECPathProperties>_>_>
                   *this,basic_oarchive *param_1,void *param_2)

{
  undefined8 uVar1;
  undefined1 local_res8 [8];
  longlong local_res18 [2];
  
                    /* 0x467380  409
                       ?save_object_data@?$oserializer@UVit_xml_oarchive@archive@serialization@basictools@@V?$vector@VCJEDECPathProperties@algo@@V?$allocator@VCJEDECPathProperties@algo@@@std@@@std@@@detail@archive@boost@@UEBAXAEAVbasic_oarchive@234@PEBX@Z
                        */
  (**(code **)(*(longlong *)this + 0x20))(this,local_res8);
  local_res18[0] = (*(longlong *)((longlong)param_2 + 8) - *(longlong *)param_2) / 0x68;
  uVar1 = serialization::
          singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
          ::
          singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
                    ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
                      *)param_1);
  FUN_14044e840(uVar1,param_2,local_res18);
  return;
}

