from ophyd.status import DeviceStatus
import datetime
import time
_time_fmtstr = '%Y-%m-%d %H:%M:%S'

valve_diag3 = EpicsSignal('XF:23ID2-VA{Diag:03-GV:1}Cmd:Opn-Cmd', name='valve_diag3')
valve_mir   = EpicsSignal('XF:23ID2-VA{Mir:3-GV:1}Cmd:Opn-Cmd')
valve_slt3  = EpicsSignal('XF:23ID2-VA{Slt:3-GV:1}Cmd:Opn-Cmd')
valve_slt1  = EpicsSignal('XF:23ID2-VA{Slt:1-GV:1}Cmd:Opn-Cmd')
valve_pmp1  = EpicsSignal('XF:23ID2-VA{Pmp:Inl:01-GV:1}Cmd:Opn-Cmd')
valve_pmp2  = EpicsSignal('XF:23ID2-VA{Pmp:Inl:02-GV:1}Cmd:Opn-Cmd')
valve_mono  = EpicsSignal('XF:23ID2-VA{Mon-GV:1}Cmd:Opn-Cmd')
valve_diag1 = EpicsSignal('XF:23ID2-VA{Diag:01-GV:1}Cmd:Opn-Cmd')

all_valves = [valve_diag3,
              valve_mir,
              valve_slt3,
              valve_slt1,
              valve_pmp1,
              valve_pmp2,
              valve_mono,
              valve_diag1]



class Valve(Device):
    open_cmd = Cpt(EpicsSignal, 'Cmd:Opn-Cmd')
    close_cmd = Cpt(EpicsSignal, 'Cmd:Cls-Cmd')
    pos_sts = Cpt(EpicsSignal, 'Pos-Sts')

    # TODO :(
    # def set(self, new_position, *,

valve_appes = Valve('XF:23ID2-VA{APPES-GV:3}', name='valve_appes')

valve_diag3_close = EpicsSignal('XF:23ID2-VA{Diag:03-GV:1}Cmd:Cls-Cmd', name='valve_diag3_close')
valve_mir3_close = EpicsSignal('XF:23ID2-VA{Mir:3-GV:1}Cmd:Cls-Cmd', name='valve_mir3_close')
valve_diag3_open = EpicsSignal('XF:23ID2-VA{Diag:03-GV:1}Cmd:Opn-Cmd', name='valve_diag3_open')
valve_mir3_open = EpicsSignal('XF:23ID2-VA{Mir:3-GV:1}Cmd:Opn-Cmd', name='valve_mir3_open')

mirror_feedback = EpicsSignal('XF:23ID2-OP{FBck}Sts:FB-Sel', name='mirror_feedback')

class TwoButtonShutter(Device):
    # TODO this needs to be fixed in EPICS as these names make no sense
    # the vlaue comingout of the PV do not match what is shown in CSS
    open_cmd = Cpt(EpicsSignal, 'Cmd:Opn-Cmd', string=True)
    open_val = 'Not Closed'

    close_cmd = Cpt(EpicsSignal, 'Cmd:Cls-Cmd', string=True)
    close_val = 'Closed'

    status = Cpt(EpicsSignalRO, 'Pos-Sts', string=True)
    fail_to_close = Cpt(EpicsSignalRO, 'Sts:FailCls-Sts', string=True)
    fail_to_open = Cpt(EpicsSignalRO, 'Sts:FailOpn-Sts', string=True)
    # user facing commands
    open_str = 'Open'
    close_str = 'Close'

    def set(self, val):
        if self._set_st is not None:
            raise RuntimeError('trying to set while a set is in progress')

        cmd_map = {self.open_str: self.open_cmd,
                   self.close_str: self.close_cmd}
        target_map = {self.open_str: self.open_val,
                      self.close_str: self.close_val}

        cmd_sig = cmd_map[val]
        target_val = target_map[val]

        st = self._set_st = DeviceStatus(self)
        enums = self.status.enum_strs

        def shutter_cb(value, timestamp, **kwargs):
            value = enums[int(value)]
            if value == target_val:
                self._set_st._finished()
                self._set_st = None
                self.status.clear_sub(shutter_cb)

        cmd_enums = cmd_sig.enum_strs
        count = 0
        def cmd_retry_cb(value, timestamp, **kwargs):
            nonlocal count
            value = cmd_enums[int(value)]
            # ts = datetime.datetime.fromtimestamp(timestamp).strftime(_time_fmtstr)
            # print('sh', ts, val, st)
            count += 1
            if count > 5:
                cmd_sig.clear_sub(cmd_retry_cb)
                st._finished(success=False)
            if value == 'None':
                if not st.done:
                    time.sleep(.5)
                    cmd_sig.set(1)
                    ts = datetime.datetime.fromtimestamp(timestamp).strftime(_time_fmtstr)
                    print('** ({}) Had to reactuate shutter while {}ing'.format(ts, val))
                else:
                    cmd_sig.clear_sub(cmd_retry_cb)

        cmd_sig.subscribe(cmd_retry_cb, run=False)
        cmd_sig.set(1)
        self.status.subscribe(shutter_cb)


        return st

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_st = None
        self.read_attrs = ['status']

ds_shutter = TwoButtonShutter('XF:23ID2-PPS{PSh}', name='ds_shutter')
us_shutter = TwoButtonShutter('XF:23ID2-PPS:2{PSh}', name='us_shutter')
