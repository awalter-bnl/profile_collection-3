from ophyd import EpicsMotor, PVPositioner, PVPositionerPC, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt, FormattedComponent as FmtCpt
from ophyd import (EpicsMCA, EpicsDXP)


class MirrorAxis(PVPositioner):
    readback = Cpt(EpicsSignalRO, 'Mtr_MON')
    setpoint = Cpt(EpicsSignal, 'Mtr_POS_SP')
    actuate = FmtCpt(EpicsSignal, '{self.parent.prefix}}}MOVE_CMD.PROC')
    actual_value = 1
    stop_signal = FmtCpt(EpicsSignal, '{self.parent.prefix}}}STOP_CMD.PROC')
    stop_value = 1
    done = FmtCpt(EpicsSignalRO, '{self.parent.prefix}}}BUSY_STS')
    done_value = 0


class Mirror(Device):
    z = Cpt(MirrorAxis, '-Ax:Z}')
    y = Cpt(MirrorAxis, '-Ax:Y}')
    x = Cpt(MirrorAxis, '-Ax:X}')
    pit = Cpt(MirrorAxis, '-Ax:Pit}')
    yaw = Cpt(MirrorAxis, '-Ax:Yaw}')
    rol = Cpt(MirrorAxis, '-Ax:Rol}')


class MotorMirror(Device):
    "a mirror with EpicsMotors, used for M3A"
    x = Cpt(EpicsMotor, '-Ax:XAvg}Mtr')
    pit = Cpt(EpicsMotor, '-Ax:P}Mtr')
    bdr = Cpt(EpicsMotor, '-Ax:Bdr}Mtr')


# M1A
m1a = Mirror('XF:23IDA-OP:1{Mir:1', name='m1a')
m1b1 = Mirror('XF:23IDA-OP:2{Mir:1A', name='m1b1')
m1b2 = Mirror('XF:23IDA-OP:2{Mir:1B', name='m1b2')

# VLS-PGM
class PGMEnergy(PVPositionerPC):
    readback = Cpt(EpicsSignalRO, '}Enrgy-I')
    setpoint = Cpt(EpicsSignal, '}Enrgy-SP', limits=(200,2200))  # IS THIS LIMITS USAGE CORRECT?
    stop_signal = Cpt(EpicsSignal, '}Cmd:Stop-Cmd')
    stop_value = 1

class MonoFly(Device):
    start = Cpt(EpicsSignal, '}Enrgy:Start-SP')
    stop = Cpt(EpicsSignal, '}Enrgy:Stop-SP')
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

# IOXAS manipulator

ioxas_x = EpicsMotor('XF:23ID2-BI{IOXAS:1-Ax:X}Mtr', name='ioxas_x')
