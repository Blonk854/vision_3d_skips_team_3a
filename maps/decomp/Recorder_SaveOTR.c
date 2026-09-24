// Recorder_SaveOTR @ 0x1406e8220
// function FUN_1406e8220 [1406e8220 ..]


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */

bool FUN_1406e8220(longlong *param_1,int param_2,longlong param_3,char *param_4,undefined8 *param_5,
                  CBlockFile *param_6)

{
  longlong lVar1;
  bool bVar2;
  bool bVar3;
  int iVar4;
  BOOL BVar5;
  DWORD DVar6;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *pCVar7;
  undefined8 uVar8;
  CSimpleStringT<char,1> *pCVar9;
  char *pcVar10;
  undefined8 *puVar11;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *pCVar12;
  ulong uVar13;
  double dVar14;
  ulonglong local_res8;
  undefined8 in_stack_ffffffffffffedb8;
  undefined4 uVar15;
  undefined8 local_1238;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1230 [8];
  undefined8 local_1228;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1220 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1218 [8];
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> local_1210 [8];
  CLogManagerFunctionML local_1208 [48];
  undefined8 local_11d8;
  ccTimer local_11d0 [40];
  CVitImgFile local_11a8 [4472];
  undefined8 uStack_30;
  
  uVar15 = (undefined4)((ulonglong)in_stack_ffffffffffffedb8 >> 0x20);
  uStack_30 = 0x1406e823b;
  local_11d8 = 0xfffffffffffffffe;
  bVar3 = false;
  local_res8 = local_res8 & 0xffffffff00000000;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
             "CVitImgFileRecorderHelper::SaveOTR");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_1208,0x10,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
             (ulonglong)*(uint *)(*param_1 + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8);
  if (*param_1 == 0) {
    CLogManagerFunctionML::Write(local_1208,4,"m_pProductionDoc = 0x%p.",0);
    bVar3 = false;
    goto LAB_1406e8792;
  }
  CTest::GetOTR_ProdFileDirectory((CTest *)(*param_1 + 0x188));
  bVar2 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)&local_1238);
  if (bVar2) {
LAB_1406e8335:
    bVar2 = false;
  }
  else {
    pCVar7 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
             ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Right
                       ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1238
                        ,(int)local_1230);
    bVar3 = true;
    local_res8 = CONCAT44(local_res8._4_4_,1);
    iVar4 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Compare(pCVar7,"\\")
    ;
    if (iVar4 == 0) goto LAB_1406e8335;
    bVar2 = true;
  }
  if (bVar3) {
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1230);
  }
  if (bVar2) {
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1238,"\\");
  }
  bVar3 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)(param_3 + 0x180));
  if (!bVar3) {
    uVar8 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
                       (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                       (param_3 + 0x180));
    pCVar9 = (CSimpleStringT<char,1> *)FiltreExoticChars2(local_1230,uVar8,&DAT_140e4c888);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1238,pCVar9);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1230);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1238,"\\");
  }
  pcVar10 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64
                      ((CSimpleStringT<char,1> *)&local_1238);
  BVar5 = CreateDirectoryA(pcVar10,(LPSECURITY_ATTRIBUTES)0x0);
  if (BVar5 == 0) {
    DVar6 = GetLastError();
    if (DVar6 == 0xb7) goto LAB_1406e8411;
    CLogManagerFunctionML::Write(local_1208,4,"::CreateDirectory(\'%s\') failed.",local_1238);
    bVar3 = false;
  }
  else {
LAB_1406e8411:
    uVar8 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
                       (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                       (param_3 + 0xf8));
    FiltreExoticChars2(&local_1228,uVar8,&DAT_140e4c888);
    bVar3 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)&local_1228);
    if ((bVar3) && (param_2 == 2)) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1228,
                 "PASTE");
    }
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1218);
    if (*param_4 == '\0') {
      uVar8 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                        ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                         &local_res8,
                         (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                          *)(param_3 + 400));
      puVar11 = (undefined8 *)FiltreExoticChars2(local_1230,uVar8,&DAT_140e4c888);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                (local_1218,"%s_%s_%i_%s.otr",local_1228,*puVar11,
                 CONCAT44(uVar15,*(undefined4 *)(param_3 + 0x198)),*param_5);
    }
    else {
      uVar8 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                        ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                         &local_res8,
                         (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                          *)(param_3 + 400));
      puVar11 = (undefined8 *)FiltreExoticChars2(local_1230,uVar8,&DAT_140e4c888);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                (local_1218,"%s_%s_%i_3D_%s.otr",local_1228,*puVar11,
                 CONCAT44(uVar15,*(undefined4 *)(param_3 + 0x198)),*param_5);
    }
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1230);
    ccTimer::ccTimer(local_11d0,false);
    ccTimer::start(local_11d0);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1238,
               (CSimpleStringT<char,1> *)local_1218);
    uVar8 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
                       (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                       &local_1238);
    CBlockFile::DuplicateToFile(param_6,uVar8);
    CVitImgFile::CVitImgFile(local_11a8);
    uVar8 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
                       (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                       &local_1238);
    bVar3 = CBlockFile::Open((CBlockFile *)local_11a8,uVar8,0);
    if (bVar3) {
      CBibliotheque::GetCompleteLibName((CBibliotheque *)(*param_1 + 0x11f8));
      local_res8 = CONCAT44(local_res8._4_4_,0xffffffff);
      lVar1 = *param_1;
      pcVar10 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64
                          ((CSimpleStringT<char,1> *)&local_1228);
      iVar4 = FUN_1406c4400(lVar1 + 0x228,pcVar10);
      uVar13 = (ulong)local_res8;
      if (iVar4 == 0) {
        uVar13 = 0xffffffff;
      }
      bVar3 = true;
      if (param_2 == 1) {
        local_res8 = _time64((__time64_t *)0x0);
        if (*(char *)(*param_1 + 0x6058) != '\0') {
          local_res8 = *(ulonglong *)(*param_1 + 0x1560);
        }
        pCVar7 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                 CBibliotheque::GetLibNameFromCompleteName(local_1210);
        pCVar12 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                  CBibliotheque::GetLibBaseFromCompleteName
                            ((CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                              *)local_1230);
        bVar2 = CVitImgFile::AddModels
                          (local_11a8,pCVar12,pCVar7,
                           (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                           &local_1228,uVar13,(CTime *)&local_res8);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1230);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_1210);
        if (!bVar2) {
          puVar11 = (undefined8 *)CBibliotheque::GetLibBaseFromCompleteName(local_1210);
          CLogManagerFunctionML::Write
                    (local_1208,4,
                     "Failed to add model familly \'%s\' in followed OTR file: \'%s\'.\n",local_1228
                     ,*puVar11);
          ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
          ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                    ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_1210);
          bVar3 = false;
        }
      }
      CBlockFile::Close((CBlockFile *)local_11a8,bVar3,false);
      *(int *)(*param_1 + 0x5e5c) = *(int *)(*param_1 + 0x5e5c) + 1;
      ccTimer::stop(local_11d0);
      dVar14 = ccTimer::msec(local_11d0);
      CLogManagerFunctionML::Write
                (local_1208,2,"#Timer:Save_OTR_<%s> = %lf (ms)\n",local_1238,dVar14);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1220);
    }
    else {
      CLogManagerFunctionML::Write(local_1208,4,"oVitImgFile() failed.",local_1238);
      bVar3 = false;
    }
    CVitImgFile::_vbase_destructor_(local_11a8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1218);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1228);
  }
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1238);
LAB_1406e8792:
  CLogManagerFunctionML::~CLogManagerFunctionML(local_1208);
  return bVar3;
}

