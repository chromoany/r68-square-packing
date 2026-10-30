"""Independent rational-box, segment-intersection and Green proof replay."""
import sys
if not __debug__ or sys.flags.optimize:
    raise RuntimeError('Python -O/-OO is forbidden for certificate replay')

def require(condition, message):
    if not condition:
        raise ValueError(message)

import argparse
import hashlib
import json
import time
from concurrent.futures import ProcessPoolExecutor,as_completed
from fractions import Fraction as Q
from pathlib import Path
from flint import arb,ctx
import radial_area_kernel as g

def check(paths):
    if not paths or len(paths)!=len(set(paths)) or any(set(p)-set('01') or len(p)>100 for p in paths):raise ValueError('invalid leaves')
    ordered=sorted(paths)
    if any(b.startswith(a) for a,b in zip(ordered,ordered[1:])):raise ValueError('prefix overlap')
    d=max(map(len,paths))
    if sum(1<<(d-len(p)) for p in paths)!=1<<d:raise ValueError('incomplete partition')
    return len(paths)

def box(path):
    a,b,c,d=g.F(0),g.F(179,40),g.F(0),g.F(179,40)
    for char in path:
        if b-a>=d-c:
            mid=(a+b)/2
            if char=='0':b=mid
            else:a=mid
        else:
            mid=(c+d)/2
            if char=='0':d=mid
            else:c=mid
    return a,b,c,d

def line_point(edge,center,side,r2):
    """Bound the actual interval intersection; no generator min-of-three."""
    require(center>=0 and side>0, 'certificate condition failed at original line 35');h2=r2-edge*edge
    if h2<=0:return g.F(0),g.F(0)
    low,high=center-side/2,center+side/2
    if h2>=high*high:return side,side
    if low>=0 and h2<=low*low:return g.F(0),g.F(0)
    root=g.ball(h2).sqrt()
    def intersection(height):return max(g.F(0),min(high,height)-max(low,-height))
    return intersection(root.lower().fmpq()),intersection(root.upper().fmpq())

def line_range(elo,ehi,clo,chi,side,r2):
    require(elo<=ehi and 0<=clo<=chi, 'certificate condition failed at original line 45')
    near=g.F(0) if elo<=0<=ehi else min(abs(elo),abs(ehi));far=max(abs(elo),abs(ehi))
    return line_point(far,chi,side,r2)[0],line_point(near,clo,side,r2)[1]

def derivative(a,b,c,d,axis):
    if axis:a,b,c,d=c,d,a,b
    lo,hi=g.F(0),g.F(0)
    for r2,weight in TERMS:
        a0,a1=line_range(a+SIDE/2,b+SIDE/2,c,d,SIDE,r2);b0,b1=line_range(a-SIDE/2,b-SIDE/2,c,d,SIDE,r2)
        if weight>=0:lo+=weight*(a0-b1);hi+=weight*(a1-b0)
        else:lo+=weight*(a1-b0);hi+=weight*(a0-b1)
    require(lo<=hi, 'certificate condition failed at original line 56');return lo,hi

def integral(x,y,width,height):
    vertices=[(x+s*width/2,y+t*height/2) for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return sum((g.ball(weight)*g.polygon_disk_area(vertices,r2,width*height) for r2,weight in TERMS),arb(0))

def initialize(state,deadline):
    global TERMS,SIDE,THRESHOLD,DEADLINE
    ctx.prec=256;SIDE=g.F(state['side']);THRESHOLD=g.F(state['threshold']);DEADLINE=deadline
    edges=list(map(g.F,state['shell_edges']));w=list(map(g.F,state['shell_weights']));TERMS=[(edges[j]*edges[j],w[j-1]-(w[j] if j<80 else 0)) for j in range(1,81) if w[j-1]!=(w[j] if j<80 else 0)]

def verify_chunk(rows):
    done=0
    for kind,path in rows:
        if time.monotonic()>DEADLINE:return dict(verified=done,incomplete=True)
        a,b,c,d=box(path);require(0<=a<=b and 0<=c<=d, 'certificate condition failed at original line 71')
        if kind=='excluded':require(b<c or (a+SIDE/2)**2+(c+SIDE/2)**2>25, ('bad exclusion',path))
        elif kind=='accepted_eroded':
            width,height=SIDE-(b-a),SIDE-(d-c);require(min(width,height)>0, 'certificate condition failed at original line 74')
            require(integral((a+b)/2,(c+d)/2,width,height)>=g.ball(THRESHOLD), ('eroded Green failed',path))
        else:
            require(kind=='accepted_gradient', 'certificate condition failed at original line 77');mid=integral((a+b)/2,(c+d)/2,SIDE,SIDE).lower().fmpq();gx=derivative(a,b,c,d,0);gy=derivative(a,b,c,d,1)
            bound=mid-max(abs(x) for x in gx)*(b-a)/2-max(abs(x) for x in gy)*(d-c)/2
            require(bound>=THRESHOLD, ('independent gradient bound failed',path,str(bound)))
        done+=1
    return dict(verified=done,incomplete=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=8);parser.add_argument('--budget',type=int,default=200);args=parser.parse_args();require(1<=args.workers<=32 and 1<=args.budget<=600, 'certificate condition failed at original line 84')
    clock=time.monotonic();ctx.prec=256;raw=Path('translation-gradient-cover-state.json').read_bytes();state=json.loads(raw)
    total=check(state['accepted']+state['excluded']+state['pending']);E=state['accepted_eroded'];G=state['accepted_gradient'];require(len(E)+len(G)==len(state['accepted']) and set(E).isdisjoint(G) and set(E)|set(G)==set(state['accepted']), 'certificate condition failed at original line 86')
    require(state['target_radius']=='39/8' and state['side']=='40/39' and state['root_limit']=='179/40' and state['frame']=='fixed_axis_single_square_center_xy_first_octant_v1', 'certificate condition failed at original line 87')
    side=g.F(40,39);threshold=g.F(state['threshold']);require(side*g.F(39,8)==5 and (g.F(179,40)+side/2)**2+(side/2)**2>25, 'certificate condition failed at original line 88')
    edges=list(map(g.F,state['shell_edges']));w=list(map(g.F,state['shell_weights']));require(len(w)==80 and len(edges)==81 and edges[0]==0 and edges[-1]==5 and min(w)>=0 and all(a<b for a,b in zip(edges,edges[1:])), 'certificate condition failed at original line 89')
    coefficient=sum(a*(b*b-c*c) for a,b,c in zip(w,edges[1:],edges));pi_upper=g.F(state['pi_upper']);require(arb.pi()<g.ball(pi_upper), 'certificate condition failed at original line 90');cost=coefficient*pi_upper;require(cost==g.F(state['cost_upper']) and cost<68*threshold and 0<threshold<=1, 'certificate condition failed at original line 90')
    initialize(state,time.monotonic()+args.budget);common=dict(target_radius='39/8',side='40/39',source_state_sha256=hashlib.sha256(raw).hexdigest(),exact_r68_claimed=False)
    if state['strict_gaps']:
        reports=[];cost_lo=Q(str((g.ball(coefficient)*arb.pi()).lower().fmpq()))-Q(1,2**120)
        for row in state['strict_gaps']:
            x,y=g.F(row['x']),g.F(row['y']);require(row['side']=='40/39' and 0<=y<=x and (x+side/2)**2+(y+side/2)**2<=25, 'certificate condition failed at original line 95')
            a,b,c,d=box(row['path']);require(x==(a+b)/2 and y==(c+d)/2, 'certificate condition failed at original line 96')
            upper=Q(str(integral(x,y,side,side).upper().fmpq()));require(upper<Q(str(threshold)), 'certificate condition failed at original line 97');necessary=68*upper<cost_lo
            if row['fixed_weight_ratio_route_refuted']:require(necessary, 'certificate condition failed at original line 98')
            reports.append(dict(path=row['path'],x=str(x),y=str(y),independent_integral_upper=str(upper),fixed_weight_ratio_route_refuted=necessary))
        result=dict(status='PASS_INDEPENDENT_GRADIENT_SEARCH_GAPS',witnesses=reports,fixed_weight_ratio_route_refuted=any(r['fixed_weight_ratio_route_refuted'] for r in reports),
            all_ring_weight_choices_refuted=False,all_gradient_leaves_replayed=False,new_radius_lower_bound_claimed=False,**common)
    elif state['pending']:
        result=dict(status='VALID_PARTIAL_GRADIENT_TOPOLOGY_NO_BOUND',total_leaves=total,pending=len(state['pending']),new_radius_lower_bound_claimed=False,**common)
    else:
        require(state['status']=='COMPLETE_TRANSLATION_GRADIENT_COVER', 'certificate condition failed at original line 105');rows=[(kind,path) for kind in ['accepted_eroded','accepted_gradient','excluded'] for path in state[kind]];chunks=[rows[i:i+250] for i in range(0,len(rows),250)];done=0;incomplete=0
        with ProcessPoolExecutor(max_workers=args.workers,initializer=initialize,initargs=(state,time.monotonic()+args.budget)) as pool:
            futures=[pool.submit(verify_chunk,chunk) for chunk in chunks]
            for future in as_completed(futures):
                r=future.result();done+=r['verified'];incomplete+=r['incomplete'];Path('gradient-replay-progress.json').write_text(json.dumps(dict(verified=done,total=total,incomplete_chunks=incomplete))+'\n')
                if done%5000==0:print('INDEPENDENT_GRADIENT_REPLAY',done,'OF',total,flush=True)
        passed=done==total and not incomplete
        result=dict(status='PASS_GLOBAL_REAL_R68_LOWER_GRADIENT' if passed else 'PARTIAL_GRADIENT_REPLAY_NO_BOUND',verified_leaves=done,total_leaves=total,
            accepted_eroded_leaves=len(E),accepted_gradient_leaves=len(G),excluded_leaves=len(state['excluded']),all_gradient_leaves_replayed=passed,
            real_r68_strict_lower_bound='39/8' if passed else None,new_radius_lower_bound_claimed=passed,uniform_integral_lower=str(threshold),disk_cost_upper=str(cost),**common)
    result.update(arithmetic='Independent rational boxes, interval segment intersections, and Green/Arb256 midpoint integrals',workers=args.workers,proof_budget_seconds=args.budget,seconds=time.monotonic()-clock)
    Path('translation-gradient-independent-replay.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
