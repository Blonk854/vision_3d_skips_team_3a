// caller FUN_14063cad0 @ 14063cad0 body=133


CVitExtReportGridWnd * FUN_14063cad0(CVitExtReportGridWnd *param_1)

{
  CVitExtReportGridWnd::CVitExtReportGridWnd(param_1,(CWnd *)0x0);
  *(undefined4 *)(param_1 + 0x1a08) = 1;
  *(undefined ***)param_1 = CMaintenanceGammaCorrection::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0xe8) = CMaintenanceGammaCorrection::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0xf0) = CMaintenanceGammaCorrection::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0x1038) = CMaintenanceGammaCorrection::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0x1218) = CMaintenanceGammaCorrection::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0x18d0) = CMaintenanceGammaCorrection::CCalibGreyGrid::vftable;
  *(undefined4 *)(param_1 + 0x1a10) = 1;
  param_1[0x1a14] = (CVitExtReportGridWnd)0x0;
  return param_1;
}

