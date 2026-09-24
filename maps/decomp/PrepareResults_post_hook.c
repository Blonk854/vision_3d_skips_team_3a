// PrepareResults_post_hook @ 0x14068ee40
// function FUN_14068ee40 [14068ee40 ..]


void FUN_14068ee40(longlong param_1,undefined8 param_2)

{
  char cVar1;
  AFX_MODULE_STATE *pAVar2;
  longlong lVar3;
  CSPC_Output *pCVar4;
  undefined8 uVar5;
  longlong lVar6;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res8 [8];
  undefined8 local_res10;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res18 [16];
  ulonglong in_stack_ffffffffffffff98;
  undefined4 uVar7;
  CLogManagerFunctionML local_50 [56];
  
  local_res10 = param_2;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res8,"CProductionDoc::OutputFileWrite");
  in_stack_ffffffffffffff98 = in_stack_ffffffffffffff98 & 0xffffffffffffff00;
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_50,0x10,local_res8,(ulonglong)*(uint *)(param_1 + 0x3924),false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
  pAVar2 = AfxGetModuleState();
  lVar3 = __RTDynamicCast(*(undefined8 *)(pAVar2 + 8),0,&CWinApp::RTTI_Type_Descriptor,
                          &CAVisionApp::RTTI_Type_Descriptor,
                          in_stack_ffffffffffffff98 & 0xffffffff00000000);
  if (DAT_141169090 != 0) {
    if (*(uint *)(param_1 + 0x3938) < DAT_1410bf540) {
      *(uint *)(param_1 + 0x3938) = *(uint *)(param_1 + 0x3938) + 1;
      CLogManagerFunctionML::Write(local_50,2,"SPC counter = %d, don\'t write to file this time.");
    }
    else {
      pCVar4 = CAvSPC_Output::GetSPC_Output(*(CAvSPC_Output **)(lVar3 + 400),DAT_141169090);
      if (pCVar4 != (CSPC_Output *)0x0) {
        uVar5 = CTest::GetProductName((CTest *)(param_1 + 0x188));
        lVar3 = *(longlong *)(param_1 + 0x5878) + (longlong)*(int *)(param_1 + 0x5c98) * 0x410;
        lVar6 = lVar3 + 0x18;
        cVar1 = (**(code **)(*(longlong *)pCVar4 + 0x38))
                          (pCVar4,*(int *)(param_1 + 0x3924) + 1,uVar5,param_2,lVar6,lVar3 + 8);
        uVar7 = (undefined4)((ulonglong)lVar6 >> 0x20);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res18);
        if (cVar1 == '\0') {
          CLogManagerFunctionML::Write
                    (local_50,4,"pSPC_Output->Write(%d) failed.",
                     (ulonglong)(*(int *)(param_1 + 0x3924) + 1));
        }
        else {
          CLogManagerFunctionML::Write
                    (local_50,2,"SPC counter = %d, l_pSPC_Output->Write(%d) succeed.",
                     (ulonglong)*(uint *)(param_1 + 0x3938),
                     CONCAT44(uVar7,*(int *)(param_1 + 0x3924) + 1));
        }
      }
      *(undefined4 *)(param_1 + 0x3938) = 1;
    }
  }
  CLogManagerFunctionML::~CLogManagerFunctionML(local_50);
  FUN_1405586b0(param_2);
  return;
}

