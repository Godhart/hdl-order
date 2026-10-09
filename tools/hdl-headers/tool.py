from __future__ import annotations
from pathlib import Path
import sys
from twylt import Tool, Requirements
from twylt.guardrails import Workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'shared'))
from hdl_common.models import AnalysisInput, IncludeEdge, Model
from hdl_common.analysis import resolved_input, analyze_input, include
from hdl_order.report import rel

class Header(Model):
    file: str
    used_by: list[str]

class HeadersOutput(Model):
    headers: list[Header]
    unresolved: list[IncludeEdge]

def execute(data):
    data = resolved_input(data)
    r = analyze_input(data)
    return dict(headers=[dict(file=rel(r, h), used_by=[rel(r, r.root / x.path) for x in r.ordered if h in r.include_graph.transitive_headers((r.root / x.path).resolve())]) for h in sorted(r.include_graph.headers)], unresolved=[include(r, e) for e in r.include_graph.unresolved])

class HDLTool(Tool[AnalysisInput, HeadersOutput]):
    input_model = AnalysisInput
    output_model = HeadersOutput
    name = 'hdl-headers'
    version = '0.8.0'
    input_schema_name = 'HDLHeadersInput'
    input_schema_version = '1.0.0'
    output_schema_name = 'HDLHeadersOutput'
    output_schema_version = '1.0.0'
    description = 'List headers, their transitive users, and unresolved includes.'
    requirements = Requirements(tool='pip', format='requirements.txt', content='hdl-order[twylt]==0.8.0\n')
    few_shots = [{'input': {'root': 'examples/twylt-empty'}, 'output': {'headers': [], 'unresolved': []}}]

    def biz(self, data):
        with Workspace(self.name):
            return HeadersOutput.model_validate(execute(data))
TOOL = HDLTool
if __name__ == '__main__':
    HDLTool.run()
