#new figure feature
import bluesky.plans as bp
import bluesky as bs
import uuid
from cycler import cycler

def relabel_fig(fig, new_label):
    fig.set_label(new_label)
    fig.canvas.manager.set_window_title(fig.get_label())

def multi_part_ascan(motor1, steps, motor2, asc_p):
    for d in steps:
        yield from bp.abs_set(motor1, d, wait=True)
        yield from bp.scan(gs.DETS, motor2, *asc_p)

def open_all_valves(valve_list):
    '''Open all the listed valves

    Parameters
    ----------
    valve_list : sequence
        The valves to open
        
    '''
    for v in valve_list:
        yield from bp.abs_set(v, 1, group='valve_set')
    yield from bp.wait('valve_set')
    # sleep might not be needed
    yield from bp.sleep(2)
        
EDGE_MAP = {'Ce_M': {'start': 875, 'step_size':1, 'num_pts': 40},
            'O_K': {'start': 525, 'step_size':1, 'num_pts': 40},
            'Ni_L': {'start': 845, 'step_size':1, 'num_pts': 40},
            'Zn_L': {'start': 1010, 'step_size':1, 'num_pts': 50},
            'Cu_L': {'start': 920, 'step_size':1, 'num_pts': 40},
            'Al_L': {'start': 1548, 'step_size':1, 'num_pts': 40},
            'Ti_L': {'start': 450, 'step_size':1, 'num_pts': 25},
            'Fe_L': {'start': 700, 'step_size':1, 'num_pts': 40},
            'C_K': {'start': 275, 'step_size':1, 'num_pts': 50},
            'N_K': {'start': 400, 'step_size':1, 'num_pts': 40}
}


SAMPLE_MAP = {'sample1': {'name': 'Ni_foil', 'pos': 252, 'interesting_edges': ['Ni_L']},
              'sample2': {'name': 'Zn_foil', 'pos': 259, 'interesting_edges': ['Zn_L']},
              'sample3': {'name': 'Cu_foil', 'pos': 267, 'interesting_edges': ['Cu_L']},
              'sample4': {'name': 'Al_foil', 'pos': 276, 'interesting_edges': ['Al_L']},
              'sample5': {'name': 'TiO2', 'pos': 282, 'interesting_edges': ['Ti_L', 'O_K']},
              'sample6': {'name': 'Fe2O3', 'pos': 290, 'interesting_edges': ['Fe_L', 'O_K']},
}

VORTEX_SETTINGS = {'Cu_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 850,
                            'mca.rois.roi4.hi_chan': 1000},

                   'Ni_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 800,
                            'mca.rois.roi4.hi_chan': 1000},

                   'Al_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 1300,
                            'mca.rois.roi4..hi_chan': 1600},

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
                            'mca.rois.roi4.lo_chan': 450,
                            'mca.rois.roi4.hi_chan': 650},

                   'Zn_L': {'vortex.peaking_time': 0.4,
                            'vortex.energy_threshold': 0.05,
                            'mca.rois.roi4.lo_chan': 900,
                            'mca.rois.roi4.hi_chan': 1150},
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
    md = ChainMap(md, local_md)
   
    e_scan_params = EDGE_MAP[edge]
    # TODO configure the vortex
    
    sample_props = SAMPLE_MAP[sample_name]
    # sample_props = sample_manager.find(sample_name)
    local_md.update(sample_props)
    
    init_group = 'ME_INIT_' + str(uuid.uuid4())
    yield from bp.abs_set(ioxas_x, sample_props['pos'], group=init_group)
    yield from bp.abs_set(pgm_energy, e_scan_params['start'], group=init_group)
    yield from open_all_valves(all_valves)
    yield from bp.wait(init_group)
    
    # TODO make this an ohypd obj!!!!!!
    #caput('XF:23IDA-PPS:2{PSh}Cmd:Opn-Cmd',1)
    yield from bp.sleep(2)
    # TODO make this an ohypd obj!!!!!!
    # TODO ask stuart
    #caput('XF:23IDA-OP:2{Mir:1A-Ax:FPit}Mtr_POS_SP',50)
    yield from bp.sleep(5)

    yield from bp.configure(vortex, VORTEX_SETTINGS[edge])
    lp_list = []
    for n in ['sclr_ch4', 'vortex_mca_rois_roi4_count']:
        fig = plt.figure(edge + ': ' + n)
        lp = bs.callbacks.LivePlot(n, 'pgm_energy_readback', fig=fig)
        lp_list.append(lp)

    scan_kwargs = {'start': e_scan_params['start'],
                   'stop': (e_scan_params['start'] + e_scan_params['step_size']*e_scan_params['num_pts']),
                   'velocity': .2,
                   'md': md}
    ret = []

    res = yield from bp.subs_wrapper(_run_E_ramp(gs.DETS, **scan_kwargs), lp_list)
    if res is None:
        res = []
    ret.extend(res)
    if not ret:
        return ret
    
    # hdr = db[ret[0]]
    # redo_count = how_many_more_times_to_take_data(hdr)
    # for j in range(redo_count):
    #     res = yield from bp.subs_wrapper(ascan(*scan_args, md=md), lp)
    #     ret.extend(res)


    # new_count_time = compute_new_count_time(hdr, old_count_time)
    # if new_count_time != old_count_time:
    #     yield from bp.configure(vortex, {'count_time': new_count_time})
    #     res = yield from bp.subs_wrapper(ascan(*scan_args, md=md), lp)
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
    edge_list = sorted(edge_list, key=lambda k: EDGE_MAP[k]['start'])        
    cy = cycler('edge', edge_list) * cycler('sample_name', sample_list)
    for inp in cy:
        if pass_filter(**inp):
            yield from edge_ascan(**inp)

def dummy_edge_scan(sample_name, edge, md=None):
    from bluesky.examples import det, motor, det2

    if md is None:
        md = {}
    local_md = {'plan_name': 'edge_ascan'}
    md = ChainMap(md, local_md)
   
    e_scan_params = EDGE_MAP[edge]
    # TODO configure the vortex
    
    sample_props = SAMPLE_MAP[sample_name]
    # sample_props = sample_manager.find(sample_name)
    local_md.update(sample_props)
    lp_list = []
    for n in ['det', 'det2']:
        fig = plt.figure(edge + ': ' + n)
        lp = bs.callbacks.LivePlot(n, 'motor', fig=fig)
        lp_list.append(lp)
    yield from bp.subs_wrapper(bp.relative_scan([det, det2], motor, -5, 5, 15, md=md),
                               lp_list)
    

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
