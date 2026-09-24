// FUN_14045c8e0 @ 14045c8e0


void FUN_14045c8e0(CWnd *param_1,undefined8 param_2,undefined8 param_3,int *param_4)

{
  HINSTANCE__ *hInstance;
  HMENU pHVar1;
  CMenu *this;
  undefined **local_20;
  HMENU local_18;
  
  local_20 = CMenu::vftable;
  local_18 = (HMENU)0x0;
  hInstance = AfxFindResourceHandle((char *)0xff0,(char *)0x4);
  pHVar1 = LoadMenuW(hInstance,(LPCWSTR)0xff0);
  CMenu::Attach((CMenu *)&local_20,pHVar1);
  pHVar1 = GetSubMenu(local_18,0);
  this = CMenu::FromHandle(pHVar1);
  CMenu::TrackPopupMenu(this,0,*param_4,param_4[1],param_1,(tagRECT *)0x0);
  local_20 = CMenu::vftable;
  CMenu::DestroyMenu((CMenu *)&local_20);
  return;
}

