// COM_SendPanelResults @ 0x1404c7580
// function FUN_1404c7580 [1404c7580 ..]


undefined1 FUN_1404c7580(longlong param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  undefined1 uVar1;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res8 [8];
  undefined8 uVar2;
  CLogManagerFunction local_30 [40];
  
  uVar2 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res8,"CCOMObjectMgr::SendPanelResults");
  CLogManagerFunction::CLogManagerFunction(local_30,5,local_res8,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
  if ((ulonglong)(*(longlong *)(param_1 + 0x10) - *(longlong *)(param_1 + 8) >> 7) < 2) {
    CLogManagerFunction::Write
              (local_30,4,"BUG: m_vComObjects.size == %Iu",
               *(longlong *)(param_1 + 0x10) - *(longlong *)(param_1 + 8) >> 7);
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_1404c2640(*(undefined8 *)(param_1 + 8),param_2,param_3,param_4,uVar2);
  }
  CLogManagerFunction::~CLogManagerFunction(local_30);
  return uVar1;
}

