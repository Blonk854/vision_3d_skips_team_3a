// FUN_1405ddc30 @ 1405ddc30 body=50


undefined1 FUN_1405ddc30(void)

{
  CWinThread *pCVar1;
  longlong lVar2;
  
  pCVar1 = AfxGetThread();
  if (pCVar1 != (CWinThread *)0x0) {
    lVar2 = (**(code **)(*(longlong *)pCVar1 + 0xf8))(pCVar1);
    return *(undefined1 *)(lVar2 + 0x979);
  }
  return uRam0000000000000979;
}

