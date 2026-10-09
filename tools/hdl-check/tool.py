from __future__ import annotations
from pathlib import Path
import sys
from twylt import Tool, Requirements
from twylt.guardrails import Workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'shared'))
from hdl_common.models import AnalysisInput, Model, Symbol
from hdl_common.analysis import resolved_input, analyze_input, symbol

class CheckOutput(Model):
    ok: bool
    compilation_units: int
    design_units: int
    headers: int
    duplicates: list[list[Symbol]]
    unresolved_includes: int

def execute(data):
    data = resolved_input(data)
    r = analyze_input(data)
    return dict(ok=not r.duplicates and (not r.include_graph.unresolved), compilation_units=len(r.ordered), design_units=len(r.symbols), headers=len(r.include_graph.headers), duplicates=[[symbol(r, s) for s in group] for group in r.duplicates.values()], unresolved_includes=len(r.include_graph.unresolved))

class HDLTool(Tool[AnalysisInput, CheckOutput]):
    input_model = AnalysisInput
    output_model = CheckOutput
    name = 'hdl-check'
    version = '0.8.0'
    input_schema_name = 'HDLCheckInput'
    input_schema_version = '1.0.0'
    output_schema_name = 'HDLCheckOutput'
    output_schema_version = '1.0.0'
    description = 'Check HDL project: duplicate symbols and unresolved includes. Cycles and analysis failures are TWYLT business errors.'
    requirements = Requirements(tool='pip', format='requirements.txt', content='hdl-order[twylt]==0.8.0\n')
    few_shots = [{'input': {'root': 'examples/twylt-empty'}, 'output': {'ok': True, 'compilation_units': 0, 'design_units': 0, 'headers': 0, 'duplicates': [], 'unresolved_includes': 0}}]

    def biz(self, data):
        with Workspace(self.name):
            return CheckOutput.model_validate(execute(data))
TOOL = HDLTool
if __name__ == '__main__':
    HDLTool.run()
