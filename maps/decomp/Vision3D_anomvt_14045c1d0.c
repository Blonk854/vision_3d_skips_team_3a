// FUN_14045c1d0 @ 14045c1d0


CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *
FUN_14045c1d0(longlong *param_1,
             CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *pCVar4;
  char *pcVar5;
  int local_res8 [2];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *local_res10;
  int local_res18 [2];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res20 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_50 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_48 [8];
  undefined8 local_40;
  
  local_40 = 0xfffffffffffffffe;
  local_res10 = param_2;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(param_2);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res20);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_50);
  iVar1 = (**(code **)(*param_1 + 0x5a8))(param_1);
  iVar2 = (**(code **)(*param_1 + 0x5c8))(param_1);
  iVar3 = (**(code **)(*param_1 + 0x1130))(param_1,param_1 + 0x348);
  local_res18[0] = 0;
  if (0 < iVar2) {
    do {
      ATL::CSimpleStringT<char,1>::Empty((CSimpleStringT<char,1> *)local_res20);
      local_res8[0] = 0;
      if (0 < iVar1) {
        do {
          if (local_res8[0] != iVar3) {
            pCVar4 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                     (**(code **)(*param_1 + 0x1198))(param_1,local_48,local_res8,local_res18);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                      (local_50,pCVar4);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_48);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
                      (local_res20,(CSimpleStringT<char,1> *)local_50);
            pcVar5 = "\t";
            if (iVar1 + -1 <= local_res8[0]) {
              pcVar5 = "\n";
            }
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
                      (local_res20,pcVar5);
          }
          local_res8[0] = local_res8[0] + 1;
        } while (local_res8[0] < iVar1);
      }
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
                (param_2,(CSimpleStringT<char,1> *)local_res20);
      local_res18[0] = local_res18[0] + 1;
    } while (local_res18[0] < iVar2);
  }
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_50);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res20);
  return param_2;
}

