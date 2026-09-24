// ProductionCommunication_SendResults @ 0x14067c7b0
// function FUN_14067c7b0 [14067c7b0 ..]


undefined8 FUN_14067c7b0(longlong param_1)

{
  longlong lVar1;
  longlong lVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  AFX_MODULE_STATE *pAVar6;
  CPanel *this;
  ulonglong *puVar7;
  undefined8 *puVar8;
  undefined8 uVar9;
  __int64 _Var10;
  CCarteId *this_00;
  CAnomalie *this_01;
  undefined *puVar11;
  CMsgPanel *this_02;
  __uint64 _Var12;
  int iVar13;
  longlong local_res8;
  longlong *local_res10;
  CCarteId *local_res18;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res20 [8];
  ulonglong uVar14;
  ulonglong in_stack_fffffffffffffeb0;
  __uint64 local_148;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_140 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_138 [24];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_120 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_118 [16];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_108 [8];
  __uint64 local_100;
  __uint64 local_f8;
  CMsgPanel *local_f0;
  CMsgImage local_e8 [8];
  undefined4 local_e0;
  undefined4 local_dc;
  undefined4 local_d8;
  __uint64 local_a0;
  uchar *local_98 [2];
  CLogManagerFunctionML local_88 [48];
  undefined8 local_58;
  
  local_58 = 0xfffffffffffffffe;
  local_res8 = param_1;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res20,"CProductionCommunication::SendResults");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_88,0x10,local_res20,(ulonglong)*(uint *)(*(longlong *)(param_1 + 0x20) + 0x3924),
             true);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res20);
  pAVar6 = AfxGetModuleState();
  lVar1 = *(longlong *)(*(longlong *)(pAVar6 + 8) + 0x40);
  lVar2 = *(longlong *)(param_1 + 0x20);
  this_02 = (CMsgPanel *)(lVar2 + 24000);
  local_f0 = this_02;
  cVar3 = FUN_14068b8a0();
  if ((cVar3 == '\0') && (cVar3 = FUN_140685d70(*(undefined8 *)(param_1 + 0x20)), cVar3 == '\0')) {
    uVar4 = 0;
  }
  else {
    uVar4 = 1;
  }
  *(undefined4 *)(lVar2 + 0x5dd0) = uVar4;
  this = CMsgPanel::_Panel_Ptr(this_02,0);
  iVar13 = 0;
  local_res10 = (longlong *)0x0;
  local_f8 = CPanel::Carte_GetNumber(this);
  local_148 = 0;
  iVar5 = 0;
  if (0 < (longlong)local_f8) {
    do {
      iVar13 = iVar5;
      puVar7 = (ulonglong *)CPanel::_csFace(this);
      puVar8 = (undefined8 *)CPanel::_csCB(this);
      in_stack_fffffffffffffeb0 = *puVar7;
      CLogManagerFunctionML::Write
                (local_88,2,"Sub-panel %Id: ID code = \'%s\', side = \'%s\'.\n",local_148,*puVar8,
                 in_stack_fffffffffffffeb0);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_140);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_138);
      CMsgImage::CMsgImage(local_e8);
      local_e0 = 0x10000;
      uVar9 = CPanel::_csCB(this);
      CCommande::_csComParam((CCommande *)local_e8,1,uVar9);
      uVar9 = CPanel::_csFace(this);
      CCommande::_csComParam((CCommande *)local_e8,2,uVar9);
      _Var10 = CPanel::_ctDate(this);
      local_dc = (undefined4)_Var10;
      this_00 = CPanel::CarteIndex(this,local_148);
      local_res18 = this_00;
      local_100 = CCarteId::TestedObjects_GetNumber(this_00);
      _Var12 = 0;
      if (0 < (longlong)local_100) {
        do {
          this_01 = CCarteId::TestedObjects_pGet(this_00,_Var12);
          if (((*(int *)(this_01 + 0x158) == 1) &&
              (this_00 = local_res18, *(longlong *)(this_01 + 400) != 0)) &&
             (*(longlong *)(this_01 + 0x198) != 0)) {
            puVar7 = (ulonglong *)CAnomalie::_csTopoCarte(this_01);
            puVar8 = (undefined8 *)CPanel::_csCB(this);
            uVar14 = *puVar7;
            CLogManagerFunctionML::Write
                      (local_88,2,"Panel \'%s\' Elmt Id \'%s\': picture ready to be sent.\n",*puVar8
                       ,uVar14);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_120);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_118);
            local_a0 = 0;
            local_98[0] = (uchar *)0x0;
            if ((*(longlong *)(this_01 + 400) != 0) && (*(longlong *)(this_01 + 0x198) != 0)) {
              CMemBuffer::GetBuffer((CMemBuffer *)(this_01 + 0x188),local_98,&local_a0);
            }
            uVar9 = CAnomalie::_csTopo(this_01);
            CCommande::_csComParam((CCommande *)local_e8,3,uVar9);
            local_d8 = *(undefined4 *)(this_01 + 8);
            in_stack_fffffffffffffeb0 = in_stack_fffffffffffffeb0 & 0xffffffff00000000;
            iVar5 = FUN_14064e110(lVar1 + 0x56b0,local_e8,&local_res10,
                                  *(undefined4 *)(lVar1 + 0x57b4),uVar14 & 0xffffffffffffff00,
                                  in_stack_fffffffffffffeb0);
            if (iVar5 == 0) {
              puVar8 = (undefined8 *)CPanel::_csCB(this);
              CLogManagerFunctionML::Write(local_88,4,"oNetwork.Send(%s) failed.\n",*puVar8);
              ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
              ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_108);
            }
            else {
              iVar13 = iVar13 + 1;
            }
            local_98[0] = (uchar *)0x0;
            local_a0 = 0;
            CMemBuffer::DeleteBuffer((CMemBuffer *)(this_01 + 0x188));
            this_00 = local_res18;
            if (local_res10 != (longlong *)0x0) {
              (**(code **)(*local_res10 + 8))(local_res10,1);
              local_res10 = (longlong *)0x0;
              this_00 = local_res18;
            }
          }
          _Var12 = _Var12 + 1;
        } while ((longlong)_Var12 < (longlong)local_100);
      }
      CMsgImage::~CMsgImage(local_e8);
      local_148 = local_148 + 1;
      param_1 = local_res8;
      this_02 = local_f0;
      iVar5 = iVar13;
    } while ((longlong)local_148 < (longlong)local_f8);
  }
  puVar8 = (undefined8 *)CPanel::_csCB(this);
  puVar11 = &DAT_140e9e944;
  if (*(int *)(this_02 + 0xc) == 0) {
    puVar11 = &DAT_140e96018;
  }
  CLogManagerFunctionML::Write
            (local_88,2,"Msg Panel <%s> to send: Send to repair <%s>.\n",*puVar8,puVar11);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8);
  uVar9 = CONCAT71((int7)((ulonglong)puVar11 >> 8),1);
  iVar5 = FUN_14064e110(lVar1 + 0x56b0,this_02,&local_res10,*(undefined4 *)(lVar1 + 0x57b4),uVar9,
                        in_stack_fffffffffffffeb0 & 0xffffffff00000000);
  uVar4 = (undefined4)((ulonglong)uVar9 >> 0x20);
  if (iVar5 == 0) {
    puVar8 = (undefined8 *)CPanel::_csCB(this);
    CLogManagerFunctionML::Write(local_88,4,"oNetwork.Send(%s) failed.\n",*puVar8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8);
  }
  puVar8 = (undefined8 *)CPanel::_csCB(this);
  CLogManagerFunctionML::Write
            (local_88,2,"Msg Panel <%s> and %d image(s) sent to supervisor.\n",*puVar8,
             CONCAT44(uVar4,iVar13));
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_res8);
  if (local_res10 != (longlong *)0x0) {
    (**(code **)(*local_res10 + 8))(local_res10,1);
    local_res10 = (longlong *)0x0;
  }
  CPanel::Clear(this);
  ReleaseSemaphore(*(HANDLE *)(*(longlong *)(param_1 + 0x20) + 0x3890),1,(LPLONG)0x0);
  CLogManagerFunctionML::~CLogManagerFunctionML(local_88);
  return 1;
}

