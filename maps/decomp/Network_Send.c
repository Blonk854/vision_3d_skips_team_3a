// Network_Send @ 0x14064e110
// function FUN_14064e110 [14064e110 ..]


int FUN_14064e110(CTalkToSuperviseur *param_1,CMsg *param_2,CMsg **param_3,int param_4,bool param_5,
                 long param_6)

{
  CCommande *this;
  bool bVar1;
  int iVar2;
  CSimpleStringT<char,1> *this_00;
  undefined8 *puVar3;
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *pCVar4;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res18 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_48 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_40 [8];
  undefined8 local_38;
  CLogManagerFunction local_30 [40];
  
  local_38 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_48,"Send");
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res18,"CNetworkDataManagement");
  CLogManagerFunction::CLogManagerFunction(local_30,0x16,local_res18,local_48,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res18);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_48);
  iVar2 = CTalkToSuperviseur::Send(param_1,param_2,param_3,param_4,param_5,param_6);
  if (iVar2 == 0x21) {
    *(undefined4 *)(param_1 + 0xe8) = 1;
  }
  this = (CCommande *)*param_3;
  if ((this != (CCommande *)0x0) && (*(int *)(this + 0x3c) == 4)) {
    this_00 = (CSimpleStringT<char,1> *)CCommande::_csComParam(this,(long)local_40);
    bVar1 = ATL::CSimpleStringT<char,1>::IsEmpty(this_00);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_40);
    if (!bVar1) {
      puVar3 = (undefined8 *)CCommande::_csComParam((CCommande *)*param_3,(long)local_40);
      CLogManagerFunction::Write
                (local_30,10,"Superviseur returned this error message: \'%s\'",*puVar3);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_40);
      if (*(int *)((CCommande *)*param_3 + 0xc) == 0) {
        pCVar4 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                 CCommande::_csComParam((CCommande *)*param_3,(long)local_40);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)(param_1 + 0xf0)
                   ,pCVar4);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_40);
      }
    }
  }
  CLogManagerFunction::~CLogManagerFunction(local_30);
  return iVar2;
}

