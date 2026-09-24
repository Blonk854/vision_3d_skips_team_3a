// CExtPropertyGridWnd::OnGbwAnalyzeCellMouseClickEvent @ 18037e940


/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */
/* protected: virtual bool __cdecl CExtPropertyGridWnd::OnGbwAnalyzeCellMouseClickEvent(unsigned
   int,unsigned int,unsigned int,class CPoint) __ptr64 */

bool __thiscall
CExtPropertyGridWnd::OnGbwAnalyzeCellMouseClickEvent
          (CExtPropertyGridWnd *this,int param_1,int param_2,undefined8 param_4,undefined8 param_5)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  BOOL BVar4;
  UINT UVar5;
  longlong lVar6;
  CObject *this_00;
  CRuntimeClass *pCVar7;
  HWND pHVar8;
  undefined1 auStackY_108 [32];
  undefined1 local_c8 [4];
  int local_c4;
  tagMSG local_c0;
  undefined1 local_90 [8];
  CExtGridHitTestInfo local_88 [8];
  long local_80;
  int local_7c;
  ulonglong local_38;
  
                    /* 0x37e940  12813
                       ?OnGbwAnalyzeCellMouseClickEvent@CExtPropertyGridWnd@@MEAA_NIIIVCPoint@@@Z */
  local_38 = DAT_180874ae0 ^ (ulonglong)auStackY_108;
  bVar1 = CExtTreeGridWnd::OnGbwAnalyzeCellMouseClickEvent();
  if (param_1 == 1) {
    if (param_2 == 2) {
      CExtGridHitTestInfo::CExtGridHitTestInfo(local_88,param_5);
      (**(code **)(*(longlong *)this + 0x538))(this,local_88,0,1);
      bVar2 = CExtGridHitTestInfo::IsHoverEmpty(local_88);
      if (((((!bVar2) && (bVar2 = CExtGridHitTestInfo::IsValidRect(local_88,true), bVar2)) &&
           ((local_7c == 0 &&
            ((iVar3 = CExtGridHitTestInfo::GetInnerOuterTypeOfColumn(local_88), iVar3 == 0 &&
             (iVar3 = CExtGridHitTestInfo::GetInnerOuterTypeOfRow(local_88), iVar3 == 0)))))) &&
          (lVar6 = (**(code **)(*(longlong *)this + 0xca8))(this,local_80), lVar6 != 0)) &&
         (this_00 = (CObject *)(**(code **)(*(longlong *)this + 0xe90))(this,lVar6),
         this_00 != (CObject *)0x0)) {
        pCVar7 = CExtPropertyValue::GetThisClass();
        iVar3 = CObject::IsKindOf(this_00,pCVar7);
        if (iVar3 != 0) {
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),0x200,0x20e,1);
          } while (BVar4 != 0);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),7,8,1);
          } while (BVar4 != 0);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),0x21,0x21,1);
          } while (BVar4 != 0);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),0x86,0x86,1);
          } while (BVar4 != 0);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),0x84,0x84,1);
          } while (BVar4 != 0);
          UVar5 = GetDoubleClickTime();
          Sleep(UVar5 / 3);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),0x200,0x20e,1);
          } while (BVar4 != 0);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),7,8,1);
          } while (BVar4 != 0);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),0x21,0x21,1);
          } while (BVar4 != 0);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),0x86,0x86,1);
          } while (BVar4 != 0);
          do {
            BVar4 = PeekMessageA(&local_c0,*(HWND *)(this + 0x40),0x84,0x84,1);
          } while (BVar4 != 0);
          CExtGridBaseWnd::EditCell((CExtGridBaseWnd *)this,1,local_80,0,0,true,(char *)0x0);
          bVar1 = true;
        }
      }
    }
  }
  else if ((param_1 == 2) && (param_2 == 1)) {
    CExtGridHitTestInfo::CExtGridHitTestInfo(local_88,param_5);
    (**(code **)(*(longlong *)this + 0x538))(this,local_88,0,0);
    bVar2 = CExtGridHitTestInfo::IsHoverEmpty(local_88);
    if ((!bVar2) &&
       (((iVar3 = CExtGridHitTestInfo::GetInnerOuterTypeOfColumn(local_88), iVar3 == 0 &&
         (iVar3 = CExtGridHitTestInfo::GetInnerOuterTypeOfRow(local_88), iVar3 == 0)) &&
        ((**(code **)(*(longlong *)this + 0x6c8))(this,local_c8), local_c4 != local_80)))) {
      pHVar8 = GetFocus();
      if (pHVar8 != *(HWND *)(this + 0x40)) {
        CWnd::SetFocus((CWnd *)this);
      }
      local_c4 = local_80;
      (**(code **)(*(longlong *)this + 0x6d0))(this,local_90,local_c8,1);
      bVar1 = true;
    }
  }
  return bVar1;
}

