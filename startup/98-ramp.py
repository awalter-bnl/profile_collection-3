# this is already done in nslsii.configure_base but being explicit here
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from collections import ChainMap

from ophyd import StatusBase
import time
#from bluesky.spec_api import inner_spec_decorator, setup_plot, setup_livetable, _figure_name
import bluesky as bs
import builtins
input = builtins.input

def change_epu_flt_link(new_target):
    v = (yield from bps.read(epu1.flt.input_pv))
    if v is None:
        return
    n = epu1.flt.input_pv.name
    cur_pv = v[n]['value']
    pts = cur_pv.split(' ', maxsplit=1)
    new_pv = ' '.join([new_target] + pts[1:])
    yield from bps.abs_set(epu1.flt.input_pv, new_pv)

class NormPlot(bs.callbacks.LivePlot):
    def event(self,doc):
        doc = dict(doc)
        doc['data'] = dict(doc['data'])
        try:
            doc['data']['norm_intensity'] = doc['data']['sclr_ch4']/doc['data']['sclr_ch3']
        except KeyError:
            pass
        super().event(doc)


class norm_plot(bs.callbacks.LivePlot):
    def __init__(self, *args, func, **kwargs):
        super().__init__(*args, **kwargs)
        self._doc_func = func

    def event(self,doc):
        doc = self._doc_func(func)
        super().event(doc)

def simple_norm(doc):
    try:
        doc.data['norm_intensity'] = doc.data['sclr_ch4']/doc.data['sclr_ch3']
    except KeyError:
        pass
    return doc


#This is no longer supported. Define a LivePlot callback or use best effort callback
#def setup_norm_plot(*, motors, gs):
#    """Setup a LivePlot by inspecting motors and gs.
#    If motors is empty, use sequence number.
#    """
#    y_key = gs.PLOT_Y
#    if motors:
#        x_key = first_key_heuristic(list(motors)[0])
#        fig_name = _figure_name('BlueSky {} v {}'.format(y_key, x_key))
#        fig = plt.figure(fig_name)
#        return NormPlot(y_key, x_key, fig=fig)
#    else:
#        fig_name = _figure_name('BlueSky: {} v sequence number'.format(y_key))
#        fig = plt.figure(fig_name)
#        return NormPlot(y_key, fig=fig)


def _run_E_ramp(dets, start, stop, velocity, deadband, *,
                streamname='primary', md=None):
    if md is None:
        md = {}

    md = ChainMap(md, {'plan_args': {'dets': list(map(repr, dets)),
                                     'start': start,
                                     'stop': stop,
                                     'velocity': velocity,
                                     'deadband': deadband},
                       'plan_name': 'E_ramp',
                       'motors': [pgm.energy.name]})
    # put the energy at the starting value
    yield from bps.abs_set(pgm.energy, start, wait=True)

    yield from bps.abs_set(pgm.fly.start_sig, start, wait=True)
    yield from bps.abs_set(pgm.fly.stop_sig, stop, wait=True)
    yield from bps.abs_set(pgm.fly.velocity, velocity, wait=True)

    # TODO do this with stage
    old_db = epu1.flt.output_deadband.get()
    yield from bps.abs_set(epu1.flt.output_deadband, deadband)

    # get the old vlaue
    v = (yield from bps.read(epu1.flt.input_pv))
    if v is None:
        old_link = ''
    else:
        n = epu1.flt.input_pv.name
        old_link = v[n]['value']

    # define a clean up plan
    def clean_up():
        # move the energy setpoint to where the energy really is
        yield from bps.abs_set(pgm.energy, pgm.energy.position, wait=True)
        # set the interpolator to look at what it was looking at before
        # the scan.  This should be the energy set point.
        yield from bps.abs_set(epu1.flt.input_pv, old_link, wait=True)
        yield from bps.abs_set(epu1.flt.output_deadband, old_db, wait=True)

    # change to track the readout energy
    yield from change_epu_flt_link(pgm_energy.readback.pvname)

    def go_plan():
        ret = (yield from bps.abs_set(pgm.fly.fly_start, 1))

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
        yield from trigger_and_read(dets, name=stream)

    print(md)
    rp = ramp_plan(go_plan(), pgm.energy,
                   inner_plan, period=None, md=md)

    return (yield from bpp.finalize_wrapper(rp, clean_up()))


# NOTE : This function has been changed to take DETS as an argument
def E_ramp(dets, start, stop, velocity, time=None, *,
           streamname='primary', deadband=8, md=None):
    '''
        dets: need to supply the detectors used
    '''
    motors = [pgm.energy]
    # DEPRECATED
    #inner = inner_spec_decorator('E_ramp', time, motors)(_run_E_ramp)
    inner = _run_E_ramp

    return (yield from inner(dets + [pgm.energy], start, stop, velocity,
                             streamname=streamname, deadband=deadband, md=md))


# THIS is no longer supported
#gs.SUB_FACTORIES['E_ramp'] = [setup_plot, setup_livetable]
#gs.SUB_FACTORIES['E_ramp'] = [setup_norm_plot, setup_livetable]


def _epu_ramp(dets, start, stop):
    def go_plan():
        return (yield from bps.abs_set(epu1.gap, stop, wait=False))

    def inner_plan():
        yield from trigger_and_read(dets)

    yield from bps.abs_set(epu1.gap, start, wait=True)

    return (yield from (ramp_plan(go_plan(), pgm.energy,
                                  inner_plan, period=None, md=md)))

def fix_epu():
    # move the energy setpoint to where the energy really is
    yield from bps.abs_set(pgm.energy, pgm.energy.position, wait=True)
    # set the interpolator to look at what it was looking at before
    # the scan.  This should be the energy set point.
    yield from bps.abs_set(epu1.flt.input_pv, 'XF:23ID2-OP{Mono}Enrgy-SP CP MS', wait=True)
    yield from bps.abs_set(epu1.flt.output_deadband, 0, wait=True)
