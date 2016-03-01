# from ophyd.controls import ProsilicaDetector, EpicsSignal, EpicsScaler
from ophyd import EpicsScaler

# CSX-2 Scalar

sclr = EpicsScaler('XF:23ID2-ES{Sclr:1}', name='sclr')
for sig in sclr.channels.signal_names:
    getattr(sclr.channels, sig).name = 'sclr_' + sig.replace('an', '')
