// vt off=0x1790 FUN_1404582b0 @ 1404582b0


undefined8 * FUN_1404582b0(undefined8 *param_1,uint param_2)

{
  undefined8 *puVar1;
  undefined1 local_res8 [8];
  
  *param_1 = boost::serialization::shared_ptr_helper<boost::shared_ptr>::vftable;
  puVar1 = (undefined8 *)param_1[1];
  if (puVar1 != (undefined8 *)0x0) {
    FUN_1404606a0(puVar1,local_res8,*(undefined8 *)*puVar1,(undefined8 *)*puVar1,0xfffffffffffffffe)
    ;
    operator_delete((void *)*puVar1);
    FUN_1404556c0(puVar1,0x10);
  }
  if ((param_2 & 1) != 0) {
    FUN_1404556c0(param_1,0x10);
  }
  return param_1;
}

