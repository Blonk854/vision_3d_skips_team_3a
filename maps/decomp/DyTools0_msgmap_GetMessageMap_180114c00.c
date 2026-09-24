// CVitExtReportGridWnd::GetMessageMap @ 180114c00


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* protected: virtual struct AFX_MSGMAP const * __ptr64 __cdecl
   CVitExtReportGridWnd::GetMessageMap(void)const __ptr64 */

AFX_MSGMAP * __thiscall CVitExtReportGridWnd::GetMessageMap(CVitExtReportGridWnd *this)

{
                    /* 0x114c00  2128  ?GetMessageMap@CVitExtReportGridWnd@@MEBAPEBUAFX_MSGMAP@@XZ
                        */
  if (*(int *)(*(longlong *)((longlong)ThreadLocalStoragePointer + (ulonglong)_tls_index * 8) + 4) <
      DAT_18026de0c) {
    _Init_thread_header(&DAT_18026de0c);
    if (DAT_18026de0c == -1) {
      _DAT_180262070 = GetThisMessageMap_exref;
      _Init_thread_footer(&DAT_18026de0c);
    }
  }
  return (AFX_MSGMAP *)&DAT_180262070;
}

