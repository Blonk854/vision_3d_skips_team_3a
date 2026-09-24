// Network_GetReviewStation @ 0x14064d6d0
// function FUN_14064d6d0 [14064d6d0 ..]


undefined8 FUN_14064d6d0(longlong param_1,uint param_2,CSimpleStringT<char,1> *param_3)

{
  bool bVar1;
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *pCVar2;
  undefined8 uVar3;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res20 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_48 [8];
  undefined8 local_40;
  CLogManagerFunction local_38 [48];
  
  local_40 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_48,"GetReviewStation");
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res20,"CNetworkDataManagement");
  CLogManagerFunction::CLogManagerFunction(local_38,0x16,local_res20,local_48,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res20);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_48);
  ATL::CSimpleStringT<char,1>::Empty(param_3);
  if (param_2 == 0) {
    pCVar2 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
             (param_1 + 0xd0);
LAB_14064d796:
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)param_3,pCVar2);
    CLogManagerFunction::Write
              (local_38,2,"ReviewStation (%s) lane (%d)\n",*(undefined8 *)param_3,param_2);
    bVar1 = ATL::CSimpleStringT<char,1>::IsEmpty(param_3);
    if (!bVar1) {
      uVar3 = 1;
      goto LAB_14064d7e7;
    }
    CLogManagerFunction::Write(local_38,5,"ReviewStation empty.\n");
  }
  else {
    if (param_2 == 1) {
      pCVar2 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               (param_1 + 0xd8);
      goto LAB_14064d796;
    }
    CLogManagerFunction::Write(local_38,4,"Wrong lane number (%d)\n",(ulonglong)param_2);
  }
  uVar3 = 0;
LAB_14064d7e7:
  CLogManagerFunction::~CLogManagerFunction(local_38);
  return uVar3;
}

