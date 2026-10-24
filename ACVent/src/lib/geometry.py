"""Two-piece curved vent deflector. All dimensions in millimetres."""
from math import sin, cos, tan, radians
from cadgen import build123d as bd, srgb

VENT_WIDTH = 225.0
VENT_DEPTH = 175.0
# Magnetic mount sits ON the vent face; its outside footprint must match the
# measured vent, rather than adding the old surround/slide-in allowance.
WALL = 2.4
DROP = 65.0
BEND_RADIUS = 25.0
RAMP_ANGLE = 10.0
LIP = 10.0  # fixed mounting-coordinate datum, now enclosed by the rear wall
MOUNT_RIM_WIDTH = 15.5  # side rims, inward from the edge
HORIZONTAL_RIM_WIDTH = 17.0  # room for the larger rear magnet pads
SEAM = 0.3
LAP_LENGTH = 8.0
LAP_THICKNESS = 1.2
LAP_CLEARANCE = 0.3
MAGNET_DIAMETER = 12.0
MAGNET_THICKNESS = 2.0
MAGNET_DIAMETRAL_CLEARANCE = 0.3
MAGNET_POCKET_DEPTH = MAGNET_THICKNESS + 0.1
MAGNET_FLOOR = 1.3
MAGNET_RADIAL_WALL = 2.0
MAGNET_X = VENT_WIDTH/2-9.0  # keep the wider reinforcement pads inside the outer edge
MAGNET_COUNT_PER_SIDE = 6
MAGNET_Y = tuple(20.0-WALL-LIP + i*(VENT_DEPTH-40.0)/(MAGNET_COUNT_PER_SIDE-1) for i in range(MAGNET_COUNT_PER_SIDE))
HORIZONTAL_MAGNET_X = (28.125, 56.25, 84.375)  # three evenly spaced per half
HORIZONTAL_MAGNET_Y = -3.75  # pocket edge clears the rear wall; pad fits the wider rim
REBATE_DEPTH = 1.2
LAP_INNER = WALL-REBATE_DEPTH+LAP_CLEARANCE
LAP_OUTER = LAP_INNER+LAP_THICKNESS
LAP_RAMP_RUN = 0.6  # 0.3 mm rise over 0.6 mm: 26.565 degrees from build direction
OVERALL_WIDTH = VENT_WIDTH
OVERALL_DEPTH = VENT_DEPTH
HALF_OUTER = OVERALL_WIDTH/2
INSIDE_WIDTH = OVERALL_WIDTH-2*WALL
DEPTH = OVERALL_DEPTH-WALL-LIP
FIT_TEST_LAYERS_DEPTH = 18.0
FIT_FRAME_HEIGHT = 5.6


def profile(offset=0.0, thickness=WALL):
    """Constant-thickness circular transition into a sloping tangent ramp."""
    r, d = BEND_RADIUS, DEPTH+LIP
    angle = radians(90-RAMP_ANGLE)
    h = DROP-r*sin(angle)-(d-r*(1-cos(angle)))*tan(radians(RAMP_ANGLE))
    def p(y,z): return (0,y-LIP,z)
    ri, ro = r+offset, r+offset+thickness
    a=p(-offset,0); b=p(-offset,h)
    c=p(r-ri*cos(angle),h+ri*sin(angle)); d1=p(d,DROP+offset/cos(radians(RAMP_ANGLE)))
    e=p(d,DROP+(offset+thickness)/cos(radians(RAMP_ANGLE))); f=p(r-ro*cos(angle),h+ro*sin(angle))
    g=p(-offset-thickness,h); j=p(-offset-thickness,0)
    edges=[bd.Edge.make_line(a,b),
           bd.Edge.make_three_point_arc(b,p(r-ri*cos(angle/2),h+ri*sin(angle/2)),c),
           bd.Edge.make_line(c,d1),bd.Edge.make_line(d1,e),bd.Edge.make_line(e,f),
           bd.Edge.make_three_point_arc(f,p(r-ro*cos(angle/2),h+ro*sin(angle/2)),g),
           bd.Edge.make_line(g,j),bd.Edge.make_line(j,a)]
    return bd.Face(bd.Wire(edges))


def along_x(face, start, end):
    return bd.extrude(face, amount=end-start, dir=(1,0,0)).moved(bd.Location((start,0,0)))


def box(x0,x1,y0,y1,z0,z1):
    return bd.Pos(x0,y0,z0)*bd.Box(x1-x0,y1-y0,z1-z0,align=(bd.Align.MIN,)*3)


def end_wall():
    r,d=BEND_RADIUS,DEPTH+LIP
    angle=radians(90-RAMP_ANGLE)
    h=DROP-r*sin(angle)-(d-r*(1-cos(angle)))*tan(radians(RAMP_ANGLE))
    pts=[(0,0,0),(0,d,0),(0,d,DROP),(0,r-r*cos(angle),h+r*sin(angle))]
    edges=[bd.Edge.make_line(pts[i],pts[i+1]) for i in range(3)]
    edges += [bd.Edge.make_three_point_arc(pts[-1],(0,r-r*cos(angle/2),h+r*sin(angle/2)),(0,0,h)),
              bd.Edge.make_line((0,0,h),pts[0])]
    return bd.Face(bd.Wire(edges)).moved(bd.Location((0,-LIP,0)))


def half(left):
    x0,x1=(-HALF_OUTER,-SEAM/2) if left else (SEAM/2,HALF_OUTER)
    body=along_x(profile(),x0,x1)
    a,b=(-HALF_OUTER,-INSIDE_WIDTH/2) if left else (INSIDE_WIDTH/2,HALF_OUTER)
    body=body.fuse(along_x(end_wall(),a,b))
    # Mounting ledges return inward. The complete outer end wall is the
    # extreme X plane, with no flange or rail projecting beyond its flat face.
    a,b=(-HALF_OUTER,-HALF_OUTER+MOUNT_RIM_WIDTH) if left else (HALF_OUTER-MOUNT_RIM_WIDTH,HALF_OUTER)
    body=body.fuse(box(a,b,-WALL-LIP,DEPTH,0,WALL))
    a,b=(-HALF_OUTER,-SEAM/2) if left else (SEAM/2,HALF_OUTER)
    body=body.fuse(box(a,b,-WALL-LIP,-WALL-LIP+HORIZONTAL_RIM_WIDTH,0,WALL))
    if left:
        # Gradually build the overlap root in the +X print direction.
        ramp=bd.loft([
            profile().moved(bd.Location((-SEAM/2-LAP_RAMP_RUN,0,0))),
            profile(0,LAP_OUTER).moved(bd.Location((-SEAM/2,0,0)))
        ],ruled=True)
        body=body.fuse(ramp)
        tongue=along_x(profile(LAP_INNER,LAP_THICKNESS),-SEAM/2,LAP_LENGTH)
        # Keep the overlap clear of the opposing mounting rim.
        tongue=tongue.cut(box(-1,LAP_LENGTH+1,-WALL-LIP-LAP_OUTER,DEPTH+1,-1,WALL+LAP_CLEARANCE))
        body=body.fuse(tongue)
    else:
        # Open rebate: no returned lip and no enclosed support channel.
        rebate=along_x(profile(WALL-REBATE_DEPTH,REBATE_DEPTH+1),SEAM/2,LAP_LENGTH+LAP_CLEARANCE)
        rebate=rebate.cut(box(-1,LAP_LENGTH+1,-WALL-LIP-LAP_OUTER,DEPTH+1,-1,WALL))
        body=body.cut(rebate)
    # Keep the rear end of the external lap flush with the overall envelope.
    # The rear mounting rim now lies wholly inward of the scoop wall.
    body=single_cut(body,box(-HALF_OUTER-1,HALF_OUTER+1,-WALL-LIP,DEPTH+1,-1,DROP+10))
    # No returned holder lips: the vent meets the open mounting face at Z=0.
    # Blind pockets open toward the vent. Thickened inward pads retain a floor;
    # no feature projects beyond either flat outer end face.
    pocket_radius=(MAGNET_DIAMETER+MAGNET_DIAMETRAL_CLEARANCE)/2
    sign=-1 if left else 1
    centres=[(sign*MAGNET_X,y) for y in MAGNET_Y]
    centres += [(sign*x,HORIZONTAL_MAGNET_Y) for x in HORIZONTAL_MAGNET_X]
    for index,(x,y) in enumerate(centres):
        # Flat pad perimeter avoids sliver faces where a circular pad would
        # intersect the end wall; the magnet bore itself remains cylindrical.
        pad_radius=pocket_radius+MAGNET_RADIAL_WALL
        pad=box(x-pad_radius,x+pad_radius,y-pad_radius,y+pad_radius,
            0,MAGNET_POCKET_DEPTH+MAGNET_FLOOR)
        body=body.fuse(pad)
        # Stagger equivalent cylinder seam vertices to avoid collinear mesh
        # junctions across the mounting face; bore geometry is unchanged.
        bore=bd.Cylinder(pocket_radius,MAGNET_POCKET_DEPTH+1,
            align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
        pocket=bd.Pos(x,y,-1)*bore.rotate(bd.Axis.Z,13+index*17)
        body=body.cut(pocket)
    body.label='left_deflector' if left else 'right_deflector'
    body.color=srgb('#F1EFE9')
    return body


def single_cut(body, cutter):
    result=body.intersect(cutter)
    if isinstance(result,bd.ShapeList):
        result=bd.Compound(children=list(result))
    solids=result.solids()
    if len(solids)!=1:
        raise ValueError(f'Fit test must be one connected solid, got {len(solids)}')
    return solids[0]


def first_layers(left):
    """Exact first 18 mm when the full part is printed on its flat end.

    Includes the complete end wall, ledge and six side magnet pockets. Return it
    already oriented with the flat outer end at Z=0 for direct slicing.
    """
    body=half(left)
    start,end=(-HALF_OUTER,-HALF_OUTER+FIT_TEST_LAYERS_DEPTH) if left else (HALF_OUTER-FIT_TEST_LAYERS_DEPTH,HALF_OUTER)
    body=single_cut(body,box(start,end,-WALL-LIP-1,DEPTH+1,-1,DROP+10))
    body=body.rotate(bd.Axis.Y,-90 if left else 90)
    low=body.bounding_box().min
    body=body.moved(bd.Location((-low.X,-low.Y,-low.Z)))
    body.label='first_layers_left' if left else 'first_layers_right'
    return body


def fit_frame(left):
    """Only the first 5.6 mm above the mounting plane, retaining all pockets."""
    body=single_cut(half(left),box(-HALF_OUTER-1,HALF_OUTER+1,-WALL-LIP-1,DEPTH+1,0,FIT_FRAME_HEIGHT))
    body.label='fit_frame_left' if left else 'fit_frame_right'
    return body
