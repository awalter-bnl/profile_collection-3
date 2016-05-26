#new figure feature
import bluesky.plans as bp
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
        yield from bp.abs_set(v, 1, 'valve_set')
    yield from bp.wait('valve_set')
    # sleep might not be needed
    yield from bp.sleep(2)
        
EDGE_MAP = {'Ce_M': {'start': 875, 'step_size':0.25, 'num_pts': 10} }

SAMPLE_MAP = {'sample1': {'name': 'long_scientific_name1', 'pos': 5, 'interesting_edges': ['Ce_M']},
              'sample2': {'name': 'long_scientific_name2', 'pos': 7},
              'sample3': {'name': 'long_scientific_name3', 'pos': 9},
              'sample4': {'name': 'long_scientific_name4', 'pos': 11},
              'sample5': {'name': 'long_scientific_name5', 'pos': 13},
              'sample6': {'name': 'long_scientific_name6', 'pos': 15},
}

VORTEX_SETTINGS = {'Ce_M': {'vortex.peaking_time': 0.25,
                            'vortex.energy_threshold': 0.65,
                            '---': 1400,
                            '---': 3600}
                   }

def edge_ascan(sample_name, edge):
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
    e_scan_params = EDGE_MAP[edge]
    # TODO configure the vortex
    
    sample_props = SAMPLE_MAP[sample_name]
    # sample_props = sample_manager.find(sample_name)
    
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

    yield from bp.configure(vortex, VORTEX_SETTING['edge'])
    
    # TODO use custom subsriptions for plotting
    yield from ascan(pgm_energy,
                     e_scan_params['start'],
                     e_scan_params['start'] +  e_scan_params['step_size']*e_scan_params['num_pts'],
                     e_scan_params['num_pts'])


def pass_filter(sample_name, edge):
    return edge in SAMPLE_MAP[sample_name]['interesting_edges']


def multi_sample_edge(*, edge_list=None, sample_list=None):
    if sample_list is None:
        sample_list = list(SAMPLE_MAP)
    if edge_list is None:
        edge_list = list(EDGE_MAP)
        
    cy = cycler('edge', edge_list) * cycler('sample_name', sample_list)
    for inp in cy:
        if pass_filter(**inp):
            yield from edge_ascan(**inp)
