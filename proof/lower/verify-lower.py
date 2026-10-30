"""Safely replay the frozen all-real-pose lower-bound certificate.

Normal mode runs the complete fixed verifier in a fresh temporary directory.
Only a fresh, complete result with all required identities/counts earns PASS.
--check-inputs performs small identity/rational/topology checks only, without
importing FLINT or replaying an integral. Do not use Python -O or -OO.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import subprocess
import sys
import tempfile

MANIFEST_NAME='proof-manifest.json'
MANIFEST_SHA256='d925b6766bfa02532cae4a5e9f67f4688118440ef42e042671279bc5577efbd4'
FROZEN_FILES={
    'radial_area_kernel.py','replay_lower_bound.py',
    'translation-gradient-cover-state.json','translation-gradient-independent-replay.json',
    'weights.json','weights.csv','cost-audit.json','requirements.txt',
}


def require(condition,message):
    if not condition:
        raise ValueError(message)


def read_packet(directory):
    raw=(directory/MANIFEST_NAME).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==MANIFEST_SHA256,'proof manifest identity mismatch')
    manifest=json.loads(raw)
    require(manifest.get('schema')=='R68_LOWER_FROZEN_PROOF_INPUTS_V2','proof manifest schema')
    require(set(manifest['files'])==FROZEN_FILES,'unexpected or missing proof payload')
    blobs={}
    for name,identity in manifest['files'].items():
        data=(directory/name).read_bytes()
        require(len(data)==identity['bytes'] and hashlib.sha256(data).hexdigest()==identity['sha256'],
                'frozen file identity mismatch: '+name)
        blobs[name]=data
    require(manifest['script']=='replay_lower_bound.py','unexpected replay source')
    require(manifest['kernel']=='radial_area_kernel.py','unexpected area kernel')
    require(manifest['state']=='translation-gradient-cover-state.json','unexpected state')
    require(manifest['historical_result']=='translation-gradient-independent-replay.json','unexpected result name')
    return manifest,blobs


def check_exact_data(manifest,blobs):
    expected=manifest['expected']
    state=json.loads(blobs[manifest['state']])
    require(state['target_radius']==expected['target_radius']=='39/8','target radius')
    require(state['side']==expected['side']=='40/39','side length')
    require(state['threshold']==expected['threshold']=='19926631/20000000','integral threshold')
    require(state['root_limit']==expected['root_limit']=='179/40','root box')
    require(state['frame']==expected['frame']=='fixed_axis_single_square_center_xy_first_octant_v1','frame')
    require(state['status']=='COMPLETE_TRANSLATION_GRADIENT_COVER','incomplete source cover')
    require(state['pending']==[] and state['strict_gaps']==[],'unclosed source leaves or gaps')
    leaves=state['accepted']+state['excluded']
    require(len(leaves)==11837 and len(leaves)==len(set(leaves)),'leaf count/uniqueness')
    require(all(type(p) is str and set(p)<=set('01') for p in leaves),'invalid binary path')
    order=sorted(leaves)
    require(all(not b.startswith(a) for a,b in zip(order,order[1:])),'overlapping prefixes')
    depth=max(map(len,leaves))
    require(sum(1<<(depth-len(p)) for p in leaves)==1<<depth,'incomplete prefix cover')
    E,G=state['accepted_eroded'],state['accepted_gradient']
    require(len(E)==1583 and len(G)==8923 and len(state['excluded'])==1331,'leaf classification counts')
    require(len(E)==len(set(E)) and len(G)==len(set(G)) and set(E).isdisjoint(G)
            and set(E)|set(G)==set(state['accepted']),'accepted-leaf partition')
    edges=list(map(Q,state['shell_edges']))
    weights=list(map(Q,state['shell_weights']))
    require(edges==[Q(j,16) for j in range(81)] and len(weights)==80 and min(weights)>=0,'shell data')
    coefficient=sum(w*(b*b-a*a) for w,a,b in zip(weights,edges,edges[1:]))
    require(coefficient==Q(345050690237,16000000000),'weighted area coefficient')
    cost=coefficient*Q(state['pi_upper'])
    require(cost==Q(state['cost_upper']),'exact disk cost product')
    require(cost<Q(338752725,5000000)<68*Q(state['threshold']),'strict rational cost chain')
    require(Q(40,39)*Q(39,8)==5,'scaling identity')
    require((Q(179,40)+Q(20,39))**2+Q(20,39)**2>25,'root containment')
    return state


def check_result(result,manifest,state,workers,budget):
    e=manifest['expected']
    require(result.get('status')==e['status']=='PASS_GLOBAL_REAL_R68_LOWER_GRADIENT','not a complete mathematical PASS')
    for key in ('verified_leaves','total_leaves'):
        require(type(result.get(key)) is int and result[key]==11837,'missing or incomplete '+key)
    for key,value in (('accepted_eroded_leaves',1583),('accepted_gradient_leaves',8923),('excluded_leaves',1331)):
        require(type(result.get(key)) is int and result[key]==value,'incorrect '+key)
    require(result.get('all_gradient_leaves_replayed') is True,'gradient coverage not complete')
    require(result.get('new_radius_lower_bound_claimed') is True,'no lower-bound result')
    require(result.get('exact_r68_claimed') is False,'unsupported exact-optimum claim')
    require(result.get('real_r68_strict_lower_bound')=='39/8','incorrect conclusion')
    require(result.get('target_radius')=='39/8' and result.get('side')=='40/39','incorrect problem instance')
    require(result.get('uniform_integral_lower')==state['threshold'],'incorrect integral lower endpoint')
    require(result.get('disk_cost_upper')==state['cost_upper'],'incorrect disk cost')
    require(result.get('source_state_sha256')==manifest['files'][manifest['state']]['sha256'],'wrong input state identity')
    require(type(result.get('workers')) is int and result['workers']==workers,'worker setting mismatch')
    require(type(result.get('proof_budget_seconds')) is int and result['proof_budget_seconds']==budget,'replay budget mismatch')
    seconds=result.get('seconds')
    require(type(seconds) in (int,float) and math.isfinite(seconds) and seconds>=0,'invalid elapsed time')


def run_fresh_replay(manifest,blobs,state,workers,budget,scratch_parent=None):
    version=importlib.metadata.version('python-flint')
    require(version==manifest['expected']['python_flint_version']=='0.8.0',
            'install the pinned dependency python-flint==0.8.0')
    base=Path(scratch_parent if scratch_parent is not None else tempfile.gettempdir()).resolve()
    require(base.is_dir(),'scratch parent must be an existing writable directory')
    with tempfile.TemporaryDirectory(prefix='r68-lower-replay-',dir=base) as temporary:
        scratch=Path(temporary)
        require(scratch.resolve().parent==base,'temporary directory escaped its parent')
        output=scratch/manifest['historical_result']
        # Crucial: NEVER seed the working directory with the historical PASS.
        # A successful process must create its own new result in this directory.
        for name,raw in blobs.items():
            if name!=manifest['historical_result']:
                (scratch/name).write_bytes(raw)
        require(not output.exists(),'result exists before new replay')
        command=[sys.executable,'-E','-B',str(scratch/manifest['script']),
                 '--workers',str(workers),'--budget',str(budget)]
        environment=os.environ.copy()
        environment.pop('PYTHONOPTIMIZE',None)
        process=subprocess.run(command,cwd=scratch,env=environment,
                               capture_output=True,text=True,encoding='utf8',errors='replace')
        require(process.returncode==0,'replay process did not exit successfully (code '+str(process.returncode)+')')
        require(output.is_file(),'replay did not create a fresh result')
        result=json.loads(output.read_bytes())
        check_result(result,manifest,state,workers,budget)
        for name,raw in blobs.items():
            if name!=manifest['historical_result']:
                require((scratch/name).read_bytes()==raw,'proof input changed during replay: '+name)
        result['fresh_full_replay']=True
        import flint
        result['environment']={'python':platform.python_version(),'python_implementation':platform.python_implementation(),'python_flint':version,'flint':flint.__FLINT_VERSION__,'system':platform.system(),'architecture':platform.machine(),'arb_precision_bits':256}
        result['replay_source_sha256']=manifest['files'][manifest['script']]['sha256']
        result['area_kernel_sha256']=manifest['files'][manifest['kernel']]['sha256']
        result['wrapper_checked_manifest_sha256']=MANIFEST_SHA256
        result['historical_result_used_as_fresh_output']=False
        return result


def main():
    require(__debug__ and sys.flags.optimize==0,'Python -O/-OO is forbidden: optimized execution is not an accepted certificate mode')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=16,
                        help='worker count accepted by the preserved verifier (1 through 32)')
    parser.add_argument('--budget',type=int,default=300,
                        help='per-invocation replay budget, in seconds (preserved verifier accepts 1 through 600)')
    parser.add_argument('--check-inputs',action='store_true',
                        help='check identities and exact data only; do not run integral verification')
    parser.add_argument('--scratch-parent',type=Path,
                        help='existing writable parent for a fresh temporary work directory')
    args=parser.parse_args()
    require(1<=args.workers<=32 and 1<=args.budget<=600,'settings outside the preserved verifier interface')
    manifest,blobs=read_packet(Path(__file__).resolve().parent)
    state=check_exact_data(manifest,blobs)
    historical=json.loads(blobs[manifest['historical_result']])
    check_result(historical,manifest,state,16,300)
    if args.check_inputs:
        result={'status':'INPUTS_CHECKED_NO_INTEGRAL_REPLAY','fresh_full_replay':False,
                'frozen_files_checked':len(blobs),'topological_leaf_count':11837,
                'historical_result_consistent':True,'pi_inequality_recomputed':False,
                'manifest_sha256':MANIFEST_SHA256}
    else:
        result=run_fresh_replay(manifest,blobs,state,args.workers,args.budget,args.scratch_parent)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'status':'FAIL_OR_INCOMPLETE','fresh_full_replay':False,
                          'error_type':type(error).__name__,'error':str(error)}),file=sys.stderr)
        sys.exit(1)
