from __future__ import annotations
from pathlib import Path
import sys
from twylt import Tool, Requirements
from twylt.guardrails import Workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'shared'))
from hdl_common.models import AnalysisInput, Model, Symbol
from hdl_common.analysis import resolved_input, analyze_input, symbol

class SymbolsOutput(Model):
    symbols: list[Symbol]

def execute(data):
    data = resolved_input(data)
    r = analyze_input(data)
    return dict(symbols=[symbol(r, s) for s in r.symbols])

class HDLTool(Tool[AnalysisInput, SymbolsOutput]):
    input_model = AnalysisInput
    output_model = SymbolsOutput
    name = 'hdl-symbols'
    version = '0.8.0'
    input_schema_name = 'HDLSymbolsInput'
    input_schema_version = '1.0.0'
    output_schema_name = 'HDLSymbolsOutput'
    output_schema_version = '1.0.0'
    description = 'List HDL design-unit declarations with library, owner and source location.'
    requirements = Requirements(tool='pip', format='requirements.txt', content='hdl-order[twylt]==0.8.0\n')
    few_shots = [{'input': {'root': 'examples/twylt-empty'}, 'output': {'symbols': []}}]

    def biz(self, data):
        with Workspace(self.name):
            return SymbolsOutput.model_validate(execute(data))
TOOL = HDLTool
if __name__ == '__main__':
    HDLTool.run()
