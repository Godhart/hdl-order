import json,os,shutil,subprocess,sys
from pathlib import Path
import pytest
from toolpack_builder.builder import BuildConfig,scan,build_from_report
BASE=Path(__file__).resolve().parents[1]

def test_copied_pack_builder_nested_transport(tmp_path,monkeypatch):
    pack=tmp_path/'copied'
    shutil.copytree(BASE/'tools',pack/'tools',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(BASE/'shared',pack/'shared',ignore=shutil.ignore_patterns('__pycache__'))
    config=BuildConfig(root=pack/'tools',glob='*/tool.py',python=sys.executable)
    report=scan(config)
    assert len(report.valid)==8,report.failed
    payload=build_from_report(config,report).payload
    tools={t['name']:t for t in payload['category']['tools']}
    workspace=tmp_path/'workspace';workspace.mkdir()
    runs=tmp_path/'transport';cwd=runs/'request'/'nested';cwd.mkdir(parents=True)
    env={**os.environ,'TWYLT_GUARDRAILS':'1','TWYLT_WORKSPACE_ROOT':str(workspace),
         'TWYLT_ALLOWED_CWD':str(runs),'TWYLT_DISABLE_NETWORK':'0','TWYLT_INCIDENT_LOG':''}
    (workspace/'project').mkdir()
    (cwd/'input.json').write_text(json.dumps({'root':'/project'}))
    code=''+tools['hdl-order']['code']
    r=subprocess.run([sys.executable,'-c',code],cwd=cwd,env=env,stdin=subprocess.DEVNULL,
                     capture_output=True,text=True,timeout=20)
    assert r.returncode==0,r.stderr
    result=json.loads((cwd/'output.json').read_text())
    assert result['compile_order']==[]
    assert not (workspace/'output.json').exists()

@pytest.mark.parametrize('mode',['order','check','symbols','map','graph','dependencies','headers','manifest'])
def test_guarded_analysis_root_traversal(tmp_path,monkeypatch,mode):
    monkeypatch.setenv('TWYLT_GUARDRAILS','1')
    monkeypatch.setenv('TWYLT_WORKSPACE_ROOT',str(tmp_path))
    payload={'root':'../outside'}
    if mode=='manifest':payload['project_id']='test'
    r=subprocess.run([sys.executable,str(BASE/'tools'/('hdl-'+mode)/'run.py'),json.dumps(payload)],
                     capture_output=True,text=True,timeout=10)
    assert r.returncode==6,r.stderr
    assert json.loads(r.stderr.splitlines()[-1])['error']['code']=='path_outside_workspace'
