from time import sleep
import numpy as np

def adrians_xps():
    yield from bps.mov(pgm_energy, 842)
    yield from bps.sleep(3730)
    yield from bps.mov(pgm_energy, 894)
    yield from bps.sleep(3730)
    yield from bps.mov(pgm_energy, 942)
    yield from bps.sleep(3730)
    yield from bps.mov(pgm_energy, 990)
    yield from bps.sleep(3730)
    yield from bps.mov(pgm_energy, 1090)
    yield from bps.sleep(3730)
    yield from bps.mov(valve_diag3_close, 1)
    yield from bps.mov(valve_mir3_close, 1)

