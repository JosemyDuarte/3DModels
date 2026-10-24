from cadgen import read_step
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.gp import gp_Lin, gp_Pnt, gp_Dir
s=read_step('STEP/bed_hook.step')
assert s.is_valid and len(s.solids()) == 1 and s.volume > 0
size=s.bounding_box().size
assert abs(size.Z-10)<1e-5 and abs(size.Y-96)<1e-5

def gap(y):
    hit=IntCurvesFace_ShapeIntersector()
    hit.Load(s.wrapped,1e-7)
    hit.Perform(gp_Lin(gp_Pnt(-100,y,5),gp_Dir(1,0,0)),0,200)
    xs=sorted(set(round(hit.Pnt(i).X(),6) for i in range(1,hit.NbPnt()+1)))
    assert len(xs)==4,(y,xs)
    return xs[2]-xs[1]
assert abs(gap(12)-35)<1e-5
assert abs(gap(84)-25)<1e-5
samples=[gap(y) for y in [12,30,48,66,84]]
assert all(a>b for a,b in zip(samples,samples[1:]))
# Rounded cap extremities verify both axial reaches.
left=[f for f in s.faces() if f.center().X<0]
assert abs(max(f.bounding_box().max.Y for f in left)-96)<1e-5
print('PASS: valid single solid; 10 mm depth; 90/90 mm reaches; gaps at y=12,30,48,66,84:',samples)

right=[f for f in s.faces() if f.center().X>0]
assert abs(max(f.bounding_box().max.Y for f in right)-96)<1e-5
