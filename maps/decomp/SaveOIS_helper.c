// SaveOIS_helper @ 0x1406e7d90
// function FUN_1406e7d90 [1406e7d90 ..]


undefined8
FUN_1406e7d90(longlong *param_1,uint param_2,longlong param_3,char *param_4,undefined8 *param_5,
             CBlockFile *param_6)

{
  bool bVar1;
  int iVar2;
  BOOL BVar3;
  DWORD DVar4;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *pCVar5;
  undefined8 uVar6;
  CSimpleStringT<char,1> *pCVar7;
  char *lpPathName;
  undefined8 *puVar8;
  undefined8 *puVar9;
  uint uVar10;
  double dVar11;
  undefined8 local_res8;
  uint local_res10;
  undefined8 in_stack_ffffffffffffff08;
  undefined4 uVar12;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_e8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_e0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_d8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_d0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_c8 [8];
  undefined8 local_c0;
  ccTimer local_b8 [32];
  CLogManagerFunctionML local_98 [48];
  CIniFileAvivion_Private local_68 [64];
  
  uVar12 = (undefined4)((ulonglong)in_stack_ffffffffffffff08 >> 0x20);
  local_c0 = 0xfffffffffffffffe;
  uVar10 = 0;
  local_res10 = 0;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_e8,"CVitImgFileRecorderHelper::SaveOIS");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_98,0x10,local_e8,(ulonglong)*(uint *)(*param_1 + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_e8);
  CIniFileAvivion_Private::CIniFileAvivion_Private(local_68);
  if (param_2 == 8) {
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              (local_d8,"Save Foreign Materials OIS");
    local_res10 = 1;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_e8,"Production");
    uVar10 = 3;
    local_res10 = 3;
    bVar1 = CIniFileBase::GetValeurIni_bool((CIniFileBase *)local_68,local_e8,local_d8);
    if (bVar1) goto LAB_1406e7e67;
    bVar1 = true;
  }
  else {
LAB_1406e7e67:
    bVar1 = false;
  }
  if ((uVar10 & 2) != 0) {
    uVar10 = uVar10 & 0xfffffffd;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_e8);
  }
  if ((uVar10 & 1) != 0) {
    uVar10 = uVar10 & 0xfffffffe;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_d8);
  }
  if (bVar1) {
    uVar6 = 1;
    goto LAB_1406e81e5;
  }
  if (*param_1 == 0) {
    CLogManagerFunctionML::Write(local_98,4,"m_pProductionDoc = 0x%p.");
    uVar6 = 0;
    goto LAB_1406e81e5;
  }
  if ((param_2 != 1) && (param_2 != 8)) {
    CLogManagerFunctionML::Write(local_98,4,"p_eVitImgFileType = %d.",(ulonglong)param_2);
    uVar6 = 0;
    goto LAB_1406e81e5;
  }
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
             (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
             (param_3 + 0x40));
  bVar1 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)&local_res8);
  if (bVar1) {
LAB_1406e7f3e:
    bVar1 = false;
  }
  else {
    pCVar5 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
             ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Right
                       ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8
                        ,(int)local_d8);
    uVar10 = uVar10 | 4;
    local_res10 = uVar10;
    iVar2 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Compare(pCVar5,"\\")
    ;
    if (iVar2 == 0) goto LAB_1406e7f3e;
    bVar1 = true;
  }
  if ((uVar10 & 4) != 0) {
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_d8);
  }
  if (bVar1) {
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,"\\");
  }
  bVar1 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)(param_3 + 0x180));
  if (!bVar1) {
    uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      (local_d8,(CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                 *)(param_3 + 0x180));
    pCVar7 = (CSimpleStringT<char,1> *)FiltreExoticChars2(local_e8,uVar6,&DAT_140e4c888);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,pCVar7);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_e8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,"\\");
  }
  lpPathName = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64
                         ((CSimpleStringT<char,1> *)&local_res8);
  BVar3 = CreateDirectoryA(lpPathName,(LPSECURITY_ATTRIBUTES)0x0);
  if (BVar3 == 0) {
    DVar4 = GetLastError();
    if (DVar4 == 0xb7) goto LAB_1406e8010;
    CLogManagerFunctionML::Write(local_98,4,"::CreateDirectory(\'%s\') failed.",local_res8);
    uVar6 = 0;
  }
  else {
LAB_1406e8010:
    ccTimer::ccTimer(local_b8,false);
    ccTimer::start(local_b8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_d0);
    if (*param_4 == '\0') {
      uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                        (local_e0,(CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                   *)(param_3 + 400));
      puVar8 = (undefined8 *)FiltreExoticChars2(local_e8,uVar6,&DAT_140e4c888);
      uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                        (local_c8,(CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                   *)(param_3 + 0xf8));
      puVar9 = (undefined8 *)FiltreExoticChars2(local_d8,uVar6,&DAT_140e4c888);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                (local_d0,"%s_%s_%i_%s.ois",*puVar9,*puVar8,
                 CONCAT44(uVar12,*(undefined4 *)(param_3 + 0x198)),*param_5);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_d8);
      pCVar5 = local_e8;
    }
    else {
      uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                        (local_d8,(CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                   *)(param_3 + 400));
      puVar8 = (undefined8 *)FiltreExoticChars2(local_e0,uVar6,&DAT_140e4c888);
      uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                        (local_e8,(CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                   *)(param_3 + 0xf8));
      puVar9 = (undefined8 *)FiltreExoticChars2(local_c8,uVar6,&DAT_140e4c888);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                (local_d0,"%s_%s_%i_3D_%s.ois",*puVar9,*puVar8,
                 CONCAT44(uVar12,*(undefined4 *)(param_3 + 0x198)),*param_5);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_c8);
      pCVar5 = local_e0;
    }
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(pCVar5);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
               (CSimpleStringT<char,1> *)local_d0);
    uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      (local_e0,(CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                                 *)&local_res8);
    CBlockFile::DuplicateToFile(param_6,uVar6);
    *(int *)(*param_1 + 0x5e58) = *(int *)(*param_1 + 0x5e58) + 1;
    ccTimer::stop(local_b8);
    dVar11 = ccTimer::msec(local_b8);
    CLogManagerFunctionML::Write(local_98,2,"#Timer:Save_OIS_<%s> = %lf (ms)\n",local_res8,dVar11);
    uVar6 = 1;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_d0);
  }
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8);
LAB_1406e81e5:
  CIniFileAvivion_Private::~CIniFileAvivion_Private(local_68);
  CLogManagerFunctionML::~CLogManagerFunctionML(local_98);
  return uVar6;
}

