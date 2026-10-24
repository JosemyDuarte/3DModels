"""Tapered bed hook. Millimetres; broad face on XY for printing."""
from cadgen import build123d as bd
from cadgen import step, stl, srgb

TOP_GAP = 35.0
THROAT_GAP = 25.0
WIDTH = 10.0
WALL = 6.0
LEG_REACH = 90.0
BRIDGE_INNER_Y = 6.0
SHOULDER_Y = 12.0
THROAT_Y = 84.0
FLARE = 3.0
EDGE_RADIUS = 0.6

@step(out='../STEP/bed_hook.step')
@stl(out='../STL/bed_hook.stl', mesh_tolerance=0.0004)
def bed_hook():
    a, b = TOP_GAP / 2, THROAT_GAP / 2
    def line(p,q): return bd.Edge.make_line((*p,0),(*q,0))
    def arc(p,m,q): return bd.Edge.make_three_point_arc((*p,0),(*m,0),(*q,0))
    def bez(points): return bd.Edge.make_bezier(*[(*p,0) for p in points])
    def leg(sign, reach, offset):
        # Bezier control points give vertical tangency at shoulder and throat.
        def p(x,y): return (sign*(x+offset),y)
        end = BRIDGE_INNER_Y + reach - WALL/2
        flare_start = end - 9
        span = THROAT_Y - SHOULDER_Y
        edges = [bez([p(a,SHOULDER_Y),p(a,SHOULDER_Y+span/3),p(b,THROAT_Y-span/3),p(b,THROAT_Y)])]
        if flare_start > THROAT_Y:
            edges.append(line(p(b,THROAT_Y),p(b,flare_start)))
        edges.append(bez([p(b,flare_start),p(b,flare_start+5),p(b+FLARE,end-3),p(b+FLARE,end)]))
        return edges
    edges = []
    for radius, crown_y in [(a,6),(a+WALL,0)]:
        for sign in [-1,1]:
            edges.append(bez([(sign*radius,12),(sign*radius,crown_y),(sign*radius*0.55,crown_y),(0,crown_y)]))
    for sign, reach in [(-1,LEG_REACH),(1,LEG_REACH)]:
        edges += leg(sign,reach,0) + leg(sign,reach,WALL)
        y=BRIDGE_INNER_Y+reach-WALL/2
        x=sign*(b+FLARE)
        edges.append(arc((x,y),(x+sign*WALL/2,y+WALL/2),(x+sign*WALL,y)))
    body = bd.extrude(bd.Face(bd.Wire(edges)), amount=WIDTH, dir=(0,0,1))
    rims = [e for e in body.edges() if abs(e.center().Z) < 1e-5 or abs(e.center().Z-WIDTH) < 1e-5]
    body = bd.fillet(rims, EDGE_RADIUS)
    body.label = 'Tapered bed hook — 35 to 25 mm'
    body.color = srgb('#247F9C')
    return body

if __name__ == '__main__':
    bed_hook()
