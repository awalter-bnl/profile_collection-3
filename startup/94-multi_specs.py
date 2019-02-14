from bluesky.plan_stubs import move_per_step

spectrum_list = {'C1s':{'low_energy': 285, 'high_energy': 300, 'step_size': 0.2},
                 'O1s':{'low_energy': 525, 'high_energy': 540, 'step_size': 0.2} }

def multi_spectrum(detectors, step, pos_cache):
    '''This function is used to trigger multiple spectra at each point in a scan.

    This function is analagous to the `bluesky.plan_stubs.one_nd_step` function and
    should be used instead of that via the kwarg `per_step=multi_spectrum` in a call
    to any default plan except count.

    Parameters
    ----------
    detectors : list
        a list of detectors to trigger at each point
    step : dict
        a dictionary mapping motors to values for this point in the scan
    pos_cache : dict
        a dictionary mapping motors to their last-set positions.
    '''
    motors=step.keys()
    # move to the required position
    yield from move_per_step(step, pos_cache)

    # take each of the required spectra from the 'spectrum_list' dictionary
    for stream_name, positions in spectrum_list.items():
        pos_list=[]
        for key, val in positions.items():
            pos_list.append(getattr(specs.cam, key))
            pos_list.append(val)
        yield from mv(*pos_list)
        yield from trigger_and_read(list(detectors)+list(motors), name=stream_name)
