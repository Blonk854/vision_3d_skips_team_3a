import java.util.Map;
import java.util.TreeMap;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.MemoryBlock;

public class ConfigureStationMfcAnalysis extends GhidraScript {
    @Override
    protected void run() throws Exception {
        if (!"0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe"
                .equalsIgnoreCase(currentProgram.getExecutableSHA256()) ||
                !"x86:LE:64:default".equals(currentProgram.getLanguageID().toString()) ||
                !"windows".equals(currentProgram.getCompilerSpec().getCompilerSpecID().toString()) ||
                currentProgram.getImageBase().getOffset() != 0x180000000L) {
            throw new IllegalStateException("Station MFC identity mismatch");
        }

        Map<String, String> options = getCurrentAnalysisOptionsAndValues(currentProgram);
        int pdbOptions = 0;
        for (Map.Entry<String, String> option : options.entrySet()) {
            String name = option.getKey();
            boolean booleanOption = "true".equalsIgnoreCase(option.getValue()) ||
                "false".equalsIgnoreCase(option.getValue());
            if (booleanOption && (name.toLowerCase(java.util.Locale.ROOT).contains("pdb") ||
                    name.equals("Decompiler Parameter ID") || name.equals("Function ID"))) {
                setAnalysisOption(currentProgram, name, "false");
                if (name.toLowerCase(java.util.Locale.ROOT).contains("pdb")) {
                    pdbOptions++;
                }
            }
        }
        if (pdbOptions == 0) {
            throw new IllegalStateException("No PDB options found; review before analysis");
        }
        for (Map.Entry<String, String> option :
                new TreeMap<>(getCurrentAnalysisOptionsAndValues(currentProgram)).entrySet()) {
            println("MFC_OPTION " + option.getKey() + "=" + option.getValue());
        }
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            println("MFC_MEMORY " + block.getName() + " " + block.getStart() + "-" +
                block.getEnd() + " initialized=" + block.isInitialized() +
                " execute=" + block.isExecute());
        }
        println("MFC_CONFIG_VERIFIED " + currentProgram.getExecutableSHA256());
    }
}