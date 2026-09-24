// FUN_1405f9270 @ 1405f9270 body=5935


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */

void FUN_1405f9270(CDataCaoTraitement *param_1,CAnomalieProd *param_2)

{
  int *piVar1;
  int iVar2;
  char cVar3;
  double dVar4;
  double dVar5;
  double dVar6;
  double dVar7;
  bool bVar8;
  longlong lVar9;
  longlong lVar10;
  longlong *plVar11;
  longlong *plVar12;
  longlong *plVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  ccPelBuffer<ccPackedRGB32Pel> *this;
  ccPelBuffer<unsigned_short> *pcVar16;
  Error *pEVar17;
  double *pdVar18;
  CMat *pCVar19;
  __uint64 _Var20;
  undefined8 *puVar21;
  CPoint_<double> *this_00;
  CPoint_<double> *this_01;
  __int64 _Var22;
  CCAD_Base *this_02;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *pCVar23;
  CModelFamily *this_03;
  ccAffineRectangle *pcVar24;
  undefined8 *puVar25;
  longlong lVar26;
  undefined8 *puVar27;
  ccColor *pcVar28;
  ulonglong uVar29;
  CViUnitLength *pCVar30;
  undefined4 uVar31;
  undefined4 uVar32;
  uint uVar33;
  uint uVar34;
  CViUnitLength *local_res10;
  undefined8 local_res18;
  undefined4 local_res20 [2];
  undefined8 in_stack_ffffffffffffcf28;
  undefined8 *local_30b8;
  undefined8 local_30b0;
  longlong local_30a8;
  longlong *local_30a0;
  undefined4 local_3098;
  undefined4 local_3094;
  undefined4 local_3090;
  eLayerType local_308c [3];
  int local_3080;
  int local_307c;
  undefined8 *local_3078;
  ulonglong local_3070;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_3068 [8];
  int local_3060;
  uint local_305c;
  int local_3058;
  int iStack_3054;
  int iStack_3050;
  int iStack_304c;
  longlong local_3048 [3];
  undefined8 *local_3030;
  CViUnitLength *local_3028;
  CViUnitLength *local_3020;
  undefined8 *local_3018;
  undefined8 *local_3010;
  double local_3008;
  double local_3000;
  undefined8 local_2ff8;
  undefined8 local_2ff0;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_2fe8 [8];
  double local_2fe0;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_2fd8 [8];
  undefined8 local_2fd0;
  double local_2fc8;
  CDPoint local_2fc0 [16];
  double local_2fb0;
  double local_2fa8;
  undefined8 local_2f98;
  undefined8 local_2f90;
  double local_2f88;
  undefined8 local_2f80;
  double local_2f78;
  undefined8 local_2f70;
  basic_string<char,std::char_traits<char>,std::allocator<char>_> local_2f68 [16];
  undefined8 local_2f58;
  undefined8 local_2f50;
  basic_string<char,std::char_traits<char>,std::allocator<char>_> local_2f48 [16];
  undefined8 local_2f38;
  undefined8 local_2f30;
  undefined8 local_2f28;
  undefined8 local_2f20;
  CViUnitLength *local_2f18;
  CViUnitLength *local_2f10;
  undefined8 local_2f08;
  undefined8 local_2f00;
  undefined8 local_2ef8;
  undefined8 local_2ef0;
  CDPoint local_2ee8 [16];
  undefined8 local_2ed8;
  undefined8 local_2ed0;
  CLogManagerFunction local_2ec0 [40];
  code *local_2e98;
  undefined8 local_2e90;
  undefined8 uStack_2e88;
  undefined8 local_2e80;
  undefined8 uStack_2e78;
  undefined8 local_2e70;
  undefined8 uStack_2e68;
  undefined8 local_2e60;
  undefined8 local_2e58;
  undefined8 *local_2e50;
  undefined8 *local_2e48;
  longlong *local_2e40;
  undefined1 local_2e30 [16];
  longlong local_2e20 [2];
  longlong local_2e10 [2];
  longlong local_2e00 [3];
  int local_2de8;
  int iStack_2de4;
  int iStack_2de0;
  int iStack_2ddc;
  CDPoint local_2dd8 [16];
  double local_2dc8;
  double local_2dc0;
  undefined8 local_2db0;
  undefined8 uStack_2da8;
  undefined8 local_2da0;
  undefined8 uStack_2d98;
  undefined8 local_2d90;
  undefined8 uStack_2d88;
  undefined8 local_2d80;
  CDPoint local_2d78 [16];
  undefined8 local_2d68;
  undefined8 local_2d60;
  CDPoint local_2d50 [40];
  CDPoint local_2d28 [48];
  Error local_2cf8 [8];
  int local_2cf0;
  CViUnitLength local_2c98 [48];
  CDPoint local_2c68 [40];
  CDPoint local_2c40 [40];
  CDPoint local_2c18 [40];
  CDPoint local_2bf0 [40];
  CDPoint local_2bc8 [40];
  CDPoint local_2ba0 [40];
  ccGraphicProps local_2b78 [64];
  CViUnitLength local_2b38 [48];
  CViUnitLength local_2b08 [48];
  CViUnitLength local_2ad8 [48];
  CViUnitLength local_2aa8 [48];
  CMat local_2a78 [112];
  ccXform<2> local_2a08 [112];
  ccPolyline local_2998 [96];
  CViUnitSize local_2938 [128];
  CViUnitPoint local_28b8 [40];
  double local_2890;
  double local_2860;
  CViUnitPoint local_2818 [160];
  CViUnitPoint local_2778 [160];
  Error local_26d8 [88];
  CPoint_<double> local_2680 [96];
  CPoint_<double> local_2620 [96];
  ccPelBuffer<unsigned_short> local_25c0 [104];
  ccAffineRectangle local_2558 [240];
  ccAffineRectangle local_2468 [240];
  CViUnitRect local_2378 [352];
  CViUnitPoint local_2218 [160];
  CViUnitPoint local_2178 [160];
  ccUITablet local_20d8 [560];
  ImageZ local_1ea8 [352];
  ccPelBuffer<ccPackedRGB32Pel> local_1d48 [224];
  ccPelBuffer<unsigned_short> local_1c68 [224];
  CMat local_1b88 [224];
  ccAffineRectangle local_1aa8 [240];
  CZoneStorage local_19b8 [2528];
  undefined1 local_fd8 [672];
  CZoneStorage local_d38 [3328];
  
  uVar31 = (undefined4)((ulonglong)in_stack_ffffffffffffcf28 >> 0x20);
  local_2e58 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            (local_3068,"CDocCompose::ExecuteArray_ForeignMaterials_AfficheResult_Console");
  CLogManagerFunction::CLogManagerFunction(local_2ec0,0x16,local_3068,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_3068);
  if ((param_2 == (CAnomalieProd *)0x0) || (DAT_1410f5ad0 == 0)) goto LAB_1405fa952;
  CDataCaoTraitement::FM_Get(param_1);
  plVar11 = local_30a0;
  uVar29 = *(ulonglong *)(param_2 + 0x278);
  local_2e50 = *(undefined8 **)(*(longlong *)(param_1 + 0x19b8) + 0xdf0);
  cVar3 = *(char *)((longlong)local_2e50[1] + 0x19);
  puVar27 = local_2e50;
  puVar25 = (undefined8 *)local_2e50[1];
  while (cVar3 == '\0') {
    if ((ulonglong)puVar25[4] < uVar29) {
      puVar21 = (undefined8 *)puVar25[2];
      puVar25 = puVar27;
    }
    else {
      puVar21 = (undefined8 *)*puVar25;
    }
    puVar27 = puVar25;
    puVar25 = puVar21;
    cVar3 = *(char *)((longlong)puVar21 + 0x19);
  }
  if ((puVar27 == local_2e50) || (uVar29 < (ulonglong)puVar27[4])) {
    puVar27 = local_2e50;
  }
  local_3070 = uVar29;
  local_2e48 = local_2e50;
  if (puVar27 == local_2e50) {
    if (local_30a0 != (longlong *)0x0) {
      LOCK();
      plVar12 = local_30a0 + 1;
      lVar9 = *plVar12;
      *(int *)plVar12 = (int)*plVar12 + -1;
      UNLOCK();
      if ((int)lVar9 == 1) {
        (**(code **)(*local_30a0 + 8))(local_30a0);
        LOCK();
        piVar1 = (int *)((longlong)plVar11 + 0xc);
        iVar2 = *piVar1;
        *piVar1 = *piVar1 + -1;
        UNLOCK();
        if (iVar2 == 1) {
          (**(code **)(*local_30a0 + 0x10))();
        }
      }
    }
    CLogManagerFunction::~CLogManagerFunction(local_2ec0);
    return;
  }
  CZoneStorage::CZoneStorage(local_d38,(CZoneStorage *)(puVar27 + 5));
  CZoneStorage::CZoneStorage(local_19b8);
  lVar9 = CAnomalieProd::_dpCoordCAO_um(param_2);
  lVar10 = CAnomalieProd::_dpCoordCAO_um(param_2);
  CDPoint::CDPoint(local_2dd8,*(double *)(lVar10 + 0x10),*(double *)(lVar9 + 0x18));
  CDPoint::_vbase_destructor_(local_2c68);
  CDPoint::_vbase_destructor_(local_2c40);
  lVar9 = *(longlong *)(local_30a8 + 0x550);
  dVar4 = algo::CPoint_<double>::y((CPoint_<double> *)(uVar29 * 0x60 + lVar9));
  dVar5 = algo::CPoint_<double>::x((CPoint_<double> *)(uVar29 * 0x60 + lVar9));
  dVar7 = DAT_140ddd0f0;
  CViUnitPoint::CViUnitPoint(local_2818,dVar5 * DAT_140ddd0f0,dVar4 * DAT_140ddd0f0);
  plVar11 = (longlong *)(**(code **)(*(longlong *)param_1 + 0x230))(param_1);
  plVar12 = (longlong *)(**(code **)(*plVar11 + 0x1f8))(plVar11,&local_3030);
  plVar11 = (longlong *)*plVar12;
  *plVar12 = 0;
  local_2e40 = plVar11;
  if (local_3030 != (undefined8 *)0x0) {
    (**(code **)*local_3030)(local_3030,1);
  }
  (**(code **)(*plVar11 + 0x130))(plVar11,local_28b8,1);
  local_res10 = local_2b38;
  plVar12 = (longlong *)(**(code **)(*(longlong *)param_1 + 0x230))(param_1);
  plVar13 = (longlong *)(**(code **)(*(longlong *)param_1 + 0x230))(param_1);
  lVar9 = (**(code **)(*plVar12 + 0x1c8))(plVar12,local_2218,1);
  uVar14 = CViUnitLength::CViUnitLength(local_2b38,(CViUnitLength *)(lVar9 + 0x38));
  lVar9 = (**(code **)(*plVar13 + 0x1c8))(plVar13,local_2178,1);
  uVar15 = CViUnitLength::CViUnitLength(local_2b08,(CViUnitLength *)(lVar9 + 8));
  CViUnitSize::CViUnitSize(local_2938,uVar15,uVar14,1);
  CViUnitPoint::_vbase_destructor_(local_2178);
  CViUnitPoint::_vbase_destructor_(local_2218);
  uVar14 = CONCAT44(uVar31,1);
  CViUnitRect::CViUnitRect(local_2378,local_2818,local_2938,true);
  plVar12 = (longlong *)(**(code **)(*(longlong *)param_1 + 0x230))(param_1);
  (**(code **)(*plVar12 + 0x1c0))(plVar12,&local_3060,1,*plVar12,uVar14);
  this = CZoneStorage::GetConsoleColor(local_d38,1);
  cc_PelBuffer::clientFromImageXform((cc_PelBuffer *)this);
  ccXform<2>::ccXform<2>((ccXform<2> *)&local_2e90);
  local_2e98 = _vftable__exref;
  local_2e90 = local_2db0;
  uStack_2e88 = uStack_2da8;
  local_2e80 = local_2da0;
  uStack_2e78 = uStack_2d98;
  local_2e70 = local_2d90;
  uStack_2e68 = uStack_2d88;
  local_2e60 = local_2d80;
  lVar9 = CViUnitRect::GetTop(local_2378);
  lVar10 = CViUnitRect::GetLeft(local_2378);
  local_2f28 = *(undefined8 *)(lVar10 + 0x20);
  uVar33 = (uint)DAT_140e446a0;
  uVar34 = (uint)((ulonglong)DAT_140e446a0 >> 0x20);
  local_2f20 = CONCAT44((uint)((ulonglong)*(undefined8 *)(lVar9 + 0x20) >> 0x20) ^ uVar34,
                        (uint)*(undefined8 *)(lVar9 + 0x20) ^ uVar33);
  CViUnitLength::_vbase_destructor_(local_2aa8);
  CViUnitLength::_vbase_destructor_(local_2ad8);
  ccXform<2>::invMapPoint((ccXform<2> *)&local_2e90,(ccVector<2> *)&local_2f18);
  dVar4 = DAT_140de2128;
  local_3028 = local_2f10;
  local_3020 = local_2f18;
  local_res10 = local_2f10;
  if (((ulonglong)local_2f10 & 0x7ff0000000000000) == 0x7ff0000000000000) {
                    /* WARNING: Subroutine does not return */
    FUN_140551ec0("boost::math::round<%1%>(%1%)",
                  "Value %1% can not be represented in the target integer type.",&local_3028);
  }
  if (((double)local_2f10 <= DAT_140e44650) || (DAT_140de2128 <= (double)local_2f10)) {
    if ((double)local_2f10 <= 0.0) {
      dVar5 = floor((double)local_2f10);
      uVar31 = SUB84(dVar5,0);
      uVar32 = (undefined4)((ulonglong)dVar5 >> 0x20);
      if ((double)local_2f10 - dVar5 <= dVar4) goto LAB_1405f9878;
      uVar31 = SUB84(DAT_140e445a0,0);
      uVar32 = (undefined4)((ulonglong)DAT_140e445a0 >> 0x20);
      dVar5 = dVar5 + DAT_140e445a0;
    }
    else {
      dVar5 = ceil((double)local_2f10);
      uVar31 = SUB84(DAT_140e445a0,0);
      uVar32 = (undefined4)((ulonglong)DAT_140e445a0 >> 0x20);
      if (dVar4 < dVar5 - (double)local_2f10) {
        dVar5 = dVar5 - DAT_140e445a0;
      }
    }
  }
  else {
    uVar31 = 0;
    uVar32 = 0;
LAB_1405f9878:
    dVar5 = (double)CONCAT44(uVar32,uVar31);
    uVar31 = SUB84(DAT_140e445a0,0);
    uVar32 = (undefined4)((ulonglong)DAT_140e445a0 >> 0x20);
  }
  local_res10 = local_2f18;
  if (((ulonglong)local_2f18 & 0x7ff0000000000000) == 0x7ff0000000000000) {
                    /* WARNING: Subroutine does not return */
    FUN_140551ec0("boost::math::round<%1%>(%1%)",
                  "Value %1% can not be represented in the target integer type.",&local_3020);
  }
  if (((double)local_2f18 <= DAT_140e44650) || (dVar4 <= (double)local_2f18)) {
    if ((double)local_2f18 <= 0.0) {
      dVar6 = floor((double)local_2f18);
      if (dVar4 < (double)local_2f18 - dVar6) {
        dVar6 = dVar6 + (double)CONCAT44(uVar32,uVar31);
      }
    }
    else {
      dVar6 = ceil((double)local_2f18);
      if (dVar4 < dVar6 - (double)local_2f18) {
        dVar6 = dVar6 - (double)CONCAT44(uVar32,uVar31);
      }
    }
  }
  else {
    dVar6 = 0.0;
  }
  local_307c = (int)dVar5;
  local_3080 = (int)dVar6;
  cc_PelBuffer::offset((cc_PelBuffer *)this,(ccPair<long> *)&local_3080);
  uVar14 = ccPelBuffer<ccPackedRGB32Pel>::ccPelBuffer<ccPackedRGB32Pel>
                     (local_1d48,(ccPelBuffer<class_ccPackedRGB32Pel> *)this);
  CZoneStorage::AddConsoleColor(local_19b8,1,uVar14);
  algo::XFormToMeshgrid(local_2a08,(int)&local_2e90,local_3060);
  FUN_1405fc9d0(local_30a8,local_1ea8);
  local_2f30 = 0xf;
  local_2f38 = 0;
  local_2f48[0] = (basic_string<char,std::char_traits<char>,std::allocator<char>_>)0x0;
  FUN_14045f320(local_2f48,&DAT_140dd3ce0,0);
  local_2f50 = 0xf;
  local_2f58 = 0;
  local_2f68[0] = (basic_string<char,std::char_traits<char>,std::allocator<char>_>)0x0;
  FUN_14045f320(local_2f68,&DAT_140dd3ce0,0);
  SharedData::Error::Error(local_2cf8,0,local_2f68,0,local_2f48);
  FUN_1404546f0(local_2f68);
  FUN_1404546f0(local_2f48);
  local_30b8 = (undefined8 *)0x0;
  local_30b0 = 0;
  local_30b8 = (undefined8 *)FUN_140541f00(&local_30b8);
  local_res18 = (ulonglong)local_res18._4_4_ << 0x20;
  pcVar16 = (ccPelBuffer<unsigned_short> *)
            ccPelBuffer<unsigned_short>::ccPelBuffer<unsigned_short>
                      (local_1c68,local_3060,local_305c,0x10);
  puVar27 = local_30b8;
  if (*(char *)((longlong)local_30b8[1] + 0x19) == '\0') {
    puVar25 = (undefined8 *)local_30b8[1];
    do {
      if (*(int *)(puVar25 + 4) < (int)local_res18) {
        puVar21 = (undefined8 *)puVar25[2];
      }
      else {
        puVar21 = (undefined8 *)*puVar25;
        puVar27 = puVar25;
      }
      puVar25 = puVar21;
    } while (*(char *)((longlong)puVar21 + 0x19) == '\0');
    if ((puVar27 == local_30b8) || ((int)local_res18 < *(int *)(puVar27 + 4))) goto LAB_1405f9aa3;
  }
  else {
LAB_1405f9aa3:
    local_3018 = &local_res18;
    lVar9 = FUN_140516190(&local_30b8,&DAT_140e7b168,&local_3018,&local_res10);
    FUN_140519a90(&local_30b8,&local_3010,puVar27,lVar9 + 0x20,lVar9);
    puVar27 = local_3010;
  }
  ccPelBuffer<unsigned_short>::operator=((ccPelBuffer<unsigned_short> *)(puVar27 + 5),pcVar16);
  ccPelBuffer<unsigned_short>::~ccPelBuffer<unsigned_short>(local_1c68);
  pEVar17 = (Error *)ImageZ::RemapOnZone2D
                               (local_1ea8,(int)local_26d8,local_3060,
                                (CViUnitPoint *)(ulonglong)local_305c,(CPoints_<float> *)local_2818,
                                (map<ImageZLayers::eLayerType,ccPelBuffer<unsigned_short>,std::less<ImageZLayers::eLayerType>,std::allocator<std::pair<ImageZLayers::eLayerType_const_,ccPelBuffer<unsigned_short>_>_>_>
                                 *)local_2a08);
  SharedData::Error::operator=(local_2cf8,pEVar17);
  SharedData::Error::~Error(local_26d8);
  if (local_2cf0 != 0) {
    SharedData::Error::Log(local_2cf8,4);
    cVar3 = *(char *)((longlong)local_30b8[1] + 0x19);
    plVar12 = (longlong *)local_30b8[1];
    while (cVar3 == '\0') {
      FUN_1405429f0(&local_30b8,plVar12[2]);
      plVar13 = (longlong *)*plVar12;
      ccPelBuffer<unsigned_short>::~ccPelBuffer<unsigned_short>
                ((ccPelBuffer<unsigned_short> *)(plVar12 + 5));
      operator_delete(plVar12);
      plVar12 = plVar13;
      cVar3 = *(char *)((longlong)plVar13 + 0x19);
    }
    local_30b8[1] = local_30b8;
    *local_30b8 = local_30b8;
    local_30b8[2] = local_30b8;
    local_30b0 = 0;
    FUN_1404729f0(local_30b8,1,0x108);
    SharedData::Error::~Error(local_2cf8);
    ImageZ::_vbase_destructor_(local_1ea8);
    algo::CPoints_<float>::~CPoints_<float>((CPoints_<float> *)local_2a08);
    vitXform::~vitXform((vitXform *)&local_2e98);
    CViUnitRect::_vbase_destructor_(local_2378);
    CViUnitSize::_vbase_destructor_(local_2938);
    CViUnitPoint::_vbase_destructor_(local_28b8);
    (**(code **)*plVar11)(plVar11,1);
    CViUnitPoint::_vbase_destructor_(local_2818);
    CDPoint::_vbase_destructor_(local_2dd8);
    CZoneStorage::~CZoneStorage(local_19b8);
    CZoneStorage::~CZoneStorage(local_d38);
    FUN_14051f750(&local_30a8);
    CLogManagerFunction::~CLogManagerFunction(local_2ec0);
    return;
  }
  if ((param_1[0x1acb] == (CDataCaoTraitement)0x0) && (param_1[0x1ac9] == (CDataCaoTraitement)0x0))
  {
    algo::CMat::CMat(local_2a78);
    local_3008 = local_2860;
    local_3000 = local_2890;
    pdVar18 = &local_3008;
    if (local_2860 <= local_2890) {
      pdVar18 = &local_3000;
    }
    CViUnitLength::CViUnitLength(local_2c98,*pdVar18);
    local_res20[0] = 0;
    FUN_14051bd30(&local_30b8,local_2e30,local_res20);
    pCVar19 = (CMat *)FromTZMapToCMat(local_25c0);
    algo::ApplyILI(pCVar19,local_2c98,local_2a78);
    algo::CMat::~CMat((CMat *)local_25c0);
    local_3098 = 0;
    pcVar16 = (ccPelBuffer<unsigned_short> *)FromCVMatToTZMap(local_1b88);
    FUN_14051bd30(&local_30b8,local_2e20,&local_3098);
    ccPelBuffer<unsigned_short>::operator=
              ((ccPelBuffer<unsigned_short> *)(local_2e20[0] + 0x28),pcVar16);
    ccPelBuffer<unsigned_short>::~ccPelBuffer<unsigned_short>
              ((ccPelBuffer<unsigned_short> *)local_1b88);
    CViUnitLength::_vbase_destructor_(local_2c98);
    algo::CMat::~CMat(local_2a78);
  }
  local_3094 = 0;
  local_3090 = 0;
  FUN_14051bd30(&local_30b8,local_2e10,&local_3094);
  FUN_14051bd30(local_fd8,local_2e00,&local_3090);
  ccPelBuffer<unsigned_short>::operator=
            ((ccPelBuffer<unsigned_short> *)(local_2e00[0] + 0x28),
             (ccPelBuffer<unsigned_short> *)(local_2e10[0] + 0x28));
  local_308c[0] = 0;
  pcVar16 = CZoneStorage::GetpZmap2DPB(local_19b8,local_308c);
  cc_PelBuffer::offset((cc_PelBuffer *)pcVar16,(ccPair<long> *)&local_3080);
  local_308c[1] = 0;
  pcVar16 = CZoneStorage::GetpZmap2DPB(local_19b8,local_308c + 1);
  cc_PelBuffer::clientFromImageXform((cc_PelBuffer *)pcVar16,(ccXform<2> *)&local_2db0);
  CConsoleDisplay::Show((CConsoleDisplay *)DAT_1410f5ad0);
  CConsoleDisplay::UpdateZoneStorage((CConsoleDisplay *)DAT_1410f5ad0,local_19b8,1,0,true,true);
  ccUITablet::ccUITablet(local_20d8);
  puVar27 = *(undefined8 **)(param_1 + 0x4ba0);
  bVar8 = true;
  for (puVar25 = (undefined8 *)*puVar27;
      (dVar4 = DAT_140e44560, local_3078 = puVar25, bVar8 && (puVar25 != puVar27));
      puVar25 = (undefined8 *)*puVar25) {
    pCVar30 = (CViUnitLength *)(puVar25 + 2);
    bVar8 = false;
    local_res10 = pCVar30;
    while (!bVar8) {
      lVar9 = CAnomalieProd::_dpCoordCAO_um(*(CAnomalieProd **)pCVar30);
      lVar10 = CAnomalieProd::_dpCoordCAO_um(*(CAnomalieProd **)pCVar30);
      CDPoint::CDPoint(local_2d50,*(double *)(lVar10 + 0x10),*(double *)(lVar9 + 0x18));
      CDPoint::_vbase_destructor_(local_2c18);
      CDPoint::_vbase_destructor_(local_2bf0);
      if (*(ulonglong *)(*(longlong *)pCVar30 + 0x278) == local_3070) {
        lVar10 = *(ulonglong *)(*(longlong *)pCVar30 + 0x278) * 0x60;
        lVar9 = *(longlong *)(local_30a8 + 0x550);
        dVar4 = algo::CPoint_<double>::y((CPoint_<double> *)(lVar10 + lVar9));
        dVar5 = algo::CPoint_<double>::x((CPoint_<double> *)(lVar10 + lVar9));
        CDPoint::CDPoint(local_2ee8,dVar5 * dVar7,dVar4 * dVar7);
        local_2f00 = CONCAT44((uint)((ulonglong)local_2ed0 >> 0x20) ^ uVar34,
                              (uint)local_2ed0 ^ uVar33);
        local_2f08 = local_2ed8;
        ccUITablet::drawPointIcon(local_20d8,(ccPoint *)&local_2f08,(ccColor *)red_exref,0);
        lVar9 = CAnomalie::GetForeignMaterialEncompasingArea_um(*(CAnomalie **)pCVar30);
        lVar10 = CAnomalie::GetForeignMaterialEncompasingArea_um(*(CAnomalie **)pCVar30);
        local_2ff8 = 0;
        local_2ff0 = 0;
        local_2ef0 = CONCAT44((uint)((ulonglong)local_2ed0 >> 0x20) ^ uVar34,
                              (uint)local_2ed0 ^ uVar33);
        local_2ef8 = local_2ed8;
        ccAffineRectangle::ccAffineRectangle
                  (local_2468,(ccVector<2> *)&local_2ef8,*(double *)(lVar10 + 0x10),
                   *(double *)(lVar9 + 0x18),(ccRadian *)&local_2ff0,(ccRadian *)&local_2ff8);
        CDPoint::_vbase_destructor_(local_2bc8);
        CDPoint::_vbase_destructor_(local_2ba0);
        ccUITablet::draw(local_20d8,local_2468,(ccColor *)red_exref,0);
        lVar9 = *(longlong *)(param_1 + 0x19b8);
        if ((*(ulonglong *)(*(longlong *)pCVar30 + 0x278) <
             (ulonglong)((*(longlong *)(lVar9 + 0x4e0) - *(longlong *)(lVar9 + 0x4d8)) / 0x68)) &&
           (lVar26 = *(longlong *)(lVar9 + 0x4e0) - *(longlong *)(lVar9 + 0x4d8),
           lVar10 = lVar26 >> 0x3f, lVar26 / 0x68 + lVar10 != lVar10)) {
          lVar10 = *(longlong *)(*(longlong *)pCVar30 + 0x278) * 0x68;
          local_res18 = lVar10;
          _Var20 = algo::CPoints_<double>::size
                             ((CPoints_<double> *)(*(longlong *)(lVar9 + 0x4d8) + lVar10));
          if (_Var20 < 2) {
            puVar21 = (undefined8 *)
                      (**(code **)(**(longlong **)pCVar30 + 0xa8))(*(longlong **)pCVar30,local_2fe8)
            ;
            CLogManagerFunction::Write(local_2ec0,2,"Fm[%s] skipped not enough points.\n",*puVar21);
            ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
            ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_2fe8);
          }
          else {
            local_3048[0] = 0;
            local_3048[1] = 0;
            local_3048[2] = 0;
            for (uVar29 = 0;
                _Var20 = algo::CPoints_<double>::size
                                   ((CPoints_<double> *)(*(longlong *)(lVar9 + 0x4f0) + lVar10)),
                uVar29 < _Var20; uVar29 = uVar29 + 1) {
              this_00 = (CPoint_<double> *)
                        algo::CPoints_<double>::operator[]
                                  ((CPoints_<double> *)(*(longlong *)(lVar9 + 0x4f0) + lVar10),
                                   (__uint64)local_2620);
              this_01 = (CPoint_<double> *)
                        algo::CPoints_<double>::operator[]
                                  ((CPoints_<double> *)(*(longlong *)(lVar9 + 0x4f0) + lVar10),
                                   (__uint64)local_2680);
              dVar4 = algo::CPoint_<double>::y(this_00);
              dVar5 = algo::CPoint_<double>::x(this_01);
              CDPoint::CDPoint(local_2d78,dVar5 * dVar7,dVar4 * dVar7);
              algo::CPoint_<double>::~CPoint_<double>(local_2680);
              algo::CPoint_<double>::~CPoint_<double>(local_2620);
              local_2f90 = CONCAT44((uint)((ulonglong)local_2d60 >> 0x20) ^ uVar34,
                                    (uint)local_2d60 ^ uVar33);
              local_2f98 = local_2d68;
              FUN_1406018a0(local_3048,&local_2f98);
              CDPoint::_vbase_destructor_(local_2d78);
              lVar10 = local_res18;
            }
            ccPolyline::ccPolyline
                      (local_2998,(vector<ccVector<2>,std::allocator<ccVector<2>_>_> *)local_3048,
                       true);
            ccGraphicProps::ccGraphicProps(local_2b78,(ccColor *)orange_exref,1,0,false);
            ccUITablet::draw(local_20d8,local_2998,local_2b78,0);
            ccGraphicProps::_vbase_destructor_(local_2b78);
            ccPolyline::_vbase_destructor_(local_2998);
            pCVar30 = local_res10;
            if (local_3048[0] != 0) {
              FUN_140667220(local_3048,local_3048[0],local_3048[2] - local_3048[0] >> 4);
              pCVar30 = local_res10;
            }
          }
        }
        ccAffineRectangle::_vbase_destructor_(local_2468);
        CDPoint::_vbase_destructor_(local_2ee8);
      }
      CDPoint::_vbase_destructor_(local_2d50);
      bVar8 = true;
    }
  }
  for (lVar9 = 0; _Var22 = CDataCao::GetSizeCadTab((CDataCao *)(param_1 + 0x180)), lVar9 < _Var22;
      lVar9 = lVar9 + 1) {
    this_02 = CDataCao::GetLineCAD((CDataCao *)(param_1 + 0x180),lVar9);
    if ((*(int *)(this_02 + 8) == 1) && (-1 < *(int *)(this_02 + 0x10))) {
      lVar10 = (longlong)*(int *)(this_02 + 0x10) * 0x370 + *(longlong *)(param_1 + 0x4bb0);
      CDPoint::CDPoint(local_2d28,*(double *)(lVar10 + 0x60) + *(double *)(this_02 + 0x38),
                       *(double *)(this_02 + 0x40) + *(double *)(lVar10 + 0x68));
      FUN_1405fa9a0(param_1,local_2fc0,*(undefined4 *)(this_02 + 0x14),local_2d28);
      CViUnitPoint::CViUnitPoint(local_2778,local_2fb0,local_2fa8);
      bVar8 = CViUnitRect::Contains(local_2378,local_2778,false);
      if (bVar8) {
        local_3070 = 0;
        local_2fe0 = (*(double *)(this_02 + 0x90) + *(double *)(lVar10 + 0x70)) * dVar4;
        local_2f80 = CONCAT44((uint)((ulonglong)local_2fa8 >> 0x20) ^ uVar34,
                              SUB84(local_2fa8,0) ^ uVar33);
        local_2f88 = local_2fb0;
        dVar5 = CCAD_Base::_dSizeHeight_um(this_02);
        dVar6 = CCAD_Base::_dSizeLength_um(this_02);
        ccAffineRectangle::ccAffineRectangle
                  (local_2558,(ccVector<2> *)&local_2f88,dVar6,dVar5,(ccRadian *)&local_2fe0,
                   (ccRadian *)&local_3070);
        pCVar23 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                  (**(code **)(*(longlong *)this_02 + 0x60))(this_02,local_2fd8);
        this_03 = CBibliotheque::GetModelFamily((CBibliotheque *)(param_1 + 0x11f8),pCVar23);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_2fd8);
        if (this_03 != (CModelFamily *)0x0) {
          local_2fd0 = 0;
          local_2fc8 = (*(double *)(this_02 + 0x90) + *(double *)(lVar10 + 0x70)) * dVar4;
          local_2f70 = CONCAT44((uint)((ulonglong)local_2fa8 >> 0x20) ^ uVar34,
                                SUB84(local_2fa8,0) ^ uVar33);
          local_2f78 = local_2fb0;
          dVar5 = CModelFamily::GetTreatmentArea3D_Y_mm(this_03);
          dVar6 = CModelFamily::GetTreatmentArea3D_X_mm(this_03);
          pcVar24 = (ccAffineRectangle *)
                    ccAffineRectangle::ccAffineRectangle
                              (local_1aa8,(ccVector<2> *)&local_2f78,dVar6 * dVar7,dVar5 * dVar7,
                               (ccRadian *)&local_2fc8,(ccRadian *)&local_2fd0);
          ccAffineRectangle::operator=(local_2558,pcVar24);
          ccAffineRectangle::_vbase_destructor_(local_1aa8);
        }
        pcVar28 = (ccColor *)green_exref;
        if ((*(byte *)(lVar10 + 0x28) & 1) != 0) {
          pcVar28 = (ccColor *)cyan_exref;
        }
        ccUITablet::draw(local_20d8,local_2558,pcVar28,0);
        ccAffineRectangle::_vbase_destructor_(local_2558);
      }
      CViUnitPoint::_vbase_destructor_(local_2778);
      CDPoint::_vbase_destructor_(local_2fc0);
      CDPoint::_vbase_destructor_(local_2d28);
    }
  }
  CVitCognexConsoleDispatcher::CalqueRemoveAll
            ((CVitCognexConsoleDispatcher *)(DAT_1410f5ad0 + 0xa40),1);
  CVitCognexConsoleDispatcher::CalqueDraw
            ((CVitCognexConsoleDispatcher *)(DAT_1410f5ad0 + 0xa40),local_20d8,2);
  iStack_304c = (int)(local_2dc0 - DAT_140e7d068);
  iStack_3050 = (int)(local_2dc8 + DAT_140e7d068);
  iStack_3054 = (int)(local_2dc0 + DAT_140e7d068);
  local_3058 = (int)(local_2dc8 - DAT_140e7d068);
  local_2de8 = local_3058;
  iStack_2de4 = iStack_3054;
  iStack_2de0 = iStack_3050;
  iStack_2ddc = iStack_304c;
  CCadEngine::ZoomInRectangle
            (*(CCadEngine **)(param_1 + 0x4950),&local_2de8,0,CONCAT44(uVar32,uVar31));
  ccUITablet::~ccUITablet(local_20d8);
  FUN_140546790(&local_30b8,&local_3058,*local_30b8,local_30b8);
  FUN_1404729f0(local_30b8,1,0x108);
  SharedData::Error::~Error(local_2cf8);
  ImageZ::_vbase_destructor_(local_1ea8);
  algo::CPoints_<float>::~CPoints_<float>((CPoints_<float> *)local_2a08);
  vitXform::~vitXform((vitXform *)&local_2e98);
  CViUnitRect::_vbase_destructor_(local_2378);
  CViUnitSize::_vbase_destructor_(local_2938);
  CViUnitPoint::_vbase_destructor_(local_28b8);
  if (plVar11 != (longlong *)0x0) {
    (**(code **)*plVar11)(plVar11,1);
  }
  CViUnitPoint::_vbase_destructor_(local_2818);
  CDPoint::_vbase_destructor_(local_2dd8);
  CZoneStorage::~CZoneStorage(local_19b8);
  CZoneStorage::~CZoneStorage(local_d38);
  FUN_14051f750(&local_30a8);
LAB_1405fa952:
  CLogManagerFunction::~CLogManagerFunction(local_2ec0);
  return;
}

