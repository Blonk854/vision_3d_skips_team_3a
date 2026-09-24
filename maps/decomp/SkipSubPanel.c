// SkipSubPanel @ 0x140541080
// function CDataCaoTraitement::SkipSubPanel [140541080 ..]


/* public: void __cdecl CDataCaoTraitement::SkipSubPanel(long) __ptr64 */

void __thiscall CDataCaoTraitement::SkipSubPanel(CDataCaoTraitement *this,long param_1)

{
  bool bVar1;
  ulonglong uVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res8 [16];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res18 [16];
  CLogManagerFunction local_50 [40];
  
                    /* 0x541080  233  ?SkipSubPanel@CDataCaoTraitement@@QEAAXJ@Z */
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res18,"SkipSubPanel");
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8,"CDataCaoTraitement");
  uVar3 = 0;
  CLogManagerFunction::CLogManagerFunction(local_50,0x10,local_res8,local_res18,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res18);
  bVar1 = IsSkippedSubPanel(this,param_1);
  if (!bVar1) {
    CUIntArray::SetAtGrow((CUIntArray *)(this + 0x23e0),*(__int64 *)(this + 0x23f0),param_1);
  }
  uVar2 = (*(longlong *)(this + 0x2450) - *(longlong *)(this + 0x2448)) / 0x28;
  uVar4 = uVar3;
  if (uVar2 != 0) {
    do {
      FUN_140540cf0(*(longlong *)(this + 0x2448) + uVar3,CONCAT71((int7)(uVar2 >> 8),1),param_1);
      uVar4 = uVar4 + 1;
      uVar3 = uVar3 + 0x28;
      uVar2 = (*(longlong *)(this + 0x2450) - *(longlong *)(this + 0x2448)) / 0x28;
    } while (uVar4 < uVar2);
  }
  CLogManagerFunction::~CLogManagerFunction(local_50);
  return;
}

