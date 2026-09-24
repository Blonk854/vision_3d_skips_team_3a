// CVitExtReportGridWnd::SelectAll @ 1801157f0


/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */
/* protected: virtual bool __cdecl CVitExtReportGridWnd::SelectAll(bool) __ptr64 */

bool __thiscall CVitExtReportGridWnd::SelectAll(CVitExtReportGridWnd *this,bool param_1)

{
  undefined1 uVar1;
  int iVar2;
  undefined1 auStack_58 [32];
  undefined1 local_38;
  undefined8 local_28;
  int local_20;
  int local_1c;
  ulonglong local_18;
  
                    /* 0x1157f0  3436  ?SelectAll@CVitExtReportGridWnd@@MEAA_N_N@Z */
  local_18 = DAT_1802635c0 ^ (ulonglong)auStack_58;
  iVar2 = (**(code **)(*(longlong *)this + 0x5c8))();
  local_20 = (**(code **)(*(longlong *)this + 0x5a8))();
  local_20 = local_20 + -1;
  local_28 = 0;
  local_38 = param_1;
  local_1c = iVar2 + -1;
  uVar1 = (**(code **)(*(longlong *)this + 0x688))(this,&local_28,1,0);
  return (bool)uVar1;
}

