from ophyd import EpicsMotor, PVPositioner, PVPositionerPC, EpicsSignal, EpicsSignalRO, Device
from ophyd.areadetector.base import EpicsSignalWithRBV
from ophyd import Component as Cpt, FormattedComponent as FmtCpt
from ophyd import (EpicsMCA, EpicsDXP)
from bluesky.plan_stubs import mv, sleep

class MirrorAxis(PVPositioner):
    readback = Cpt(EpicsSignalRO, 'Mtr_MON')
    setpoint = Cpt(EpicsSignal, 'Mtr_POS_SP')
    actuate = FmtCpt(EpicsSignal, '{self.parent.prefix}}}MOVE_CMD.PROC')
    actual_value = 1
    stop_signal = FmtCpt(EpicsSignal, '{self.parent.prefix}}}STOP_CMD.PROC')
    stop_value = 1
    done = FmtCpt(EpicsSignalRO, '{self.parent.prefix}}}BUSY_STS')
    done_value = 0

class FeedbackLoop(Device):
    # this is added to allow for bluesky control of an M1b feedback loop
    # implemented at the IOC layer
    enable = Cpt(EpicsSignalWithRBV, 'Sts:FB-Sel', name='enable')
    setpoint = Cpt(EpicsSignalWithRBV, 'PID-SP', name='setpoint')
    requested_value = Cpt(EpicsSignalWithRBV, 'PID.VAL', name='requested_value')
    actual_value = Cpt(EpicsSignalRO, 'PID.CVAL', name='actual_value')
    output_value = Cpt(EpicsSignalRO, 'PID.OVAL', name='output_value')
    error = Cpt(EpicsSignalRO, 'PID.Err', name='error')
    high_limit = Cpt(EpicsSignal, 'PID.DRVH', name='high_limit')
    low_limit = Cpt(EpicsSignal, 'PID.DRVL', name='low_limit')
    delta_t = Cpt(EpicsSignalRO, 'PID.DT', name='delta_t')
    min_delta_t = Cpt(EpicsSignal, 'PID.MDT', name='min_delta_t')
    scan_mode = Cpt(EpicsSignal, 'PID.SCAN', name='scan_mode')
    deadband = Cpt(EpicsSignalWithRBV, 'Val:Sbl-SP', name='deadband')

class Mirror(Device):
    z = Cpt(MirrorAxis, '-Ax:Z}')
    y = Cpt(MirrorAxis, '-Ax:Y}')
    x = Cpt(MirrorAxis, '-Ax:X}')
    pit = Cpt(MirrorAxis, '-Ax:Pit}')
    yaw = Cpt(MirrorAxis, '-Ax:Yaw}')
    rol = Cpt(MirrorAxis, '-Ax:Rol}')

class M1bMirror(Mirror):
    # adds a feedback loop component to a Mirror Device for the m1b mirror
    fbl = Cpt(FeedbackLoop, 'XF:23ID2-OP{FBck}', add_prefix='')

class MotorMirror(Device):
    "a mirror with EpicsMotors, used for M3A"
    x = Cpt(EpicsMotor, '-Ax:XAvg}Mtr')
    pit = Cpt(EpicsMotor, '-Ax:P}Mtr')
    bdr = Cpt(EpicsMotor, '-Ax:Bdr}Mtr')


# M1A
m1a = Mirror('XF:23IDA-OP:1{Mir:1', name='m1a')
m1b1 = M1bMirror('XF:23IDA-OP:2{Mir:1A', name='m1b1')
m1b2 = Mirror('XF:23IDA-OP:2{Mir:1B', name='m1b2')

# VLS-PGM
class PGMEnergy(PVPositionerPC):
    readback = Cpt(EpicsSignalRO, '}Enrgy-I')
    setpoint = Cpt(EpicsSignal, '}Enrgy-SP', limits=(200,2200))  # IS THIS LIMITS USAGE CORRECT?
    stop_signal = Cpt(EpicsSignal, '}Cmd:Stop-Cmd')
    stop_value = 1

class MonoFly(Device):
    start_sig = Cpt(EpicsSignal, '}Enrgy:Start-SP')
    stop_sig = Cpt(EpicsSignal, '}Enrgy:Stop-SP')
    velocity = Cpt(EpicsSignal, '}Enrgy:FlyVelo-SP')

    fly_start = Cpt(EpicsSignal, '}Cmd:FlyStart-Cmd.PROC')
    fly_stop = Cpt(EpicsSignal, '}Cmd:Stop-Cmd.PROC')
    scan_status = Cpt(EpicsSignalRO, '}Sts:Scan-Sts', string=True)

class PGM(Device):
    energy = Cpt(PGMEnergy, '')
    pit = Cpt(EpicsMotor, '-Ax:MirP}Mtr')
    x = Cpt(EpicsMotor, '-Ax:MirX}Mtr')
    grt_pit = Cpt(EpicsMotor, '-Ax:GrtP}Mtr')
    grt_x = Cpt(EpicsMotor, '-Ax:GrtX}Mtr')
    fly = Cpt(MonoFly, '')
    move_status = Cpt(EpicsSignalRO, '}Sts:Move-Sts', string=True)

    def reset_fbl(self, energy, epu_lookup_table=None, epu_input_offset=None,
                  fbl_setpoint=None):
        '''This function performs the process used to reset the feedback loop.

        The aim of this function is to reset the m1b feedback loop (fbl) for
        the requested photon energy. It performs the steps:
        1. Disables the feedback loop if it is enabled.
        2. Changes the EPU lookup table and/or epu input_offset if requested.
        3. Sets the requested PGM energy (which also sets a new EPU gap).
        4. Sets a new fbl position setpoint if requested.
        5. Enables the feedback loop.
        6. Waits 5s for the feedback loop to reposition the m1b mirror.
        7. Returns the feedback loop enable status to its initial value.

        Parameters
        ----------
        energy : float
            The energy value to use when resetting the feedback loop
        epu_lookup_table : str, optional
            The epu lookup table to use with this energy, default value is the
            currently used table.
        epu_input_offset : float, optional
            The offset value to use against the selected epu_table, default is
            the current value.
        fbl_setpoint : int, optional
            The position t which the beam should be located (in pixels) for the
            fbl, default is the current value.
        '''

        initial_fbl_status = m1b2.enable.read()['m1b2_fbl_enable']['value']

        yield from mv(m1b1.fbl.enable, 0)  # turn off the fbl
        if epu_lookup_table:
            yield from mv(epu1.flt.table, epu_lookup_table)
            # need to add mv to new epu lookup table here when it exists
        if epu_input_offset:
            yield from mv(epu1.flt.input_offset, epu_input_offset)

        yield from mv(pgm.energy, energy)  # move to the requested energy

        if fbl_setpoint:
            yield from mv(m1b1, fbl_setpoint)  # set the new setpoint value
        yield from mv(m1b1.fbl.enable, 0)  # turn on the fbl
        yield from sleep(5)  # wait 5s for the feedback loop to reposition the beam
        yield from mv(m1b1.fbl.enable, initial_fbl_status)  # return to initial


pgm = PGM('XF:23ID2-OP{Mono', name='pgm')
#pgm_en = PGMEnergy('XF:23ID1-OP{Mono', name='pgm_en')
pgm_energy = pgm.energy
pgm_energy.name = 'pgm_energy'
pgm.energy.read_attrs = ['readback', 'setpoint']

class SlitsGapCenter(Device):
    xg = Cpt(EpicsMotor, '-Ax:XGap}Mtr')
    xc = Cpt(EpicsMotor, '-Ax:XCtr}Mtr')
    yg = Cpt(EpicsMotor, '-Ax:YGap}Mtr')
    yc = Cpt(EpicsMotor, '-Ax:YCtr}Mtr')


# Slits
slt1 = SlitsGapCenter('XF:23ID2-OP{Slt:1', name='slt1')
slt2 = EpicsMotor('XF:23ID2-OP{Slt:2-Ax:Y}Mtr', name='slt2')



# Diagnostic Manipulators

diag1_y = EpicsMotor('XF:23ID2-BI{Diag:1-Ax:Y}Mtr', name='diag1_y')
diag3_y = EpicsMotor('XF:23ID2-BI{Diag:3-Ax:Y}Mtr', name='diag3_y')
diag4_y = EpicsMotor('XF:23ID2-BI{Diag:4-Ax:Y}Mtr', name='diag4_y')
au_mesh = EpicsMotor('XF:23ID2-BI{AuMesh:1-Ax:Y}Mtr', name='au_mesh')

# IOXAS manipulator

ioxas_x = EpicsMotor('XF:23ID2-BI{IOXAS:1-Ax:X}Mtr', name='ioxas_x')

# Vortex manipulator

vortex_x = EpicsMotor('XF:23ID2-BI{Vortex:1-Ax:X}Mtr', name='vortex_x')

# APPES manipulator

appes_y = EpicsMotor('XF:23ID2-ES{APPES:1-Ax:Y}Mtr', name='appes_y')
appes_x = EpicsMotor('XF:23ID2-ES{APPES:1-Ax:X}Mtr', name='appes_x')
appes_z = EpicsMotor('XF:23ID2-ES{APPES:1-Ax:Z}Mtr', name='appes_z')
appes_t = EpicsMotor('XF:23ID2-ES{APPES:1-Ax:R}Mtr', name='appes_t')
