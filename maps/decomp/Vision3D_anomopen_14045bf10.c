// FUN_14045bf10 @ 14045bf10 body=125


undefined8 FUN_14045bf10(longlong *param_1)

{
  undefined8 *puVar1;
  char cVar2;
  undefined8 uVar3;
  undefined8 *puVar4;
  undefined8 *puVar5;
  undefined8 *puVar6;
  int local_res8 [8];
  
  uVar3 = (**(code **)(*param_1 + 0x1140))();
  cVar2 = FUN_14045bfd0(param_1,uVar3,local_res8);
  if (cVar2 != '\0') {
    puVar1 = (undefined8 *)param_1[0x344];
    cVar2 = *(char *)((longlong)puVar1[1] + 0x19);
    puVar5 = puVar1;
    puVar4 = (undefined8 *)puVar1[1];
    while (cVar2 == '\0') {
      if (*(int *)(puVar4 + 4) < local_res8[0]) {
        puVar6 = (undefined8 *)puVar4[2];
        puVar4 = puVar5;
      }
      else {
        puVar6 = (undefined8 *)*puVar4;
      }
      puVar5 = puVar4;
      puVar4 = puVar6;
      cVar2 = *(char *)((longlong)puVar6 + 0x19);
    }
    if ((puVar5 == puVar1) || (local_res8[0] < *(int *)(puVar5 + 4))) {
      puVar5 = puVar1;
    }
    if (puVar5 != puVar1) {
      return puVar5[5];
    }
  }
  return 0;
}

