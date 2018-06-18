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

def multi_XAS():
    dets = [sclr, norm_ch4, ring_curr]
    for channel in ['channels.chan3','channels.chan4']:
        getattr(sclr, channel).kind = 'hinted'

#   Al K measurements
#    yield from bps.abs_set(feedback, 0, wait=True)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)
#    yield from bps.abs_set(epu1table, 7, wait=True)
#    yield from bps.abs_set(epu1offset, 8, wait=True)
#    yield from bps.sleep(30)
#    yield from bps.abs_set(feedback, 1, wait=True)
#    yield from bps.sleep(30)
#    yield from bps.abs_set(feedback, 0, wait=True)
#    yield from bps.abs_set(sample_sclr_gain, 0, wait=True)
#    yield from bps.abs_set(sample_sclr_decade, 3, wait=True)
#    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
#    yield from bps.abs_set(aumesh_sclr_decade, 2, wait=True)

#    yield from bps.abs_set(ioxas_x, 250.4, wait=True)
#    yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 253.3, wait=True)
#    yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 256.5, wait=True)
#    yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 259.1, wait=True)
#    yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)
#    yield from bps.abs_set(ioxas_x, 250.4, wait=True)
#    yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 253.3, wait=True)
#    yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 256.5, wait=True)
#    yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 259.1, wait=True)
#    yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#   Si K measurements
#    yield from bps.abs_set(feedback, 0, wait=True)
#    yield from bps.abs_set(pgm_energy, 1845, wait=True)
#    yield from bps.abs_set(epu1table, 7, wait=True)
#    yield from bps.abs_set(epu1offset, 10, wait=True)
#    yield from bps.sleep(10)
#    yield from bps.abs_set(feedback, 1, wait=True)
#    yield from bps.sleep(5)
#    yield from bps.abs_set(feedback, 0, wait=True)
#    yield from bps.abs_set(sample_sclr_gain, 2, wait=True)
#    yield from bps.abs_set(sample_sclr_decade, 2, wait=True)
#    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
#    yield from bps.abs_set(aumesh_sclr_decade, 2, wait=True)

#    yield from bps.abs_set(ioxas_x, 250.3, wait=True)
#    yield from E_ramp(dets, 1830, 1875, 0.1, deadband=4)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 253.2, wait=True)
#    yield from E_ramp(dets, 1830, 1875, 0.1, deadband=4)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 256.35, wait=True)
#    yield from E_ramp(dets, 1830, 1875, 0.1, deadband=4)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#    yield from bps.abs_set(ioxas_x, 259.1, wait=True)
#    yield from E_ramp(dets, 1830, 1875, 0.1, deadband=4)
#    yield from bps.abs_set(pgm_energy, 1565, wait=True)

#O K measurement


    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 540, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(sample_sclr_gain, 2, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 3, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

#    yield from bps.abs_set(ioxas_x, 250.3, wait=True)
#    yield from E_ramp(dets, 520, 570, 0.05, deadband=8)
#    yield from bps.abs_set(pgm_energy, 520, wait=True)
    
    yield from bps.abs_set(ioxas_x, 253.2, wait=True)
    yield from E_ramp(dets, 520, 570, 0.05, deadband=8)
    yield from bps.abs_set(pgm_energy, 520, wait=True)

    yield from bps.abs_set(ioxas_x, 256.35, wait=True)
    yield from E_ramp(dets, 520, 570, 0.05, deadband=8)
    yield from bps.abs_set(pgm_energy, 520, wait=True)

    yield from bps.abs_set(ioxas_x, 259.1, wait=True)
    yield from E_ramp(dets, 520, 570, 0.05, deadband=8)
    yield from bps.abs_set(pgm_energy, 520, wait=True)

    yield from bps.abs_set(sample_sclr_gain, 1, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 3, wait=True)
    
    yield from bps.abs_set(ioxas_x, 273.45, wait=True)
    yield from E_ramp(dets, 520, 570, 0.1, deadband=8)
    yield from bps.abs_set(pgm_energy, 520, wait=True)


    yield from bps.abs_set(ioxas_x, 276.3, wait=True)
    yield from E_ramp(dets, 520, 570, 0.1, deadband=8)
    yield from bps.abs_set(pgm_energy, 520, wait=True)

    yield from bps.abs_set(ioxas_x, 279.6, wait=True)
    yield from E_ramp(dets, 520, 570, 0.1, deadband=8)
    yield from bps.abs_set(pgm_energy, 520, wait=True)

    yield from bps.abs_set(ioxas_x, 281.9, wait=True)
    yield from E_ramp(dets, 520, 570, 0.1, deadband=8)
    yield from bps.abs_set(pgm_energy, 520, wait=True)

#Mo M2,3  measurments

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 410, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(sample_sclr_gain, 0, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 3, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 0, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

 #   yield from bps.abs_set(ioxas_x, 0, wait=True)
 #   yield from bps.abs_set(valve_mir3_close, 1, wait=True)


    yield from bps.abs_set(ioxas_x, 273.45, wait=True)
    yield from E_ramp(dets, 380, 430, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 380, wait=True)


    yield from bps.abs_set(ioxas_x, 276.1, wait=True)
    yield from E_ramp(dets, 380, 430, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 380, wait=True)

    yield from bps.abs_set(ioxas_x, 279.8, wait=True)
    yield from E_ramp(dets, 380, 430, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 380, wait=True)

    yield from bps.abs_set(ioxas_x, 282.0, wait=True)
    yield from E_ramp(dets, 380, 430, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 380, wait=True)


def PD_scans():
    dets = [sclr, norm_ch4, ring_curr]
    for channel in ['channels.chan3','channels.chan4']:
        getattr(sclr, channel).kind = 'hinted'

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 845, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 2, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)
    yield from bps.abs_set(au_mesh, -76.3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 845, wait=True)
        yield from E_ramp(dets, 845, 877, 0.1, deadband=8)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 770, wait=True)
        yield from E_ramp(dets, 845, 885, 0.1, deadband=8)


    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 845, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 1, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)
    yield from bps.abs_set(au_mesh, -106.3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 845, wait=True)
        yield from E_ramp(dets, 845, 877, 0.1, deadband=8)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 770, wait=True)
        yield from E_ramp(dets, 845, 885, 0.1, deadband=8)


    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 380, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 2, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 6, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 1, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 380, wait=True)
        yield from E_ramp(dets, 380, 430, 0.05, deadband=4)

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 430, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 2, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 6, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 1, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 430, wait=True)
        yield from E_ramp(dets, 430, 470, 0.1, deadband=8)

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 520, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 0, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 520, wait=True)
        yield from E_ramp(dets, 520, 570, 0.1, deadband=8)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 520, wait=True)
        yield from E_ramp(dets, 520, 570, 0.05, deadband=8)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 520, wait=True)
        yield from E_ramp(dets, 520, 565, 0.1, deadband=8)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 525, wait=True)
        yield from E_ramp(dets, 525, 570, 0.1, deadband=8)

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 655, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 1, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 655, wait=True)
        yield from E_ramp(dets, 655, 710, 0.1, deadband=8)

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 770, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 1, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 770, wait=True)
        yield from E_ramp(dets, 770, 810, 0.1, deadband=6)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 770, wait=True)
        yield from E_ramp(dets, 770, 810, 0.05, deadband=6)

#    yield from bps.abs_set(feedback, 0, wait=True)
#    yield from bps.abs_set(pgm_energy, 845, wait=True)
#    yield from bps.abs_set(epu1table, 6, wait=True)
#    yield from bps.abs_set(epu1offset, 0, wait=True)
#    yield from bps.sleep(10)
#    yield from bps.abs_set(feedback, 1, wait=True)
#    yield from bps.abs_set(pd_sclr_gain, 1, wait=True)
#    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
#    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
#    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

#    for ii in range(0,4):
#        yield from bps.abs_set(pgm_energy, 845, wait=True)
#        yield from E_ramp(dets, 845, 877, 0.1, deadband=8)

#    for ii in range(0,4):
#        yield from bps.abs_set(pgm_energy, 770, wait=True)
#        yield from E_ramp(dets, 845, 885, 0.1, deadband=8)

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 870, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 1, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 870, wait=True)
        yield from E_ramp(dets, 870, 920, 0.1, deadband=8)

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 925, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 0, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 1, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 925, wait=True)
        yield from E_ramp(dets, 925, 975, 0.1, deadband=8)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 925, wait=True)
        yield from E_ramp(dets, 925, 960, 0.05, deadband=8)


    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 925, wait=True)
        yield from E_ramp(dets, 925, 975, 0.05, deadband=8)

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 1552, wait=True)
    yield from bps.abs_set(epu1table, 7, wait=True)
    yield from bps.abs_set(epu1offset, 8, wait=True)
    yield from bps.sleep(20)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 0, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 0, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 1552, wait=True)
        yield from E_ramp(dets, 1552, 1592, 0.05, deadband=1.2)

    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 1830, wait=True)
    yield from bps.abs_set(epu1table, 7, wait=True)
    yield from bps.abs_set(epu1offset, 10, wait=True)
    yield from bps.sleep(20)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(pd_sclr_gain, 0, wait=True)
    yield from bps.abs_set(pd_sclr_decade, 7, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 0, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)

    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 1830, wait=True)
        yield from E_ramp(dets, 1830, 1875, 0.1, deadband=4)   
    
    for ii in range(0,4):
        yield from bps.abs_set(pgm_energy, 1830, wait=True)
        yield from E_ramp(dets, 1830, 1875, 0.1, deadband=6)

    yield from bps.abs_set(diag4_y, 0, wait=True)
    yield from bps.abs_set(valve_mir3_close, 1, wait=True)


def O_K_Ctape():
    dets = [sclr, norm_ch4, ring_curr]
    for channel in ['channels.chan3','channels.chan4']:
        getattr(sclr, channel).kind = 'hinted'

    for ii in range(0,2):
        yield from bps.abs_set(pgm_energy, 520, wait=True)
        yield from E_ramp(dets, 520, 570, 0.1, deadband=8)

    for ii in range(0,2):
        yield from bps.abs_set(pgm_energy, 520, wait=True)
        yield from E_ramp(dets, 520, 570, 0.05, deadband=8)

    for ii in range(0,2):
        yield from bps.abs_set(pgm_energy, 520, wait=True)
        yield from E_ramp(dets, 520, 565, 0.1, deadband=8)

    for ii in range(0,2):
        yield from bps.abs_set(pgm_energy, 525, wait=True)
        yield from E_ramp(dets, 525, 570, 0.1, deadband=8)
 
