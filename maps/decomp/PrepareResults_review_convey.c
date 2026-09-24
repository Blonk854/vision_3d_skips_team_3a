// PrepareResults_review_convey @ 0x140685e50
// function FUN_140685e50 [140685e50 ..]


void FUN_140685e50(longlong *param_1,longlong param_2,CPanel *param_3)

{
  int *piVar1;
  int iVar2;
  CAnomalie *pCVar3;
  longlong *plVar4;
  longlong lVar5;
  longlong *plVar6;
  char cVar7;
  CCarteId *pCVar8;
  undefined8 *puVar9;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_68 [8];
  undefined8 *local_60;
  undefined8 local_58;
  undefined8 *local_50;
  CAnomalie *local_48;
  longlong *local_40;
  CLogManagerFunctionML local_38 [48];
  
  local_58 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_68,"CProductionDoc::FM_CopyAnomaliesToPanel");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_38,0x10,local_68,(ulonglong)*(uint *)((longlong)param_1 + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_68);
  cVar7 = (**(code **)(*param_1 + 0x238))(param_1);
  if (cVar7 != '\0') {
    local_50 = (undefined8 *)(param_2 + 8);
    local_60 = (undefined8 *)*local_50;
    for (puVar9 = (undefined8 *)*local_60; puVar9 != local_60; puVar9 = (undefined8 *)*puVar9) {
      pCVar3 = (CAnomalie *)puVar9[2];
      plVar4 = (longlong *)puVar9[3];
      if (plVar4 != (longlong *)0x0) {
        LOCK();
        *(int *)(plVar4 + 1) = (int)plVar4[1] + 1;
        UNLOCK();
      }
      local_48 = pCVar3;
      local_40 = plVar4;
      cVar7 = (**(code **)(*(longlong *)pCVar3 + 0x30))(pCVar3);
      if ((cVar7 == '\x01') &&
         (pCVar8 = CPanel::Carte(param_3,*(long *)(pCVar3 + 8)),
         (*(uint *)(pCVar8 + 0x34) & 0x100) == 0)) {
        pCVar8 = CPanel::Carte(param_3,*(long *)(pCVar3 + 8));
        CCarteId::TestedObjects_Add(pCVar8,pCVar3);
      }
      plVar6 = local_40;
      if (plVar4 != (longlong *)0x0) {
        LOCK();
        plVar4 = plVar4 + 1;
        lVar5 = *plVar4;
        *(int *)plVar4 = (int)*plVar4 + -1;
        UNLOCK();
        if ((int)lVar5 == 1) {
          (**(code **)(*local_40 + 8))(local_40);
          LOCK();
          piVar1 = (int *)((longlong)plVar6 + 0xc);
          iVar2 = *piVar1;
          *piVar1 = *piVar1 + -1;
          UNLOCK();
          if (iVar2 == 1) {
            (**(code **)(*local_40 + 0x10))();
          }
        }
      }
    }
  }
  CLogManagerFunctionML::~CLogManagerFunctionML(local_38);
  return;
}

