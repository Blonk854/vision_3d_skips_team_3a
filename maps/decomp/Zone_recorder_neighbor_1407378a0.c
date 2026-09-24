// Zone_recorder_neighbor_1407378a0 @ 0x1407378a0
// function FUN_1407378a0 [1407378a0 ..]


undefined8
FUN_1407378a0(longlong param_1,
             CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *param_2,
             undefined8 param_3,undefined8 *param_4)

{
  int *piVar1;
  longlong *plVar2;
  int iVar3;
  longlong *plVar4;
  longlong lVar5;
  bool bVar6;
  char cVar7;
  CModelFamily *this;
  undefined8 uVar8;
  undefined8 *puVar9;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res8 [8];
  longlong *local_res20;
  undefined8 local_90;
  longlong *plStack_88;
  undefined8 local_80;
  longlong *local_78;
  CLogManagerFunctionML local_70 [56];
  
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res8,"CZoneAnalysis::GetModelFamilyComponent");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_70,0x10,local_res8,(ulonglong)*(uint *)(*(longlong *)(param_1 + 0x10) + 0x3924),
             false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
  uVar8 = 0;
  *param_4 = 0;
  this = CBibliotheque::GetModelFamily
                   ((CBibliotheque *)(*(longlong *)(param_1 + 0x10) + 0x11f8),param_2);
  *param_4 = this;
  if (this == (CModelFamily *)0x0) {
    CLogManagerFunctionML::Write
              (local_70,4,
               "Zone index %Id, GetProdDocument()->m_CBib.GetModelFamily(\'%s\') failed.\n",param_3,
               *(undefined8 *)param_2);
  }
  else if (*(int *)(this + 0x30) == 0) {
    bVar6 = CModelFamily::IsImagesAnalysisAuthorized(this,true);
    if (bVar6) {
      if (*(longlong *)(param_1 + 8) != 0) {
        local_90 = 0;
        plStack_88 = (longlong *)0x0;
        cVar7 = FUN_140737720(*(longlong *)(param_1 + 8),param_4,&local_90);
        if (cVar7 == '\0') {
          uVar8 = (**(code **)(*(longlong *)*param_4 + 0x48))();
          local_78 = (longlong *)0x0;
          local_80 = uVar8;
          puVar9 = (undefined8 *)FUN_140734fb0(&local_res20,uVar8);
          plVar4 = (longlong *)*puVar9;
          *puVar9 = local_78;
          local_78 = plVar4;
          if (local_res20 != (longlong *)0x0) {
            LOCK();
            plVar4 = local_res20 + 1;
            lVar5 = *plVar4;
            *(int *)plVar4 = (int)*plVar4 + -1;
            UNLOCK();
            if ((int)lVar5 == 1) {
              (**(code **)(*local_res20 + 8))(local_res20);
              LOCK();
              piVar1 = (int *)((longlong)local_res20 + 0xc);
              iVar3 = *piVar1;
              *piVar1 = *piVar1 + -1;
              UNLOCK();
              if (iVar3 == 1) {
                (**(code **)(*local_res20 + 0x10))(local_res20);
              }
            }
          }
          FUN_140467b70(&local_80,uVar8,uVar8);
          FUN_1407352e0(&local_90,&local_80);
          plVar4 = local_78;
          if (local_78 != (longlong *)0x0) {
            LOCK();
            plVar2 = local_78 + 1;
            lVar5 = *plVar2;
            *(int *)plVar2 = (int)*plVar2 + -1;
            UNLOCK();
            if ((int)lVar5 == 1) {
              (**(code **)(*local_78 + 8))(local_78);
              LOCK();
              piVar1 = (int *)((longlong)plVar4 + 0xc);
              iVar3 = *piVar1;
              *piVar1 = *piVar1 + -1;
              UNLOCK();
              if (iVar3 == 1) {
                (**(code **)(*plVar4 + 0x10))(plVar4);
              }
            }
          }
          FUN_140735410(*(undefined8 *)(param_1 + 8),param_4,&local_90);
          CLogManagerFunctionML::Write
                    (local_70,2,"Zone index %Id, Clone Family = \'%s\'\n",param_3,
                     *(undefined8 *)param_2);
        }
        plVar4 = plStack_88;
        *param_4 = local_90;
        if (plStack_88 != (longlong *)0x0) {
          LOCK();
          plVar2 = plStack_88 + 1;
          lVar5 = *plVar2;
          *(int *)plVar2 = (int)*plVar2 + -1;
          UNLOCK();
          if ((int)lVar5 == 1) {
            (**(code **)(*plStack_88 + 8))(plStack_88);
            LOCK();
            piVar1 = (int *)((longlong)plVar4 + 0xc);
            iVar3 = *piVar1;
            *piVar1 = *piVar1 + -1;
            UNLOCK();
            if (iVar3 == 1) {
              (**(code **)(*plStack_88 + 0x10))();
            }
          }
        }
      }
      uVar8 = 1;
    }
  }
  CLogManagerFunctionML::~CLogManagerFunctionML(local_70);
  return uVar8;
}

