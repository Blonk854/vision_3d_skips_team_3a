// CExtFormulaGridWnd::OnGbwAnalyzeCellMouseClickEvent @ 1801ab170


/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */
/* public: virtual bool __cdecl CExtFormulaGridWnd::OnGbwAnalyzeCellMouseClickEvent(unsigned
   int,unsigned int,unsigned int,class CPoint) __ptr64 */

bool __thiscall
CExtFormulaGridWnd::OnGbwAnalyzeCellMouseClickEvent
          (CExtFormulaGridWnd *this,undefined4 param_1,int param_2,undefined4 param_3,
          undefined8 param_5)

{
  bool bVar1;
  char cVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  BOOL BVar6;
  HWND__ *pHVar7;
  int iVar8;
  bool bVar9;
  bool bVar10;
  bool bVar11;
  undefined1 auStack_178 [32];
  undefined8 *local_158;
  undefined8 *local_150;
  undefined8 *local_148;
  undefined8 *local_140;
  undefined8 local_138;
  int local_130;
  undefined8 local_128;
  undefined4 local_120;
  undefined4 local_11c;
  undefined8 local_118;
  undefined8 local_110;
  undefined8 local_108;
  undefined8 local_100;
  undefined8 local_f8 [2];
  int local_e8;
  int iStack_e4;
  int iStack_e0;
  int iStack_dc;
  int local_d8;
  int iStack_d4;
  int iStack_d0;
  int iStack_cc;
  RECT local_c8;
  int local_b8;
  int iStack_b4;
  int iStack_b0;
  int iStack_ac;
  POINT local_a8;
  int local_a0;
  int local_9c;
  uint local_90;
  int local_8c;
  int local_88;
  int local_84;
  int local_80;
  ulonglong local_58;
  
                    /* 0x1ab170  12810
                       ?OnGbwAnalyzeCellMouseClickEvent@CExtFormulaGridWnd@@UEAA_NIIIVCPoint@@@Z */
  local_58 = DAT_180874ae0 ^ (ulonglong)auStack_178;
  local_130 = param_2;
  local_120 = param_3;
  local_11c = param_1;
  uVar3 = (**(code **)(*(longlong *)this + 0xcd8))();
  if (((uVar3 & 3) != 0) &&
     (pHVar7 = CExtGridBaseWnd::GetSafeInplaceActiveHwnd((CExtGridBaseWnd *)this),
     pHVar7 == (HWND__ *)0x0)) {
    CExtGridHitTestInfo::CExtGridHitTestInfo((CExtGridHitTestInfo *)&local_a8,param_5);
    local_158 = (undefined8 *)((ulonglong)local_158 & 0xffffffffffffff00);
    (**(code **)(*(longlong *)this + 0x538))(this,&local_a8,0,1);
    if (((((local_90 & 0x200) == 0) ||
         ((bVar1 = CExtGridHitTestInfo::IsHoverEmpty((CExtGridHitTestInfo *)&local_a8), bVar1 ||
          (bVar1 = CExtGridHitTestInfo::IsValidRect((CExtGridHitTestInfo *)&local_a8,true), !bVar1))
         )) || ((uVar4 = (**(code **)(*(longlong *)this + 0x438))(this), (uVar4 >> 0x19 & 1) == 0 &&
                (cVar2 = (**(code **)(*(longlong *)this + 0x4e8))(this), cVar2 == '\0')))) ||
       (iVar5 = (**(code **)(*(longlong *)this + 0x660))(this), iVar5 != 1)) goto LAB_1801ab545;
    (**(code **)(*(longlong *)this + 0x668))(this,&local_b8,1,0);
    bVar1 = local_b8 == local_9c;
    bVar9 = iStack_b4 == local_a0;
    bVar10 = iStack_b0 == local_9c;
    bVar11 = iStack_ac == local_a0;
    if (((bVar1) || (bVar10)) && ((local_a0 < iStack_b4 || (iStack_ac < local_a0)))) {
      bVar10 = false;
      bVar1 = false;
    }
    if (((bVar9) || (bVar11)) && ((local_9c < local_b8 || (iStack_b0 < local_9c)))) {
      bVar11 = false;
      bVar9 = false;
    }
    if ((((!bVar1) && (!bVar9)) && (!bVar10)) && (!bVar11)) goto LAB_1801ab545;
    local_140 = &local_138;
    iVar8 = 0;
    iVar5 = 0;
    local_148 = &local_118;
    local_150 = &local_110;
    local_128 = 0;
    local_158 = &local_108;
    local_f8[0] = 0;
    local_100 = 0;
    local_108 = 0;
    local_110 = 0;
    local_118 = 0;
    local_138 = 0;
    (**(code **)(*(longlong *)this + 0xd58))(this,&local_128,local_f8,&local_100);
    if (((bVar10) && (bVar11)) && ((uVar3 & 2) != 0)) {
      local_c8.top = ((local_80 - local_138._4_4_) - local_128._4_4_) + 1;
      local_c8.left = ((local_84 - (int)local_138) - (int)local_128) + 1;
      local_c8.right = (int)local_138 + local_c8.left;
      local_c8.bottom = local_c8.top + local_138._4_4_;
      BVar6 = PtInRect(&local_c8,local_a8);
      if (BVar6 != 0) {
        if (local_130 != 1) {
          return true;
        }
        local_d8 = local_c8.left;
        iStack_d4 = local_c8.top;
        iStack_d0 = local_c8.right;
        iStack_cc = local_c8.bottom;
        local_e8 = local_b8;
        iStack_e4 = iStack_b4;
        iStack_e0 = iStack_b0;
        iStack_dc = iStack_ac;
        (**(code **)(*(longlong *)this + 0xd90))(this,&local_e8,&local_d8,local_a8);
        return true;
      }
    }
    if ((uVar3 & 1) == 0) goto LAB_1801ab545;
    if ((bVar9) || (bVar11)) {
      iVar5 = local_84 - local_8c;
    }
    if ((((bVar1) || (bVar10)) && (iVar8 = local_80 - local_88, bVar1)) && (0 < iVar8)) {
      local_c8.bottom = local_88 + iVar8;
      local_c8.right = (int)local_138 + local_8c;
      local_c8.top = local_88;
      local_c8.left = local_8c;
      BVar6 = PtInRect(&local_c8,local_a8);
      if (BVar6 != 0) goto LAB_1801ab519;
    }
    if ((bVar9) && (0 < iVar5)) {
      local_c8.right = local_8c + iVar5;
      local_c8.bottom = local_138._4_4_ + local_88;
      local_c8.left = local_8c;
      local_c8.top = local_88;
      BVar6 = PtInRect(&local_c8,local_a8);
      if (BVar6 != 0) goto LAB_1801ab519;
    }
    if ((bVar10) && (0 < iVar8)) {
      local_c8.left = (local_84 - (int)local_138) - (int)local_128;
      local_c8.right = (int)local_138 + local_c8.left;
      local_c8.bottom = local_88 + iVar8;
      local_c8.top = local_88;
      BVar6 = PtInRect(&local_c8,local_a8);
      if (BVar6 != 0) goto LAB_1801ab519;
    }
    if ((bVar11) && (0 < iVar5)) {
      local_c8.right = local_8c + iVar5;
      local_c8.top = (local_80 - local_138._4_4_) - local_128._4_4_;
      local_c8.bottom = local_c8.top + local_138._4_4_;
      local_c8.left = local_8c;
      BVar6 = PtInRect(&local_c8,local_a8);
      if (BVar6 != 0) {
LAB_1801ab519:
        if (local_130 != 1) {
          return true;
        }
        local_e8 = local_b8;
        iStack_e4 = iStack_b4;
        iStack_e0 = iStack_b0;
        iStack_dc = iStack_ac;
        (**(code **)(*(longlong *)this + 0xd88))(this,&local_e8,&local_a8);
        return true;
      }
    }
  }
LAB_1801ab545:
  local_158 = (undefined8 *)param_5;
  bVar1 = CExtGridWnd::OnGbwAnalyzeCellMouseClickEvent
                    ((CExtGridWnd *)this,local_11c,local_130,local_120);
  return bVar1;
}

