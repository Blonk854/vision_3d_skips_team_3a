// vt off=0x890 boost::archive::detail::oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<CZone3dInstruction,std::allocator<CZone3dInstruction>_>_>::save_object_data @ 140467540


/* public: virtual void __cdecl boost::archive::detail::oserializer<struct
   basictools::serialization::archive::Vit_xml_oarchive,class std::vector<class
   CZone3dInstruction,class std::allocator<class CZone3dInstruction> > >::save_object_data(class
   boost::archive::detail::basic_oarchive & __ptr64,void const * __ptr64)const __ptr64 */

void __thiscall
boost::archive::detail::
oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<CZone3dInstruction,std::allocator<CZone3dInstruction>_>_>
::save_object_data(oserializer<basictools::serialization::archive::Vit_xml_oarchive,std::vector<CZone3dInstruction,std::allocator<CZone3dInstruction>_>_>
                   *this,basic_oarchive *param_1,void *param_2)

{
  undefined8 uVar1;
  undefined1 local_res8 [8];
  longlong local_res18 [2];
  
                    /* 0x467540  414
                       ?save_object_data@?$oserializer@UVit_xml_oarchive@archive@serialization@basictools@@V?$vector@VCZone3dInstruction@@V?$allocator@VCZone3dInstruction@@@std@@@std@@@detail@archive@boost@@UEBAXAEAVbasic_oarchive@234@PEBX@Z
                        */
  (**(code **)(*(longlong *)this + 0x20))(this,local_res8);
  local_res18[0] = (*(longlong *)((longlong)param_2 + 8) - *(longlong *)param_2) / 0x1b8;
  uVar1 = serialization::
          singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
          ::
          singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
                    ((singleton<boost::serialization::extended_type_info_typeid<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char>_>_const_,CJedecInfo>_>_>
                      *)param_1);
  FUN_14044edc0(uVar1,param_2,local_res18);
  return;
}

