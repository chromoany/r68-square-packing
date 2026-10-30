"""Read-only exact verification of a supplied 68-square packing.

Python standard library only. This program generates no layouts, invokes no
optimizer, and needs no historical job directory or previous packing.

Usage:
  python verify-upper.py best-68-exact-state.json --radius best-68-exact-radius.json
  python verify-upper.py --self-test

PASS requires every one of the 2,278 pairs and all 272 corners to pass. No
floating-point number, geometric tolerance, or source-reported PASS is used.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational(value, label):
    require(type(value) is str, label + ' must be a rational string')
    # An unreduced fraction is still exact: the published safe upper endpoint
    # deliberately retains denominator 10^15. Fraction normalizes it internally.
    return Q(value)


def pair(value, label):
    require(type(value) is list and len(value) == 2, label + ' needs two coordinates')
    return tuple(rational(v, label) for v in value)


def dot(a, b):
    return a[0]*b[0]+a[1]*b[1]


def determinant(a, b):
    return a[0]*b[1]-a[1]*b[0]


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False)+'\n').encode('ascii')


def verify_layout(state, expected_count=68):
    require(type(state) is dict, 'state must be an object')
    poses = state.get('poses')
    require(type(poses) is list and len(poses) == expected_count,
            'unexpected number of squares')
    upper = rational(state['radius_upper'], 'radius_upper')
    require(upper > 0, 'radius must be positive')
    centers,axes = [],[]
    farthest = Q(-1)
    farthest_ids = []
    corner_count = 0
    for i,row in enumerate(poses,1):
        require(type(row) is dict and type(row.get('id')) is int and row['id']==i,
                'square IDs must be 1,...,n')
        c = pair(row['center'], 'center')
        u = pair(row['axis'], 'axis')
        require(dot(u,u)==1, 'axis is not an exact unit vector at square '+str(i))
        v = (-u[1],u[0])
        centers.append(c)
        axes.append((u,v))
        for e,h in ((-1,-1),(1,-1),(1,1),(-1,1)):
            vertex = (c[0]+(e*u[0]+h*v[0])/2,
                      c[1]+(e*u[1]+h*v[1])/2)
            norm2 = dot(vertex,vertex)
            require(norm2 <= upper*upper,
                    'corner is outside supplied disk: '+str((i,e,h)))
            if norm2 > farthest:
                farthest,farthest_ids = norm2,[[i,e,h]]
            elif norm2 == farthest:
                farthest_ids.append([i,e,h])
            corner_count += 1

    pairs = 0
    first_separating_axis_counts = [0,0,0,0]
    minimum_selected_gap = None
    for i in range(expected_count):
        for j in range(i+1,expected_count):
            delta = (centers[i][0]-centers[j][0],
                     centers[i][1]-centers[j][1])
            # For any of the four side-normal axes of two unit squares, the
            # sum of their projected half-widths equals this exact number.
            cosine = dot(axes[i][0],axes[j][0])
            sine = determinant(axes[i][0],axes[j][0])
            half_width_sum = (1+abs(cosine)+abs(sine))/2
            found = False
            for k,n in enumerate(axes[i]+axes[j]):
                gap = abs(dot(delta,n))-half_width_sum
                if gap >= 0:
                    first_separating_axis_counts[k] += 1
                    if minimum_selected_gap is None or gap < minimum_selected_gap:
                        minimum_selected_gap = gap
                    found = True
                    break
            require(found, 'interiors overlap for square pair '+str((i+1,j+1)))
            pairs += 1
    require(pairs == expected_count*(expected_count-1)//2, 'pair coverage')
    require(corner_count == 4*expected_count, 'corner coverage')

    if 'geometry_id' in state:
        geometry = {'schema':'T431_GEOMETRY_ID_V1','unit_side':'1',
                    'boundary':'CLOSED_CONTAINER_INTERIOR_DISJOINT_SQUARES',
                    'poses':poses}
        require(state['geometry_id']==hashlib.sha256(canonical(geometry)).hexdigest(),
                'geometry identity does not match supplied coordinates')
    return {
        'square_count':expected_count,
        'pairs_checked':pairs,
        'corners_checked':corner_count,
        'all_unit_axes_exact':True,
        'all_pairs_interior_disjoint':True,
        'all_corners_in_supplied_disk':True,
        'first_separating_axis_counts':first_separating_axis_counts,
        'minimum_selected_gap_is_zero':minimum_selected_gap==0,
        'maximum_corner_radius_squared':farthest,
        'maximising_corners':farthest_ids,
        'supplied_radius_upper':upper,
    }


def verify_radius(result, document, state_raw):
    require(document['source_state']['sha256']==hashlib.sha256(state_raw).hexdigest(),
            'radius file is not bound to the supplied state')
    p,q = int(document['squared_radius_numerator']),int(document['squared_radius_denominator'])
    require(p>0 and q>0 and math.gcd(p,q)==1, 'p,q must be coprime positive integers')
    require(Q(p,q)==result['maximum_corner_radius_squared'], 'incorrect exact squared radius')
    interval = document['radius_interval']
    lower,upper = rational(interval['lower'],'lower'),rational(interval['upper'],'upper')
    require(0<lower<upper and lower*lower<Q(p,q)<upper*upper, 'strict isolating interval failed')
    safe = rational(document['safe_rational_upper'],'safe upper')
    require(safe>0 and Q(p,q)<safe*safe, 'safe strict rational upper failed')
    recorded = [[r['square_id'],r['epsilon'],r['eta']] for r in document['maximising_corners']]
    require(recorded==result['maximising_corners'], 'incorrect maximizing corner list')
    return {'radius_equation':'q R^2 - p = 0, R > 0',
            'p_digits':len(str(p)), 'q_digits':len(str(q)),
            'p_q_coprime':True,
            'strict_isolating_interval':[str(lower),str(upper)],
            'interval_width':str(upper-lower),
            'safe_rational_upper':str(safe),
            'radius_is_for_fixed_origin_only':True,
            'global_optimality_claimed':False}


def make_square(i,x,y,u=('1','0')):
    return {'id':i,'center':[str(Q(x)),str(Q(y))],'axis':list(u)}


def self_test():
    # Independent elementary witnesses: tangency and positive separation.
    for x in ('1','3/2'):
        data={'radius_upper':'4','poses':[make_square(1,0,0),make_square(2,x,0)]}
        require(verify_layout(data,2)['pairs_checked']==1,'tangent/gap control')
    # A rational rotation, checked against an explicitly distant square.
    data={'radius_upper':'4','poses':[make_square(1,0,0,('3/5','4/5')),make_square(2,2,0)]}
    verify_layout(data,2)
    # Separators supplied only by the second square's u- or v-axis.
    for x,y,k in (('39/50','26/25',2),('-26/25','39/50',3)):
        data={'radius_upper':'4','poses':[make_square(1,0,0),make_square(2,x,y,('3/5','4/5'))]}
        result=verify_layout(data,2)
        require(result['first_separating_axis_counts'][k]==1,'second-owner axis control')
    rejected=0
    for data in (
        {'radius_upper':'4','poses':[make_square(1,0,0),make_square(2,'9/10',0)]},
        {'radius_upper':'4','poses':[make_square(1,0,0),make_square(2,'357/500','119/125',('3/5','4/5'))]},
        {'radius_upper':'1/2','poses':[make_square(1,0,0)]},
        {'radius_upper':'4','poses':[make_square(1,0,0,('1','1'))]},
    ):
        try:
            verify_layout(data,len(data['poses']))
        except ValueError:
            rejected+=1
    require(rejected==4,'all invalid controls must fail')
    return {'status':'PASS_SMALL_CONTROLS','valid_controls':5,'invalid_controls_rejected':4,
            'actual_68_square_packing_replayed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state',nargs='?',type=Path)
    parser.add_argument('--radius',type=Path)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    start=time.monotonic()
    if args.self_test:
        require(args.state is None and args.radius is None,'self-test takes no data')
        output=self_test()
    else:
        require(args.state is not None,'supply a state JSON file')
        raw=args.state.read_bytes()
        output=verify_layout(json.loads(raw),68)
        if args.radius is not None:
            output['exact_radius_certificate']=verify_radius(output,json.loads(args.radius.read_bytes()),raw)
        output['maximum_corner_radius_squared']=str(output['maximum_corner_radius_squared'])
        output['supplied_radius_upper']=str(output['supplied_radius_upper'])
        output['source_state_sha256']=hashlib.sha256(raw).hexdigest()
        output['status']='PASS_EXACT_68_SQUARE_UPPER_BOUND'
        output['arithmetic']='Python standard-library Fraction; exact rational comparisons'
        output['global_optimality_claimed']=False
    output['seconds']=time.monotonic()-start
    print(json.dumps(output,indent=2))


if __name__=='__main__':
    try:
        main()
    except (ValueError,KeyError,TypeError,OSError,ZeroDivisionError) as error:
        print(json.dumps({'status':'FAIL','error':str(error)}),file=sys.stderr)
        sys.exit(1)
