"""Continuous-pose certification of a nonnegative radial weighted-area bound.

Exact rational geometry determines every branch. Arb only encloses sqrt/atan2/pi.
Boundary-root uncertainty is integrated with an explicit absolute error bound.
For every parameter box, an eroded rational square lies in every actual square.
The complete binary leaf cover, not finite sampling, is the acceptance criterion.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from fractions import Fraction as PythonFraction
from pathlib import Path

if Path('temp-cert-deps').is_dir():sys.path.insert(0,str(Path('temp-cert-deps').resolve()))
from flint import arb,ctx,fmpq

def F(p=0,q=None):
    if q is not None:return fmpq(p,q)
    if isinstance(p,fmpq):return p
    if isinstance(p,str):
        if '/' in p:return fmpq(p)
        p=PythonFraction(p)
    if isinstance(p,PythonFraction):return fmpq(p.numerator,p.denominator)
    return fmpq(p)

ctx.prec=128
RHO_MAX=F(179,40)
T_MAX=F(5,12)


def ball(q):
    q=F(q)
    return arb(q)


def endpoint(x,upper=False):
    q=(x.upper() if upper else x.lower()).fmpq()
    return q


def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def det(a,b):return a[0]*b[1]-a[1]*b[0]
def point(a,d,t):return tuple(a[k]+t*d[k] for k in (0,1))


def norm_range(a,d,lo=F(0),hi=F(1)):
    dd=dot(d,d);ad=dot(a,d)
    t=max(lo,min(hi,-ad/dd))
    q=lambda t:dot(point(a,d,t),point(a,d,t))
    return q(t),max(q(lo),q(hi))


def edge_disk_area(a,b,r2):
    d=tuple(b[k]-a[k] for k in (0,1));cross=det(a,d)
    if not cross:return arb(0)
    aa,ad,dd=dot(a,a),dot(a,d),dot(d,d)
    qmin,qmax=norm_range(a,d)
    if qmax<=r2:return ball(cross/2)
    if qmin>=r2:return ball(r2/2)*arb.atan2(ball(cross),ball(dot(a,b)))
    disc=ad*ad-dd*(aa-r2)
    assert disc>0
    root=ball(disc).sqrt()
    cuts={F(0),F(1)}
    for sign in (-1,1):
        interval=(-ball(ad)+sign*root)/ball(dd)
        for upper in (False,True):cuts.add(max(F(0),min(F(1),endpoint(interval,upper))))
    cuts=sorted(cuts);total=arb(0)
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        if lo==hi:continue
        mn,mx=norm_range(a,d,lo,hi)
        if mx<=r2:total+=ball(cross*(hi-lo)/2)
        elif mn>=r2:
            x,y=point(a,d,lo),point(a,d,hi)
            total+=ball(r2/2)*arb.atan2(ball(det(x,y)),ball(dot(x,y)))
        else:
            # Green's edge integrand = cross/2 * min(1,r2/|p(t)|^2).
            # A tiny root-bracketing interval needs no topology decision.
            total+=arb(0,ball(abs(cross)*(hi-lo)/2).upper())
    return total


def polygon_disk_area(vertices,r2,side2):
    if r2==0:return arb(0)
    if max(dot(v,v) for v in vertices)<=r2:return ball(side2)
    if all(det(tuple(vertices[(k+1)%4][j]-vertices[k][j] for j in (0,1)),
               tuple(-vertices[k][j] for j in (0,1)))>=0 for k in range(4)):
        minimum=F(0)
    else:
        minimum=min(norm_range(vertices[k],tuple(vertices[(k+1)%4][j]-vertices[k][j] for j in (0,1)))[0] for k in range(4))
    if minimum>=r2:return arb(0)
    return sum((edge_disk_area(vertices[k],vertices[(k+1)%4],r2) for k in range(4)),arb(0))


def vertices(rho,t,side):
    u=((1-t*t)/(1+t*t),2*t/(1+t*t));v=(-u[1],u[0])
    return [tuple((rho if k==0 else F(0))+side/2*(a*u[k]+b*v[k]) for k in (0,1))
            for a,b in ((-1,-1),(1,-1),(1,1),(-1,1))]


def load_weights(path):
    raw=Path(path).read_bytes();data=json.loads(raw)
    edges=[F(str(x)) for x in data['shell_edges']]
    # Rationalize once; the exact weights define the certificate, not floats.
    weights=[F(round(x*10**8),10**8) for x in data['shell_weights']]
    assert edges[0]==0 and edges[-1]==5 and all(x>=0 for x in weights)
    assert len(edges)==len(weights)+1 and all(a<b for a,b in zip(edges,edges[1:]))
    terms=[]
    for j in range(1,len(edges)):
        change=weights[j-1]-(weights[j] if j<len(weights) else 0)
        if change:terms.append((edges[j]**2,change))
    cost_coefficient=sum(w*(b*b-a*a) for a,b,w in zip(edges,edges[1:],weights))
    return terms,cost_coefficient,hashlib.sha256(raw).hexdigest(),edges,weights


def weighted_square(rho,t,side,terms):
    vv=vertices(rho,t,side)
    return sum((ball(w)*polygon_disk_area(vv,r2,side*side) for r2,w in terms),arb(0))


def cvalue(t):return (1-t*t+2*t)/(1+t*t)


def box(path):
    rlo,rhi,tlo,thi=F(0),RHO_MAX,F(0),T_MAX
    for ch in path:
        assert ch in '01'
        if rhi-rlo>=thi-tlo:
            mid=(rlo+rhi)/2
            if ch=='0':rhi=mid
            else:rlo=mid
        else:
            mid=(tlo+thi)/2
            if ch=='0':thi=mid
            else:tlo=mid
    return rlo,rhi,tlo,thi


def assess(path,terms,threshold):
    rlo,rhi,tlo,thi=box(path)
    # c(t) has one interior maximum on [0,5/12], so endpoints bound its minimum.
    if rlo*rlo+rlo*min(cvalue(tlo),cvalue(thi))+F(1,2)>25:return 'excluded',None
    # |delta-delta_mid| <= thi-tlo since delta=2 atan(t).
    # cos(h)+sin(h)<=1+h; center translation <= (rhi-rlo)/2.
    side=(1-(rhi-rlo))/(1+(thi-tlo))
    if side<=0:return 'split',None
    value=weighted_square((rlo+rhi)/2,(tlo+thi)/2,side,terms)
    if value>=ball(threshold):return 'accepted',endpoint(value)
    return 'split',endpoint(value)


def selftest():
    # An exactly inscribed disk and exactly enclosed square, with rotations.
    for t in (F(0),F(1,5),F(2,5)):
        vv=vertices(F(0),t,F(1))
        a=polygon_disk_area(vv,F(1,4),F(1))
        assert a.contains(arb.pi()/4),(t,a)
        assert polygon_disk_area(vv,F(1),F(1)).contains(1)
    # A triangle fan whose edge passes through the origin must remain finite.
    vv=vertices(F(1,2),F(0),F(1))
    a=polygon_disk_area(vv,F(1,4),F(1))
    assert a.contains(arb.pi()/8)
    assert polygon_disk_area(vertices(F(3),F(1,5),F(1)),F(1),F(1)).contains(0)
    # Root intervals, positive and negative fan determinants, and tangent vertices.
    vv=vertices(F(1),F(1,3),F(1))
    for k in range(1,25):
        a=polygon_disk_area(vv,F(k,16),F(1))
        assert a.is_finite() and a.upper()>=0 and a.lower()<=1
    print('RATIONAL_GEOMETRY_ARB_AREA_SELFCHECK_PASS',flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--weights',type=Path,default=Path('temp-radial-area-80.json'))
    ap.add_argument('--state',type=Path,default=Path('radial-certificate-state.json'))
    ap.add_argument('--threshold',default='4971/5000')
    ap.add_argument('--max-boxes',type=int,default=2000)
    ap.add_argument('--budget',type=float,default=180)
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--selftest-only',action='store_true')
    args=ap.parse_args();selftest()
    if args.selftest_only:return
    terms,costcoef,digest,edges,weights=load_weights(args.weights)
    threshold=F(args.threshold);cost=ball(costcoef)*arb.pi()
    assert cost/ball(threshold)<72,'threshold cannot prove N<=71'
    if args.resume:
        state=json.loads(args.state.read_text())
        assert state['weight_source_sha256']==digest and state['threshold']==str(threshold)
        pending=state['pending'];accepted=state['accepted'];excluded=state['excluded']
    else:pending=[''];accepted=[];excluded=[]
    start=time.monotonic();processed=0;lowest=None
    while pending and processed<args.max_boxes and time.monotonic()-start<args.budget:
        path=pending.pop();kind,lo=assess(path,terms,threshold);processed+=1
        if kind=='accepted':
            accepted.append(path)
            lowest=lo if lowest is None else min(lowest,lo)
        elif kind=='excluded':excluded.append(path)
        else:pending.extend((path+'1',path+'0'))
        if processed%500==0:print('BOXES',processed,'ACCEPTED',len(accepted),'EXCLUDED',len(excluded),'PENDING',len(pending),'SECONDS',round(time.monotonic()-start,3),flush=True)
    state=dict(kernel_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),arithmetic='FLINT fmpq exact rational geometry + Arb enclosures',status='CERTIFIED_ALL_POSES' if not pending else 'PARTIAL_COVER_NO_GLOBAL_BOUND',
               weight_source_sha256=digest,threshold=str(threshold),precision_bits=ctx.prec,
               shell_edges=list(map(str,edges)),shell_weights=list(map(str,weights)),
               cost_upper=str(endpoint(cost,True)),bound_upper=str(endpoint(cost/ball(threshold),True)),
               accepted=accepted,excluded=excluded,pending=pending,
               last_run_boxes=processed,last_run_seconds=time.monotonic()-start,
               last_run_min_accepted_lower=None if lowest is None else str(lowest),
               global_quantity_upper_bound=71 if not pending else None,
               note='A complete leaf cover is required. Each leaf must be independently replayed; numerical samples are not proof.')
    args.state.write_text(json.dumps(state,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in state.items() if k not in ('accepted','excluded','pending','shell_edges','shell_weights')},indent=2),flush=True)


if __name__=='__main__':main()
