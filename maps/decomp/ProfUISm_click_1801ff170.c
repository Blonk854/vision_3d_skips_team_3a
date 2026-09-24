// CExtGridBaseWnd::OnGbwAnalyzeCellMouseClickEvent @ 1801ff170


/* public: virtual bool __cdecl CExtGridBaseWnd::OnGbwAnalyzeCellMouseClickEvent(unsigned
   int,unsigned int,unsigned int,class CPoint) __ptr64 */

bool __thiscall
CExtGridBaseWnd::OnGbwAnalyzeCellMouseClickEvent
          (CExtGridBaseWnd *this,undefined8 param_2_00,int param_2)

{
                    /* 0x1ff170  12811
                       ?OnGbwAnalyzeCellMouseClickEvent@CExtGridBaseWnd@@UEAA_NIIIVCPoint@@@Z */
  if (((param_2 - 1U < 3) && (this != (CExtGridBaseWnd *)0xfffffffffffff840)) &&
     (*(longlong *)(this + 0x800) != 0)) {
    SendMessageA(*(HWND *)(this + 0x40),0x1f,0,0);
  }
  return false;
}

