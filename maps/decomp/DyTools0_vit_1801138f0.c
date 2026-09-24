// CVitExtReportGridWnd::DeleteSelectedRows @ 1801138f0


/* protected: virtual bool __cdecl CVitExtReportGridWnd::DeleteSelectedRows(void) __ptr64 */

bool __thiscall CVitExtReportGridWnd::DeleteSelectedRows(CVitExtReportGridWnd *this)

{
  int iVar1;
  int iVar2;
  
                    /* 0x1138f0  1421  ?DeleteSelectedRows@CVitExtReportGridWnd@@MEAA_NXZ */
  iVar1 = (**(code **)(*(longlong *)this + 0x5c8))();
  (**(code **)(*(longlong *)this + 0xf80))(this,1);
  (**(code **)(*(longlong *)this + 0x12a8))(this,1);
  iVar2 = (**(code **)(*(longlong *)this + 0x5c8))(this);
  return iVar2 < iVar1;
}

