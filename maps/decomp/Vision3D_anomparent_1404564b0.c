// FUN_1404564b0 @ 1404564b0


undefined8 FUN_1404564b0(undefined8 *param_1,longlong param_2)

{
  char cVar1;
  code *local_res8;
  
  cVar1 = (**(code **)*param_1)();
  if (((((cVar1 != '\0') && (*(int *)(param_1 + 0x24) == *(int *)(param_2 + 0x120))) &&
       (*(int *)((longlong)param_1 + 0x124) == *(int *)(param_2 + 0x124))) &&
      ((*(char *)(param_1 + 0x25) == *(char *)(param_2 + 0x128) &&
       (*(char *)((longlong)param_1 + 0x129) == *(char *)(param_2 + 0x129))))) &&
     ((*(char *)((longlong)param_1 + 0x12a) == *(char *)(param_2 + 0x12a) &&
      (*(char *)((longlong)param_1 + 299) == *(char *)(param_2 + 299))))) {
    local_res8 = FUN_140451e70;
    cVar1 = FUN_140448380(param_1[0x26],param_1[0x27],*(undefined8 *)(param_2 + 0x130),&local_res8,0
                         );
    if (cVar1 != '\0') {
      local_res8 = FUN_140451e70;
      cVar1 = FUN_140448380(param_1[0x30],param_1[0x31],*(undefined8 *)(param_2 + 0x180),&local_res8
                            ,0);
      if (cVar1 != '\0') {
        cVar1 = FUN_140447510(param_1 + 0x29,param_2 + 0x148);
        if (cVar1 != '\0') {
          cVar1 = FUN_140447490(param_1 + 0x2c,param_2 + 0x160);
          if ((cVar1 != '\0') && (*(char *)(param_1 + 0x2f) == *(char *)(param_2 + 0x178))) {
            if (((*(longlong *)(param_2 + 0x1a0) - *(longlong *)(param_2 + 0x198) ^
                 param_1[0x34] - param_1[0x33]) & 0xffffffffffffffe0U) == 0) {
              cVar1 = FUN_1404482d0();
              if (cVar1 != '\0') {
                return 1;
              }
            }
          }
        }
      }
    }
  }
  return 0;
}

