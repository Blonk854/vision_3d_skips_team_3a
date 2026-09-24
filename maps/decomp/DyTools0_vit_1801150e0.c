// CVitExtReportGridWnd::HasSelection @ 1801150e0


/* protected: virtual bool __cdecl CVitExtReportGridWnd::HasSelection(void)const __ptr64 */

bool __thiscall CVitExtReportGridWnd::HasSelection(CVitExtReportGridWnd *this)

{
  long lVar1;
  
                    /* 0x1150e0  2550  ?HasSelection@CVitExtReportGridWnd@@MEBA_NXZ */
  lVar1 = CExtGridBaseWnd::SelectionGetFirstRowInColumn((CExtGridBaseWnd *)this,0);
  return lVar1 != -1;
}

