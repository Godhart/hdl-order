from __future__ import annotations
from typing import Literal
from pydantic import Field
from pathlib import Path
import sys
from twylt import Tool, Requirements
from twylt.guardrails import Workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'shared'))
from hdl_common.models import AnalysisInput, IncludeEdge, Model
from hdl_common.analysis import resolved_input, analyze_input, include
from hdl_order.report import rel, explain

class DependenciesInput(AnalysisInput):
    file: str | None = Field(None, description='Optional project-relative file to explain. Omit for all includes and explicit dependencies.')

class ExplicitEdge(Model):
    dependent: str
    dependency: str
    reason: str | None = None

class DependenciesOutput(Model):
    includes: list[IncludeEdge]
    explicit: list[ExplicitEdge]
    completeness: Literal['include-and-explicit-only'] = 'include-and-explicit-only'
    explanation: str | None = None

def execute(data):
    data = resolved_input(data)
    r = analyze_input(data)
    focus = None
    if data.file:
        focus = (r.root / data.file).resolve()
        if not focus.is_relative_to(r.root) or not focus.is_file():
            raise ValueError('file must be an existing file inside the project root')
    includes = [include(r, e) for src, es in sorted(r.include_graph.edges.items()) for e in es if focus is None or src.resolve() == focus]
    explicit = [dict(dependent=rel(r, a), dependency=rel(r, b), reason=reason) for a, b, reason in r.explicit if focus is None or a.resolve() == focus]
    return dict(includes=includes, explicit=explicit, explanation=explain(r, data.file) if focus else None)

class HDLTool(Tool[DependenciesInput, DependenciesOutput]):
    input_model = DependenciesInput
    output_model = DependenciesOutput
    name = 'hdl-dependencies'
    version = '0.8.0'
    input_schema_name = 'HDLDependenciesInput'
    input_schema_version = '1.0.0'
    output_schema_name = 'HDLDependenciesOutput'
    output_schema_version = '1.0.0'
    description = 'List include and explicit file dependencies; optionally explain one project file.'
    requirements = Requirements(tool='pip', format='requirements.txt', content='hdl-order[twylt]==0.8.0\n')
    few_shots = [{'input': {'root': 'examples/twylt-empty'}, 'output': {'includes': [], 'explicit': [], 'completeness': 'include-and-explicit-only', 'explanation': None}}]

    def biz(self, data):
        with Workspace(self.name):
            return DependenciesOutput.model_validate(execute(data))
TOOL = HDLTool
if __name__ == '__main__':
    HDLTool.run()
