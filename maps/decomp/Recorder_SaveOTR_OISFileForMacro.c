// Recorder_SaveOTR_OISFileForMacro @ 0x1406e87c0
// function FUN_1406e87c0 [1406e87c0 ..]


undefined8 FUN_1406e87c0(longlong *param_1,longlong param_2,undefined8 *param_3,longlong param_4)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  BOOL BVar4;
  DWORD DVar5;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *this;
  undefined8 uVar6;
  CSimpleStringT<char,1> *pCVar7;
  char *pcVar8;
  undefined8 *puVar9;
  double dVar10;
  __uint64 local_res8;
  undefined8 in_stack_fffffffffffffe18;
  undefined4 uVar11;
  undefined8 local_1d8;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d0 [8];
  uchar *local_1c8;
  undefined8 local_1c0;
  CLogManagerFunctionML local_1b8 [48];
  CFile local_188 [40];
  undefined8 local_160;
  ccTimer local_140 [296];
  
  uVar11 = (undefined4)((ulonglong)in_stack_fffffffffffffe18 >> 0x20);
  local_160 = 0xfffffffffffffffe;
  bVar2 = false;
  local_res8 = local_res8 & 0xffffffff00000000;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
             "CVitImgFileRecorderHelper::SaveOTR_OISFileForMacro");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_1b8,0x10,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
             (ulonglong)*(uint *)(*param_1 + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8);
  if (*param_1 == 0) {
    CLogManagerFunctionML::Write(local_1b8,4,"m_pProductionDoc = 0x%p.",0);
LAB_1406e8c09:
    CLogManagerFunctionML::~CLogManagerFunctionML(local_1b8);
    uVar6 = 0;
  }
  else {
    CTest::GetOTR_ProdFileDirectory((CTest *)(*param_1 + 0x188));
    bVar1 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)&local_1d8);
    if (bVar1) {
LAB_1406e88bd:
      bVar1 = false;
    }
    else {
      bVar2 = true;
      this = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
             ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Right
                       ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1d8,
                        (int)&local_1c8);
      local_res8 = CONCAT44(local_res8._4_4_,1);
      iVar3 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Compare(this,"\\")
      ;
      if (iVar3 == 0) goto LAB_1406e88bd;
      bVar1 = true;
    }
    if (bVar2) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1c8);
    }
    if (bVar1) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1d8,"\\");
    }
    bVar2 = ATL::CSimpleStringT<char,1>::IsEmpty((CSimpleStringT<char,1> *)(param_2 + 0x180));
    if (!bVar2) {
      uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                        ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                         &local_res8,
                         (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                          *)(param_2 + 0x180));
      pCVar7 = (CSimpleStringT<char,1> *)FiltreExoticChars2(&local_1c8,uVar6,&DAT_140e4c888);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1d8,pCVar7)
      ;
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1c8);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1d8,"\\");
    }
    pcVar8 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64
                       ((CSimpleStringT<char,1> *)&local_1d8);
    BVar4 = CreateDirectoryA(pcVar8,(LPSECURITY_ATTRIBUTES)0x0);
    if (BVar4 == 0) {
      DVar5 = GetLastError();
      if (DVar5 != 0xb7) {
        CLogManagerFunctionML::Write(local_1b8,4,"::CreateDirectory(\'%s\') failed.",local_1d8);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1d8);
        goto LAB_1406e8c09;
      }
    }
    uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
                       (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                       (param_2 + 0xf8));
    FiltreExoticChars2(&local_1c0,uVar6,&DAT_140e4c888);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1d0);
    uVar6 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                      ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8,
                       (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                       (param_2 + 400));
    puVar9 = (undefined8 *)FiltreExoticChars2(&local_1c8,uVar6,&DAT_140e4c888);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
              (local_1d0,"%s_%s_%i_%s.ois",local_1c0,*puVar9,
               CONCAT44(uVar11,*(undefined4 *)(param_2 + 0x198)),*param_3);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1c8);
    ccTimer::ccTimer(local_140,false);
    ccTimer::start(local_140);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator+=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1d8,
               (CSimpleStringT<char,1> *)local_1d0);
    CFile::CFile(local_188);
    local_res8 = 0;
    local_1c8 = (uchar *)0x0;
    if ((*(longlong *)(param_4 + 400) != 0) && (*(longlong *)(param_4 + 0x198) != 0)) {
      CMemBuffer::GetBuffer((CMemBuffer *)(param_4 + 0x188),&local_1c8,&local_res8);
    }
    pcVar8 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64
                       ((CSimpleStringT<char,1> *)&local_1d8);
    iVar3 = CFile::Open(local_188,pcVar8,0x9001,(CFileException *)0x0);
    if (iVar3 == 0) {
      CLogManagerFunctionML::Write(local_1b8,4,"WARNING : Cannot Save picture \"%s\"\n",local_1d8);
      CFile::~CFile(local_188);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1d0);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1c0);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1d8);
      CLogManagerFunctionML::~CLogManagerFunctionML(local_1b8);
      uVar6 = 0;
    }
    else {
      CFile::Write(local_188,local_1c8,(uint)local_res8);
      CFile::Close(local_188);
      CFile::~CFile(local_188);
      *(int *)(*param_1 + 0x5e5c) = *(int *)(*param_1 + 0x5e5c) + 1;
      ccTimer::stop(local_140);
      dVar10 = ccTimer::msec(local_140);
      CLogManagerFunctionML::Write(local_1b8,2,"#Timer:Save_OTR_<%s> = %lf (ms)\n",local_1d8,dVar10)
      ;
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1d0);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1c0);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1d8);
      CLogManagerFunctionML::~CLogManagerFunctionML(local_1b8);
      uVar6 = 1;
    }
  }
  return uVar6;
}

