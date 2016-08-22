from bluesky.plans import *
from ophyd import StatusBase
import time
from bluesky.spec_api import inner_spec_decorator, setup_plot, setup_livetable

def change_epu_flt_link(new_target):
    v = (yield from read(epu1.flt.input_pv))
    if v is None:
        return
    n = epu1.flt.input_pv.name
    cur_pv = v[n]['value']
    pts = cur_pv.split(' ', maxsplit=1)
    new_pv = ' '.join([new_target] + pts[1:])
    yield from abs_set(epu1.flt.input_pv, new_pv)

    
def _run_E_ramp(dets, start, stop, velocity, *, md=None):
    # put the energy at the starting value
    yield from abs_set(pgm.energy, start, wait=True)

    yield from abs_set(pgm.fly.start, start, wait=True)
    yield from abs_set(pgm.fly.stop, stop, wait=True)
    yield from abs_set(pgm.fly.velocity, velocity, wait=True)

    # get the old vlaue
    v = (yield from read(epu1.flt.input_pv))
    if v is None:
        old_link = ''
    else:
        n = epu1.flt.input_pv.name
        old_link = v[n]['value']

    # define a clean up plan
    def clean_up():
        # move the energy setpoint to where the energy really is
        yield from abs_set(pgm.energy, pgm.energy.position, wait=True)
        # set the interpolator to look at what it was looking at before
        # the scan.  This should be the energy set point.
        yield from abs_set(epu1.flt.input_pv, old_link)
    
    # change to track the readout energy
    yield from change_epu_flt_link(pgm_energy.readback.pvname)
    
    def go_plan():
        ret = (yield from abs_set(pgm.fly.fly_start, 1))
        
        st = StatusBase()
        enum_map = pgm.fly.scan_status.describe()[pgm.fly.scan_status.name]['enum_strs']
        def _done_cb(value, old_value, **kwargs):
            old_value = enum_map[int(old_value)]
            value = enum_map[int(value)]
            if old_value != value and value == 'Ready':
                st._finished()
                pgm.fly.scan_status.clear_sub(_done_cb)
                
        if ret is not None:
            pgm.fly.scan_status.subscribe(_done_cb, run=False)
        else:
            st._finished()
            print('SIM MODE')

        return st

    def inner_plan():
        yield from trigger_and_read(dets)

    rp = ramp_plan(go_plan(), pgm.energy,
                   inner_plan, period=None, md=md)
        
    return (yield from finalize_wrapper(rp, clean_up()))

    
def E_ramp(start, stop, velocity, time=None, *, md=None):
    motors = [pgm.energy]
    inner = inner_spec_decorator('E_ramp', time, motors)(_run_E_ramp)

    return (yield from inner(gs.DETS + [pgm.energy], start, stop, velocity, md=md))

gs.SUB_FACTORIES['E_ramp'] = [setup_plot, setup_livetable]


def _epu_ramp(dets, start, stop):
    def go_plan():
        return (yield from abs_set(epu1.gap, stop, wait=False))

    def inner_plan():
        yield from trigger_and_read(dets)

    yield from abs_set(epu1.gap, start, wait=True)
        
    return (yield from (ramp_plan(go_plan(), pgm.energy,
                                  inner_plan, period=None, md=md)))
