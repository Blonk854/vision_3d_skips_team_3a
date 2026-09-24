// CVitExtReportGridWnd::GetSelectedRowsList @ 180114e80


/* protected: virtual void __cdecl CVitExtReportGridWnd::GetSelectedRowsList(class
   std::list<long,class std::allocator<long> > & __ptr64) __ptr64 */

void __thiscall
CVitExtReportGridWnd::GetSelectedRowsList
          (CVitExtReportGridWnd *this,list<long,std::allocator<long>_> *param_1)

{
  longlong *plVar1;
  longlong lVar2;
  code *pcVar3;
  longlong lVar4;
  longlong *plVar5;
  long local_res10 [2];
  
                    /* 0x114e80  2289
                       ?GetSelectedRowsList@CVitExtReportGridWnd@@MEAAXAEAV?$list@JV?$allocator@J@std@@@std@@@Z
                        */
  plVar1 = *(longlong **)param_1;
  plVar5 = (longlong *)*plVar1;
  *plVar1 = (longlong)plVar1;
  *(longlong *)(*(longlong *)param_1 + 8) = *(longlong *)param_1;
  *(undefined8 *)(param_1 + 8) = 0;
  if (plVar5 != *(longlong **)param_1) {
    do {
      plVar1 = (longlong *)*plVar5;
      operator_delete(plVar5);
      plVar5 = plVar1;
    } while (plVar1 != (longlong *)*(longlong *)param_1);
  }
  local_res10[0] = CExtGridBaseWnd::SelectionGetFirstRowInColumn((CExtGridBaseWnd *)this,0);
  while( true ) {
    if (local_res10[0] == -1) {
      return;
    }
    lVar2 = *(longlong *)param_1;
    lVar4 = FUN_180112490(param_1,lVar2,*(undefined8 *)(lVar2 + 8),local_res10);
    if (*(longlong *)(param_1 + 8) == 0xaaaaaaaaaaaaaa9) break;
    *(longlong *)(param_1 + 8) = *(longlong *)(param_1 + 8) + 1;
    *(longlong *)(lVar2 + 8) = lVar4;
    **(longlong **)(lVar4 + 8) = lVar4;
    local_res10[0] =
         CExtGridBaseWnd::SelectionGetNextRowInColumn((CExtGridBaseWnd *)this,0,local_res10[0]);
  }
  std::_Xlength_error("list<T> too long");
  pcVar3 = (code *)swi(3);
  (*pcVar3)();
  return;
}

