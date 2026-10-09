from pathlib import Path
from contextlib import redirect_stdout
import sys
from twylt.guardrails import workspace

def resolved_input(data):
    ws=workspace()
    paths=dict(root=str(ws.resolve(data.root)),
               config=str(ws.resolve(data.config)) if data.config else None,
               include_dirs=[str(ws.resolve(p)) for p in data.include_dirs]) if ws.enabled else dict(
                   root=data.root,config=data.config,include_dirs=data.include_dirs)
    # Check roots before calling the backend; this is cooperative validation, not OS isolation.
    for path in [paths['root'],*paths['include_dirs']]: ws.tree(Path(path))
    return data.model_copy(update=paths)

def analyze_input(data):
    from hdl_order.project import analyze
    root=Path(data.root)
    if not root.is_dir(): raise ValueError(f'Not a project directory: {root}')
    with redirect_stdout(sys.stderr):
        return analyze(root,Path(data.config) if data.config else None,
                       [Path(p) for p in data.include_dirs],data.defines,data.allow_missing_includes)

def units(result):
    from hdl_order.report import rel
    return [dict(id=u.label(),library=u.library,kind=u.kind,name=u.name,file=rel(result,p),line=n)
            for u,(p,n) in sorted(result.unit_map.items())]

def symbol(result,s):
    from hdl_order.report import rel
    return dict(library=s.library,kind=s.kind,name=s.name,owner=s.owner,file=rel(result,s.path),line=s.line)

def include(result,e):
    from hdl_order.report import rel
    return dict(dependent=rel(result,e.source),dependency=rel(result,e.target) if e.target else None,spelling=e.spelling,line=e.line)
