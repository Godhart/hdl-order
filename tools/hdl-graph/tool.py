from __future__ import annotations
from typing import Literal
from pydantic import Field
from pathlib import Path
import sys
from twylt import Tool, Requirements
from twylt.guardrails import Workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'shared'))
from hdl_common.models import AnalysisInput, Model, Unit
from hdl_common.analysis import resolved_input, analyze_input, units
from hdl_order.report import rel

class GraphInput(AnalysisInput):
    render: Literal['text', 'dot'] | None = Field(None, description='Optional additional graph rendering.')

class UnitEdge(Model):
    dependent: str
    dependency: str
    relation: str
    file: str
    line: int

class GraphOutput(Model):
    nodes: list[Unit]
    edges: list[UnitEdge]
    completeness: Literal['partial'] = 'partial'
    rendered: str | None = None

def execute(data):
    data = resolved_input(data)
    r = analyze_input(data)
    from hdl_order.unitreport import graph_dot, graph_text
    rendered = None
    if data.render == 'dot':
        rendered = graph_dot(r)
    if data.render == 'text':
        rendered = graph_text(r)
    return dict(nodes=units(r), edges=[dict(dependent=e.source.label(), dependency=e.target.label(), relation=e.relation, file=rel(r, e.path), line=e.line) for e in r.unit_edges], rendered=rendered)

class HDLTool(Tool[GraphInput, GraphOutput]):
    input_model = GraphInput
    output_model = GraphOutput
    name = 'hdl-graph'
    version = '0.8.0'
    input_schema_name = 'HDLGraphInput'
    input_schema_version = '1.0.0'
    output_schema_name = 'HDLGraphOutput'
    output_schema_version = '1.0.0'
    description = 'Get the partial syntactic HDL design-unit graph using dependent/dependency roles.'
    requirements = Requirements(tool='pip', format='requirements.txt', content='hdl-order[twylt]==0.8.0\n')
    few_shots = [{'input': {'root': 'examples/twylt-empty'}, 'output': {'nodes': [], 'edges': [], 'completeness': 'partial', 'rendered': None}}]

    def biz(self, data):
        with Workspace(self.name):
            return GraphOutput.model_validate(execute(data))
TOOL = HDLTool
if __name__ == '__main__':
    HDLTool.run()
