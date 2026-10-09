from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from pathlib import Path
import json, hdl_order
class Model(BaseModel):
    model_config = ConfigDict(extra='forbid')

class AnalysisInput(Model):
    root: str = Field(..., min_length=1, description='HDL project directory; each immediate subdirectory is a library. Relative to process cwd.')
    config: str | None = Field(None, description='Optional TOML file with explicit dependencies; relative to process cwd.')
    include_dirs: list[str] = Field(default_factory=list, description='Ordered additional include directories; relative to process cwd.')
    defines: dict[str, str] = Field(default_factory=dict, description="Preprocessor definitions, for example {SIM: '1'}.")
    allow_missing_includes: bool = Field(False, description='Report unresolved includes instead of aborting.')

class Symbol(Model):
    library: str
    kind: str
    name: str
    owner: str | None = None
    file: str
    line: int

class Unit(Model):
    id: str
    library: str
    kind: str
    name: str
    file: str
    line: int

class IncludeEdge(Model):
    dependent: str
    dependency: str | None
    spelling: str
    line: int
