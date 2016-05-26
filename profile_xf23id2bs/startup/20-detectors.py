# from ophyd.controls import ProsilicaDetector, EpicsSignal, EpicsScaler
from ophyd import EpicsScaler

# CSX-2 Scalar

sclr = EpicsScaler('XF:23ID2-ES{Sclr:1}', name='sclr')
for sig in sclr.channels.signal_names:
    getattr(sclr.channels, sig).name = 'sclr_' + sig.replace('an', '')
sclr.channels.read_attrs = ['chan2', 'chan3', 'chan4']

# Saturn interface for Vortex MCA detector
vortex = Vortex('XF:23ID2-ES{Vortex}', name='vortex')
#vortex.read_attrs = ['mca.spectrum', 'mca.preset_live_time']
#vortex.read_attrs = ['mca.spectrum', 'mca.preset_live_time', 'mca.rois']
vortex.read_attrs = ['mca.rois']
vortex.mca.read_attrs.append('rois')
vortex.mca.rois.read_attrs = ['roi0','roi1','roi2','roi3','roi4']
vortex.configuration_attrs = ['vortex.peaking_time', 'vortex.energy_threshold', 'mca.rois.roi4.hi_chan',
                              'mca.rois.roi4.lo_chan']
#gs.TABLE_COLS = ['vortex_mca_rois_roi4_count']; gs.PLOT_Y = 'vortex_mca_rois_roi4_count'

