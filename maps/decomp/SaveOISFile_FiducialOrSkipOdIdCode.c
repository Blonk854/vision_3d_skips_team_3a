// SaveOISFile_FiducialOrSkipOdIdCode @ 0x14053c440
// function CDataCaoTraitement::SaveOISFile_FiducialOrSkipOdIdCode [14053c440 ..]


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */
/* public: bool __cdecl CDataCaoTraitement::SaveOISFile_FiducialOrSkipOdIdCode(class
   ATL::CStringT<char,class StrTraitMFC_DLL<char,class ATL::ChTraitsCRT<char> > > const &
   __ptr64,class CcPelBuffer const & __ptr64,class CCAD_Base * __ptr64,class
   ATL::CStringT<char,class StrTraitMFC_DLL<char,class ATL::ChTraitsCRT<char> > > const &
   __ptr64,class CConsoleDisplay * __ptr64,bool) __ptr64 */

bool __thiscall
CDataCaoTraitement::SaveOISFile_FiducialOrSkipOdIdCode
          (CDataCaoTraitement *this,
          CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *param_1,
          CcPelBuffer *param_2,CCAD_Base *param_3,
          CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *param_4,
          CConsoleDisplay *param_5,bool param_6)

{
  void *pvVar1;
  double dVar2;
  double dVar3;
  CcPelBuffer *pCVar4;
  byte bVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  long lVar9;
  long lVar10;
  CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *pCVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  longlong *plVar14;
  longlong lVar15;
  CImagesDefinitions *this_00;
  CZmapScanParameter *pCVar16;
  HANDLE hFileMappingObject;
  LPVOID lpBaseAddress;
  undefined8 *puVar17;
  undefined8 *puVar18;
  CRunContextModel_SkipMark *pCVar19;
  CRunContextModel_Fiducial *pCVar20;
  CRunContextModel_IDCode *pCVar21;
  int iVar22;
  void *pvVar23;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *this_01;
  int iVar24;
  CDPoint *pCVar25;
  int iVar26;
  char *pcVar27;
  int iVar28;
  double dVar29;
  short local_res20 [4];
  undefined8 in_stack_ffffffffffffdf28;
  short *psVar30;
  undefined4 uVar32;
  ulonglong uVar31;
  undefined4 uVar33;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *in_stack_ffffffffffffdf38;
  ulonglong uVar34;
  undefined8 local_2078;
  undefined8 uStack_2070;
  LPVOID local_2068;
  CRunContextModel_SkipMark *local_2058;
  short local_2050 [2];
  short local_204c [2];
  short local_2048 [4];
  double local_2040;
  CcPelBuffer *local_2038;
  uint local_2030;
  int local_202c;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_2028 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_2020 [8];
  CDPoint local_2018;
  undefined7 uStack_2017;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_2010 [8];
  undefined8 local_2008;
  ulonglong local_2000;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1ff8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1ff0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1fe8 [8];
  longlong local_1fe0 [2];
  double local_1fd0;
  double local_1fc8;
  char local_1fb8;
  undefined7 uStack_1fb7;
  undefined8 local_1fa8;
  ulonglong local_1fa0;
  eShapDefinition local_1f98 [2];
  double local_1f90;
  double local_1f88;
  undefined8 local_1f80;
  undefined8 local_1f78;
  CcArea local_1f70 [8];
  CRunContextModel_Fiducial *local_1f68 [3];
  CLogManagerFunction local_1f50 [40];
  int local_1f28 [4];
  undefined8 local_1f18;
  CZConvert local_1f10 [40];
  vitXform local_1ee8 [8];
  double local_1ee0;
  double dStack_1ed8;
  undefined1 local_1ea8 [64];
  undefined8 local_1e68;
  undefined8 uStack_1e60;
  undefined1 local_1e58 [40];
  undefined4 local_1e30;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1e28 [32];
  HANDLE pvStack_1e08;
  undefined4 local_1e00;
  undefined8 local_1d70 [4];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d50 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d48 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d40 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d38 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d30 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d28 [8];
  bool local_1d20;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d18 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1d10 [32];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1cf0 [16];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1ce0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1cd8 [8];
  undefined4 local_1cd0;
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1cc8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1cc0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1cb8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1cb0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1ca8 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1ca0 [8];
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> local_1c98 [24];
  undefined2 local_1c80;
  CDataCaoTraitement local_1c38;
  undefined4 local_1c34;
  double local_1c30;
  double local_1b98 [6];
  CViUnitPoint local_1b68 [160];
  CViUnitPoint local_1ac8 [160];
  CViUnitPoint local_1a28 [160];
  CViUnitPoint local_1988 [160];
  CImagesDefinitions local_18e8 [736];
  undefined1 local_1608 [8];
  CViUnitLength local_1600 [64];
  SAcquisitionCapabilities local_15c0 [1792];
  undefined1 local_ec0 [416];
  CViUnitLength local_d20 [56];
  CZoneStorage local_ce8 [104];
  ccPelBuffer<unsigned_char> local_c80 [3144];
  
                    /* 0x53c440  224
                       ?SaveOISFile_FiducialOrSkipOdIdCode@CDataCaoTraitement@@QEAA_NAEBV?$CStringT@DV?$StrTraitMFC_DLL@DV?$ChTraitsCRT@D@ATL@@@@@ATL@@AEBVCcPelBuffer@@PEAVCCAD_Base@@0PEAVCConsoleDisplay@@_N@Z
                        */
  uVar8 = (uint)((ulonglong)in_stack_ffffffffffffdf28 >> 0x20);
  local_1f18 = 0xfffffffffffffffe;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2058,
             "SaveOISFile");
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078,
             "CDataCaoTraitement");
  pCVar19 = (CRunContextModel_SkipMark *)0x0;
  psVar30 = (short *)((ulonglong)uVar8 << 0x20);
  CLogManagerFunction::CLogManagerFunction
            (local_1f50,0x16,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078,
             (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2058,0);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
            ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2058);
  if (param_3 == (CCAD_Base *)0x0) {
    CLogManagerFunction::Write(local_1f50,4,"Not element present. Ptr NULL.\n");
    goto LAB_14053d53a;
  }
  CDPoint::CDPoint((CDPoint *)local_1fe0);
  local_2030 = 0;
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_2020);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1fe8);
  dVar2 = DAT_140e44650;
  uVar8 = *(uint *)(param_3 + 8);
  if (uVar8 == 0x20) {
    iVar28 = 4;
    in_stack_ffffffffffffdf38 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)0x0
    ;
    CSkip_bloc::GetParaString
              ((CSkip_bloc *)param_3,&local_2040,(double *)&local_2058,&local_202c,(short *)0x0,
               (short *)0x0,(short *)0x0,(short *)0x0,
               (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)0x0,(int *)0x0,
               (int *)0x0,(int *)0x0,(int *)0x0,(eShapDefinition *)0x0,(int *)0x0);
    psVar30 = local_2048;
    CSkip_bloc::GetParamSize((CSkip_bloc *)param_3,local_res20,local_2050,local_204c,psVar30);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              (**(code **)(*(longlong *)param_3 + 0x48))(param_3,&local_2078);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_2020,pCVar11);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
    uVar12 = CDPoint::CDPoint(&local_2018,0.0,0.0);
    (**(code **)(local_1fe0[0] + 0x10))(local_1fe0,uVar12);
    CDPoint::_vbase_destructor_(&local_2018);
LAB_14053c822:
    FUN_1406492e0(this + 0x1a58,local_1fe0,local_202c);
LAB_14053c832:
    iVar26 = (int)local_res20[0];
    iVar22 = -(int)local_2050[0];
    iVar24 = (int)local_204c[0];
    iVar6 = -(int)local_2048[0];
    iVar7 = iVar26;
    if (iVar24 < iVar26) {
      iVar7 = iVar24;
      iVar24 = iVar26;
    }
    iVar26 = iVar22;
    if (iVar6 < iVar22) {
      iVar26 = iVar6;
      iVar6 = iVar22;
    }
    uStack_2070 = (HANDLE)CONCAT44(iVar6,iVar24);
    local_2078 = (undefined **)CONCAT44(iVar26,iVar7);
    local_2038 = (CcPelBuffer *)0x0;
    uVar34 = (ulonglong)in_stack_ffffffffffffdf38 & 0xffffffff00000000;
    uVar31 = DAT_140e445a0;
    CcPelBuffer::GetImgCentered
              (param_2,&local_2038,&local_2078,0,(ulonglong)psVar30 & 0xffffffffffffff00,
               DAT_140e445a0,uVar34);
    if (local_2038 == (CcPelBuffer *)0x0) {
      pcVar27 = "Failed to extract images.\n";
      goto LAB_14053d505;
    }
    if (param_5 != (CConsoleDisplay *)0x0) {
      CVitCognexConsoleDispatcher::CalqueRemoveAll
                ((CVitCognexConsoleDispatcher *)(param_5 + 0xa40),1);
    }
    CcPelBuffer::GetXform(param_2);
    CcPelBuffer::GetPixelSize_um(param_2,&local_1f88,&local_1f90);
    iVar7 = CcPelBuffer::Height_px(local_2038);
    iVar24 = CcPelBuffer::Width_px(local_2038);
    local_1ee0 = (double)iVar24 * local_1f88 * dVar2;
    dStack_1ed8 = (double)iVar7 * local_1f90 * dVar2;
    CcPelBuffer::SetXform_Transform_Micron2Pixel(local_2038,local_1ee8);
    CcArea::CcArea(local_1f70);
    iVar7 = CcPelBuffer::Height_px(local_2038);
    iVar24 = CcPelBuffer::Width_px(local_2038);
    CcArea::SetCoor(local_1f70,0,0,iVar24,iVar7);
    uVar12 = *(undefined8 *)(param_2 + 0xe0);
    vitXform::GetDoubleTab(local_1ee8,local_1b98);
    CZConvert::CZConvert(local_1f10);
    CZConvert::GetParamIntTab(local_1f10,local_1f28);
    uVar31 = uVar31 & 0xffffffffffffff00;
    FUN_140764f30(local_1ea8,0,local_1b98,local_1f28,uVar12,uVar31,uVar34 & 0xffffffffffffff00,0xd,0
                 );
    uVar33 = (undefined4)(uVar31 >> 0x20);
    uVar32 = (undefined4)((ulonglong)uVar12 >> 0x20);
    FUN_1404e2dc0(&local_1e68);
    local_2058 = (CRunContextModel_SkipMark *)&local_2078;
    uVar12 = CTest::GetOIS_ProdFileDirectory((CTest *)(this + 0x188));
    uVar13 = CTest::GetRecordPanelTypeInfo((CTest *)(this + 0x188));
    FUN_14052c240(local_1e58,uVar13,uVar12);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1ff8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2000);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2008);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_2010);
    plVar14 = (longlong *)(**(code **)(*(longlong *)this + 0x230))(this);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              (**(code **)(*plVar14 + 0x20))(plVar14,&local_2078);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1d48,pCVar11);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              CTest::GetProductName((CTest *)(this + 0x188));
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1cf0,pCVar11);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              CTest::GetCompleteLibName((CTest *)(this + 0x188));
    pCVar11 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                        (local_1cc8,pCVar11);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1cc0,pCVar11);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_1ce0,"");
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1ca0,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)param_4)
    ;
    local_1c80 = 0;
    local_1c38 = this[0xe01];
    plVar14 = (longlong *)(**(code **)(*(longlong *)this + 0x230))(this);
    lVar15 = (**(code **)(*plVar14 + 0x28))(plVar14,local_1608);
    local_1c34 = *(undefined4 *)(lVar15 + 0x220);
    CViUnitLength::_vbase_destructor_(local_d20);
    _eh_vector_destructor_iterator_(local_ec0,0x68,4,FUN_14046ea90);
    ViVMachineController::SAcquisitionCapabilities::~SAcquisitionCapabilities(local_15c0);
    CViUnitLength::_vbase_destructor_(local_1600);
    this_00 = (CImagesDefinitions *)CTest::GetZMapScanParams((CTest *)(this + 0x188));
    pCVar16 = CImagesDefinitions::GetZmapScanParam(this_00);
    local_1c30 = CGlobalAcquisitionParameters::GetLightingPower_percent
                           ((CGlobalAcquisitionParameters *)(pCVar16 + 8));
    CImagesDefinitions::_vbase_destructor_(local_18e8);
    pcVar27 = (char *)algo::IAlgorithm::GetComputerNameA();
    if (0xf < *(ulonglong *)(pcVar27 + 0x18)) {
      pcVar27 = *(char **)pcVar27;
    }
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1d40,pcVar27);
    if (0xf < local_2000) {
      pvVar1 = (void *)CONCAT71(uStack_2017,local_2018);
      pvVar23 = pvVar1;
      if (0xfff < local_2000 + 1) {
        if (((byte)local_2018 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
          _invalid_parameter_noinfo_noreturn();
        }
        pvVar23 = *(void **)((longlong)pvVar1 - 8);
        if (pvVar1 <= pvVar23) {
                    /* WARNING: Subroutine does not return */
          _invalid_parameter_noinfo_noreturn();
        }
        if ((ulonglong)((longlong)pvVar1 - (longlong)pvVar23) < 8) {
                    /* WARNING: Subroutine does not return */
          _invalid_parameter_noinfo_noreturn();
        }
        if (0x27 < (ulonglong)((longlong)pvVar1 - (longlong)pvVar23)) {
                    /* WARNING: Subroutine does not return */
          _invalid_parameter_noinfo_noreturn();
        }
      }
      operator_delete(pvVar23);
    }
    plVar14 = (longlong *)(**(code **)(*(longlong *)this + 0x230))(this);
    lVar15 = (**(code **)(*plVar14 + 0x28))(plVar14,local_1608);
    pcVar27 = (char *)(lVar15 + 0xf0);
    if (0xf < *(ulonglong *)(lVar15 + 0x108)) {
      pcVar27 = *(char **)pcVar27;
    }
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1d38,pcVar27);
    CViUnitLength::_vbase_destructor_(local_d20);
    _eh_vector_destructor_iterator_(local_ec0,0x68,4,FUN_14046ea90);
    ViVMachineController::SAcquisitionCapabilities::~SAcquisitionCapabilities(local_15c0);
    CViUnitLength::_vbase_destructor_(local_1600);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1ff0);
    CBmFileData::GetFileVersionMinor((CBmFileData *)(this + 0x1200));
    uVar8 = CBmFileData::GetFileVersionMajor((CBmFileData *)(this + 0x1200));
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
              (local_1ff0,"%d.%d",(ulonglong)uVar8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1ca8,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               local_1ff0);
    local_1f80 = *(undefined8 *)(this + 0x1560);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              FUN_140493160(&local_1f80,&local_2078,"%Y%m%dT%H%M%S");
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1cb0,pCVar11);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
    local_1f78 = *(undefined8 *)(this + 0x11f0);
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              FUN_140493160(&local_1f78,&local_2078,"%Y%m%dT%H%M%S");
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1cb8,pCVar11);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_1d30,"");
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_1d28,"");
    pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
              CTest::GetCustomer((CTest *)(this + 0x188));
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1c98,pCVar11);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
    local_1d20 = param_6;
    if (param_6) {
      local_2078 = CViSharedMemory::vftable;
      lpBaseAddress = (LPCVOID)0x0;
      local_2068 = (LPVOID)0x0;
      pcVar27 = ATL::CSimpleStringT<char,1>::operator_char_const____ptr64
                          ((CSimpleStringT<char,1> *)&DAT_141111ac0);
      hFileMappingObject = OpenFileMappingA(2,0,pcVar27);
      uStack_2070 = hFileMappingObject;
      if (hFileMappingObject == (HANDLE)0x0) {
        CLogManagerFunction::Write(local_1f50,4,"oSharedMemoryPCBiSimulation.Init() failed.\n");
      }
      else {
        uVar32 = 0;
        lpBaseAddress = MapViewOfFile(hFileMappingObject,2,0,0,0);
        local_2000 = 0xf;
        local_2008 = 0;
        local_2018 = (CDPoint)0x0;
        local_2068 = lpBaseAddress;
        FUN_14045f320(&local_2018,&DAT_140dd3ce0,0);
        if ((lpBaseAddress != (LPVOID)0x0) &&
           (&local_2018 != (CDPoint *)((longlong)lpBaseAddress + 0x780))) {
          FUN_14045f1f0(&local_2018,(CDPoint *)((longlong)lpBaseAddress + 0x780),0,
                        0xffffffffffffffff);
        }
        pCVar25 = &local_2018;
        if (0xf < local_2000) {
          pCVar25 = (CDPoint *)CONCAT71(uStack_2017,local_2018);
        }
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                  (local_1d18,(char *)pCVar25);
        local_1fa0 = 0xf;
        local_1fa8 = 0;
        local_1fb8 = '\0';
        FUN_14045f320(&local_1fb8,&DAT_140dd3ce0,0);
        if ((lpBaseAddress != (LPVOID)0x0) &&
           (&local_1fb8 != (char *)((longlong)lpBaseAddress + 0x7a0))) {
          FUN_14045f1f0(&local_1fb8,(char *)((longlong)lpBaseAddress + 0x7a0),0,0xffffffffffffffff);
        }
        pcVar27 = &local_1fb8;
        if (0xf < local_1fa0) {
          pcVar27 = (char *)CONCAT71(uStack_1fb7,local_1fb8);
        }
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                  (local_1d10,pcVar27);
        FUN_1404546f0(&local_1fb8);
        FUN_1404546f0(&local_2018);
      }
      if (lpBaseAddress != (LPCVOID)0x0) {
        UnmapViewOfFile(lpBaseAddress);
      }
      if (hFileMappingObject != (HANDLE)0x0) {
        CloseHandle(hFileMappingObject);
      }
    }
    local_1e68 = 0;
    uStack_1e60 = 0;
    local_1e30 = 1;
    lVar9 = ccRectangle<long>::width((ccRectangle<long> *)local_1f68);
    lVar10 = ccRectangle<long>::height((ccRectangle<long> *)local_1f68);
    local_2078 = (undefined **)local_1f68[0];
    uStack_2070 = (HANDLE)CONCAT44(lVar10 + (int)((ulonglong)local_1f68[0] >> 0x20),
                                   lVar9 + (int)local_1f68[0]);
    pvStack_1e08 = uStack_2070;
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_1d70,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               local_1fe8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
              (local_1cd8,
               (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
               local_2020);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=(local_1d50,"");
    local_1cd0 = *(undefined4 *)(param_3 + 0x14);
    local_1e00 = *(undefined4 *)(param_3 + 8);
    CZoneStorage::CZoneStorage(local_ce8);
    ccPelBuffer<unsigned_char>::operator=(local_c80,(ccPelBuffer<unsigned_char> *)local_2038);
    cc_PelBuffer::clientFromImageXform((cc_PelBuffer *)local_c80,(ccXform<2> *)&local_1ee0);
    CViUnitPoint::CViUnitPoint(local_1b68,local_1fd0,local_1fc8);
    if (param_5 != (CConsoleDisplay *)0x0) {
      CConsoleDisplay::UpdateZoneStorage(param_5,local_ce8,2,0,true,true);
    }
    if (iVar28 == 4) {
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078,
                 (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                 param_1);
      AssureEndBackSlach((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                         &local_2078);
      puVar17 = (undefined8 *)FUN_140765460(local_1ea8,local_2028);
      uVar12 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
               CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                         ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                          &local_2058,
                          (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                           *)local_1cd8);
      puVar18 = (undefined8 *)FiltreExoticChars2(&local_2040,uVar12,&DAT_140e4c888);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                (local_1e28,"%sSKIP_%s_%i_%s.ois",local_2078,*puVar18,CONCAT44(uVar32,local_1cd0),
                 *puVar17);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2040);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_2028);
      pCVar19 = (CRunContextModel_SkipMark *)FUN_14076d550(0x110);
      local_2058 = pCVar19;
      if (pCVar19 == (CRunContextModel_SkipMark *)0x0) {
        pCVar21 = (CRunContextModel_IDCode *)0x0;
      }
      else {
        uVar12 = CViUnitPoint::CViUnitPoint(local_1ac8,local_1b68);
        CRunContextModel_SkipMark::CRunContextModel_SkipMark(pCVar19,local_ce8,DAT_1410f5ad0,uVar12)
        ;
        *(undefined ***)pCVar19 = CRunContextModel_SkipMark::vftable;
        pCVar21 = (CRunContextModel_IDCode *)pCVar19;
      }
      this_01 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078;
LAB_14053d426:
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(this_01);
    }
    else {
      if (iVar28 == 3) {
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2058,
                   (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                   param_1);
        AssureEndBackSlach((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                           &local_2058);
        puVar17 = (undefined8 *)FUN_140765460(local_1ea8,local_2028);
        uVar12 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                 CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                           ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                            &local_2078,
                            (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                             *)local_1cd8);
        puVar18 = (undefined8 *)FiltreExoticChars2(&local_2040,uVar12,&DAT_140e4c888);
        uVar31 = CONCAT44(uVar32,local_1cd0);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                  (local_1e28,"%sFIDUCIAL_%s_%i-%i-%s_%s.ois",local_2058,*puVar18,uVar31,
                   CONCAT44(uVar33,local_2030),local_1d70[0],*puVar17);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2040);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_2028);
        pCVar20 = (CRunContextModel_Fiducial *)FUN_14076d550(0x118);
        local_2078 = (undefined **)pCVar20;
        if (pCVar20 == (CRunContextModel_Fiducial *)0x0) {
          pCVar21 = (CRunContextModel_IDCode *)0x0;
        }
        else {
          uVar12 = CViUnitPoint::CViUnitPoint(local_1a28,local_1b68);
          CRunContextModel_Fiducial::CRunContextModel_Fiducial
                    (pCVar20,local_ce8,DAT_1410f5ad0,uVar12,uVar31 & 0xffffffffffffff00);
          *(undefined ***)pCVar20 = CRunContextModel_Fiducial::vftable;
          pCVar21 = (CRunContextModel_IDCode *)pCVar20;
        }
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)local_1d70,"%i",
                   (ulonglong)local_2030);
        this_01 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2058;
        goto LAB_14053d426;
      }
      pCVar21 = (CRunContextModel_IDCode *)pCVar19;
      if (iVar28 == 7) {
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2040,
                   (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                   param_1);
        AssureEndBackSlach((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                           &local_2040);
        puVar17 = (undefined8 *)FUN_140765460(local_1ea8,local_2028);
        uVar12 = ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
                 CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                           ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)
                            &local_2078,
                            (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_>
                             *)local_1cd8);
        puVar18 = (undefined8 *)FiltreExoticChars2(&local_2058,uVar12,&DAT_140e4c888);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::Format
                  (local_1e28,"%sIDCODE_%s_%i-%s_%s.ois",local_2040,*puVar18,
                   CONCAT44(uVar32,local_1cd0),local_1d70[0],*puVar17);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                  ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2058);
        ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
        ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_2028);
        pCVar21 = (CRunContextModel_IDCode *)FUN_14076d550(0x140);
        local_2078 = (undefined **)pCVar21;
        if (pCVar21 == (CRunContextModel_IDCode *)0x0) {
          pCVar21 = (CRunContextModel_IDCode *)0x0;
        }
        else {
          uVar12 = CViUnitAngle::CViUnitAngle
                             ((CViUnitAngle *)&local_2018,*(double *)(param_3 + 0x90));
          uVar13 = CViUnitPoint::CViUnitPoint(local_1988,local_1b68);
          CRunContextModel_IDCode::CRunContextModel_IDCode
                    (pCVar21,local_ce8,DAT_1410f5ad0,uVar13,uVar12,1);
          *(undefined ***)pCVar21 = CRunContextModel_IDCode::vftable;
        }
        this_01 = (CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2040;
        goto LAB_14053d426;
      }
    }
    bVar5 = FUN_1407696c0(local_1ea8,iVar28,pCVar21,&local_1e68);
    pCVar19 = (CRunContextModel_SkipMark *)(ulonglong)bVar5;
    if (bVar5 == 0) {
      CLogManagerFunction::Write(local_1f50,4,"Failed to save image.\n");
    }
    pCVar4 = local_2038;
    if (local_2038 != (CcPelBuffer *)0x0) {
      CcPelBuffer::~CcPelBuffer(local_2038);
      FUN_1404556c0(pCVar4,0xf8);
      local_2038 = (CcPelBuffer *)0x0;
    }
    if (pCVar21 != (CRunContextModel_IDCode *)0x0) {
      (*(code *)**(undefined8 **)pCVar21)(pCVar21,1);
    }
    CViUnitPoint::_vbase_destructor_(local_1b68);
    CZoneStorage::~CZoneStorage(local_ce8);
    ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
    ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1ff0);
    FUN_1404e33f0(&local_1e68);
    CZConvert::~CZConvert(local_1f10);
    CcArea::~CcArea(local_1f70);
    vitXform::~vitXform(local_1ee8);
  }
  else {
    if ((uVar8 & 0xc0) != 0) {
      iVar28 = 3;
      CImagesDefinitions::CImagesDefinitions(local_18e8);
      in_stack_ffffffffffffdf38 = local_2020;
      CMire::GetParaString
                ((CMire *)param_3,(CDPoint *)local_1fe0,(int *)&local_2030,&local_202c,
                 (int *)&local_2078,local_18e8,in_stack_ffffffffffffdf38,(int *)&local_2058,
                 (int *)&local_2040,(int *)local_2028,local_1f98);
      psVar30 = local_2048;
      CMire::GetParamSize((CMire *)param_3,local_res20,local_2050,local_204c,psVar30);
      uVar12 = CDPoint::CDPoint(&local_2018,0.0,0.0);
      (**(code **)(local_1fe0[0] + 0x10))(local_1fe0,uVar12);
      CDPoint::_vbase_destructor_(&local_2018);
      FUN_1406492e0(this + 0x1a58,local_1fe0,local_202c);
      CImagesDefinitions::_vbase_destructor_(local_18e8);
      goto LAB_14053c832;
    }
    if ((uVar8 >> 0xe & 1) != 0) {
      iVar28 = 7;
      dVar29 = CcPelBuffer::Width(param_2);
      dVar3 = DAT_140e51090;
      local_res20[0] = (short)(int)(dVar29 * DAT_140e51090 * dVar2);
      dVar29 = CcPelBuffer::Height(param_2);
      local_2050[0] = (short)(int)(dVar29 * dVar3 * DAT_140de2128);
      dVar29 = CcPelBuffer::Width(param_2);
      local_204c[0] = (short)(int)(dVar29 * dVar3 * DAT_140de2128);
      dVar29 = CcPelBuffer::Height(param_2);
      local_2048[0] = (short)(int)(dVar29 * dVar3 * dVar2);
      pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                (**(code **)(*(longlong *)param_3 + 0x48))(param_3,&local_2078);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                (local_2020,pCVar11);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
      pCVar11 = (CStringT<char,class_StrTraitMFC_DLL<char,class_ATL::ChTraitsCRT<char>_>_> *)
                (**(code **)(*(longlong *)param_3 + 0x60))(param_3,&local_2078);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::operator=
                (local_1fe8,pCVar11);
      ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
      ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>
                ((CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_> *)&local_2078);
      uVar12 = CDPoint::CDPoint(&local_2018,0.0,0.0);
      (**(code **)(local_1fe0[0] + 0x10))(local_1fe0,uVar12);
      CDPoint::_vbase_destructor_(&local_2018);
      local_202c = *(int *)(param_3 + 0x14);
      goto LAB_14053c822;
    }
    pcVar27 = "Element type not supported.\n";
LAB_14053d505:
    CLogManagerFunction::Write(local_1f50,4,pcVar27);
    pCVar19 = (CRunContextModel_SkipMark *)0x0;
  }
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_1fe8);
  ATL::CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>::
  ~CStringT<char,StrTraitMFC_DLL<char,ATL::ChTraitsCRT<char>_>_>(local_2020);
  CDPoint::_vbase_destructor_((CDPoint *)local_1fe0);
LAB_14053d53a:
  CLogManagerFunction::~CLogManagerFunction(local_1f50);
  return (bool)(char)pCVar19;
}

