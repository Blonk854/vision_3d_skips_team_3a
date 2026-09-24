// FUN_14045c740 @ 14045c740


undefined8 FUN_14045c740(undefined8 param_1,undefined8 param_2,undefined8 param_3)

{
  long lVar1;
  char cVar2;
  bool bVar3;
  longlong lVar4;
  CAnomalieProd *this;
  CSimpleStringT<char,1> *this_00;
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *pCVar5;
  CCAD_Base *pCVar6;
  undefined8 uVar7;
  uint uVar8;
  uint local_38 [2];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_30 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_28 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_20 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_18 [8];
  undefined8 local_10;
  
  local_10 = 0xfffffffffffffffe;
  local_38[0] = 0;
  lVar4 = FUN_14045bf90();
  if (((lVar4 == 0) || (cVar2 = FUN_1405ddc30(lVar4), cVar2 != '\0')) ||
     (this = (CAnomalieProd *)FUN_14045bf10(param_1,param_3), this == (CAnomalieProd *)0x0)) {
    return 0;
  }
  if ((*(uint *)(this + 0x18) & 0x2000000) == 0) {
    this_00 = (CSimpleStringT<char,1> *)CAnomalieProd::_csOCV_Reader(this);
    bVar3 = ATL::CSimpleStringT<char,1>::IsEmpty(this_00);
    if (bVar3) {
      pCVar5 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               CAnomalie::_csTopo((CAnomalie *)this);
      uVar8 = 1;
    }
    else {
      pCVar5 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               CAnomalieProd::_csOCV_Reader(this);
      uVar8 = 2;
    }
    local_38[0] = uVar8;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_30,pCVar5);
    if ((uVar8 & 2) != 0) {
      uVar8 = uVar8 & 0xfffffffd;
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_28);
    }
    if ((uVar8 & 1) != 0) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_20);
    }
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_18);
    lVar1 = *(long *)(this + 8);
    pCVar6 = CDataCao::GetObjectA((CDataCao *)(lVar4 + 0x180),local_30,lVar1);
    if (pCVar6 == (CCAD_Base *)0x0) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_30);
      return 0;
    }
    if (*(int *)(pCVar6 + 8) == 0x200000) {
      pCVar5 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               CAnomalie::_csTopo((CAnomalie *)this);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_30,pCVar5)
      ;
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_38);
    }
    uVar7 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_38,
                       (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                       local_30);
    FUN_1405f4730(lVar4,uVar7,lVar1);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_30);
  }
  else {
    FUN_1405f9270(lVar4,this);
  }
  return 1;
}

