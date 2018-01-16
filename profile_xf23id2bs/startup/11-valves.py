

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

