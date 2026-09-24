// Recorder_Save @ 0x1406e79c0
// function FUN_1406e79c0 [1406e79c0 ..]


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */

ulonglong FUN_1406e79c0(longlong *param_1,uint param_2,uint param_3,undefined8 param_4,
                       undefined8 param_5,undefined8 param_6,longlong param_7,undefined8 *param_8)

{
  uint *puVar1;
  int *piVar2;
  longlong *plVar3;
  uint uVar4;
  int iVar5;
  longlong *plVar6;
  longlong lVar7;
  char cVar8;
  bool bVar9;
  ulonglong extraout_RAX;
  ulonglong uVar10;
  undefined1 local_res8 [8];
  undefined8 local_1218;
  uint local_1210;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1208 [8];
  undefined8 local_1200;
  longlong local_11f8;
  CLogManagerFunctionML local_11f0 [48];
  undefined8 local_11c0;
  CVitImgFile local_11b8 [96];
  uchar *local_1158;
  uint local_1150;
  undefined8 uStack_40;
  
  uStack_40 = 0x1406e79e2;
  local_11c0 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_1208,"CVitImgFileRecorderHelper::Save");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_11f0,0x10,local_1208,(ulonglong)*(uint *)(*param_1 + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1208);
  CVitImgFile::CVitImgFile(local_11b8);
  local_1200 = *param_8;
  local_11f8 = param_8[1];
  if (local_11f8 != 0) {
    LOCK();
    *(int *)(local_11f8 + 8) = *(int *)(local_11f8 + 8) + 1;
    UNLOCK();
  }
  cVar8 = FUN_140769320(param_5,param_2,param_3,local_11b8,param_4,param_6,&local_1200,0,0);
  if (cVar8 == '\0') {
    CLogManagerFunctionML::Write(local_11f0,4,"p_oVitImgFileRecorder.SaveOISMemory() failed.");
    CBlockFile::Close((CBlockFile *)local_11b8,false,false);
    CVitImgFile::_vbase_destructor_(local_11b8);
    CLogManagerFunctionML::~CLogManagerFunctionML(local_11f0);
    plVar6 = (longlong *)param_8[1];
    uVar10 = extraout_RAX;
    if (plVar6 != (longlong *)0x0) {
      LOCK();
      puVar1 = (uint *)(plVar6 + 1);
      uVar4 = *puVar1;
      uVar10 = (ulonglong)uVar4;
      *puVar1 = *puVar1 - 1;
      UNLOCK();
      if (uVar4 == 1) {
        uVar10 = (**(code **)(*plVar6 + 8))(plVar6);
        LOCK();
        piVar2 = (int *)((longlong)plVar6 + 0xc);
        iVar5 = *piVar2;
        *piVar2 = *piVar2 + -1;
        UNLOCK();
        if (iVar5 == 1) {
          uVar10 = (**(code **)(*plVar6 + 0x10))(plVar6);
        }
      }
    }
    uVar10 = uVar10 & 0xffffffffffffff00;
  }
  else {
    uVar10 = 1;
    if (((param_3 & 8) != 0) && (cVar8 = FUN_1406e78a0(param_1,param_7,local_11b8), cVar8 == '\0'))
    {
      CLogManagerFunctionML::Write(local_11f0,4,"CreateThumbnail() failed.");
      uVar10 = 0;
    }
    FUN_140765460(param_5,&local_1218);
    local_res8[0] = FUN_1407653a0(param_5,param_4);
    if (((param_3 & 1) != 0) &&
       (cVar8 = FUN_1406e7d90(param_1,param_2,param_6,local_res8,&local_1218,local_11b8),
       cVar8 == '\0')) {
      CLogManagerFunctionML::Write
                (local_11f0,4,"SaveOIS(%d, \'%s\') failed.",(ulonglong)param_2,local_1218);
      uVar10 = 0;
    }
    if (((param_3 & 2) != 0) &&
       (cVar8 = FUN_1406e8220(param_1,param_2,param_6,local_res8,&local_1218,local_11b8),
       cVar8 == '\0')) {
      CLogManagerFunctionML::Write(local_11f0,4,"SaveOTR(\'%s\') failed.",local_1218);
      uVar10 = 0;
    }
    FUN_1407652d0(param_5,local_11b8,param_3);
    CBlockFile::Close((CBlockFile *)local_11b8,false,(param_3 & 0x14) != 0);
    if ((param_3 & 0x14) != 0) {
      local_1210 = local_1150;
      CMemBuffer::DeleteBuffer((CMemBuffer *)(param_7 + 0x188));
      bVar9 = CMemBuffer::CreateBufferAndCopyData
                        ((CMemBuffer *)(param_7 + 0x188),local_1158,(ulonglong)local_1210,true);
      if (!bVar9) {
        CLogManagerFunctionML::Write
                  (local_11f0,4,"p_pAno->ImgSet(%u) failed.\n",(ulonglong)local_1210);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1218);
        CVitImgFile::_vbase_destructor_(local_11b8);
        CLogManagerFunctionML::~CLogManagerFunctionML(local_11f0);
        uVar10 = FUN_140584a10(param_8);
        return uVar10 & 0xffffffffffffff00;
      }
      if ((param_3 & 4) != 0) {
        *(undefined4 *)(param_7 + 0x158) = 1;
        *(int *)(*param_1 + 0x5e60) = *(int *)(*param_1 + 0x5e60) + 1;
      }
    }
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_1218);
    CVitImgFile::_vbase_destructor_(local_11b8);
    CLogManagerFunctionML::~CLogManagerFunctionML(local_11f0);
    plVar6 = (longlong *)param_8[1];
    if (plVar6 != (longlong *)0x0) {
      LOCK();
      plVar3 = plVar6 + 1;
      lVar7 = *plVar3;
      *(int *)plVar3 = (int)*plVar3 + -1;
      UNLOCK();
      if ((int)lVar7 == 1) {
        (**(code **)(*plVar6 + 8))(plVar6);
        LOCK();
        piVar2 = (int *)((longlong)plVar6 + 0xc);
        iVar5 = *piVar2;
        *piVar2 = *piVar2 + -1;
        UNLOCK();
        if (iVar5 == 1) {
          (**(code **)(*plVar6 + 0x10))(plVar6);
        }
      }
    }
  }
  return uVar10;
}

