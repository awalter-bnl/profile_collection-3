# from ophyd.controls import ProsilicaDetector, EpicsSignal, EpicsScaler
from ophyd import EpicsScaler
from ophyd.device import Component as C
from ophyd.device import DynamicDeviceComponent as DDC
from ophyd.scaler import _scaler_fields
from ophyd.signal import waveform_to_string

# CSX-2 Scalar


class DodgyEpicsSignal(EpicsSignal):

    #def read(self):
    #    return {self.name: {'value':self.get(), 'timestamp': self.timestamp}}

    def get(self, *, as_string=None, connection_timeout=1.0, **kwargs):
        '''Get the readback value through an explicit call to EPICS
        Parameters
        ----------
        count : int, optional
            Explicitly limit count for array data
        as_string : bool, optional
            Get a string representation of the value, defaults to as_string
            from this signal, optional
        as_numpy : bool
            Use numpy array as the return type for array data.
        timeout : float, optional
            maximum time to wait for value to be received.
            (default = 0.5 + log10(count) seconds)
        use_monitor : bool, optional
            to use value from latest monitor callback or to make an
            explicit CA call for the value. (default: True)
        connection_timeout : float, optional
            If not already connected, allow up to `connection_timeout` seconds
            for the connection to complete.
        '''
        # NOTE: in the future this should be improved to grab self._readback
        #       instead, when all of the kwargs match up
        if as_string is None:
            as_string = self._string

        with self._lock:
            if not self._read_pv.connected:
                if not self._read_pv.wait_for_connection(connection_timeout):
                    raise TimeoutError('Failed to connect to %s' %
                                       self._read_pv.pvname)
            ret = None
            while ret is None:
                ret = self._read_pv.get(as_string=as_string, **kwargs)
                if ret is None:
                    print('Failed to get value, retrying to read {self}')

        if ret is None:
            ret = np.nan

        if as_string:
            return waveform_to_string(ret)

        return ret




class DodgyEpicsScaler(Device):
    '''SynApps Scaler Record interface'''

    # tigger + trigger mode
    count = C(DodgyEpicsSignal, '.CNT', trigger_value=1)
    count_mode = C(DodgyEpicsSignal, '.CONT', string=True)

    # delay from triggering to starting counting
    delay = C(DodgyEpicsSignal, '.DLY')
    auto_count_delay = C(DodgyEpicsSignal, '.DLY1')

    # the data
    channels = DDC(_scaler_fields(DodgyEpicsSignal, 'chan', '.S', range(1, 33)))
    names = DDC(_scaler_fields(DodgyEpicsSignal, 'name', '.NM', range(1, 33)))

    time = C(DodgyEpicsSignal, '.T')
    freq = C(DodgyEpicsSignal, '.FREQ')

    preset_time = C(DodgyEpicsSignal, '.TP')
    auto_count_time = C(DodgyEpicsSignal, '.TP1')

    presets = DDC(_scaler_fields(DodgyEpicsSignal, 'preset', '.PR', range(1, 33)))
    gates = DDC(_scaler_fields(DodgyEpicsSignal, 'gate', '.G', range(1, 33)))

    update_rate = C(DodgyEpicsSignal, '.RATE')
    auto_count_update_rate = C(DodgyEpicsSignal, '.RAT1')

    egu = C(DodgyEpicsSignal, '.EGU')

    def __init__(self, prefix, *, read_attrs=None, configuration_attrs=None,
                 name=None, parent=None, **kwargs):
        if read_attrs is None:
            read_attrs = ['channels', 'time']

        if configuration_attrs is None:
            configuration_attrs = ['preset_time', 'presets', 'gates',
                                   'names', 'freq', 'auto_count_time',
                                   'count_mode', 'delay',
                                   'auto_count_delay', 'egu']

        super().__init__(prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         name=name, parent=parent, **kwargs)

        self.stage_sigs.update([('count_mode', 0)])
        self.hints = {'fields': ['sclr_ch2', 'sclr_ch3', 'sclr_ch4']}



#sclr = EpicsScaler('XF:23ID2-ES{Sclr:1}', name='sclr')
sclr = DodgyEpicsScaler('XF:23ID2-ES{Sclr:1}', name='sclr')


for sig in sclr.channels.component_names:
    getattr(sclr.channels, sig).name = 'sclr_' + sig.replace('an', '')
sclr.channels.read_attrs = ['chan2', 'chan3', 'chan4']

# Saturn interface for Vortex MCA detector
vortex = Vortex('XF:23ID2-ES{Vortex}', name='vortex')
vortex.hints = {'fields': ['vortex_mca_rois_roi4_count',
                           'vortex_mca_rois_roi3_count']}

#vortex.read_attrs = ['mca.spectrum', 'mca.preset_live_time']
#vortex.read_attrs = ['mca.spectrum', 'mca.preset_live_time', 'mca.rois']
vortex.read_attrs = ['mca.spectrum', 'mca.rois']
#vortex.read_attrs = ['mca.rois']
vortex.mca.read_attrs.append('rois')
vortex.mca.rois.read_attrs = ['roi0','roi1','roi2','roi3','roi4']
vortex.vortex.energy_threshold.tolerance = .005
vortex.configuration_attrs = ['vortex.peaking_time', 'vortex.energy_threshold', 'mca.rois.roi4.hi_chan',
                              'mca.rois.roi4.lo_chan']
#gs.TABLE_COLS = ['vortex_mca_rois_roi4_count']; gs.PLOT_Y = 'vortex_mca_rois_roi4_count'

ring_curr = EpicsSignal('XF:23ID-SR{}I-I', name='ring_curr')
norm_ch4 = EpicsSignal('XF:23ID2-ES{Sclr:1}_calc5.VAL', name='norm_ch4')

DETS = [sclr, norm_ch4, ring_curr]
DETS_V =  [sclr, norm_ch4, ring_curr, vortex]

sample_sclr_gain = EpicsSignal('XF:23ID2-ES{CurrAmp:3}Gain:Val-SP', name='sample_sclr_gain', string=True)
sample_sclr_decade = EpicsSignal('XF:23ID2-ES{CurrAmp:3}Gain:Decade-SP', name='sample_sclr_decade', string=True)

aumesh_sclr_gain = EpicsSignal('XF:23ID2-ES{CurrAmp:2}Gain:Val-SP', name='aumesh_sclr_gain', string=True)
aumesh_sclr_decade = EpicsSignal('XF:23ID2-ES{CurrAmp:2}Gain:Decade-SP', name='aumesh_sclr_decade', string=True)

epu1table = EpicsSignal('XF:23ID-ID{EPU:1}Val:Table-Sel', name='epu1table')

feedback = EpicsSignal('XF:23ID2-OP{FBck}Sts:FB-Sel', name='feedback')
