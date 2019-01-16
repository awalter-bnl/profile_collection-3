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

"""def Felix_and_Friends():
    dets = [sclr, vortex, norm_ch4, ring_curr]
 
    for channel in ['mca.rois.roi2.count','mca.rois.roi3.count','mca.rois.roi4.count']:
        getattr(vortex, channel).kind = 'hinted'
    for channel in ['mca.rois.roi2.count','mca.rois.roi3.count']:
        getattr(vortex, channel).kind = 'normal'

    for channel in ['channels.chan3','channels.chan4']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan2']:
        getattr(sclr, channel).kind = 'normal'

    yield from bps.mov(appes_x, 39)
    yield from bps.mov(appes_y,-145)
    yield from bps.mov(pgm_energy, 1245)
    yield from E_ramp(dets, 1245, 1170, 0.2, deadband=18)

    yield from bps.mov(appes_x, 39)
    yield from bps.mov(appes_y,-137.5)
    yield from bps.mov(pgm_energy, 1245)
    yield from E_ramp(dets, 1245, 1170, 0.2, deadband=18)

    yield from bps.mov(appes_x, 45)
    yield from bps.mov(appes_y,-145)
    yield from bps.mov(pgm_energy, 1245)
    yield from E_ramp(dets, 1245, 1170, 0.2, deadband=18)

    yield from bps.mov(appes_x, 45)
    yield from bps.mov(appes_y,-137.5)
    yield from bps.mov(pgm_energy, 1245)
    yield from E_ramp(dets, 1245, 1170, 0.2, deadband=18)
"""

def multi_XAS():
    for channel in ['mca.rois.roi2.count','mca.rois.roi3.count','mca.rois.roi4.count']:
        getattr(vortex, channel).kind = 'hinted'
    for channel in ['mca.rois.roi2.count','mca.rois.roi3.count']:
        getattr(vortex, channel).kind = 'normal'
    dets = [sclr, vortex, norm_ch4, ring_curr]

    for channel in ['channels.chan3','channels.chan4']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan2']:
        getattr(sclr, channel).kind = 'normal'

# Make sure Au mesh is in position
    yield from bps.abs_set(au_mesh, -103.950, wait=True)


#   Al K measurements
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 1565, wait=True)
    yield from bps.abs_set(epu1table, 7, wait=True)
    yield from bps.abs_set(epu1offset, 6, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(sample_sclr_gain, 1, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 1, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 2, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.lo_chan, 1500, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.hi_chan, 1900, wait=True)


    yield from bps.abs_set(ioxas_x, 278.6, wait=True)
    yield from E_ramp(dets, 1592, 1552, 0.1, deadband=4)
    yield from bps.abs_set(pgm_energy, 1592, wait=True)

    yield from bps.abs_set(ioxas_x, 290.0, wait=True)
    yield from E_ramp(dets, 1592, 1552, 0.1, deadband=4)
    yield from bps.abs_set(pgm_energy, 1592, wait=True)

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
    yield from bps.abs_set(epu1offset, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(sample_sclr_gain, 2, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 3, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.lo_chan, 500, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.hi_chan, 700, wait=True)


#    yield from bps.abs_set(ioxas_x, 250.3, wait=True)
#    yield from E_ramp(dets, 520, 570, 0.05, deadband=8)
#    yield from bps.abs_set(pgm_energy, 520, wait=True)
    
    yield from bps.abs_set(ioxas_x, 254.8, wait=True)
    yield from E_ramp(dets, 575, 520, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 575, wait=True)

    yield from bps.abs_set(ioxas_x, 266.7, wait=True)
    yield from E_ramp(dets, 575, 520, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 575, wait=True)

    yield from bps.abs_set(ioxas_x, 278.6, wait=True)
    yield from E_ramp(dets, 575, 520, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 575, wait=True)

    yield from bps.abs_set(ioxas_x, 290.0, wait=True)
    yield from E_ramp(dets, 575, 520, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 575, wait=True)

#Ni L2,3  measurements
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 855, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(sample_sclr_gain, 1, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 3, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 0, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.lo_chan, 900, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.hi_chan, 1100, wait=True)

    yield from bps.abs_set(ioxas_x, 254.8, wait=True)
    yield from E_ramp(dets, 882, 842, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 882, wait=True)

    yield from bps.abs_set(ioxas_x, 266.7, wait=True)
    yield from E_ramp(dets, 882, 842, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 882, wait=True)

    yield from bps.abs_set(ioxas_x, 278.6, wait=True)
    yield from E_ramp(dets, 882, 842, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 882, wait=True)

    yield from bps.abs_set(ioxas_x, 290.0, wait=True)
    yield from E_ramp(dets, 882, 842, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 882, wait=True)

#F K measurements
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 705, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(sample_sclr_gain, 1, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 3, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 0, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.lo_chan, 700, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.hi_chan, 900, wait=True)

    yield from bps.abs_set(ioxas_x, 254.8, wait=True)
    yield from E_ramp(dets, 715, 680, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 715, wait=True)

    yield from bps.abs_set(ioxas_x, 266.7, wait=True)
    yield from E_ramp(dets, 715, 680, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 715, wait=True)

    yield from bps.abs_set(ioxas_x, 278.6, wait=True)
    yield from E_ramp(dets, 715, 680, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 715, wait=True)

    yield from bps.abs_set(ioxas_x, 290.0, wait=True)
    yield from E_ramp(dets, 715, 680, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 715, wait=True)

#Co L2,3 measurements
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 785, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(sample_sclr_gain, 1, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 3, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 0, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 3, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.lo_chan, 900, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.hi_chan, 1000, wait=True)

    yield from bps.abs_set(ioxas_x, 254.8, wait=True)
    yield from E_ramp(dets, 810, 770, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 810, wait=True)

    yield from bps.abs_set(ioxas_x, 266.7, wait=True)
    yield from E_ramp(dets, 810, 770, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 810, wait=True)

    yield from bps.abs_set(ioxas_x, 278.6, wait=True)
    yield from E_ramp(dets, 810, 770, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 810, wait=True)

    yield from bps.abs_set(ioxas_x, 290.0, wait=True)
    yield from E_ramp(dets, 810, 770, 0.1, deadband=6)
    yield from bps.abs_set(pgm_energy, 810, wait=True)

# Make sure Au mesh is out of the way
    yield from bps.abs_set(au_mesh, -73.950, wait=True)

# C K measurements
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, 291.5, wait=True)
    yield from bps.abs_set(epu1table, 6, wait=True)
    yield from bps.abs_set(epu1offset, 1.5, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.sleep(10)
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(sample_sclr_gain, 2, wait=True)
    yield from bps.abs_set(sample_sclr_decade, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, 2, wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, 2, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.lo_chan, 220, wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.hi_chan, 400, wait=True)

    yield from bps.abs_set(ioxas_x, 253.8, wait=True)
    yield from E_ramp(dets, 320, 275, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 320, wait=True)

    yield from bps.abs_set(ioxas_x, 259.5, wait=True)
    yield from E_ramp(dets, 320, 275, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 320, wait=True)

    yield from bps.abs_set(ioxas_x, 265.7, wait=True)
    yield from E_ramp(dets, 320, 275, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 320, wait=True)

    yield from bps.abs_set(ioxas_x, 270.1, wait=True)
    yield from E_ramp(dets, 320, 275, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 320, wait=True)

    yield from bps.abs_set(ioxas_x, 277.6, wait=True)
    yield from E_ramp(dets, 320, 275, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 320, wait=True)

    yield from bps.abs_set(ioxas_x, 283.8, wait=True)
    yield from E_ramp(dets, 320, 275, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 320, wait=True)

    yield from bps.abs_set(ioxas_x, 289, wait=True)
    yield from E_ramp(dets, 320, 275, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 320, wait=True)

    yield from bps.abs_set(ioxas_x, 294.4, wait=True)
    yield from E_ramp(dets, 320, 275, 0.05, deadband=4)
    yield from bps.abs_set(pgm_energy, 320, wait=True)


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
 
