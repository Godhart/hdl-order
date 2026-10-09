from __future__ import annotations
from pathlib import Path
import sys
from twylt import Tool, Requirements
from twylt.guardrails import Workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'shared'))
from hdl_common.models import AnalysisInput, Model, Unit
from hdl_common.analysis import resolved_input, analyze_input, units

class MapOutput(Model):
    units: list[Unit]

def execute(data):
    data = resolved_input(data)
    r = analyze_input(data)
    return dict(units=units(r))

class HDLTool(Tool[AnalysisInput, MapOutput]):
    input_model = AnalysisInput
    output_model = MapOutput
    name = 'hdl-map'
    version = '0.8.0'
    input_schema_name = 'HDLMapInput'
    input_schema_version = '1.0.0'
    output_schema_name = 'HDLMapOutput'
    output_schema_version = '1.0.0'
    description = 'Map library-qualified HDL design units to source files.'
    requirements = Requirements(tool='pip', format='requirements.txt', content='hdl-order[twylt]==0.8.0\n')
    few_shots = [{'input': {'root': 'examples/twylt-empty'}, 'output': {'units': []}}]

    def biz(self, data):
        with Workspace(self.name):
            return MapOutput.model_validate(execute(data))
TOOL = HDLTool
if __name__ == '__main__':
    HDLTool.run()
