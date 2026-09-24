// ProductionCommunication_ResultsAvailable @ 0x14067c5b0
// function FUN_14067c5b0 [14067c5b0 ..]


void FUN_14067c5b0(longlong param_1)

{
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res8 [32];
  CLogManagerFunctionML local_40 [56];
  
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res8,"CProductionCommunication::ResultsAvailable");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_40,0x10,local_res8,(ulonglong)*(uint *)(*(longlong *)(param_1 + 0x20) + 0x3924),
             false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
  SetEvent(*(HANDLE *)(param_1 + 0x40));
  CLogManagerFunctionML::~CLogManagerFunctionML(local_40);
  return;
}

