"""Small failure-path controls for verify-lower.py; no integral replay."""
from pathlib import Path
from unittest.mock import patch
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r68_lower_wrapper',HERE/'verify-lower.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def require(ok,message):
    if not ok:
        raise RuntimeError(message)

def rejection(name,call,rows):
    try:
        call()
    except ValueError as error:
        rows.append({'control':name,'rejected':True,'reason':str(error)})
    else:
        raise RuntimeError('invalid case was accepted: '+name)

manifest,blobs=module.read_packet(HERE)
state=module.check_exact_data(manifest,blobs)
saved=json.loads(blobs[manifest['historical_result']])
module.check_result(saved,manifest,state,16,300)
rows=[]

for field,value in (
    ('status','PARTIAL_GRADIENT_REPLAY_NO_BOUND'),
    ('verified_leaves',11836),('total_leaves',11836),
    ('all_gradient_leaves_replayed',False),
    ('new_radius_lower_bound_claimed',False),
    ('source_state_sha256','0'*64),('disk_cost_upper','0'),
    ('exact_r68_claimed',True),('workers',8),
):
    bad=copy.deepcopy(saved)
    bad[field]=value
    rejection('altered result field '+field,lambda b=bad:module.check_result(b,manifest,state,16,300),rows)

for filename in ('proof-manifest.json','radial_area_certificate_fast.py','translation-gradient-cover-state.json'):
    with tempfile.TemporaryDirectory(prefix='temp-r68-wrapper-control-',dir=Path.cwd()) as temporary:
        path=Path(temporary)
        require(path.resolve().parent==Path.cwd().resolve(),'control directory escaped its parent')
        shutil.copy2(HERE/'proof-manifest.json',path/'proof-manifest.json')
        for name,data in blobs.items():
            (path/name).write_bytes(data)
        (path/filename).write_bytes((path/filename).read_bytes()+b'\n')
        rejection('tampered '+filename,lambda:module.read_packet(path),rows)

def fake_core(mode):
    def run(command,**kwargs):
        scratch=Path(kwargs['cwd'])
        output=scratch/manifest['historical_result']
        require(not output.exists(),'historical result was copied into fresh scratch')
        if mode!='no-output':
            result=copy.deepcopy(saved)
            if mode=='partial':
                result['status']='PARTIAL_GRADIENT_REPLAY_NO_BOUND'
            output.write_text(json.dumps(result),encoding='utf8')
        if mode=='tampered-input':
            target=scratch/manifest['kernel']
            target.write_bytes(target.read_bytes()+b'\n')
        return subprocess.CompletedProcess(command,1 if mode=='nonzero-exit' else 0,stdout='',stderr='')
    return run

for mode in ('no-output','partial','nonzero-exit','tampered-input'):
    with patch.object(module.importlib.metadata,'version',return_value='0.8.0'):
        with patch.object(module.subprocess,'run',side_effect=fake_core(mode)):
            rejection('simulated core '+mode,lambda:module.run_fresh_replay(manifest,blobs,state,16,300,Path.cwd()),rows)

optimized=subprocess.run([sys.executable,'-O',str(HERE/'verify-lower.py'),'--check-inputs'],
                         capture_output=True,text=True,encoding='utf8')
require(optimized.returncode!=0 and 'Python -O/-OO is forbidden' in optimized.stderr,
        'optimized Python was not rejected')
rows.append({'control':'actual Python -O invocation','rejected':True})

print(json.dumps({'status':'SMALL_WRAPPER_CONTROLS_OK','controls_rejected':len(rows),
                  'frozen_input_preflight':True,'historical_result_gate_control':True,
                  'integral_verifier_executed':False,'fresh_full_replay':False,
                  'subprocess_core_controls_are_simulated':True,'controls':rows},indent=2))
