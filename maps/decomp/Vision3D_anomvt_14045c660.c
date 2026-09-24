// FUN_14045c660 @ 14045c660


bool FUN_14045c660(CVitExtReportGridWnd *param_1,CWnd *param_2)

{
  bool bVar1;
  
  bVar1 = CVitExtReportGridWnd::Init(param_1,param_2);
  if (!bVar1) {
    return bVar1;
  }
  FUN_14045aa00(param_1);
  CImageListErrorProfUIS::Init((CImageListErrorProfUIS *)(param_1 + 0x1a50),(CExtGridWnd *)param_1);
  (**(code **)(*(longlong *)param_1 + 0x1108))(param_1);
  return true;
}

