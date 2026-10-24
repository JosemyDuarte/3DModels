from cadgen import build123d as bd, step
from deflector_left import deflector_left
from deflector_right import deflector_right

@step(out='../STEP/vent_assembly.step')
def vent_assembly():
    return bd.Compound(children=[deflector_left(),deflector_right()],label='two_piece_vent_deflector')

if __name__ == '__main__':
    vent_assembly()
