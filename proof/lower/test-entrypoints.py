"""Regression controls for retired entry points and optimization-resistant checks.

The isolated leaf controls use test doubles, not numerical integration. A fresh
full certificate replay is a separate required release check.
"""
import ast
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
rows=[]

def require(condition,message):
    if not condition:raise RuntimeError(message)

for filename in ('verify-lower.py','replay_lower_bound.py'):
    for flag in ('-O','-OO'):
        result=subprocess.run([sys.executable,flag,'-B',str(HERE/filename),'--help'],capture_output=True,text=True)
        require(result.returncode!=0 and 'Python -O/-OO is forbidden' in result.stderr,'optimization guard failed: '+filename)
        rows.append({'control':filename+' '+flag,'rejected':True})
for filename in ('temp-verify-translation-gradient.py','radial_area_certificate_fast.py'):
    for flag in ('','-O','-OO'):
        result=subprocess.run([sys.executable]+([flag] if flag else [])+['-B',str(HERE/filename)],capture_output=True,text=True)
        require(result.returncode!=0 and 'Retired entry point' in result.stderr,'retired entry was executable')
        require('PASS' not in result.stdout and 'CERTIFIED' not in result.stdout,'retired entry printed success')
        rows.append({'control':filename+' '+(flag or 'normal'),'rejected':True})

source=ast.parse((HERE/'replay_lower_bound.py').read_text(encoding='utf-8'))
isolated=ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ('require','verify_chunk')],type_ignores=[])
class LowIntegral:
    def __ge__(self,other):return False
    def lower(self):return self
    def fmpq(self):return Fraction(0)

for optimization in (0,2):
    scope={'time':SimpleNamespace(monotonic=lambda:0),'DEADLINE':1,'SIDE':Fraction(1),'THRESHOLD':Fraction(1),
           'g':SimpleNamespace(ball=lambda x:x),'box':lambda path:(Fraction(0),)*4,
           'integral':lambda *args:LowIntegral(),'derivative':lambda *args:(Fraction(0),Fraction(0))}
    exec(compile(isolated,'isolated-certificate-leaf-control','exec',optimize=optimization),scope)
    for kind in ('excluded','accepted_eroded','accepted_gradient','unknown'):
        try:scope['verify_chunk']([(kind,'0')])
        except ValueError:rows.append({'control':kind+' invalid leaf optimize='+str(optimization),'rejected':True})
        else:raise RuntimeError('invalid leaf reached a successful count')
    scope['box']=lambda path:(Fraction(10),Fraction(10),Fraction(0),Fraction(0))
    require(scope['verify_chunk']([('excluded','0')])=={'verified':1,'incomplete':False},'valid exclusion positive control failed')
    scope['DEADLINE']=-1
    require(scope['verify_chunk']([('excluded','0')])=={'verified':0,'incomplete':True},'expired replay was counted as verified')
    rows.append({'control':'valid exclusion and deadline optimize='+str(optimization),'passed':True})

print(json.dumps({'status':'ENTRYPOINT_REGRESSION_CONTROLS_OK','controls':rows,'count':len(rows),
                  'integral_verifier_executed':False,'leaf_controls_use_test_doubles':True},indent=2))
