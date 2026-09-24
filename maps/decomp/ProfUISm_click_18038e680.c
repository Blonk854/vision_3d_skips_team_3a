// CExtReportGridWnd::OnGbwAnalyzeCellMouseClickEvent @ 18038e680


/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */
/* public: virtual bool __cdecl CExtReportGridWnd::OnGbwAnalyzeCellMouseClickEvent(unsigned
   int,unsigned int,unsigned int,class CPoint) __ptr64 */

bool __thiscall
CExtReportGridWnd::OnGbwAnalyzeCellMouseClickEvent
          (CExtReportGridWnd *this,int param_1,int param_2,ulonglong param_4,tagPOINT param_5)

{
  bool bVar1;
  char cVar2;
  undefined1 auStack_f8 [32];
  tagPOINT local_d8;
  undefined8 *local_d0;
  undefined4 local_c8;
  tagPOINT local_b8;
  undefined8 local_b0;
  undefined8 local_a8;
  undefined8 local_a0;
  undefined8 local_98;
  CExtGridHitTestInfo local_88 [24];
  int local_70;
  ulonglong local_38;
  
                    /* 0x38e680  12814
                       ?OnGbwAnalyzeCellMouseClickEvent@CExtReportGridWnd@@UEAA_NIIIVCPoint@@@Z */
  local_38 = DAT_180874ae0 ^ (ulonglong)auStack_f8;
  local_d8 = param_5;
  bVar1 = CExtTreeGridWnd::OnGbwAnalyzeCellMouseClickEvent();
  if (bVar1) {
LAB_18038e6bf:
    bVar1 = true;
  }
  else {
    if (((param_1 == 2) && (param_2 == 0)) && ((param_4 & 0xc) == 0)) {
      CExtGridHitTestInfo::CExtGridHitTestInfo(local_88,param_5);
      local_d8 = (tagPOINT)((ulonglong)local_d8 & 0xffffffffffffff00);
      (**(code **)(*(longlong *)this + 0x538))(this,local_88,0,1);
      if (local_70 == 0x101) {
        local_b8 = param_5;
        ClientToScreen(*(HWND *)(this + 0x40),&local_b8);
        local_c8 = 0;
        local_a0 = 0;
        local_98 = 0;
        local_b0 = 0;
        local_a8 = 0;
        local_d0 = &local_b0;
        local_d8 = (tagPOINT)&local_a0;
        cVar2 = (**(code **)(*(longlong *)this + 0x1070))(this,this,0,&local_b8);
        if (cVar2 != '\0') goto LAB_18038e6bf;
      }
    }
    bVar1 = false;
  }
  return bVar1;
}

