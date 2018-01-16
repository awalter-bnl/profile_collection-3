from epics import caget, caput
from time import sleep
import numpy as np

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

def save_xas_csv(first_id, last_id):
    for scanid in range(first_id,last_id+1,1):
        df = db.get_table(db[scanid])
        df['Norm'] = df['sclr_ch4']/df['sclr_ch3']
        #fn = 'csv_data/Scan_{scan_id}.csv'.format(db[scanid].start)
        df.to_csv('~/Adhunt/N2_filter_testing/Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'vortex_mca_rois_roi4_count', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4', 'Norm'], index=False)

def save_xas_csv_short(first_id, last_id):
        for scanid in range(first_id,last_id+1,1):
                df = db.get_table(db[scanid])
                #fn = 'csv_data/Scan_{scan_id}.csv'.format(db[scanid].start)
                df.to_csv('~/Yildiz_Group_XAS/Jiayue_Oct2017/Scan_%d.csv' % scanid, columns=['time', 'pgm_energy_readback', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4', 'vortex_mca_rois_roi4_count'])




def save_xas_csv_all(first_id, last_id):
        for scanid in range(first_id,last_id+1,1):
                df = db.get_table(db[scanid])
#                df['Norm'] = df['sclr_ch4']/df['sclr_ch3']
                #fn = 'csv_data/Scan_{scan_id}.csv'.format(db[scanid].start)
                df.to_csv('~/User_Data/Schroeder/Nov2017/Scan_%d.csv' % scanid, columns=['pgm_energy_readback', 'ioxas_x', 'sclr_ch2', 'sclr_ch3', 'sclr_ch4', 'vortex_mca_rois_roi3_count', 'vortex_mca_rois_roi4_count'], index=False)


def start_vortex():
        gs.DETS.append(vortex)
        # Use best-effort callbacks now
        #gs.TABLE_COLS.append('vortex_mca_rois_roi4_count')
        #gs.TABLE_COLS.append('vortex_mca_rois_roi3_count')

def stop_vortex():
    gs.DETS.remove(vortex)
        # no longer supported. use best effort callbacks now
    #gs.TABLE_COLS.remove('vortex_mca_rois_roi4_count')
    #gs.TABLE_COLS.remove('vortex_mca_rois_roi3_count')

def liveplot_raw_tey():
    gs.PLOT_Y = 'sclr_ch4'

def liveplot_norm_tey():
    gs.PLOT_Y = 'norm_intensity'

def liveplot_raw_pfy():
    gs.PLOT_Y = 'vortex_mca_rois_roi4_count'

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
                df1['Norm'] = df1['vortex_mca_rois_roi4_count']/dfn['sclr_ch2']
                df1.plot(x = 'pgm_energy_readback', y = 'Norm', label = str(i), ax=label)

def plot_norm_tey(scanid1,scanid2,label):
    plt.figure(label)
    label = plt.gca()
    for i in range (scanid1, scanid2+1):
        df1 = db.get_table(db[i])
        df1['Norm'] = df1['sclr_ch4']/df1['sclr_ch3']
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


def nexafs_pey(e_start,e_finish):

    #turn off feedback before moving energy
    caput('XF:23ID2-OP{FBck}Sts:FB-Sel',0)
    sleep(2)
    #to close downstream shutter
    caput('XF:23ID2-PPS{PSh}Cmd:Cls-Cmd',1)
    sleep(2)
    print ('Moving to start energy...')
    #move energy to start position
    mov(pgm_energy, e_start)

    sleep(2)

    print ('Scan is starting...')

    #to open downstream shutter just when scan is started
    caput('XF:23ID2-PPS{PSh}Cmd:Opn-Cmd',1)
    sleep(3)
    #turn on feedback
    caput('XF:23ID2-OP{FBck}Sts:FB-Sel',1)
    #caput('XF:23IDA-OP:2{Mir:1A-Ax:FPit}Mtr_POS_SP',50)
    #sleep(2)

    #to start the scan
    #RE(ascan(pgm_energy, e_start, e_finish, e_points), group='nexafs')
    RE(E_ramp(e_start,e_finish,0.1,deadband=6))

    #to close downstream shutter after scan is finished
    caput('XF:23ID2-OP{FBck}Sts:FB-Sel',0)
    caput('XF:23ID2-PPS{PSh}Cmd:Cls-Cmd',1)


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

    sleep(5)
    caput('XF:23ID2-PPS{PSh}Cmd:Opn-Cmd',1)
    sleep(2)
    caput('XF:23ID2-OP{FBck}Sts:FB-Sel',1)


def test():
    yield from abs_set(pgm_energy, 890, wait=True)
    yield from E_ramp(890, 895, 0.1, deadband=8)

def find_sample():
        # gs no longer supported
    #gs.TABLE_COLS.append('vortex_mca_rois_roi2_count')
    #gs.PLOT_Y = 'vortex_mca_rois_roi2_count'
#    mov(vortex.mca.rois.roi2.lo_chan, 1400)
#    mov(vortex.mca.rois.roi2.hi_chan, 2000)
    mov(pgm_energy, 932)
    sleep(2)
    RE(ascan(ioxas_x, 245, 295, 250))
    sleep(2)
    #gs.TABLE_COLS.remove('vortex_mca_rois_roi2_count')
    #gs.PLOT_Y = 'vortex_mca_rois_roi4_count'

