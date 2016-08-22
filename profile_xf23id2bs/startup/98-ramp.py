from bluesky.plans import *
from ophyd import StatusBase
import time
from bluesky.spec_api import inner_spec_decorator, setup_plot, setup_livetable

def ramp_plan(configuration_plan,
              go_plan,
              monitor_sig,
              inner_plan_func,
              timeout=None,
              period=None, md=None):
    '''Take data while ramping one or more positioners.

    The pseudo code for this plan is ::

       yield from configure_plan
       sts = (yield from open_run())
       yield from inner_plan_func()
       while not st.don:
           yield from inner_plan_func()
       yield from inner_plan_func()
       yield from close_run()
    Parameters
    ----------
    configuration_plan : iterable
        plan to set the system
    go_plan : iterable
        plan to start the ramp.  This will be run inside of a open/close
        run.
        This plan must return a status object.
    inner_plan_func : generator function
        generator which takes no input
        This will be called for every data point.  This should create
        one or more events.
    timeout : float, optional
        If not None, the maximum time the ramp can run.
        In seconds
    period : fload, optional
        If not None, take data no faster than this.  If None, take
        data as fast as possible
        If running the inner plan takes longer than `period` than take
        data with no dead time.
        In seconds.
    '''
    if md is None:
        md = {}

    @monitor_during_decorator((monitor_sig,))
    @run_decorator(md=md)
    def polling_plan():
        # sort out if we should watch the clock
        fail_time = None
        last_time = None
        if timeout is not None:
            fail_time = time.time() + timeout
        if period:
            last_time = time.time()

        
        # take a 'pre' data point
        yield from inner_plan_func()
        # start the ramp
        status = (yield from go_plan)

        while not status.done:
            yield from inner_plan_func()
            if fail_time is not None:
                if time.time() > fail_time:
                    raise RampFail()
            if period is not None:
                cur_time = time.time()
                wait_time = (last_time + period) - cur_time
                last_time = cur_time
                if wait_time > 0:
                    yield from sleep(wait_time)

        # take a 'post' data point
        yield from inner_plan_func()

    return (yield from configuration_plan(polling_plan()))


def change_epu_flt_link(new_target):
    v = (yield from read(epu1.flt.input_pv))
    if v is None:
        return
    n = epu1.flt.input_pv.name
    cur_pv = v[n]['value']
    pts = cur_pv.split(' ', maxsplit=1)
    new_pv = ' '.join([new_target] + pts[1:])
    yield from abs_set(epu1.flt.input_pv, new_pv)
    

def conf_plan(polling_plan):
    # get the old vlaue
    v = (yield from read(epu1.flt.input_pv))
    if v is None:
        old_link = ''
    else:
        n = epu1.flt.input_pv.name
        old_link = v[n]['value']

    # define a clean up plan
    def clean_up():
        yield from abs_set(pgm.energy, stop, wait=True)
        yield from abs_set(epu1.flt.input_pv, old_link)

    
    # change to track the readout energy
    yield from change_epu_flt_link(pgm_energy.readback.pvname)
    
    return (yield from finalize_wrapper(polling_plan, clean_up()))


def _run_E_ramp(dets, start, stop, velocity, *, md=None):
    # put the energy at the starting value
    yield from abs_set(pgm.energy, start, wait=True)

    yield from abs_set(pgm.fly.start, start, wait=True)
    yield from abs_set(pgm.fly.stop, stop, wait=True)
    yield from abs_set(pgm.fly.velocity, velocity, wait=True)

    
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

    ret = (yield from ramp_plan(conf_plan, go_plan(), pgm.energy,
                                inner_plan, period=None, md=md))
    return ret
    
def E_ramp(start, stop, velocity, time=None, *, md=None):
    motors = [pgm.energy]
    inner = inner_spec_decorator('E_ramp', time, motors)(_run_E_ramp)

    return (yield from inner(gs.DETS + [pgm.energy], start, stop, velocity, md=md))

gs.SUB_FACTORIES['E_ramp'] = [setup_plot, setup_livetable]
