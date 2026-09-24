// caller FUN_14055a8a0 @ 14055a8a0 body=126


CVitExtReportGridWnd * FUN_14055a8a0(CVitExtReportGridWnd *param_1)

{
  CVitExtReportGridWnd::CVitExtReportGridWnd(param_1,(CWnd *)0x0);
  *(undefined4 *)(param_1 + 0x1a08) = 1;
  *(undefined ***)param_1 = CDlgCalibColorCam::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0xe8) = CDlgCalibColorCam::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0xf0) = CDlgCalibColorCam::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0x1038) = CDlgCalibColorCam::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0x1218) = CDlgCalibColorCam::CCalibGreyGrid::vftable;
  *(undefined ***)(param_1 + 0x18d0) = CDlgCalibColorCam::CCalibGreyGrid::vftable;
  *(undefined4 *)(param_1 + 0x1a10) = 1;
  return param_1;
}

