// CExtTreeGridWnd::OnGbwAnalyzeCellMouseClickEvent @ 180479290


/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */
/* public: virtual bool __cdecl CExtTreeGridWnd::OnGbwAnalyzeCellMouseClickEvent(unsigned
   int,unsigned int,unsigned int,class CPoint) __ptr64 */

bool __thiscall
CExtTreeGridWnd::OnGbwAnalyzeCellMouseClickEvent
          (CExtTreeGridWnd *this,int param_1,int param_2,undefined4 param_3,undefined8 param_5)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  longlong lVar5;
  undefined1 auStack_b8 [32];
  ulonglong local_98;
  CExtGridHitTestInfo local_88 [8];
  undefined4 local_80;
  undefined4 local_7c;
  uint local_70;
  ulonglong local_38;
  
                    /* 0x479290  12815
                       ?OnGbwAnalyzeCellMouseClickEvent@CExtTreeGridWnd@@UEAA_NIIIVCPoint@@@Z */
  local_38 = DAT_180874ae0 ^ (ulonglong)auStack_b8;
  if (param_1 == 1) {
    CExtGridHitTestInfo::CExtGridHitTestInfo(local_88,param_5);
    local_98 = local_98 & 0xffffffffffffff00;
    (**(code **)(*(longlong *)this + 0x538))(this,local_88,0,1);
    bVar1 = CExtGridHitTestInfo::IsHoverEmpty(local_88);
    if ((bVar1) || (bVar1 = CExtGridHitTestInfo::IsValidRect(local_88,true), !bVar1)) {
      return false;
    }
    iVar3 = CExtGridHitTestInfo::GetInnerOuterTypeOfColumn(local_88);
    iVar4 = CExtGridHitTestInfo::GetInnerOuterTypeOfRow(local_88);
    if ((iVar3 == 0) && (iVar4 == 0)) {
      if (param_2 == 1) {
        cVar2 = (**(code **)(*(longlong *)this + 0xdf8))(this,local_7c);
        if ((cVar2 == '\0') || ((local_70 >> 0x18 & 1) == 0)) goto LAB_1804793e3;
      }
      else if (param_2 != 2) goto LAB_1804793e3;
      if (((local_70 & 0x14000) == 0) &&
         ((((lVar5 = (**(code **)(*(longlong *)this + 0xca8))(this,local_80), param_2 == 2 &&
            (lVar5 != 0)) &&
           (iVar3 = (**(code **)(*(longlong *)this + 0xd08))(this,lVar5), 0 < iVar3)) ||
          ((local_70 & 0x400000) != 0)))) {
        (**(code **)(*(longlong *)this + 0xe00))(this,local_80,local_88,3);
        return true;
      }
    }
  }
LAB_1804793e3:
  local_98 = param_5;
  bVar1 = CExtGridWnd::OnGbwAnalyzeCellMouseClickEvent((CExtGridWnd *)this,param_1,param_2,param_3);
  return bVar1;
}

