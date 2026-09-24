// SendPanelToReviewStation_log @ 0x14067c710
// function FUN_14067c710 [14067c710 ..]


void FUN_14067c710(longlong param_1,char param_2)

{
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res18 [16];
  CLogManagerFunction local_30 [40];
  
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res18,"CMsgPanelProd::SendPanelToReviewStation");
  CLogManagerFunction::CLogManagerFunction(local_30,0x10,local_res18,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res18);
  if (param_2 == '\0') {
    CLogManagerFunction::Write(local_30,2,"Send panel to repair <NO>.\n");
    *(undefined4 *)(param_1 + 0xc) = 1;
  }
  else {
    CLogManagerFunction::Write(local_30,2,"Send panel to repair <YES>.\n");
    *(undefined4 *)(param_1 + 0xc) = 0;
  }
  CLogManagerFunction::~CLogManagerFunction(local_30);
  return;
}

