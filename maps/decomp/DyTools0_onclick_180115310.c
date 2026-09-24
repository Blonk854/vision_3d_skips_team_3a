// CVitExtReportGridWnd::OnClickRightBtnUpInnerCell @ 180115310


/* protected: virtual bool __cdecl CVitExtReportGridWnd::OnClickRightBtnUpInnerCell(long const &
   __ptr64,long const & __ptr64,class CPoint const & __ptr64) __ptr64 */

bool __thiscall
CVitExtReportGridWnd::OnClickRightBtnUpInnerCell
          (CVitExtReportGridWnd *this,long *param_1,long *param_2,CPoint *param_3)

{
  CVitExtReportGridWnd CVar1;
  long local_res8;
  long local_resc;
  tagPOINT local_18;
  undefined1 local_10 [8];
  
                    /* 0x115310  2934
                       ?OnClickRightBtnUpInnerCell@CVitExtReportGridWnd@@MEAA_NAEBJ0AEBVCPoint@@@Z
                        */
  CVar1 = this[0x1a1c];
  if (CVar1 != (CVitExtReportGridWnd)0x0) {
    local_res8 = *param_1;
    local_resc = *param_2;
    CWnd::SetFocus((CWnd *)this);
    (**(code **)(*(longlong *)this + 0x6d0))(this,local_10,&local_res8,1,1,0,1,0);
    local_18 = *(tagPOINT *)param_3;
    ClientToScreen(*(HWND *)(this + 0x40),&local_18);
    (**(code **)(*(longlong *)this + 0x1298))(this,param_1,param_2,&local_18);
  }
  return CVar1 != (CVitExtReportGridWnd)0x0;
}

