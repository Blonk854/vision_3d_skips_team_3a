// CVitExtReportGridWnd::OnGbwAnalyzeCellMouseClickEvent @ 1801153d0


/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */
/* protected: virtual bool __cdecl CVitExtReportGridWnd::OnGbwAnalyzeCellMouseClickEvent(unsigned
   int,unsigned int,unsigned int,class CPoint) __ptr64 */

bool __thiscall
CVitExtReportGridWnd::OnGbwAnalyzeCellMouseClickEvent
          (CVitExtReportGridWnd *this,int param_1,int param_2,undefined4 param_3,undefined8 param_5)

{
  bool bVar1;
  char cVar2;
  WPARAM wParam;
  longlong lParam;
  undefined1 auStack_c8 [32];
  ulonglong local_a8;
  int local_98;
  int local_94 [3];
  undefined8 local_88;
  int local_80;
  int local_7c;
  ulonglong local_38;
  
                    /* 0x1153d0  3014
                       ?OnGbwAnalyzeCellMouseClickEvent@CVitExtReportGridWnd@@MEAA_NIIIVCPoint@@@Z
                        */
  local_38 = DAT_1802635c0 ^ (ulonglong)auStack_c8;
  CExtGridHitTestInfo::CExtGridHitTestInfo((CExtGridHitTestInfo *)&local_88,param_5);
  local_88 = param_5;
  local_a8 = local_a8 & 0xffffffffffffff00;
  (**(code **)(*(longlong *)this + 0x538))(this,&local_88,1);
  if (((param_1 == 1) && (param_2 == 1)) &&
     (bVar1 = CExtGridHitTestInfo::IsHoverEmpty((CExtGridHitTestInfo *)&local_88), bVar1)) {
    (**(code **)(*(longlong *)this + 0x12a8))(this,1);
    return true;
  }
  bVar1 = CExtGridHitTestInfo::IsHoverInner((CExtGridHitTestInfo *)&local_88);
  if (bVar1) {
    wParam = (WPARAM)local_7c;
    lParam = (longlong)local_80;
    local_94[0] = local_7c;
    local_98 = local_80;
    if (param_1 == 1) {
      if (param_2 == 0) {
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026dde8,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1250))(this,local_94,&local_98,&param_5);
      }
      else if (param_2 == 1) {
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026ddec,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1258))(this,local_94,&local_98,&param_5);
      }
      else {
        if (param_2 != 2) goto LAB_1801156d2;
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026ddf0,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1260))(this,local_94,&local_98,&param_5);
      }
    }
    else if (param_1 == 2) {
      if (param_2 == 0) {
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026ddf4,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1268))(this,local_94,&local_98,&param_5);
      }
      else if (param_2 == 1) {
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026ddf8,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1270))(this,local_94,&local_98,&param_5);
      }
      else {
        if (param_2 != 2) goto LAB_1801156d2;
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026ddfc,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1278))(this,local_94,&local_98,&param_5);
      }
    }
    else {
      if (param_1 != 4) goto LAB_1801156d2;
      if (param_2 == 0) {
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026de00,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1280))(this,local_94,&local_98,&param_5);
      }
      else if (param_2 == 1) {
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026de04,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1288))(this,local_94,&local_98,&param_5);
      }
      else {
        if (param_2 != 2) goto LAB_1801156d2;
        PostMessageA(*(HWND *)(*(longlong *)(this + 0x1a00) + 0x40),DAT_18026de08,wParam,lParam);
        cVar2 = (**(code **)(*(longlong *)this + 0x1290))(this,local_94,&local_98,&param_5);
      }
    }
    if (cVar2 != '\0') {
      return true;
    }
  }
LAB_1801156d2:
  local_a8 = param_5;
  bVar1 = CExtReportGridWnd::OnGbwAnalyzeCellMouseClickEvent
                    ((CExtReportGridWnd *)this,param_1,param_2,param_3);
  return bVar1;
}

