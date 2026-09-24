// CExtGridWnd::OnGbwAnalyzeCellMouseClickEvent @ 1801ff1b0


/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */
/* WARNING: Type propagation algorithm not settling */
/* public: virtual bool __cdecl CExtGridWnd::OnGbwAnalyzeCellMouseClickEvent(unsigned int,unsigned
   int,unsigned int,class CPoint) __ptr64 */

bool __thiscall
CExtGridWnd::OnGbwAnalyzeCellMouseClickEvent
          (CExtGridWnd *this,int param_1,uint param_2,undefined4 param_3,ulonglong param_5)

{
  uint uVar1;
  bool bVar2;
  char cVar3;
  undefined1 uVar4;
  SHORT SVar5;
  SHORT SVar6;
  SHORT SVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  longlong *plVar13;
  undefined1 auStack_188 [32];
  ulonglong local_168;
  ulonglong local_160;
  int local_158;
  undefined1 *local_150;
  undefined1 *local_148;
  undefined8 *local_140;
  undefined1 local_138;
  undefined8 local_130;
  undefined8 local_128;
  uint local_118;
  CExtGridHitTestInfo local_108 [8];
  undefined4 local_100;
  undefined4 local_fc;
  byte local_f0;
  undefined8 local_b8;
  undefined8 local_b0;
  CExtGridHitTestInfo local_a8 [8];
  int local_a0;
  int local_9c;
  undefined4 local_98;
  undefined4 local_94;
  uint local_90;
  undefined1 local_8c [16];
  undefined1 local_7c [36];
  ulonglong local_58;
  
                    /* 0x1ff1b0  12812
                       ?OnGbwAnalyzeCellMouseClickEvent@CExtGridWnd@@UEAA_NIIIVCPoint@@@Z */
  local_58 = DAT_180874ae0 ^ (ulonglong)auStack_188;
  local_168 = param_5;
  local_b8 = CONCAT44(local_b8._4_4_,param_3);
  bVar2 = CExtGridBaseWnd::OnGbwAnalyzeCellMouseClickEvent();
  if (bVar2) {
    return true;
  }
  CExtGridHitTestInfo::CExtGridHitTestInfo(local_108,param_5);
  local_168 = local_168 & 0xffffffffffffff00;
  (**(code **)(*(longlong *)this + 0x538))(this,local_108,0,1);
  bVar2 = CExtGridHitTestInfo::IsHoverEmpty(local_108);
  if ((bVar2) || (bVar2 = CExtGridHitTestInfo::IsValidRect(local_108,true), !bVar2)) {
    return false;
  }
  iVar8 = CExtGridHitTestInfo::GetInnerOuterTypeOfColumn(local_108);
  uVar9 = CExtGridHitTestInfo::GetInnerOuterTypeOfRow(local_108);
  uVar10 = (**(code **)(*(longlong *)this + 0x438))(this);
  local_118 = (**(code **)(*(longlong *)this + 0x8d0))(this);
  uVar11 = (**(code **)(*(longlong *)this + 0x8e0))(this);
  if (((((uVar11 & 0x3c000) != 0) && (param_1 == 1)) && (param_2 == 2)) && ((local_f0 & 0xf0) != 0))
  {
    CExtGridHitTestInfo::CExtGridHitTestInfo(local_a8,local_108);
    if ((((uVar10 >> 9 & 1) == 0) && ((local_90 & 0xc0) != 0)) &&
       ((0 < local_9c || ((char)local_90 < '\0')))) {
      if (((local_90 & 0x40) != 0) && (0 < local_9c)) {
        local_9c = local_9c + -1;
        local_90 = local_90 & 0xffffffbf | 0x80;
      }
      if ((char)local_90 < '\0') {
        if (uVar9 == 0) {
          uVar1 = uVar11 >> 0xf;
        }
        else {
          uVar1 = uVar11 >> 0xe;
        }
        if (((uVar1 & 1) != 0) &&
           (cVar3 = (**(code **)(*(longlong *)this + 0xb18))(this,1,local_a8), cVar3 != '\0')) {
          if (((uVar11 >> 0x14 & 1) == 0) && ((uVar11 >> 0x15 & 1) == 0)) {
            return true;
          }
          local_158 = CONCAT31(local_158._1_3_,1);
          local_160 = CONCAT71(local_160._1_7_,(char)(uVar11 >> 0x12)) & 0xffffffffffffff01;
          local_168 = CONCAT71(local_168._1_7_,(char)(uVar11 >> 0x15)) & 0xffffffffffffff01;
          (**(code **)(*(longlong *)this + 0xb20))(this,local_9c,iVar8,(byte)(uVar11 >> 0x14) & 1);
          return true;
        }
      }
    }
    if ((((uVar10 >> 10 & 1) == 0) && ((local_90 & 0x30) != 0)) &&
       ((0 < local_a0 || ((local_90 & 0x20) != 0)))) {
      if (((local_90 & 0x10) != 0) && (0 < local_a0)) {
        local_a0 = local_a0 + -1;
        local_90 = local_90 & 0xffffffef | 0x20;
      }
      if ((local_90 & 0x20) != 0) {
        if (iVar8 == 0) {
          uVar10 = uVar11 >> 0x11;
        }
        else {
          uVar10 = uVar11 >> 0x10;
        }
        if (((uVar10 & 1) != 0) &&
           (cVar3 = (**(code **)(*(longlong *)this + 0xb18))(this,0,local_a8), cVar3 != '\0')) {
          if (((uVar11 >> 0x16 & 1) == 0) && ((uVar11 >> 0x17 & 1) == 0)) {
            return true;
          }
          local_158 = CONCAT31(local_158._1_3_,1);
          local_160 = CONCAT71(local_160._1_7_,(char)(uVar11 >> 0x13)) & 0xffffffffffffff01;
          local_168 = CONCAT71(local_168._1_7_,(char)(uVar11 >> 0x17)) & 0xffffffffffffff01;
          (**(code **)(*(longlong *)this + 0xb28))(this,local_a0,uVar9,(byte)(uVar11 >> 0x16) & 1);
          return true;
        }
      }
    }
  }
  local_150 = (undefined1 *)CONCAT71(local_150._1_7_,1);
  local_158 = CONCAT31(local_158._1_3_,1);
  local_160 = 0;
  local_168._0_4_ = uVar9;
  plVar13 = (longlong *)(**(code **)(*(longlong *)this + 0x908))(this,local_fc,local_100,iVar8);
  if (plVar13 != (longlong *)0x0) {
    local_160 = CONCAT44(local_160._4_4_,(int)local_b8);
    local_168._0_4_ = param_2;
    cVar3 = (**(code **)(*plVar13 + 0x1b8))(plVar13,this,local_108,param_1);
    if (cVar3 != '\0') {
      return true;
    }
  }
  uVar9 = local_118;
  if (param_1 != 1) {
    return false;
  }
  if (param_2 == 2) {
    uVar10 = local_118 >> 0x13;
  }
  else {
    if (param_2 != 3) {
      return false;
    }
    uVar10 = local_118 >> 0x11;
  }
  if ((uVar10 & 1) == 0) {
    return false;
  }
  CExtGridHitTestInfo::CExtGridHitTestInfo(local_a8,param_5);
  local_168._0_4_ = (uint)local_168 & 0xffffff00;
  (**(code **)(*(longlong *)this + 0x538))(this,local_a8,0,1);
  bVar2 = CExtGridHitTestInfo::IsHoverEmpty(local_a8);
  if (bVar2) {
    return false;
  }
  bVar2 = CExtGridHitTestInfo::IsValidRect(local_a8,true);
  if (!bVar2) {
    return false;
  }
  if ((local_90 >> 0xf & 1) != 0) {
    return false;
  }
  if ((local_90 >> 0xe & 1) != 0) {
    return false;
  }
  if ((local_90 >> 0x10 & 1) != 0) {
    return false;
  }
  if ((local_90 >> 0x13 & 1) != 0) {
    return false;
  }
  if ((local_90 >> 0x14 & 1) != 0) {
    return false;
  }
  if ((local_90 & 0x60000) == 0) {
    return false;
  }
  iVar8 = CExtGridHitTestInfo::GetInnerOuterTypeOfColumn(local_a8);
  iVar12 = CExtGridHitTestInfo::GetInnerOuterTypeOfRow(local_a8);
  if (param_2 != 3) {
    if (param_2 == 2) {
      SVar5 = GetAsyncKeyState(0x12);
      SVar6 = GetAsyncKeyState(0x11);
      SVar7 = GetAsyncKeyState(0x10);
      if (SVar6 < 0) {
        return false;
      }
      if (SVar5 < 0) {
        return false;
      }
      if (SVar7 < 0) {
        return false;
      }
    }
    goto LAB_1801ff6a0;
  }
  if ((uVar9 >> 0x12 & 1) == 0) goto LAB_1801ff6a0;
  (**(code **)(*(longlong *)this + 0x6c8))(this,&local_b8);
  uVar9 = (**(code **)(*(longlong *)this + 0x438))();
  uVar9 = uVar9 & 0x3000;
  if (uVar9 == 0x1000) {
    if ((local_90 >> 9 & 1) == 0) {
      if ((local_90 & 0xf) == 0) {
        return false;
      }
      if (iVar8 != 0) {
        return false;
      }
      goto LAB_1801ff648;
    }
    if (local_9c != (int)local_b8) {
      return false;
    }
    bVar2 = local_a0 == local_b8._4_4_;
  }
  else if (uVar9 == 0x2000) {
    if (local_a0 != local_b8._4_4_) {
      return false;
    }
    bVar2 = iVar8 == 0;
  }
  else {
    if (uVar9 != 0x3000) goto LAB_1801ff6a0;
    if (local_9c != (int)local_b8) {
      return false;
    }
LAB_1801ff648:
    bVar2 = iVar12 == 0;
  }
  if (!bVar2) {
    return false;
  }
LAB_1801ff6a0:
  local_128 = *(undefined8 *)(this + 0x40);
  local_140 = &local_b8;
  local_130 = 0;
  local_138 = 1;
  local_148 = local_8c;
  local_150 = local_7c;
  local_b8 = 0;
  local_b0 = 0;
  local_160 = CONCAT44(local_160._4_4_,iVar8);
  local_168 = CONCAT44(local_168._4_4_,local_a0);
  local_158 = iVar12;
  uVar4 = (**(code **)(*(longlong *)this + 0x800))(this,local_94,local_98,local_9c);
  return (bool)uVar4;
}

