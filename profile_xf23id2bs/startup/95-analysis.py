import numpy as np

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
                df1['Norm'] = df1['norm_ch4']/dfn['norm_ch4']
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

def plot_norm_pfy_ROI2(scanid1,scanid2,label):
        plt.figure(label)
        label = plt.gca()
        for i in range (scanid1, scanid2+1):
                df1 = db.get_table(db[i])
                df1['Norm'] = df1['vortex_mca_rois_roi2_count']/df1['sclr_ch3']
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

def save_mca(runid, filename, mca_name):
    hdr = db[runid]
    data_all = hdr.table()
    data_mca = data_all[mca_name]
    d = np.vstack(data_mca.values).T
    np.savetxt(filename, d)

