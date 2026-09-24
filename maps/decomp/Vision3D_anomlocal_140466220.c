// vt off=0x1538 FUN_140466220 @ 140466220


char * FUN_140466220(undefined8 param_1,int param_2,char *param_3,longlong param_4)

{
  char *_Source;
  
  if (param_4 != 0) {
    if (param_4 == 1) {
      *param_3 = '\0';
      return param_3;
    }
    _Source = strerror(param_2);
    if (_Source == (char *)0x0) {
      return "Unknown error";
    }
    strncpy(param_3,_Source,param_4 - 1);
    param_3[param_4 + -1] = '\0';
  }
  return param_3;
}

