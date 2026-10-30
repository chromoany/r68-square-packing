"""Exact geometry and Arb area enclosures used by the fixed certificate replay.

This module has no search, resume, or standalone certification entry point.
"""
from fractions import Fraction as PythonFraction
from flint import arb,ctx,fmpq

def require(condition, message):
    if not condition:
        raise ValueError(message)

ctx.prec=128

def F(p=0,q=None):
    if q is not None:return fmpq(p,q)
    if isinstance(p,fmpq):return p
    if isinstance(p,str):
        if '/' in p:return fmpq(p)
        p=PythonFraction(p)
    if isinstance(p,PythonFraction):return fmpq(p.numerator,p.denominator)
    return fmpq(p)


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
    require(disc>0, 'certificate condition failed at original line 58')
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


def selftest():
    # An exactly inscribed disk and exactly enclosed square, with rotations.
    for t in (F(0),F(1,5),F(2,5)):
        vv=vertices(F(0),t,F(1))
        a=polygon_disk_area(vv,F(1,4),F(1))
        require(a.contains(arb.pi()/4), (t,a))
        require(polygon_disk_area(vv,F(1),F(1)).contains(1), 'certificate condition failed at original line 103')
    # A triangle fan whose edge passes through the origin must remain finite.
    vv=vertices(F(1,2),F(0),F(1))
    a=polygon_disk_area(vv,F(1,4),F(1))
    require(a.contains(arb.pi()/8), 'certificate condition failed at original line 107')
    require(polygon_disk_area(vertices(F(3),F(1,5),F(1)),F(1),F(1)).contains(0), 'certificate condition failed at original line 108')
    # Root intervals, positive and negative fan determinants, and tangent vertices.
    vv=vertices(F(1),F(1,3),F(1))
    for k in range(1,25):
        a=polygon_disk_area(vv,F(k,16),F(1))
        require(a.is_finite() and a.upper()>=0 and a.lower()<=1, 'certificate condition failed at original line 113')
    print('RATIONAL_GEOMETRY_ARB_AREA_SELFCHECK_PASS',flush=True)


if __name__=='__main__':
    raise SystemExit('Library module only. Run verify-lower.py for full certificate verification.')
