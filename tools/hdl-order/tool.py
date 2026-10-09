from __future__ import annotations
from typing import Literal
from pydantic import Field
from pathlib import Path
import sys
from twylt import Tool, Requirements
from twylt.guardrails import Workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'shared'))
from hdl_common.models import AnalysisInput, Model
from hdl_common.analysis import resolved_input, analyze_input
from hdl_order.report import rel

class OrderInput(AnalysisInput):
    render: Literal['plain', 'csv', 'modelsim'] | None = Field(None, description='Optional additional rendered compile-order text. No commands are executed.')

class CompilationUnit(Model):
    index: int
    library: str
    file: str
    type: str

class OrderOutput(Model):
    compile_order: list[CompilationUnit]
    defines: dict[str, str]
    headers: list[str]
    rendered: str | None = None

def execute(data):
    data = resolved_input(data)
    r = analyze_input(data)
    from hdl_order.formatters import FORMATTERS
    return dict(compile_order=[dict(index=x.index, library=x.library, file=x.path.as_posix(), type=x.file_type) for x in r.ordered], defines=r.defines, headers=[rel(r, h) for h in sorted(r.include_graph.headers)], rendered=FORMATTERS[data.render](r) if data.render else None)

class HDLTool(Tool[OrderInput, OrderOutput]):
    input_model = OrderInput
    output_model = OrderOutput
    name = 'hdl-order'
    version = '0.8.0'
    input_schema_name = 'HDLOrderInput'
    input_schema_version = '1.0.0'
    output_schema_name = 'HDLOrderOutput'
    output_schema_version = '1.0.0'
    description = 'Compute HDL compilation order across libraries; optionally render plain, CSV or ModelSim commands.'
    requirements = Requirements(tool='pip', format='requirements.txt', content='hdl-order[twylt]==0.8.0\n')
    few_shots = [{'input': {'root': 'examples/twylt-empty'}, 'output': {'compile_order': [], 'defines': {}, 'headers': [], 'rendered': None}}]

    def biz(self, data):
        with Workspace(self.name):
            return OrderOutput.model_validate(execute(data))
TOOL = HDLTool
if __name__ == '__main__':
    HDLTool.run()
