from __future__ import annotations
from typing import Any, Literal
from pydantic import Field
from pathlib import Path
import json, hdl_order
import sys
from twylt import Tool, Requirements
from twylt.guardrails import Workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'shared'))
from hdl_common.models import AnalysisInput, Model
from hdl_common.analysis import resolved_input, analyze_input

class ManifestInput(AnalysisInput):
    project_id: str = Field(..., min_length=1, description='Stable project identity in dependency-manifest scope.')
    analysis_profile: str = Field('default', min_length=1, description='Analysis profile, e.g. simulation or synthesis.')

class Producer(Model):
    name: str
    version: str
    analyzer: str

class Scope(Model):
    project: str
    profile: str
    area: str
    configuration: dict[str, Any]

class Source(Model):
    id: str
    revision: str | None = None

class FileNode(Model):
    id: str
    kind: Literal['file']
    source: str
    path: str
    content_hash: str

class SymbolNode(Model):
    id: str
    kind: Literal['symbol']
    name: str
    file: str
    attributes: dict[str, Any]
    line: int | None = None

class ExternalNode(Model):
    id: str
    kind: Literal['external']
    name: str
    uri: str | None = None

class Evidence(Model):
    file: str
    line: int | None = None
    precision: Literal['file', 'symbol', 'line']

class Edge(Model):
    dependent: str
    dependency: str
    relation: str
    evidence: Evidence | None = None
    note: str | None = None

class Coverage(Model):
    status: Literal['partial', 'complete']
    files: list[str]
    relation_types: list[str]
    limitations: list[str]

class Diagnostic(Model):
    severity: Literal['info', 'warning', 'error']
    code: str
    message: str

class Manifest(Model):
    format: Literal['dependency-manifest']
    version: Literal['1.0']
    producer: Producer
    scope: Scope
    sources: list[Source]
    nodes: list[FileNode | SymbolNode | ExternalNode]
    edges: list[Edge]
    coverage: Coverage
    diagnostics: list[Diagnostic]

class ManifestOutput(Model):
    manifest: dict[str, Any] = Field(..., json_schema_extra=json.loads(Path(hdl_order.__file__).with_name('manifest_output_schema.json').read_text(encoding='utf-8')), description='Unmodified dependency-manifest 1.0 object, ready for dependencies_import_prepare.manifest.')

def execute(data):
    data = resolved_input(data)
    from hdl_order.manifest import capture
    before = capture([Path(data.root), *(Path(p) for p in data.include_dirs)])
    r = analyze_input(data)
    from hdl_order.manifest import build_manifest
    manifest = build_manifest(r, data.project_id, data.analysis_profile, before)
    Manifest.model_validate(manifest)
    return dict(manifest=manifest)

class HDLTool(Tool[ManifestInput, ManifestOutput]):
    input_model = ManifestInput
    output_model = ManifestOutput
    name = 'hdl-manifest'
    version = '0.8.0'
    input_schema_name = 'HDLManifestInput'
    input_schema_version = '1.0.0'
    output_schema_name = 'HDLManifestOutput'
    output_schema_version = '1.0.0'
    description = 'Export dependency-manifest 1.0 as a JSON object for OKF import; coverage is partial.'
    requirements = Requirements(tool='pip', format='requirements.txt', content='hdl-order[twylt]==0.8.0\n')
    few_shots = [{'input': {'root': 'examples/twylt-empty', 'project_id': 'empty-demo'}, 'output': {'manifest': {'format': 'dependency-manifest', 'version': '1.0', 'producer': {'name': 'hdl-order', 'version': '0.8.0', 'analyzer': 'hdl-order-syntactic'}, 'scope': {'project': 'empty-demo', 'profile': 'default', 'area': 'hdl', 'configuration': {'defines': {}, 'include_roots': ['rtl'], 'include_search': [], 'explicit_dependencies': []}}, 'sources': [{'id': 'rtl', 'revision': '70c46c0a58230148f0e3bd9d45eec8ba1acc18de'}], 'nodes': [], 'edges': [], 'coverage': {'status': 'partial', 'files': [], 'relation_types': [], 'limitations': ['HDL symbol edges are syntactic observations, not the complete VUnit semantic graph.', 'Unresolved symbol references may be absent. Missing edges must not delete previous observations.']}, 'diagnostics': []}}}]

    def biz(self, data):
        with Workspace(self.name):
            return ManifestOutput.model_validate(execute(data))
TOOL = HDLTool
if __name__ == '__main__':
    HDLTool.run()
