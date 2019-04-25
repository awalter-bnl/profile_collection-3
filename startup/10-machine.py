from ophyd import EpicsMotor, PVPositioner, PVPositionerPC, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt, FormattedComponent as FmCpt

# Undulator

class GapMotor1(PVPositionerPC):
    readback = Cpt(EpicsSignalRO, 'Pos-I')
    setpoint = Cpt(EpicsSignal, 'Pos-SP')
    stop_signal = FmCpt(EpicsSignal,
                        'SR:C23-ID:G1A{EPU:1-Ax:Gap}-Mtr.STOP', add_prefix=())
    stop_value = 1

class PhaseMotor1(PVPositionerPC):
    readback = Cpt(EpicsSignalRO, 'Pos-I')
    setpoint = Cpt(EpicsSignal, 'Pos-SP')
    stop_signal = FmCpt(EpicsSignal,
                        'SR:C23-ID:G1A{EPU:1-Ax:Phase}-Mtr.STOP', add_prefix=())
    stop_value = 1

class GapMotor2(PVPositionerPC):
    readback = Cpt(EpicsSignalRO, 'Pos-I')
    setpoint = Cpt(EpicsSignal, 'Pos-SP')
    stop_signal = FmCpt(EpicsSignal,
                        'SR:C23-ID:G1A{EPU:2-Ax:Gap}-Mtr.STOP', add_prefix=())
    stop_value = 1

class PhaseMotor2(PVPositionerPC):
    readback = Cpt(EpicsSignalRO, 'Pos-I')
    setpoint = Cpt(EpicsSignal, 'Pos-SP')
    stop_signal = FmCpt(EpicsSignal,
                        'SR:C23-ID:G1A{EPU:2-Ax:Phase}-Mtr.STOP', add_prefix=())

    stop_value = 1

class Interpolator(Device):
    input = Cpt(EpicsSignal, 'Val:Inp1-SP')
    input_offset = Cpt(EpicsSignal, 'Val:InpOff1-SP')
    # {'Enabled', 'Disabled'}
    input_link = Cpt(EpicsSignal, 'Enbl:Inp1-Sel', string=True)
    input_pv = Cpt(EpicsSignal, 'Val:Inp1-SP.DOL$', string=True)
    output = Cpt(EpicsSignalRO, 'Val:Out1-I')
    # {'Enable', 'Disable'}
    output_link = Cpt(EpicsSignalRO, 'Enbl:Out1-Sel', string=True)
    output_pv = Cpt(EpicsSignal, 'Calc1.OUT$', string=True)
    output_deadband = Cpt(EpicsSignal, 'Val:DBand1-SP')
    output_drive = Cpt(EpicsSignalRO, 'Val:OutDrv1-I')
    interpolation_status = Cpt(EpicsSignalRO, 'Sts:Interp1-Sts', string=True)
#    table = Cpt(EpicsSignal, 'Val:Table-Sel', name='table')


class EPU1(Device):
    gap = Cpt(GapMotor1, '-Ax:Gap}')
    phase = Cpt(PhaseMotor1, '-Ax:Phase}')
    flt = Cpt(Interpolator, '-FLT}')
    rlt = Cpt(Interpolator, '-RLT}')
    table = Cpt(EpicsSignal, '}Val:Table-Sel', name='table')


class EPU2(Device):
    gap = Cpt(GapMotor2, '-Ax:Gap}')
    phase = Cpt(PhaseMotor2, '-Ax:Phase}')



epu1 = EPU1('XF:23ID-ID{EPU:1', name='epu1')

epu2 = EPU2('XF:23ID-ID{EPU:2', name='epu2')

# Front End Slits (Primary Slits)

# fe_xc = PVPositioner('FE:C23A-OP{Slt:12-Ax:X}center',
#                      readback='FE:C23A-OP{Slt:12-Ax:X}t2.D',
#                      stop='FE:C23A-CT{MC:1}allstop',
#                      stop_val=1, put_complete=True,
#                      name='fe_xc')

# fe_yc = PVPositioner('FE:C23A-OP{Slt:12-Ax:Y}center',
#                      readback='FE:C23A-OP{Slt:12-Ax:Y}t2.D',
#                      stop='FE:C23A-CT{MC:1}allstop',
#                      stop_val=1,
#                      put_complete=True,
#                      name='fe_yc')

# fe_xg = PVPositioner('FE:C23A-OP{Slt:12-Ax:X}size',
#                      readback='FE:C23A-OP{Slt:12-Ax:X}t2.C',
#                      stop='FE:C23A-CT{MC:1}allstop',
#                      stop_val=1, put_complete=True,
#                      name='fe_xg')

# fe_yg = PVPositioner('FE:C23A-OP{Slt:12-Ax:Y}size',
#                      readback='FE:C23A-OP{Slt:12-Ax:Y}t2.C',
#                      stop='FE:C23A-CT{MC:1}allstop',
#                      stop_val=1,
#                      put_complete=True,
#                      name='fe_yg')
