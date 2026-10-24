from cadgen import build123d as bd, step
from deflector_left import deflector_left
from deflector_right import deflector_right

@step(out='../STEP/vent_exploded.step')
def vent_exploded():
    left=deflector_left().moved(bd.Location((-14,0,0)))
    right=deflector_right().moved(bd.Location((14,0,0)))
    return bd.Compound(children=[left,right],label='exploded_two_piece_deflector')

if __name__ == '__main__':
    vent_exploded()
