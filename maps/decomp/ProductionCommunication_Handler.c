// ProductionCommunication_Handler @ 0x14067c480
// function FUN_14067c480 [14067c480 ..]


undefined8 FUN_14067c480(longlong param_1)

{
  DWORD DVar1;
  ELogManagerStateLevel EVar2;
  char *pcVar3;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res8 [32];
  HANDLE local_50;
  undefined8 local_48;
  undefined8 local_40;
  CLogManagerFunctionML local_38 [48];
  
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_res8,"CProductionCommunication::Handler");
  CLogManagerFunctionML::CLogManagerFunctionML
            (local_38,0x10,local_res8,(ulonglong)*(uint *)(*(longlong *)(param_1 + 0x20) + 0x3924),
             false);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res8);
LAB_14067c4e2:
  do {
    local_50 = *(HANDLE *)(param_1 + 0x18);
    local_48 = *(undefined8 *)(param_1 + 0x40);
    local_40 = *(undefined8 *)(param_1 + 0x38);
    CLogManagerFunctionML::Write(local_38,2,"Waiting results...\n");
    DVar1 = WaitForMultipleObjects(3,&local_50,0,0xffffffff);
    if (DVar1 == 0) {
      pcVar3 = "Stop event received.\n";
      EVar2 = 2;
LAB_14067c590:
      CLogManagerFunctionML::Write(local_38,EVar2,pcVar3);
      CLogManagerFunctionML::~CLogManagerFunctionML(local_38);
      return 0;
    }
    if (DVar1 != 1) {
      if (DVar1 != 2) {
        pcVar3 = "WaitForMultipleObjects() failed.\n";
        EVar2 = 4;
        goto LAB_14067c590;
      }
      CLogManagerFunctionML::Write(local_38,2,"Alarm received.\n");
      FUN_14067c630(param_1);
      goto LAB_14067c4e2;
    }
    CLogManagerFunctionML::Write(local_38,2,"Inspection results available.\n");
    FUN_14067c7b0(param_1);
  } while( true );
}

