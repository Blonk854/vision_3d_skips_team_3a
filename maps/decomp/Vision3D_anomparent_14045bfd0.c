// FUN_14045bfd0 @ 14045bfd0


undefined8 FUN_14045bfd0(longlong *param_1,longlong param_2,undefined4 *param_3,undefined8 param_4)

{
  undefined4 uVar1;
  undefined8 uVar2;
  longlong *plVar3;
  undefined4 local_res10 [2];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_res18 [8];
  
  *param_3 = 0;
  if (param_2 != 0) {
    local_res10[0] = 0xc09;
    uVar2 = (**(code **)(*param_1 + 0x1118))
                      (param_1,local_res18,local_res10,param_4,0xfffffffffffffffe);
    plVar3 = (longlong *)(**(code **)(*param_1 + 0x1150))(param_1,uVar2,param_2);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_res18);
    if (plVar3 != (longlong *)0x0) {
      uVar1 = (**(code **)(*plVar3 + 0x28))(plVar3);
      *param_3 = uVar1;
      return 1;
    }
  }
  return 0;
}

