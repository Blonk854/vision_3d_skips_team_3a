# Dump decompilations for review-path candidates.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"

TARGETS = [
    ("Missing_string_site", "0x140289870"),
    ("Text_fault_string_site", "0x1406d2af0"),
    ("ShouldItGoToReviewStation_log", "0x140674820"),
    ("CSV_failure_mode_header", "0x1405b7220"),
    ("SendPanelToReviewStation_log", "0x14067c710"),
    ("CAPM_SetInspectionStatus", "0x14069b2a0"),
    ("PrepareResultsAndAskComThreadToSend", "0x14068fab0"),
    ("ProductionCommunication_Handler", "0x14067c480"),
    ("ProductionCommunication_ResultsAvailable", "0x14067c5b0"),
    ("ProductionCommunication_SendResults", "0x14067c7b0"),
    ("Network_Send", "0x14064e110"),
    ("Network_GetReviewStation", "0x14064d6d0"),
    ("PrepareResults_post_hook", "0x14068ee40"),
    ("PrepareResults_review_convey", "0x140685e50"),
    ("Recorder_Save", "0x1406e79c0"),
    ("SaveOIS_helper", "0x1406e7d90"),
    ("Recorder_SaveOTR", "0x1406e8220"),
    ("Recorder_SaveOTR_OISFileForMacro", "0x1406e87c0"),
    ("Zone_SaveOIS_callsite", "0x140737b20"),
    ("Zone_recorder_neighbor_1407378a0", "0x1407378a0"),
    ("Zone_recorder_neighbor_140737af0", "0x140737af0"),
    ("SaveOISFile_FiducialOrSkipOdIdCode", "0x14053c440"),
    ("COM_SendPanelResults", "0x1404c7580"),
    ("PV_COMMAND_BTN_OIS", "0x1406b0c00"),
    ("ExecuteOne_Component", "0x1407368d0"),
    ("ExecuteAll_Components", "0x1407354b0"),
    ("SkipSubPanel", "0x140541080"),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    decomp = DecompInterface()
    decomp.openProgram(currentProgram)
    monitor = ConsoleTaskMonitor()
    for label, addr_s in TARGETS:
        addr = toAddr(addr_s)
        fn = getFunctionAt(addr) or getFunctionContaining(addr)
        path = os.path.join(OUT_DIR, label + ".c")
        with open(path, "w", encoding="utf-8") as f:
            f.write("// %s @ %s\n" % (label, addr_s))
            if fn is None:
                f.write("// NO FUNCTION\n")
                print("NOFN", label, addr_s)
                continue
            f.write("// function %s [%s ..]\n\n" % (fn.getName(True), fn.getEntryPoint()))
            res = decomp.decompileFunction(fn, 60, monitor)
            if res and res.getDecompiledFunction():
                f.write(res.getDecompiledFunction().getC())
            else:
                f.write("// DECOMPILE FAILED\n")
            print("WROTE", path, fn.getName(True))
    decomp.dispose()


if __name__ == "__main__":
    main()
else:
    main()
