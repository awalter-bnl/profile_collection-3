#new figure feature
import os
import json
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
import uuid
from cycler import cycler
import pandas as pd

def relabel_fig(fig, new_label):
    fig.set_label(new_label)
    fig.canvas.manager.set_window_title(fig.get_label())

# NOTE : This now requires DETS as a list
def multi_part_ascan(DETS, motor1, steps, motor2, asc_p):
    for d in steps:
        yield from bps.abs_set(motor1, d, wait=True)
        yield from bp.scan(DETS, motor2, *asc_p)

def open_all_valves(valve_list):
    '''Open all the listed valves

    Parameters
    ----------
    valve_list : sequence
        The valves to open

    '''
    for v in valve_list:
        yield from bps.abs_set(v, 1, group='valve_set')
    yield from bps.wait('valve_set')
    # sleep might not be needed
    yield from bps.sleep(2)

_edge_fn = os.path.join(os.path.dirname(__file__), 'edge_map.json')
with open(_edge_fn, 'rt') as fin:
    EDGE_MAP = json.load(fin)

def save_edge_map(edge_map, fname=None):
    if fname is None:
        fname = _edge_fn
    with open(fname, 'wt') as fout:
        json.dump(edge_map, fout, indent=4)



CONTAINER = None
SAMPLE_MAP = {'sample1': {'name': 'AS-21_Spent', 'pos': 252, 'interesting_edges': []},
              'sample2': {'name': 'AS-21', 'pos': 259, 'interesting_edges': []},
              'sample3': {'name': 'AS-4-1_Spent', 'pos': 267, 'interesting_edges': []},
              'sample4': {'name': '30CoCeO2', 'pos': 276, 'interesting_edges': ['Ce_M', 'Co_L2', 'O_K']},
              'sample5': {'name': '8CoCeO2', 'pos': 282, 'interesting_edges': ['Ce_M2', 'Co_L', 'O_K']},
              'sample6': {'name': '2CoCeO2', 'pos': 290, 'interesting_edges': ['Ce_M', 'Co_L', 'O_K2']},
}

DET_SETTINGS = {'O_K': {'samplegain': '2', 'sampledecade': '1 nA/V', 'aumeshgain': '5', 'aumeshdecade': '1 nA/V', 'vortex_pos': -220, 'scan_count': 2},
              'Ce_M': {'samplegain': '2', 'sampledecade': '1 nA/V', 'aumeshgain': '2', 'aumeshdecade': '1 nA/V', 'vortex_pos': -220, 'scan_count': 2},
              'Co_L': {'samplegain': '1', 'sampledecade': '1 nA/V', 'aumeshgain': '2', 'aumeshdecade': '1 nA/V', 'vortex_pos': -220, 'scan_count': 2},
          'Co_L2': {'samplegain': '5', 'sampledecade': '1 nA/V', 'aumeshgain': '2', 'aumeshdecade': '1 nA/V', 'vortex_pos': -220, 'scan_count':2},
          'Ce_M2': {'samplegain': '1', 'sampledecade': '1 nA/V', 'aumeshgain': '2', 'aumeshdecade': '1 nA/V', 'vortex_pos': -220, 'scan_count': 2},
          'O_K2': {'samplegain': '1', 'sampledecade': '1 nA/V', 'aumeshgain': '5', 'aumeshdecade': '1 nA/V', 'vortex_pos': -220, 'scan_count': 2},
}



for k in SAMPLE_MAP:
    samp = SAMPLE_MAP[k]
    samp['sample_index'] = k
    res = list(sample_reference.find(name=samp['name']))
    if res:
        sample_reference.update(query={'name': samp['name']},
                                update=samp
                                )
    else:
        sample_reference.create(**SAMPLE_MAP[k], container=CONTAINER)



def load_samples(fname, container=CONTAINER):
    f = pd.read_excel(fname).dropna()
    SAMPLE_MAP2 = dict()
    loaded_excel = f.T.to_dict().values()
    for entry in loaded_excel:
        samp_idx = entry.pop('sample_index')
        entry['interesting_edges'] = str(entry['interesting_edges']).split(', ')
        entry['sample_index'] = samp_idx
        SAMPLE_MAP2[samp_idx] = entry
    for k in SAMPLE_MAP2:
        samp = SAMPLE_MAP2[k]
        res = list(sample_reference.find(name=samp['name']))
        if res:
            sample_reference.update(query={'name': samp['name']},
                                    update=samp
                                )
        else:
            sample_reference.create(**SAMPLE_MAP2[k], container=container)
    return SAMPLE_MAP2

def load_det_settings(fname, container=CONTAINER):
    f = pd.read_excel(fname).dropna()
    SAMPLE_MAP2 = dict()
    loaded_excel = f.T.to_dict().values()
    for entry in loaded_excel:
        edge_idx = entry.pop('edge_index')
        entry['samplegain'] = str(entry['samplegain'])
        entry['aumeshgain'] = str(entry['aumeshgain'])
        entry['edge_index'] = edge_idx
        SAMPLE_MAP2[edge_idx] = entry
#    for k in SAMPLE_MAP2:
#        samp = SAMPLE_MAP2[k]
#        res = list(sample_reference.find(name=samp['name']))
#        if res:
#            sample_reference.update(query={'name': samp['name']},
#                                    update=samp
#                                    )
#        else:
#            sample_reference.create(**SAMPLE_MAP2[k], container=container)
    return SAMPLE_MAP2

def load_scan_parameters(fname, container=CONTAINER):
    f = pd.read_excel(fname).dropna()
    SAMPLE_MAP2 = dict()
    loaded_excel = f.T.to_dict().values()
    for entry in loaded_excel:
        edge_idx = entry.pop('edge_index')
        entry['edge_index'] = edge_idx
        SAMPLE_MAP2[edge_idx] = entry
    return SAMPLE_MAP2

# SAMPLE_MAP = load_samples('/home/xf23id2/Desktop/mock_sample.xlsx', container=CONTAINER)

VORTEX_SETTINGS = {'Cu_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 900,
                            'mca.rois.roi4.hi_chan': 1200},

                   'Ni_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 800,
                            'mca.rois.roi4.hi_chan': 1000},

                   'Al_K': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 1500,
                            'mca.rois.roi4.hi_chan': 1900},

                   'Fe_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 700,
                            'mca.rois.roi4.hi_chan': 900},

                   'Ti_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 400,
                            'mca.rois.roi4.hi_chan': 600},

                   'O_K': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 500,
                            'mca.rois.roi4.hi_chan': 700},

                   'O_K_IPFY': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi3.lo_chan': 500,
                            'mca.rois.roi3.hi_chan': 700},

                   'O_K2': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 500,
                            'mca.rois.roi4.hi_chan': 700},


                   'Zn_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 900,
                            'mca.rois.roi4.hi_chan': 1150},

                   'Mo_M': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 400,
                            'mca.rois.roi4.hi_chan': 700},

                   'Si_K': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 1800,
                            'mca.rois.roi4.hi_chan': 2200},

                   'Co_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 700,
                            'mca.rois.roi4.hi_chan': 1000},

                   'Co_L2': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 700,
                            'mca.rois.roi4.hi_chan': 1000},

                   'Ce_M': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 900,
                            'mca.rois.roi4.hi_chan': 1100},


                   'Ce_M2': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 900,
                            'mca.rois.roi4.hi_chan': 1100},

                   'Ga_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 1000,
                            'mca.rois.roi4.hi_chan': 1300},
                   'Rh_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 1600,
                            'mca.rois.roi4.hi_chan': 1800},
                   'Mn_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 700,
                            'mca.rois.roi4.hi_chan': 800},
}



def edge_ascan(sample_name, edge, md=None):
    '''Run a multi-edge nexafs scan for single sample and edge

    Parameters
    ----------
    sample_name : str
        Base sample name

    sample_position : float
        Postion of sample on manipulator arm

    edge : str
        Key into EDGE_MAP


    '''
    if md is None:
        md = {}
    local_md = {'plan_name': 'edge_ascan'}
    local_md['edge'] = edge
    md = ChainMap(md, local_md)

    e_scan_params = EDGE_MAP[edge]
    # TODO configure the vortex
    det_settings = DET_SETTINGS[edge]
    sample_props = SAMPLE_MAP[sample_name]
#    sample_props = list(sample_manager.find(name=sample_name))
    local_md.update(sample_props)

    # init_group = 'ME_INIT_' + str(uuid.uuid4())
    yield from bps.abs_set(ioxas_x, sample_props['pos'], wait=True)
    yield from bps.abs_set(feedback, 0, wait=True)
    yield from bps.abs_set(pgm_energy, e_scan_params['start'], wait=True)
    yield from bps.abs_set(epu1table, e_scan_params['epu_table'], wait=True)
    yield from bps.abs_set(feedback, 1, wait=True)
    yield from bps.abs_set(vortex_x, det_settings['vortex_pos'], wait=True)
    yield from bps.abs_set(sample_sclr_gain, det_settings['samplegain'], wait=True)
    yield from bps.abs_set(sample_sclr_decade, det_settings['sampledecade'], wait=True)
    yield from bps.abs_set(aumesh_sclr_gain, det_settings['aumeshgain'], wait=True)
    yield from bps.abs_set(aumesh_sclr_decade, det_settings['aumeshdecade'], wait=True)
 #   yield from open_all_valves(all_valves)
    # yield from bp.wait(init_group)

# TODO make this an ohypd obj!!!!!!
    #caput('XF:23IDA-PPS:2{PSh}Cmd:Opn-Cmd',1)
#   yield from bp.sleep(2)
    # TODO make this an ohypd obj!!!!!!
    # TODO ask stuart
    #caput('XF:23IDA-OP:2{Mir:1A-Ax:FPit}Mtr_POS_SP',50)
    yield from bps.sleep(5)

    yield from bps.configure(vortex, VORTEX_SETTINGS[edge])
    yield from bps.sleep(2)
    yield from bps.abs_set(vortex.mca.rois.roi4.lo_chan, det_settings['vortex_low'], wait=True)
    yield from bps.abs_set(vortex.mca.rois.roi4.hi_chan, det_settings['vortex_high'], wait=True)


    lp_list = []
    for n in ['sclr_ch4', 'vortex_mca_rois_roi4_count']:
        fig = plt.figure(edge + ': ' + n)
        lp = bs.callbacks.LivePlot(n, 'pgm_energy_readback', fig=fig)
        lp_list.append(lp)

#    class norm_plot(bs.callbacks.LivePlot):
#        def event(self,doc):
#            try:
#                doc.data['norm_intensity'] = doc.data['sclr_ch4']/doc.data['sclr_ch3']
#            except KeyError:
#                pass
#            super().event(doc)

#    for n in ['sclr_ch4']:
#        fig = plt.figure(edge + ': ' + n)
        # lp = bs.callbacks.LivePlot(n, 'pgm_energy_readback', fig=fig)
#        lp = norm_plot('norm_intensity', 'pgm_energy_readback', fig=fig)
#        lp_list.append(lp)

    scan_kwargs = {'start': e_scan_params['start'],
                   'stop': e_scan_params['stop'],
                   'velocity': e_scan_params['velocity'],
                   'deadband': e_scan_params['deadband'],
                   'md': md}
    ret = []
    for j in range(e_scan_params['scan_count']):
        tmp_pos = sample_props['pos'] + (j-((e_scan_params['scan_count']-1)/2))*e_scan_params['intervals']
        yield from bps.abs_set(ioxas_x, tmp_pos, wait=True)
        yield from bps.abs_set(pgm_energy, e_scan_params['start'], wait=True)
        yield from open_all_valves(all_valves)
        res = yield from bpp.subs_wrapper(E_ramp(**scan_kwargs), {'all': lp_list,
                                                                 'stop': save_csv})
        yield from bps.abs_set(valve_diag3_close, 1, wait=True)
        yield from bps.abs_set(valve_mir3_close, 1, wait=True)
        yield from bps.sleep(5)
        if res is None:
            res = []
        ret.extend(res)
        if not ret:
            return ret


    # hdr = db[ret[0]]
    # redo_count = how_many_more_times_to_take_data(hdr)
    # for j in range(redo_count):
    #     res = yield from bpp.subs_wrapper(ascan(*scan_args, md=md), lp)
    #     ret.extend(res)


    # new_count_time = compute_new_count_time(hdr, old_count_time)
    # if new_count_time != old_count_time:
    #     yield from bps.configure(vortex, {'count_time': new_count_time})
    #     res = yield from bpp.subs_wrapper(ascan(*scan_args, md=md), lp)
    #     ret.extend(res)

    return ret

#def how_many_more_times_to_take_data(hdr):
#    table = db.get_table()
#    return int(15 // (table.sclr2.max() / table.sclr2.min()))

def pass_filter(sample_name, edge):
    return edge in SAMPLE_MAP[sample_name]['interesting_edges']


def multi_sample_edge(*, edge_list=None, sample_list=None):
    if sample_list is None:
        sample_list = list(SAMPLE_MAP)
    if edge_list is None:
        edge_list = list(EDGE_MAP)
#    edge_list = sorted(edge_list, key=lambda k: EDGE_MAP[k]['start'])
    cy = cycler('edge', edge_list) * cycler('sample_name', sample_list)
    for inp in cy:
        if pass_filter(**inp):
            yield from edge_ascan(**inp)
    yield from bps.abs_set(valve_diag3_close, 1)
    yield from bps.abs_set(valve_mir3_close, 1)

def dummy_edge_scan(sample_name, edge, md=None):
    from bluesky.examples import det, motor, det2

    if md is None:
        md = {}
    local_md = {'plan_name': 'edge_ascan'}
    md = ChainMap(md, local_md)

    e_scan_params = EDGE_MAP[edge]
    # TODO configure the vortex

    sample_props = SAMPLE_MAP[sample_name]
    # sample_props = list(sample_manager.find(sample_name))[0]
    local_md.update(sample_props)
    lp_list = []
    for n in ['det', 'det2']:
        fig = plt.figure(edge + ': ' + n)
        lp = bs.callbacks.LivePlot(n, 'motor', fig=fig)
        lp_list.append(lp)
    yield from bpp.subs_wrapper(bp.relative_scan([det, det2], motor, -5, 5, 15, md=md),
                               lp_list)


def save_csv(name, stop_doc):
    h = db[stop_doc['run_start']]
    df = db.get_table(h)
    df['Norm_TEY'] = df['sclr_ch4'] / df['sclr_ch3']
    df['Norm_PFY'] = df['vortex_mca_rois_roi4_count'] / df['sclr_ch3']
    fn = '{name}_{edge}_{scan_id}.csv'.format(**h.start)
    df.to_csv(fn,columns=['pgm_energy_readback', 'sclr_ch3', 'sclr_ch4', 'vortex_mca_rois_roi4_count', 'Norm_TEY', 'Norm_PFY'])


#def save_csv_callback(name, doc):

#    if name != 'stop':
#        return
#    print(doc)
#    start_doc = doc['run_start']
#    hdr = db[start_doc]
#    if
#    table = db.get_table(hdr)

#    fn_template = '/tmp/scan_{name}.csv'
#    file_name = fn_template.format(**hdr['start'])
#    table.to_csv(file_name, index=False)
#    print('saved CVS to: {!r}'.format(file_name))
