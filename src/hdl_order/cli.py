import argparse,sys
from pathlib import Path
from .project import analyze
from .preprocessor import parse_cli_defines
from .formatters import FORMATTERS
from .report import *
from .unitreport import unit_map_text,unit_map_json,graph_text,graph_json,graph_dot
def parser():
    p=argparse.ArgumentParser(prog="hdl-order")
    p.add_argument("root",type=Path);p.add_argument("-f","--format",choices=FORMATTERS,default="plain")
    p.add_argument("-c","--config",type=Path);p.add_argument("-I","--include",action="append",default=[],type=Path)
    p.add_argument("-D","--define",action="append",default=[],metavar="NAME[=VALUE]")
    p.add_argument("--allow-missing-includes",action="store_true")
    g=p.add_mutually_exclusive_group()
    g.add_argument("--check",action="store_true");g.add_argument("--symbols",action="store_true");g.add_argument("--unit-map",action="store_true");g.add_argument("--unit-graph",action="store_true")
    p.add_argument("--graph-format",choices=("text","json","dot"),default="text");p.add_argument("--map-format",choices=("text","json"),default="text")
    g.add_argument("--deps",action="store_true");g.add_argument("--headers",action="store_true");g.add_argument("--explain")
    return p
def main():
    p=parser();a=p.parse_args()
    if not a.root.is_dir():p.error(f"not a directory: {a.root}")
    try:
        r=analyze(a.root,a.config,a.include,parse_cli_defines(a.define),a.allow_missing_includes)
        if a.check:
            out=check_report(r); code=1 if r.duplicates else 0
        elif a.symbols:out=symbols_report(r);code=0
        elif a.unit_map:out=unit_map_json(r) if a.map_format=="json" else unit_map_text(r);code=0
        elif a.unit_graph:out={"text":graph_text,"json":graph_json,"dot":graph_dot}[a.graph_format](r);code=0
        elif a.deps:out=deps_report(r);code=0
        elif a.headers:out=headers_report(r);code=0
        elif a.explain:out=explain(r,a.explain);code=0
        else:out=FORMATTERS[a.format](r);code=0
        print(out);return code
    except Exception as e:
        print("hdl-order: error:",e,file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
