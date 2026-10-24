"""Measure exported joint facets in the intended flat-end build orientation."""
import json
import math
import struct
from pathlib import Path

root=Path(__file__).resolve().parents[1]
report={}
for side,direction in [('left',1),('right',-1)]:
    data=(root/'STL'/f'deflector_{side}.stl').read_bytes()
    worst=0.0
    bad_area=0.0
    measured=0
    for i in range(struct.unpack_from('<I',data,80)[0]):
        values=struct.unpack_from('<12fH',data,84+50*i)
        a,b,c=[values[j:j+3] for j in (3,6,9)]
        # Joint-local window includes ramp, lap, rebate and its shoulder.
        if not all(-1.01<p[0]<10 for p in (a,b,c)):
            continue
        u=[b[j]-a[j] for j in range(3)]
        v=[c[j]-a[j] for j in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.sqrt(sum(n*n for n in normal))
        assert length>1e-12
        measured+=1
        down=-direction*normal[0]/length
        if down>1e-6:
            angle=math.degrees(math.asin(min(1,down)))
            worst=max(worst,angle)
            if angle>45.1:
                bad_area+=length/2
    assert measured>0
    assert bad_area<1e-6,(side,bad_area)
    report[side]={'build_direction':'+X' if direction==1 else '-X',
                  'joint_facets_checked':measured,
                  'max_overhang_from_vertical_deg':round(worst,4),
                  'area_above_45_1_deg_mm2':bad_area}
report['scope']='Joint facets only; no slicing or physical print validation.'
(root/'previews/joint_printability.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
