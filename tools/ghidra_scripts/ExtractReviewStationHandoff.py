# Export review-station callers, callees, and call instructions.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os


OUT_PATH = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\review_station_handoff.json"

TARGETS = [
    ("should_review", "0x140674820", "CProdCarte::ShouldItGoToReviewStation"),
    ("capm_finalize", "0x14069b2a0", "CProductionThread::CAPM_SetInspectionStatus"),
    ("prepare_results", "0x14068fab0", "CProductionDoc::PrepareResultsAndAskComThreadToSend"),
    ("mark_review", "0x14067c710", "CMsgPanelProd::SendPanelToReviewStation"),
    ("results_available", "0x14067c5b0", "CProductionCommunication::ResultsAvailable"),
    ("comm_handler", "0x14067c480", "CProductionCommunication::Handler"),
    ("send_results", "0x14067c7b0", "CProductionCommunication::SendResults"),
    ("network_send", "0x14064e110", "network send helper"),
    ("get_review_station", "0x14064d6d0", "CNetworkDataManagement::GetReviewStation"),
    ("post_prepare", "0x14068ee40", "post-prepare hook"),
    ("review_convey", "0x140685e50", "review convey helper"),
    ("recorder_save", "0x1406e79c0", "CVitImgFileRecorderHelper::Save"),
    ("save_ois", "0x1406e7d90", "CVitImgFileRecorderHelper::SaveOIS"),
    ("save_otr", "0x1406e8220", "CVitImgFileRecorderHelper::SaveOTR"),
    ("save_macro", "0x1406e87c0", "CVitImgFileRecorderHelper::SaveOTR_OISFileForMacro"),
    ("zone_save_callsite", "0x140737b20", "zone OIS save callsite"),
    ("zone_neighbor_a", "0x1407378a0", "zone recorder neighbor"),
    ("zone_neighbor_b", "0x140737af0", "zone recorder neighbor"),
    ("fiducial_ois", "0x14053c440", "CDataCaoTraitement::SaveOISFile_FiducialOrSkipOdIdCode"),
    ("com_send_results", "0x1404c7580", "CCOMObjectMgr::SendPanelResults"),
]


def function_row(fn):
    return {
        "address": str(fn.getEntryPoint()),
        "name": fn.getName(True),
        "thunk": bool(fn.isThunk()),
    }


def callers_of(fn):
    fm = currentProgram.getFunctionManager()
    rm = currentProgram.getReferenceManager()
    rows = {}
    for ref in rm.getReferencesTo(fn.getEntryPoint()):
        if not ref.getReferenceType().isCall():
            continue
        caller = fm.getFunctionContaining(ref.getFromAddress())
        if caller is not None:
            rows[str(caller.getEntryPoint())] = function_row(caller)
    return [rows[key] for key in sorted(rows)]


def calls_from(fn):
    fm = currentProgram.getFunctionManager()
    listing = currentProgram.getListing()
    rm = currentProgram.getReferenceManager()
    callees = {}
    instructions = []
    for inst in listing.getInstructions(fn.getBody(), True):
        if not inst.getFlowType().isCall():
            continue
        destinations = []
        for ref in rm.getReferencesFrom(inst.getAddress()):
            if not ref.getReferenceType().isCall():
                continue
            destination = ref.getToAddress()
            destinations.append(str(destination))
            callee = fm.getFunctionAt(destination)
            if callee is not None:
                callees[str(callee.getEntryPoint())] = function_row(callee)
        instructions.append(
            {
                "site": str(inst.getAddress()),
                "instruction": str(inst),
                "destinations": sorted(set(destinations)),
            }
        )
    return [callees[key] for key in sorted(callees)], instructions


def main():
    fm = currentProgram.getFunctionManager()
    output = {
        "schema": 1,
        "program": currentProgram.getName(),
        "version": "70.06.59.00",
        "image_base": str(currentProgram.getImageBase()),
        "analysis_mode": "read-only",
        "targets": [],
    }
    for key, address, inferred_name in TARGETS:
        addr = toAddr(address)
        fn = fm.getFunctionAt(addr) or fm.getFunctionContaining(addr)
        if fn is None:
            output["targets"].append(
                {
                    "key": key,
                    "address": address.lower(),
                    "inferred_name": inferred_name,
                    "error": "no function",
                }
            )
            continue
        callees, instructions = calls_from(fn)
        output["targets"].append(
            {
                "key": key,
                "address": address.lower(),
                "function_start": str(fn.getEntryPoint()),
                "function_end": str(fn.getBody().getMaxAddress()),
                "ghidra_name": fn.getName(True),
                "inferred_name": inferred_name,
                "callers": callers_of(fn),
                "callees": callees,
                "direct_call_instructions": instructions,
            }
        )
    output["targets"].sort(key=lambda row: row["address"])
    parent = os.path.dirname(OUT_PATH)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    with open(OUT_PATH, "w", encoding="utf-8") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print("WROTE", OUT_PATH, len(output["targets"]))


main()
