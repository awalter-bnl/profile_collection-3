from time import sleep
import numpy as np
from matplotlib import pyplot as plt


def user_checkin():
    proposal_id = input('Enter your proposal number:  ')
    PI_name = input('Enter the last name of the PI:  ')
    endstation = input('Which endstation (APPES or IOXAS)?  ')
    cycle = input('Run cycle?  ')

    RE.md['PI'] = PI_name
    RE.md['proposal_id'] = proposal_id
    RE.md['endstation'] = endstation
    RE.md['cycle'] = cycle

def user_checkout():
    del RE.md['PI']
#    RE.md['group'] = ''
    del RE.md['proposal_id']
    del RE.md['endstation']
    del RE.md['cycle']

def save_xas_csv(first_id, last_id, exptype = 'normal'):
    for scanid in range(first_id,last_id+1,1):
        if exptype == 'normal':
            df = db[scanid].table()
            df.to_csv('~/User_Data/Vanloonerjee_2018_December/Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'time', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4', 'norm_ch4', 'vortex_mca_rois_roi3_count', 'vortex_mca_rois_roi4_count'], index=False)
#            df.to_csv('~/Documents/Yildiz/LSM_Co/Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'time', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4', 'norm_ch4'], index=False)
        elif exptype == 'PD':
            df = db[scanid].table()
            df.to_csv('~/User_Data/Felix_And_Friends/PD_Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4'], index=False)
#            df.to_csv('~/Documents/Yildiz/LSM_Co/Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'time', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4', 'norm_ch4'], index=False)
        else:
            print('Unknown file type')


def save_xas_csv_short(first_id, last_id):
        for scanid in range(first_id,last_id+1,1):
                df = db.get_table(db[scanid])
                #fn = 'csv_data/Scan_{scan_id}.csv'.format(db[scanid].start)
#                df.to_csv('~/User_Data/Hunt/Carbon_contamination/PD_Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'sclr_ch2', 'sclr_ch3'])
                df.to_csv('~/User_Data/Hunt/Carbon_contamination/XAS_Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4'])


def save_xas_csv_time(first_id, last_id):
        for scanid in range(first_id,last_id+1,1):
                df = db.get_table(db[scanid])
                #fn = 'csv_data/Scan_{scan_id}.csv'.format(db[scanid].start)
                df.to_csv('~/User_Data/Hunt/Carbon_contamination/Time_Scan_%d.csv' % scanid, columns=['time', 'sclr_ch2', 'sclr_ch3'])

def save_xas_csv_all(first_id, last_id):
        for scanid in range(first_id,last_id+1,1):
                df = db.get_table(db[scanid])
#                df['Norm'] = df['sclr_ch4']/df['sclr_ch3']
                #fn = 'csv_data/Scan_{scan_id}.csv'.format(db[scanid].start)
                df.to_csv('~/User_Data/Wen/Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'ioxas_x', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4', 'vortex_mca_rois_roi2_count',  'vortex_mca_rois_roi3_count', 'vortex_mca_rois_roi4_count'], index=False)


def liveplot_photodiode():
     sclr.hints = {'fields': ['sclr_ch2']} 

def liveplot_xas():
     sclr.hints = {'fields': ['sclr_ch4']} 

def liveplot_aumesh():
     sclr.hints = {'fields': ['sclr_ch3']} 



def plot_norm_trans(scanid1,scanid2,normid,label):
        plt.figure(label)
        label = plt.gca()
        dfn = db.get_table(db[normid])
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1['Norm'] = -1*np.log(df1['sclr_ch4']/dfn['sclr_ch4'])
                df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_norm_async_tey(scanid1,scanid2,normid,label):
        plt.figure(label)
        label = plt.gca()
        dfn = db.get_table(db[normid])
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1['Norm'] = df1['sclr_ch4']/dfn['sclr_ch2']
                df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_norm_async_pfy(scanid1,scanid2,normid,label):
        plt.figure(label)
        label = plt.gca()
        dfn = db.get_table(db[normid])
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1['Norm2'] = df1['vortex_mca_rois_roi4_count']/dfn['sclr_ch2']
                df1.plot(x = 'pgm_energy_readback', y = 'Norm2', label = str(i), ax=label)

def plot_PD_EnergyScan(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1.plot(x = 'pgm_energy_readback', y = 'sclr_ch2', label = str(i), ax=label)

def plot_Aumesh(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1.plot(x = 'pgm_energy_readback', y = 'sclr_ch3', label = str(i), ax=label)


def plot_PD_TimeScan(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1.plot(x = 'time', y = 'sclr_ch2', label = str(i), ax=label)

def plot_PFY_TimeScan(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1.plot(x = 'time', y = 'vortex_mca_rois_roi4_count', label = str(i), ax=label)

def plot_norm_tey(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1['Norm'] = df1['sclr_ch4']/df1['sclr_ch3']
        df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_normto1_tey(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1['Norm'] = df1['sclr_ch4']/df1['sclr_ch3']
        df1['Norm'] = df1['Norm']-min(df1['Norm'])
        df1['Norm'] = df1['Norm']/max(df1['Norm'])
        df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_normto1_pfy(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1['Norm'] = df1['vortex_mca_rois_roi4_count']/df1['sclr_ch3']
        df1['Norm'] = df1['Norm']-min(df1['Norm'])
        df1['Norm'] = df1['Norm']/max(df1['Norm'])
        df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_norm_pfy(scanid1,scanid2,label):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1['Norm'] = df1['vortex_mca_rois_roi4_count']/df1['sclr_ch3']
                df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_norm_ipfy(scanid1,scanid2,label):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1['Norm'] = 1/(df1['vortex_mca_rois_roi3_count']/df1['sclr_ch3'])
                df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_normto1_ipfy(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1['Norm'] = 1/(df1['vortex_mca_rois_roi3_count']/df1['sclr_ch3'])
        df1['Norm'] = df1['Norm']-min(df1['Norm'])
        df1['Norm'] = df1['Norm']/max(df1['Norm'])
        df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_raw_ipfy(scanid1,scanid2,label):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1['IPFY'] = 1/(df1['vortex_mca_rois_roi3_count'])
                df1.plot(x = 'pgm_energy_readback', y = 'IPFY', label = str(i), ax=label)

def plot_raw_pfy(scanid1,scanid2,label):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1.plot(x = 'pgm_energy_readback', y = 'vortex_mca_rois_roi4_count', label = str(i), ax=label)

def plot_raw_tey(scanid1,scanid2,label):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1.plot(x = 'pgm_energy_readback', y = 'sclr_ch4', label = str(i), ax=label)

def plot_sample_map_tey(scanid1,scanid2,label):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1.plot(x = 'ioxas_x', y = 'sclr_ch4', label = str(i), ax=label)

def plot_sample_map_pfy(scanid1,scanid2,label):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1.plot(x = 'appes_y', y = 'vortex_mca_rois_roi4_count', label = str(i), ax=label)

# Composite plotting routines

def plot_norm_async_xas(scanid1,scanid2,normid,label,scan_type='TEY',normto1='Y'):
        plt.figure(label)
        label = plt.gca()
        dfn = db.get_table(db[normid])
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                if ((scan_type == 'TEY') or (scan_type == 'tey')):
                       df1['Norm'] = df1['sclr_ch4']/dfn['sclr_ch2']
                elif ((scan_type == 'PFY') or (scan_type == 'pfy')):
                       df1['Norm'] = df1['vortex_mca_rois_roi4_count']/dfn['sclr_ch2']
                elif ((scan_type == 'TFY') or (scan_type == 'tfy')):
                       df1['Norm'] = df1['vortex_mca_rois_roi1_count']/dfn['sclr_ch2']
                elif ((scan_type == 'TRANS') or (scan_type == 'trans')):
                       df1['Norm'] = -1*np.log(df1['sclr_ch4']/dfn['sclr_ch4'])
                
                if (normto1 == 'Y' or normto1 == 'y' or normto1 == 'yes' or normto1 == 'YES'):
                       df1['Norm'] = df1['Norm']-min(df1['Norm'])
                       df1['Norm'] = df1['Norm']/max(df1['Norm'])

                df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_norm_xas(scanid1,scanid2,label,scan_type='TEY',normto1='Y'):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                if ((scan_type == 'TEY') or (scan_type == 'tey')):
                       df1['Norm'] = df1['sclr_ch4']/df1['sclr_ch3']
                elif ((scan_type == 'PFY') or (scan_type == 'pfy')):
                       df1['Norm'] = df1['vortex_mca_rois_roi4_count']/df1['sclr_ch3']
                elif ((scan_type == 'TFY') or (scan_type == 'tfy')):
                       df1['Norm'] = df1['vortex_mca_rois_roi1_count']/df1['sclr_ch3']
                elif ((scan_type == 'IPFY') or (scan_type == 'ipfy')):
                       df1['Norm'] = 1/(df1['vortex_mca_rois_roi3_count']/df1['sclr_ch3'])

                if (normto1 == 'Y' or normto1 == 'y' or normto1 == 'yes' or normto1 == 'YES'):
                       df1['Norm'] = df1['Norm']-min(df1['Norm'])
                       df1['Norm'] = df1['Norm']/max(df1['Norm'])

                df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)


def plot_raw_xas(scanid1,scanid2,label,scan_type='TEY',normto1='Y'):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                if ((scan_type == 'TEY') or (scan_type == 'tey')):
                       df1['Raw'] = df1['sclr_ch4']
                elif ((scan_type == 'PFY') or (scan_type == 'pfy')):
                       df1['Raw'] = df1['vortex_mca_rois_roi4_count']
                elif ((scan_type == 'TFY') or (scan_type == 'tfy')):
                       df1['Raw'] = df1['vortex_mca_rois_roi1_count']

                if (normto1 == 'Y' or normto1 == 'y' or normto1 == 'yes' or normto1 == 'YES'):
                       df1['Raw'] = df1['Raw']-min(df1['Raw'])
                       df1['Raw'] = df1['Raw']/max(df1['Raw'])

                df1.plot(x = 'pgm_energy_readback', y = 'Raw', label = str(i), ax=label)


def XAS_scan(e_start, e_finish, velocity, deadband, inc_vortex = True):
    if inc_vortex == True:
        for channel in ['mca.rois.roi2.count','mca.rois.roi3.count','mca.rois.roi4.count']:
            getattr(vortex, channel).kind = 'hinted'
        for channel in ['mca.rois.roi2.count','mca.rois.roi3.count']:
            getattr(vortex, channel).kind = 'normal'
        dets = [sclr, vortex, norm_ch4, ring_curr]
    else:
        dets = [sclr, norm_ch4, ring_curr]

    for channel in ['channels.chan3','channels.chan4']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan2']:
        getattr(sclr, channel).kind = 'normal'

    yield from bps.mov(pgm_energy, e_start)
    yield from E_ramp(dets, e_start, e_finish, velocity, deadband=deadband)

def PD_scan(e_start, e_finish, velocity, deadband):
    for channel in ['channels.chan3','channels.chan2']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan4']:
        getattr(sclr, channel).kind = 'normal'

    dets = [sclr, ring_curr]

    yield from bps.mov(pgm_energy, e_start)
    yield from E_ramp(dets, e_start, e_finish, velocity, deadband=deadband)


def PD_count():
    for channel in ['channels.chan3','channels.chan2']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan4', 'channels.chan3']:
        getattr(sclr, channel).kind = 'normal'

    dets = [sclr, ring_curr]

    yield from bp.count(dets, num=None, delay=10)

def Aumesh_count():
    for channel in ['channels.chan3','channels.chan2']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan4', 'channels.chan2']:
        getattr(sclr, channel).kind = 'normal'

    dets = [sclr, ring_curr]

    yield from bp.count(dets, num=None)

def Felix_and_Friends(e_start, e_finish, numpoints):
    dets = [sclr, vortex, norm_ch4, ring_curr]
 
    for channel in ['mca.rois.roi2.count','mca.rois.roi3.count','mca.rois.roi4.count']:
        getattr(vortex, channel).kind = 'hinted'
    for channel in ['mca.rois.roi2.count','mca.rois.roi3.count']:
        getattr(vortex, channel).kind = 'normal'

    for channel in ['channels.chan3','channels.chan4']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan2']:
        getattr(sclr, channel).kind = 'normal'

#    yield from bps.mov(appes_x, 41.8)
#    yield from bps.mov(appes_y,-145.5)
    yield from bps.mov(pgm_energy, e_start)
    yield from bp.scan(dets, pgm_energy, e_start, e_finish, numpoints)
#    yield from E_ramp(dets, e_start, e_finish, velocity, deadband=deadband)

#    yield from bps.mov(appes_x, 38)
#    yield from bps.mov(appes_y,-145.4)
    yield from bps.mov(pgm_energy, e_start)
    yield from bp.scan(dets, pgm_energy, e_start, e_finish, numpoints)
#   yield from E_ramp(dets, e_start, e_finish, velocity, deadband=deadband)

#    yield from bps.mov(appes_x, 45)
#    yield from bps.mov(appes_y,-145)
#    yield from bps.mov(pgm_energy, e_start)
#    yield from bp.scan(dets, pgm_energy, e_start, e_finish, numpoints)
#   yield from E_ramp(dets, e_start, e_finish, velocity, deadband=deadband)

#    yield from bps.mov(appes_x, 45)
#    yield from bps.mov(appes_y,-137.5)
#    yield from bps.mov(pgm_energy, e_start)
    yield from bp.scan(dets, pgm_energy, e_start, e_finish, numpoints)
#   yield from E_ramp(dets, e_start, e_finish, velocity, deadband=deadband)
    
def epu_gap_scans():
    dets=[sclr, ring_curr]

    for channel in ['channels.chan2']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan3','channels.chan4']:
        getattr(sclr, channel).kind = 'normal'

#   1st order horizontal

    yield from bps.abs_set(epu1table, 2)
    yield from bps.sleep(20)
    yield from bps.mov(pgm_energy, 250)

    for ene_val in range(250, 1251, 50):
        yield from bps.abs_set(feedback, 0)
        yield from bps.abs_set(pgm_energy, ene_val, wait=True)
        yield from bps.abs_set(feedback, 1)
        yield from bps.sleep(10)
        yield from bps.abs_set(feedback, 0)
        yield from bps.sleep(5)
        yield from bp.rel_scan(dets, epu1.gap, -2, 2, 80)

    for ene_val2 in range(1300, 1651, 50):
        yield from bps.abs_set(feedback, 0)
        yield from bps.abs_set(pgm_energy, ene_val2, wait=True)
        yield from bps.abs_set(feedback, 1)       
        yield from bps.sleep(10)
        yield from bps.abs_set(feedback, 0)
        yield from bps.sleep(5)
        yield from bp.rel_scan(dets, epu1.gap, -3, 3, 120)

#   3rd order horizontal
    yield from bps.abs_set(epu1.phase, 0, wait=True)
    yield from bps.abs_set(epu1table, 3)
    yield from bps.sleep(20)
    yield from bps.abs_set(pgm_energy, 750, wait=True)

    for ene_val3 in range(750, 1951, 50):
        yield from bps.abs_set(feedback, 0)
        yield from bps.abs_set(pgm_energy, ene_val3, wait=True)
        yield from bps.abs_set(feedback, 1)
        yield from bps.sleep(10)
        yield from bps.abs_set(feedback, 0)
        yield from bps.sleep(5)
        yield from bp.rel_scan(dets, epu1.gap, -1, 1, 80)

#   1st order vertical
#    yield from bps.abs_set(epu1.phase, 24.6, wait=True)
#    yield from bps.abs_set(epu1table, 5)
#    yield from bps.abs_set(pgm_energy, 250, wait=True)
#    yield from bps.sleep(30)

#    for ene_val in range(250, 401, 50):
#        yield from bps.abs_set(feedback, 0)
#        yield from bps.abs_set(pgm_energy, ene_val, wait=True)
#        yield from bps.sleep(10)
#        yield from bp.scan(dets, epu1.gap, 12, 15, 120)

#    for ene_val in range(450, 1251, 50):
#        yield from bps.abs_set(feedback, 0)
#        yield from bps.abs_set(pgm_energy, ene_val, wait=True)
#        yield from bps.abs_set(feedback, 1)
#        yield from bps.sleep(10)
#        yield from bps.abs_set(feedback, 0)
#        yield from bps.sleep(5)
#        yield from bp.rel_scan(dets, epu1.gap, -2, 2, 80)

#    for ene_val2 in range(1300, 1651, 50):
#        yield from bps.abs_set(feedback, 0)
#        yield from bps.abs_set(pgm_energy, ene_val2, wait=True)
#        yield from bps.abs_set(feedback, 1)
#        yield from bps.sleep(10)
#        yield from bps.abs_set(feedback, 0)
#        yield from bps.sleep(5)
#        yield from bp.rel_scan(dets, epu1.gap, -3, 3, 60)

#   3rd order vertical


#    yield from bps.abs_set(epu1table ,9)
#    yield from bps.sleep(20)
#    yield from bps.abs_set(pgm_energy, 750, wait=True)

#    for ene_val in range(750, 1151, 50):
#        yield from bps.abs_set(feedback, 0)
#        yield from bps.abs_set(pgm_energy, ene_val, wait=True)
#        yield from bps.sleep(10)
#        yield from bp.scan(dets, epu1.gap, 12, 15, 120)


#    for ene_val3 in range(1200, 1951, 50):
#        yield from bps.abs_set(feedback, 0)
#        yield from bps.abs_set(pgm_energy, ene_val3, wait=True)
#        yield from bps.abs_set(feedback, 1)
#        yield from bps.sleep(10)
#        yield from bps.abs_set(feedback, 0)
#        yield from bps.sleep(5)
#        yield from bp.rel_scan(dets, epu1.gap, -1, 1, 80)

    yield from bps.abs_set(valve_diag3_close, 1, wait=True)
    yield from bps.abs_set(valve_mir3_close, 1, wait=True)
    yield from bps.mov(diag3_y, 46) 




def nexafs_pey(dets, e_start, e_finish):

    #turn off feedback before moving energy
    # caput('XF:23ID2-OP{FBck}Sts:FB-Sel',0)
    yield from bps.mov(mirror_feedback, 0)
    yield from bps.sleep(2)
    #to close downstream shutter
    # caput('XF:23ID2-PPS{PSh}Cmd:Cls-Cmd',1)
    yield from bps.mov(ds_shutter, 'Close')
    # sleep(2)
    print ('Moving to start energy...')
    #move energy to start position
    yield from bps.mov(pgm_energy, e_start)

    yield from bps.sleep(2)

    print ('Scan is starting...')

    #to open downstream shutter just when scan is started
    # caput('XF:23ID2-PPS{PSh}Cmd:Opn-Cmd',1)
    yield from bps.mov(ds_shutter, 'Open')    
    yield from bps.sleep(3)
    
    #turn on feedback
    # caput('XF:23ID2-OP{FBck}Sts:FB-Sel',1)
    yield from bps.mov(mirror_feedback, 1)    
    #caput('XF:23IDA-OP:2{Mir:1A-Ax:FPit}Mtr_POS_SP',50)
    #sleep(2)

    #to start the scan
    #RE(ascan(pgm_energy, e_start, e_finish, e_points), group='nexafs')
    yield from E_ramp(dets, e_start, e_finish, 0.1, deadband=6)

    # caput('XF:23ID2-OP{FBck}Sts:FB-Sel',0)
    yield from bps.mov(mirror_feedback, 0)
    yield from bps.sleep(2)
    #to close downstream shutter
    # caput('XF:23ID2-PPS{PSh}Cmd:Cls-Cmd',1)
    yield from bps.mov(ds_shutter, 'Close')
    # sleep(2)
    yield from bps.sleep(2)

    #to open downstream shutter just when scan is started
    # caput('XF:23ID2-PPS{PSh}Cmd:Opn-Cmd',1)
    yield from bps.mov(ds_shutter, 'Open')    
    yield from bps.sleep(3)
    
    #turn on feedback
    # caput('XF:23ID2-OP{FBck}Sts:FB-Sel',1)
    yield from bps.mov(mirror_feedback, 1)    

    #saving scan
#    save_q = input("The scan is finished. Do you want to save the data (as csv)? (yes/no) ")
#    if save_q in ["yes", "Y", "Yes", "y", "YES"]:
#        filename = input("Type file name here (no spaces, no special characters other than dash or underscore): ")
#        savedname = filename+'.csv'
#        df = db.get_table(db[-1])
#        df.to_csv('Documents/Yildiz/savedname')
#        print ('The scan has been saved as', savedname)
#    else:
#        print ('The scan has not been saved!')

def test():
    yield from abs_set(pgm_energy, 890, wait=True)
    yield from E_ramp(890, 895, 0.1, deadband=8)

CONTAINER = None
REF_EDGES = {'Al' : {'energy': 1560 , 'epu_table': 3 , 'vortex_low': 3200 , 'vortex_high': 4000},
             'Cu' : {'energy': 932  , 'epu_table': 2 , 'vortex_low': 1600 , 'vortex_high': 2200},
             'O'  : {'energy': 540  , 'epu_table': 2 , 'vortex_low': 500 , 'vortex_high': 700},
             'Ni' : {'energy': 855  , 'epu_table': 2 , 'vortex_low': 900 , 'vortex_high': 1100},
             'Fe' : {'energy': 709  , 'epu_table': 2 , 'vortex_low': 700  , 'vortex_high': 1000},
             'F'  : {'energy': 691  , 'epu_table': 2 , 'vortex_low': 700  , 'vortex_high': 1000},
             'Na' : {'energy': 1075 , 'epu_table': 2 , 'vortex_low': 1000 , 'vortex_high': 1400},
             'N'  : {'energy': 407  , 'epu_table': 2 , 'vortex_low': 300  , 'vortex_high': 400},
             'Co' : {'energy': 775  , 'epu_table': 2 , 'vortex_low': 850  , 'vortex_high': 1000},
             'Mn' : {'energy': 654  , 'epu_table': 2 , 'vortex_low': 700  , 'vortex_high': 800},
             'Ti' : {'energy': 466  , 'epu_table': 2 , 'vortex_low': 350  , 'vortex_high': 600},
             'Mo' : {'energy': 380  , 'epu_table': 2 , 'vortex_low': 300  , 'vortex_high': 500},
             'C' : {'energy': 320 , 'epu_table': 2 , 'vortex_low': 220 , 'vortex_high': 400},
             'Cd' : {'energy': 620  , 'epu_table': 2 , 'vortex_low': 700  , 'vortex_high': 800},
             'La' : {'energy': 860  , 'epu_table': 2 , 'vortex_low': 800  , 'vortex_high': 1000},
}

def find_sample(edge, xstart, xstop, step):
    edge_params = REF_EDGES[edge]
    pts = abs(int(round((xstop-xstart)/step)))
    yield from bps.abs_set(feedback, 0)
    yield from bps.abs_set(pgm_energy, edge_params['energy'], wait=True)
    yield from bps.abs_set(epu1table, edge_params['epu_table'], wait=True)
    yield from bps.sleep(15)
    yield from bps.abs_set(feedback, 1)
    yield from bps.abs_set(vortex.mca.rois.roi2.lo_chan, edge_params['vortex_low'], wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi2.hi_chan, edge_params['vortex_high'], wait=True)
    old_hints_vortex = save_hint_state(vortex)
    old_hints_sclr = save_hint_state(sclr)
    for channel in ['mca.rois.roi2.count']:
        getattr(vortex, channel).kind = 'hinted'
    for channel in ['mca.rois.roi3.count','mca.rois.roi4.count']:
        getattr(vortex, channel).kind = 'normal'
    for channel in ['channels.chan4']:
        getattr(sclr, channel).kind = 'hinted'
    for channel in ['channels.chan2','channels.chan3']:
        getattr(sclr, channel).kind = 'normal'
    dets = [sclr, vortex]
#    vortex.mca.rois.roi2.count.kind = 'hinted'
#    yield from bp.scan(dets, appes_y, xstart, xstop, pts)
    yield from bp.scan(dets, ioxas_x, xstart, xstop, pts)
    yield from bps.sleep(2)
    restore_hint_state(vortex, old_hints_vortex)
    restore_hint_state(sclr, old_hints_sclr)


#def find_sample(energy, xstart, xstop, pts):
        # gs no longer supported
    #gs.TABLE_COLS.append('vortex_mca_rois_roi2_count')
    #gs.PLOT_Y = 'vortex_mca_rois_roi2_count'
#    mov(vortex.mca.rois.roi2.lo_chan, 1400)
#    mov(vortex.mca.rois.roi2.hi_chan, 2000)
#    yield from bps.abs_set(vortex.mca.rois.roi2.lo_chan, 700)
#    yield from bps.abs_set(vortex.mca.rois.roi2.hi_chan, 1000)
#    old_hints = save_hint_state(vortex)
#    for channel in ['mca.rois.roi2.count']:
#        getattr(vortex, channel).kind = 'hinted'
#    for channel in ['mca.rois.roi3.count','mca.rois.roi4.count']:
#        getattr(vortex, channel).kind = 'normal'
#    vortex.mca.rois.roi2.count.kind = 'hinted'
#    yield from bps.abs_set(feedback, 0)
#    yield from bps.abs_set(pgm_energy, energy, wait=True)
#    yield from bps.abs_set(feedback, 1)
#    yield from bps.sleep(2)
#    yield from bp.scan([vortex], ioxas_x, xstart, xstop, pts)
#    yield from bps.sleep(2)
#    restore_hint_state(vortex, old_hints)
    #gs.TABLE_COLS.remove('vortex_mca_rois_roi2_count')
    #gs.PLOT_Y = 'vortex_mca_rois_roi4_count'

def save_hint_state(dev):
    return {c: getattr(dev, c).kind for c in dev.read_attrs}

def restore_hint_state(dev, prev_state):
    for channel, state in prev_state.items():
        getattr(dev, channel).kind = state


