// vt off=0x778 FUN_1404568f0 @ 1404568f0


undefined8 * FUN_1404568f0(undefined8 *param_1,ulonglong param_2)

{
  *param_1 = boost::exception_detail::
             clone_impl<boost::exception_detail::error_info_injector<boost::thread_resource_error>_>
             ::vftable;
  param_1[9] = boost::exception_detail::
               clone_impl<boost::exception_detail::error_info_injector<boost::thread_resource_error>_>
               ::vftable;
  *(undefined ***)((longlong)*(int *)(param_1[0xe] + 4) + 0x70 + (longlong)param_1) =
       boost::exception_detail::
       clone_impl<boost::exception_detail::error_info_injector<boost::thread_resource_error>_>::
       vftable;
  *(int *)((longlong)*(int *)(param_1[0xe] + 4) + 0x6c + (longlong)param_1) =
       *(int *)(param_1[0xe] + 4) + -0x10;
  FUN_1404548c0();
  param_1[0x10] = boost::exception_detail::clone_base::vftable;
  if ((param_2 & 1) != 0) {
    FUN_1404556c0(param_1,0x88);
  }
  return param_1;
}

