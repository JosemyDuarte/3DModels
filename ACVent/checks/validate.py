"""Check saved STEP geometry, interfaces, and binary STL topology."""
import json
import struct
from collections import defaultdict, deque
from math import cos, radians, tan
from pathlib import Path
from cadgen import read_step

ROOT=Path(__file__).resolve().parents[1]
parts={name:read_step(ROOT/'STEP'/f'deflector_{name}.step') for name in ('left','right')}
report={}
for name,part in parts.items():
    solids=part.solids()
    assert len(solids)==1, (name,len(solids))
    assert part.is_valid and solids[0].volume>0, name
    size=part.bounding_box().size
    report[name]={'solid_count':len(solids),'valid':part.is_valid,'volume_mm3':round(part.volume,3),'bounds_mm':[round(v,3) for v in size]}
left,right=parts['left'].solids()[0],parts['right'].solids()[0]
intersection=left.intersect(right)
overlap=0.0 if intersection is None else sum(s.volume for s in intersection.solids())
assert overlap<1e-6,overlap
assembly=read_step(ROOT/'STEP/vent_assembly.step')
assert assembly.is_valid and len(assembly.solids())==2
size=assembly.bounding_box().size
# User-facing finished dimensions, including every mounting and joint feature.
assert abs(size.X-225)<1e-6,size.X
assert abs(size.Y-175)<1e-6,size.Y
assert abs(size.Z-(65+2.7/cos(radians(10))))<1e-6,size.Z
separation=left.distance_to(right)
assert abs(separation-0.3)<1e-6,separation

def inside(solid,point):
    return solid.is_inside(point,tolerance=1e-7)

# Flat exterior ends and open magnetic mounting ledges.
for sign,solid in [(-1,left),(1,right)]:
    # A single broad end face lies at the outermost plane. A narrow rail
    # touching that plane is insufficient: the full end must be flat.
    end_x=sign*112.5
    end_faces=[f for f in solid.faces() if abs(f.bounding_box().min.X-end_x)<1e-6 and abs(f.bounding_box().max.X-end_x)<1e-6]
    assert len(end_faces)==1, ('outer end face count',len(end_faces))
    end=end_faces[0]
    assert end.geom_type.name=='PLANE'
    assert end.area>5000, end.area
    assert abs(end.bounding_box().size.Y-175)<1e-6
    assert abs(end.bounding_box().size.Z-(65+2.4/cos(radians(10))))<1e-6
    bounds=solid.bounding_box()
    assert abs((bounds.min.X if sign<0 else bounds.max.X)-end_x)<1e-6
    # Returned slot cap is gone; open regions remain above the flat ledge.
    for y in (55,120):
        assert not inside(solid,(sign*108,y,3.5))
    # Each blind bore has a 6.15 mm radius, 2.1 mm depth and solid floor.
    centres=[(sign*103.5,y) for y in (7.6,34.6,61.6,88.6,115.6,142.6)]
    centres += [(sign*x,-3.75) for x in (28.125,56.25,84.375)]
    for x,y in centres:
        for z in (0.1,1.0,2.0):
            assert not inside(solid,(x,y,z))
        assert inside(solid,(x,y,2.2))
        assert inside(solid,(x,y,3.3))
        assert not inside(solid,(x,y,3.5))
        assert inside(solid,(x,y+6.3,1.5))
        assert not inside(solid,(x,y+5.5,1.5))
    bores=[f for f in solid.faces() if f.geom_type.name=='CYLINDER' and abs(f.radius-6.15)<1e-6]
    assert len(bores)==9, ('magnet bore count',len(bores))
    for face in bores:
        assert abs(face.bounding_box().size.Z-2.1)<1e-6

# The side rims remain 15.5 mm; the rear rim is widened to 17.0 mm inward.
for sign,solid in [(-1,left),(1,right)]:
    for y in (45,100):
        assert inside(solid,(sign*(112.5-15.4),y,1.0))
        assert not inside(solid,(sign*(112.5-15.6),y,1.0))
    x=sign*10
    assert inside(solid,(x,-12.4+16.9,1.0))
    assert not inside(solid,(x,-12.4+17.1,1.0))

# The rear rim is internal: rear wall rises from the outer mounting edge,
# while the rim and horizontal magnet pads lie on its opening side.
for sign,solid in [(-1,left),(1,right)]:
    for x in (sign*10,sign*45,sign*100):
        for z in (0.5,5,10):
            assert inside(solid,(x,-12.3,z)), 'rear wall not flush to rim edge'
        assert not inside(solid,(x,-12.5,5)), 'external rear projection'
        assert not inside(solid,(x,-9.9,5)), 'rear wall too thick'
        assert inside(solid,(x,-5,1)), 'internal rear ledge missing'

# Open lap and rebate, sampled along the straight scoop section.
for y in (70,110,155):
    inner_z=65-(162.6-y)*tan(radians(10))
    def point(x,offset): return (x,y,inner_z+offset/cos(radians(10)))
    assert inside(left,point(4,2.0)), 'missing overlap'
    assert inside(right,point(4,0.6)), 'missing recessed edge'
    for solid in (left,right):
        assert not inside(solid,point(4,1.35)), 'missing lap clearance'
        assert not inside(solid,point(4,3.0)), 'returned lip remains'
    assert inside(right,point(9,2.0)), 'wall beyond rebate missing'
    assert not inside(left,point(8.15,2.0)), 'missing end clearance'
    assert not inside(right,point(8.15,2.0)), 'missing end clearance'
    # Gentle root ramp rises 0.3 mm over 0.6 mm of build height.
    for x in (-0.65,-0.45,-0.25):
        boundary=2.4+(x+0.75)*0.5
        assert inside(left,point(x,boundary-0.01))
        assert not inside(left,point(x,boundary+0.01))

# Direct normal approach: vent lies above the Z=0 magnetic contact face.
# No insertion or flexing through a returned holder is needed.
from cadgen import build123d as bd
vent=bd.Pos(-112.5,-12.4,-3)*bd.Box(225,175,3,align=(bd.Align.MIN,)*3)
for gap in (0,0.2,1,5,20):
    target=vent.moved(bd.Location((0,0,-gap)))
    for solid in (left,right):
        hit=solid.intersect(target)
        if isinstance(hit,bd.ShapeList): hit=bd.Compound(children=list(hit))
        assert hit is None or sum(s.volume for s in hit.solids())<1e-6,'normal approach collision'
# Pocket pads and the full mounting face must remain within the vent outline.
for solid in (left,right):
    bb=solid.bounding_box()
    assert bb.min.X>=-112.5-1e-6 and bb.max.X<=112.5+1e-6
    assert bb.min.Y>=-12.4-1e-6 and bb.max.Y<=162.6+1e-6
report['assembly']={'solid_count':2,'overlap_mm3':overlap,'bounds_mm':[round(v,3) for v in size], 'minimum_part_distance_mm':round(separation,3), 'flat_outer_end_faces_checked':True,'holder_slots_removed':True,'open_lap_rebate_checked':True,'root_ramp_degrees':26.565,'magnet_pockets':18,'pocket_diameter_mm':12.3,'pocket_depth_mm':2.1,'floor_mm':1.3,'vent_normal_approach_checked':True,'mounting_footprint_matches_vent':True,'mounting_rim_width_mm':15.5,'horizontal_rim_width_mm':17.0,'rear_rim_inside_scoop':True}

def check_stl(path):
    data=path.read_bytes()
    count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*count, 'unexpected STL encoding'
    edges=defaultdict(list)
    adjacency=defaultdict(set)
    volume=0.0
    vertices=[]
    for i in range(count):
        values=struct.unpack_from('<12fH',data,84+50*i)
        a,b,c=[tuple(values[j:j+3]) for j in (3,6,9)]
        assert len({a,b,c})==3, 'degenerate triangle'
        vertices.extend((a,b,c))
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for u,v in ((a,b),(b,c),(c,a)):
            edges[tuple(sorted((u,v)))].append((i,u,v))
    for uses in edges.values():
        assert len(uses)==2, 'open or non-manifold mesh edge'
        a,b=uses
        assert a[1]==b[2] and a[2]==b[1], 'inconsistent winding'
        adjacency[a[0]].add(b[0]); adjacency[b[0]].add(a[0])
    visited={0}; todo=deque([0])
    while todo:
        for other in adjacency[todo.popleft()]:
            if other not in visited:
                visited.add(other);todo.append(other)
    assert len(visited)==count, 'multiple disconnected mesh components'
    assert volume>0, 'inverted mesh'
    extents=[max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in range(3)]
    return {'triangles':count,'watertight':True,'consistent_winding':True,'components':1,'volume_mm3':round(volume,3),'bounds_mm':[round(v,3) for v in extents]}

for name in ('left','right'):
    report[name]['stl']=check_stl(ROOT/'STL'/f'deflector_{name}.stl')
    for actual,expected in zip(report[name]['stl']['bounds_mm'],report[name]['bounds_mm']):
        assert abs(actual-expected)<0.01
# Fit tests must remain literal cuts of the corresponding production geometry.
report['fit_tests']={}
for kind in ('first_layers','fit_frame'):
    total=0
    for name,solid in [('left',left),('right',right)]:
        stem=f'{kind}_{name}'
        sample=read_step(ROOT/'STEP'/f'{stem}.step')
        assert sample.is_valid and len(sample.solids())==1
        assert sample.volume>0
        bb=sample.bounding_box()
        if kind=='first_layers':
            start,end=(-112.5,-94.5) if name=='left' else (94.5,112.5)
            cut=bd.Pos(start,-20,-1)*bd.Box(end-start,200,80,align=(bd.Align.MIN,)*3)
            assert abs(bb.size.Z-18.0)<1e-6
            assert abs(bb.min.Z)<1e-6
            exact=solid.intersect(cut)
            if isinstance(exact,bd.ShapeList): exact=bd.Compound(children=list(exact))
            expected=exact.rotate(bd.Axis.Y,-90 if name=='left' else 90)
            low=expected.bounding_box().min
            expected=expected.moved(bd.Location((-low.X,-low.Y,-low.Z)))
        else:
            cut=bd.Pos(-120,-20,0)*bd.Box(240,200,5.6,align=(bd.Align.MIN,)*3)
            assert abs(bb.size.Z-5.6)<1e-6
            expected=solid.intersect(cut)
            if isinstance(expected,bd.ShapeList): expected=bd.Compound(children=list(expected))
            hit=sample.solids()[0].intersect(vent)
            assert hit is None or sum(s.volume for s in hit.solids())<1e-6
        for diff in (sample.cut(expected),expected.cut(sample)):
            if isinstance(diff,bd.ShapeList): diff=bd.Compound(children=list(diff))
            assert diff is None or sum(s.volume for s in diff.solids())<1e-5,stem
        total+=sample.volume
        report['fit_tests'][stem]={'valid':True,'exact_cut_of_full_model':True,'volume_mm3':round(sample.volume,3),'bounds_mm':[round(v,3) for v in bb.size], 'stl':check_stl(ROOT/'STL'/f'{stem}.stl')}
    report['fit_tests'][kind+'_material_fraction']=round(total/(left.volume+right.volume),3)
(ROOT/'previews/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
