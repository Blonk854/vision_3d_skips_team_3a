// CVitExtReportGridWnd::GetThisMessageMap @ 180114fd0


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* protected: static struct AFX_MSGMAP const * __ptr64 __cdecl
   CVitExtReportGridWnd::GetThisMessageMap(void) */

AFX_MSGMAP * __cdecl CVitExtReportGridWnd::GetThisMessageMap(void)

{
                    /* 0x114fd0  2444  ?GetThisMessageMap@CVitExtReportGridWnd@@KAPEBUAFX_MSGMAP@@XZ
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

