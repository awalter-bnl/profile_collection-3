from bluesky.plan_stubs import (move_per_step, trigger_and_read, trigger, read,
                                mv, wait, abs_set, repeat)
from bluesky.preprocessors import stub_wrapper, stage_decorator, run_decorator
from bluesky.utils import short_uid as _short_uid
import copy
from collections import OrderedDict
from dataclasses import dataclass
from functools import partial
from IPython import get_ipython
import numpy
from ophyd.signal import Signal
from ophyd import StatusBase
import pandas
import typing
ip = get_ipython()


# Define ``ophyd.Signal``'s that we can use to track which spectra, group and
# step we are at in the scan when necessary.
spectra_num = Signal(name='spectra_num')
group_num = Signal(name='group_num')
step_num = Signal(name='step_num')
spectra_detectors = Signal(name='spectra_detectors', value=[])


class MultiSpectraValueError(ValueError):
    ...


class FileDataRouterValueError(ValueError):
    ...


# This section is some temporary test objects
from ophyd.sim import hw
from bluesky import RunEngine
from ophyd.device import Component as Cpt, Device
from bluesky.plan_stubs import sleep
from bluesky.plans import count, scan, grid_scan
from bluesky.simulators import summarize_plan
from databroker import Broker
import time


RE = RunEngine()
db = Broker.named('local')
RE.subscribe(db.insert)


def ERamp(dets, start, stop, velocity, streamname='primary'):
    yield from count(dets)

class Cam():
    def __init__(self,name):
        self.name=name

    low_energy = Signal(name='specs_low_energy')
    high_energy = Signal(name='specs_high_energy')
    step_size = Signal(name='specs_step_size')
    num_images = Signal(name='specs_num_images')

hw = hw()
specs = hw.det2
specs.name = 'specs'
specs.gain = Signal(name='specs_gain')
specs.decade = Signal(name='specs_decade')
specs.cam=Cam(name='specs_cam')

def _set_mode(val):
    yield from mv(specs.acquisition_mode, val)


specs.set_mode = _set_mode
specs.acquisition_mode = Signal(name='specs_acquisition_mode')
vortex = hw.det1
vortex.name = 'vortex'
vortex.gain = Signal(name='vortex_gain')
vortex.decade = Signal(name='vortex_decade')


class MonoFly():
    def __init__(self, name):
        self.name=name

    start_sig = Signal(name='start_sig')
    stop_sig = Signal(name='stop_sig', kind='omitted')
    velocity = Signal(name='velocity')

    fly_start = Signal(name='fly_start')
    fly_stop = Signal(name='fly_stop')
    scan_status = Signal(name='scan_status',value=0)

class Pgm():
    def __init__(self, name):
        self.energy = hw.motor1
        self.name = name

    fly=MonoFly(name='fly')

    def reset_fbl(self, *args, **kwargs):
        yield from sleep(0.1)

def describe_func():
    return {'scan_status':{'enum_strs':['done','scaning']}}

def set_function(val):
    if val==1:
        pgm.fly.scan_status.set(1)
        time.sleep(0.00001)
        pgm.fly.scan_status.set(0)
        return pgm.energy.set(pgm.fly.stop_sig.get())
    else:
        return StatusBase(done=True, success=True)


pgm = Pgm('pgm')
pgm.energy.name='pgm_energy'
pgm.fly.scan_axis=pgm.energy
pgm.fly.scan_status.describe=describe_func
pgm.fly.fly_start.set=set_function
pgm.energy.delay=0.1
motor = hw.motor
motor1 = hw.motor1
motor2 = hw.motor2
motor3 = hw.motor3
det = hw.det


class Flt():
    def __init__(self, name):
        self.name=name

    input_pv = Signal(name='input_pv')
    output_deadband = Signal(name='output_deadband')


class Epu1():
    def __init__(self, name):
        self.name=name

    flt = Flt(name='flt')

epu1=Epu1(name='epu1')

# above are the temporary objects for testing.


class StashSignal(Signal):
    '''An ``ophyd.Signal`` class to be used when holding 'stashed' values.

    This class acts like an ``ophyd.Signal`` class except that each instances
     ``describe`` method returns information relevant to proper 'describe'
    process.
    '''

    def __init__(self, *args, describe_dict, **kwargs):
        '''*args and **kwargs are passed to ``super().__init__(),
        associated_obj is used in the custom describe method below.``
        '''
        self._describe_dict = describe_dict
        super().__init__(*args, **kwargs)

    def describe(self):
        return self._describe_dict


def _str_to_obj(str_ref):
    '''Converts a string ref to an ``ophyd.Device`` object reference.

    Parameters
    ----------
    str_ref : str
        A string reference to an ``ophyd.Device`` object, should have the form
        'attribute', 'parent.attribute', 'grandparent.parent.attribute' or
        'ancestor.(...).parent.attribute'.

    Returns
    -------
    obj : object
        The ``ophyd.Device`` object referenced by the string
    '''
    parent, _, attrs = str_ref.partition('.')
    obj = ip.user_ns[parent]
    if attrs:
        obj = getattr(obj, attrs)
    return obj


def _move_from_dict(move_dict):
    '''Returns a plan to moves a set of motors mapped to positions.

    This expects a dictionary whose keys are strings containing an
    ``ophyd.Device`` reference of the form ``parent.attribute`` or
    ``grandparent.parent.attribute``, where the attribute is the
    ``ophyd.Device`` to be moved. The values of the dictionary are the
    positions to move to.

    Parameters
    ----------
    move_dict, Dict[obj, value]
        A dictionary mapping ``ophyd.Device``s to be moved to positions
        to move to. See above for a description of this dictionary.
    '''
    settings_list = []
    for key, value in move_dict.items():
        obj = _str_to_obj(key)
        settings_list.extend([obj, value])

    return (yield from mv(*settings_list))


def ios_multiscan_plan_factory_wrapper(scans):
    '''Returns a plan that will perform multiple scans in order.

    This generates a plan to set each value required to generate a scan at IOS
    for each scan in 'scans', it is a wrapper around ios_multiscan_plan_factory
    which parses the plan arguments string loaded from the Excel file first.

    Parameters
    ----------
    scans : list
        A list of (scan_name, parameters, settings) tuples with the
        following parameters:

        scan_name : str
            The name of the scan to perform.
        parameters : dict
            A dictionary mapping parameter names to values for the scan given
            by scan_name.
        settings : dict
            A dictionary mapping ``ophyd.Device``s to values that need to be
            set prior to the scan given by scan_name being acquired.
    '''

    def _parse_plan_arguments(scans):
        '''Parses the scan arguments and detectors loaded from the Excel file.

        Returns a parsed version of ``scans`` where ``parameters['arguments']``
        is converted from a string to an argument list and
        ``parameters['detectors']`` is converted into ophyd objects.

        Parameters
        ----------
        scans : list
            A list of (scan_name, parameters, settings) tuples with the
            following parameters:

            scan_name : str
                The name of the scan to perform.
            parameters : dict
                A dictionary mapping parameter names to values for the scan
                given by scan_name.
            settings : dict
                A dictionary mapping ``ophyd.Device``s to values that need to
                be set prior to the scan given by scan_name being acquired.
        '''

        # Below is a dictionary that maps scan types (count, scan,...) to a
        # dictionary that maps the arguments that each scan requires to a type.
        # Types can be any ``type`` object or 'obj'. For all types but 'obj'
        # the input will be converted using the type (eg. str(val) ). For obj
        # the val will be passed to ``_str_2_obj``. Kwargs assume default
        # values.
        plan_arguments = {
            'scan': {'motor1': 'obj', 'start1': float, 'stop1': float,
                     'num': int},
            'grid_scan': {'motor1': 'obj', 'start1': float, 'stop1': float,
                          'num1': int, 'motor2': 'obj', 'start2': float,
                          'stop2': float, 'num2': int, 'snake': bool},
            'ios_count': {}}

        def _convert_arguments(plan, arguments):
            '''Converts the arguments value in scanmap to a usable list.

            Parameters
            ----------
            plan : str
                The key to extract the type information from plan_arguments.
            arguments : list
                The list of arguments extracted from the Excel spreadsheet

            Returns
            -------
            args : list
                A list of converted arguments ready to be fed to the plan.
            '''
            args = []

            if isinstance(arguments, str):
                arguments = arguments.split(',')
            elif not isinstance(arguments, list):
                arguments = [arguments]

            for i, (key, val) in enumerate(plan_arguments[plan].items()):
                if isinstance(val, type):
                    args.append(val(arguments[i]))
                elif isinstance(val, str) and val == 'obj':
                    args.append(_str_to_obj(arguments[i]))
                else:
                    raise FileDataRouterValueError(
                        f'The value found from plan_arguments[{key}] in '
                        f'"ios_multi_scan_plan_factory" is not a valid value.'
                        f'Valid values are any ``type`` object or the string '
                        f'"obj"'
                        )
            return args

        parsed_scans = []

        for (scan_name, parameters, settings) in scans:
            # parse the plan arguments
            parameters['arguments'] = _convert_arguments(
                parameters.get('plan', 'count'),
                parameters.get('arguments', []))
            # convert detectors to a list of ``ophyd.Device`` objects.
            parameters['detectors'] = [
                _str_to_obj(det) for det in parameters['detectors'].split(',')]
            parsed_scans.append((scan_name, parameters, settings))

        return parsed_scans

    yield from ios_multiscan_plan_factory(_parse_plan_arguments(scans))


# define the plan that results in multiple 'scans' being performed at each step
def ios_multiscan_plan_factory(scans):
    '''Returns a plan that will perform multiple scans in order.

    This generates a plan to set each value required to generate a scan at IOS
    for each scan in 'scans'.

    Parameters
    ----------
    scans : list
        A list of (scan_name, parameters, settings) tuples with the
        following parameters:

        scan_name : str
            The name of the scan to perform.
        parameters : dict
            A dictionary mapping parameter names to values for the scan given
            by scan_name.
        settings : dict
            A dictionary mapping ``ophyd.Device``s to values that need to be
            set prior to the scan given by scan_name being acquired.
    '''

    def _sanitize_dict(d):
        '''replace all periods in the dict with '_' for json compatibility
        '''
        new = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = _sanitize_dict(v)
            if type(k) is str:
                k = k.replace('.', '_')
            if type(v) is str:
                v = v.replace('.', '_')
            new[k] = v
        return new

    # step through each of the requested scans and perform it.
    for (scan_name, parameters, settings) in scans:
        # check if a plan and arguments are given, use 'count' if not.
        plan = parameters.get('plan', 'count')
        args = parameters.get('arguments', [])
        dets = parameters.get('detectors', [])

        # move to the predefined positions for this scan
        yield from _move_from_dict(settings)

        # extract the per_step function from the 'spectra_type' parameter
        spectra_obj = ip.user_ns[parameters['spectra_type']]
        spectra_list = parameters['interesting_spectra'].split(',')

        # set the required list of detectors for each spectra point. using
        # `.set()` purely to make summarize_plan produce useful output as
        # 'spectra_detectors' is a `Signal` not connected to hardware this
        # approach is safe.
        spectra_detectors.set(dets+[pgm.energy])
        _per_step = spectra_obj(spectra_list)

        # define a function that loops over each spectra group 'group_num'
        # times
        def _group_step(detectors, step, pos_cache):
            extra_dets = []
            # add ``group_num`` to the extra_dets list if needed
            if parameters['num_groups'] is None:
                parameters['num_groups'] = 1
            elif parameters['num_groups'] > 1:
                extra_dets.append(group_num)
            # collect num_spectra individual spectra at this point.
            for num_group in range(1, parameters['num_groups']+1):
                if group_num in extra_dets:  # update group_num if needed
                    yield from mv(group_num, num_group)
                yield from _per_step(extra_dets, step, pos_cache)

        # extract out the spectra meta-data
        md = {}
        md['spectra'] = {
            k: {'parameters': _sanitize_dict(
                load_dictionary(spectra_obj.parameters,
                                spectra_obj.defaults._parameters_index)[k]),
                'settings': _sanitize_dict(
                load_dictionary(spectra_obj.settings,
                                spectra_obj.defaults._settings_index)[k])}
            for k in spectra_list}

        # remove duplicate info from the parameters dictionary
        md_parameters = _sanitize_dict(parameters)
        md_parameters.pop('arguments')
        md_parameters.pop('detectors')

        md['scan'] = {'settings': _sanitize_dict(settings),
                      'parameters': md_parameters}

        # yield from the required plan, num_scans times.
        for scan_num in range(parameters['num_scans']):
            yield from ip.user_ns[plan](dets, *args, per_step=_group_step,
                                        md=md)
        spectra_detectors.set([])

# define the plan that results in multiple 'xps' spectra being taken per_step.
def ios_xps_per_step_factory(spectra):
    '''Returns a per_step function that will perform multiple XPS spectra.

    This yields a per_step function that will set each value required to
    generate an XPS spectra using the specs detector at IOS and then triggers
    the detector (and any ancillary detectors) which executes the spectra for
    each spectrum in `spectra`.

    Parameters
    ----------
    spectra : list
        A list of (peak_name, parameters, settings) tuples with the
        following parameters:

        peak_name : str
            The name to use for the stream.
        parameters : dict
            A dictionary mapping parameter names to values for the peak given
            by peak_name.
        settings : dict
            A dictionary mapping ``ophyd.Device``s to values that need to be
            set prior to the peak given by peak_name being acquired.
    '''
    def _per_step(detectors, step, pos_cache):
        '''This triggers multiple spectra at each point in a plan.

        This function is analogous to the `bluesky.plan_stubs.one_nd_step`
        function and should be used instead of that via the kwarg
        `per_step=multi_spectrum` in a call to any default plan except
        count.

        Parameters
        ----------
        detectors : list
            a list of detectors to trigger at each point
        step : dict
            a dictionary mapping motors to values for this point in the
            scan
        pos_cache : dict
            a dictionary mapping motors to their last-set positions.
        '''

        detectors.extend(spectra_detectors.get())
        # use `.get` for summarize_plan logic

        motors = step.keys()
        # move any motors that the outer plan requires to be moved.
        yield from move_per_step(step, pos_cache)

        for (peak_name, parameters, settings) in spectra:
            # move the devices in settings into place
            yield from _move_from_dict(settings)

            # reset the photon energy and the feedback loop for the given
            # spectra
            yield from pgm.reset_fbl(
                parameters['alignment_energy'],
                epu_lookup_table=int(parameters['epu_lookup_table']),
                epu_input_offset=parameters['epu_input_offset'],
                fbl_setpoint=parameters['fbl_setpoint'])


            # set the parameters for the scan
            yield from mv(specs.cam.low_energy, parameters['low_energy'],
                          specs.cam.high_energy, parameters['high_energy'],
                          specs.cam.step_size, parameters['step_size'],
                          specs.cam.num_images, parameters['num_spectra'],
                          pgm.energy, parameters['photon_energy'])
            # set the specs detector mode
            yield from specs.set_mode('spectrum')
            # perform the scan
            yield from trigger_and_read(list(detectors)+list(motors),
                                        name=peak_name)

    return _per_step


# define the plan that results in multiple 'xas' spectra being taken per_step
# using a 'flyscan' over the photon energy axis.
def ios_xas_flyspectra_per_step_factory(spectra):
    '''Returns a per_step function that will perform multiple XAS spectra.

    This yields a per_step function that will set each value required to
    generate an XAS spectrum by fly scanning over the energy axis at IOS for
    each spectrum in `spectra`.

    Parameters
    ----------
    spectra : list
        A list of (edge_name, parameters, settings) tuples with the
        following parameters:

        edge_name : str
            The name to use for the stream.
        parameters : dict
            A dictionary mapping parameter names to values for the edge given
            by edge_name.
        settings : dict
            A dictionary mapping ``ophyd.Device``s to values that need to be
            set prior to the edge given by edge_name being acquired.
    '''

    def _generate_stash_object(detectors):
        '''Generates a dictionary that links detectors to temporary signals

        This function takes in a list of ophyd objects (detectors) and for each
        one creates a temporary `Ophyd.Signal` object within which we can store
        the cached read values and return on a `Siganl.read()` call.

        Parameters
        ----------
        detectors : list[objs]
            A list of ophyd objects to be read at each point in the spectra.

        Returns
        -------
        stash_objects : dict{name: obj}
            A dictionary mapping field names to Ophyd.Signal objects.
        '''
        stash_objects = OrderedDict()
        for obj in detectors:
            describe_dict=obj.describe()
            for field in obj.describe():  # each field
                # update the describe dict to indicate an array
                describe_dict[f'{field}']['dtype']='array'
                describe_dict[f'{field}']['shape']=[1, -1]
                # add the field: stash_object pair to stash_objects
                stash_objects[f'{field}_value'] = StashSignal(
                    name=f'{field}',
                    describe_dict={
                        f'{field}': describe_dict[f'{field}']})
                # copy and update the timestamp describe dict.
                timestamp_describe_dict = copy.deepcopy(
                    describe_dict[f'{field}'])
                timestamp_describe_dict = {
                    f'{field}_timestamp':copy.deepcopy(
                        describe_dict[f'{field}'])}
                timestamp_describe_dict[f'{field}_timestamp'][
                    'dtype'] = 'array'
                timestamp_describe_dict[f'{field}_timestamp']['precision'] = 7
                # add the field_timestamp: stash object pair to stash_objects
                stash_objects[f'{field}_timestamp'] = StashSignal(
                    name=f'{field}_timestamp',
                    describe_dict=timestamp_describe_dict)

        return stash_objects

    # create the list of ophyd objects for stashing values
    spectra_objects = spectra_detectors.get()
    stash_objects=_generate_stash_object(spectra_objects)

    def _per_step(detectors, step, pos_cache):
        '''This triggers multiple spectra at each point in a plan.

        This function is analogous to the `bluesky.plan_stubs.one_nd_step`
        function and should be used instead of that via the kwarg
        `per_step=multi_spectrum` in a call to any default plan except
        count.

        Parameters
        ----------
        detectors : list
            a list of detectors to trigger at each point
        step : dict
            a dictionary mapping motors to values for this point in the
            scan
        pos_cache : dict
            a dictionary mapping motors to their last-set positions.
        '''
        motors = step.keys()
        # move any motors that the outer plan requires to be moved.
        yield from move_per_step(step, pos_cache)

        # set the mode for the specs detector if necessary
        if specs in detectors:
            yield from specs.set_mode('single_point')

        for (edge_name, parameters, settings) in spectra:
            # move the devices in settings into place
            yield from _move_from_dict(settings)

            # reset the photon energy and the feedback loop for the given
            # spectra
            yield from pgm.reset_fbl(
                float(parameters['alignment_energy']),
                epu_lookup_table=int(parameters['epu_lookup_table']),
                epu_input_offset=parameters['epu_input_offset'],
                fbl_setpoint=parameters['fbl_setpoint'])

            # collect num_spectra individual spectra at this point.
            for num_spectra in range(1, parameters['num_spectra']+1):
                cache_dict={}  # ensure the cache_dict is empty

                # perform the fly scan

                # put the energy at the starting value and set the fly
                # parameters
                yield from mv(
                    pgm.energy, float(parameters['low_energy']),
                    pgm.fly.start_sig, float(parameters['low_energy']),
                    pgm.fly.stop_sig, float(parameters['high_energy']),
                    pgm.fly.velocity, float(parameters['velocity']))
                old_db = epu1.flt.output_deadband.get()
                yield from mv(epu1.flt.output_deadband, parameters['deadband'])
                # get the old value
                v = (yield from read(epu1.flt.input_pv))
                if v is None:
                    old_link = 'original value'
                else:
                    n = epu1.flt.input_pv.name
                    old_link = v[n]['value']

                # change to track the readout energy.
                yield from mv(epu1.flt.output_deadband, old_db)

                # start the energy flying
                ret = (yield from abs_set(pgm.fly.fly_start, 1))
                st = StatusBase()
                enum_map = pgm.fly.scan_status.describe()[
                    pgm.fly.scan_status.name]['enum_strs']

                def _done_cb(value, old_value, **kwargs):
                    old_value = enum_map[int(old_value)]
                    value = enum_map[int(value)]
                    if old_value != value and value == 'Ready':
                        st._finished()
                        pgm.fly.scan_status.clear_sub(_done_cb)

                # subscribe the scan_status to the moving axis if running scan
                if ret is not None:
                    pgm.fly.scan_status.subscribe(_done_cb, run=False)
                else:
                    st._finished()
                    print('SIM MODE')

                # measure while the scan axis is still moving
                while ret is not None and not ret.done:                 # for testing
                #while st is not None and not st.done:
                    # trigger all of the devices and wait for completion
                    grp = _short_uid('trigger')
                    for obj in detectors:
                        yield from trigger(obj, group=grp)
                    yield from wait(group=grp)

                    # read all of the devices to the cache

                    for obj in spectra_objects:
                        data = yield from read(obj)
                        if data: # purely for summarize_plan
                            for k1, reading in data.items():
                                for k2, value in reading.items():
                                    if f'{k1}_{k2}' not in cache_dict.keys():
                                        cache_dict[f'{k1}_{k2}']=[value]
                                    else:
                                        cache_dict[f'{k1}_{k2}'].append(value)

                    yield from sleep(0.02) # for testing, limits the num of points

                # move stashed readings to the stashes objects
                for field, sig in stash_objects.items():
                    if field in cache_dict.keys(): # for summarize_plan
                        yield from mv(sig, list(cache_dict[field]))

                # trigger and read the stash_objects Signal objects
                yield from trigger_and_read(
                    list(stash_objects.values())+list(detectors)+list(motors),
                    name=edge_name)

                # clean up afterwards
                # move the energy setpoint to where the energy really is
                yield from mv(pgm.energy, pgm.energy.position)
                # set the interpolator to look at what it was looking at before
                # the scan.  This should be the energy set point.
                yield from mv(epu1.flt.input_pv, old_link)

    return _per_step


# define the plan that results in multiple 'xas_step' spectra being taken
# per_step.
def ios_xas_stepspectra_per_step_factory(spectra):
    '''Returns a per_step function that will perform multiple XAS spectra.

    This returns a per_step function, and a metadata dict that will set each
    value required to generate an XAS step spectrum using the specs detector at
    IOS and then steps through each energy point and triggers and reads the
    detector (and any ancillary detectors) for each spectrum in `spectra`.

    Parameters
    ----------
    spectra : list
        A list of (edge_name, parameters, settings) tuples with the
        following parameters:

        edge_name : str
            The name to use for the stream.
        parameters : dict
            A dictionary mapping parameter names to values for the peak given
            by peak_name.
        settings : dict
            A dictionary mapping ``ophyd.Device``s to values that need to be
            set prior to the peak given by peak_name being acquired.
    '''

    def _generate_stash_object(detectors):
        '''Generates a dictionary that links detectors to temporary signals

        This function takes in a list of ophyd objects (detectors) and for each
        one creates a temporary `Ophyd.Signal` object within which we can store
        the cached read values and return on a `Siganl.read()` call.

        Parameters
        ----------
        detectors : list[objs]
            A list of ophyd objects to be read at each point in the spectra.

        Returns
        -------
        stash_objects : dict{name: obj}
            A dictionary mapping field names to Ophyd.Signal objects.
        '''
        stash_objects = OrderedDict()
        for obj in detectors:
            describe_dict=obj.describe()
            for field in obj.describe():  # each field
                # update the describe dict to indicate an array
                describe_dict[f'{field}']['dtype']='array'
                describe_dict[f'{field}']['shape']=[1, -1]
                # add the field: stash_object pair to stash_objects
                stash_objects[f'{field}_value'] = StashSignal(
                    name=f'{field}',
                    describe_dict={
                        f'{field}': describe_dict[f'{field}']})
                # copy and update the timestamp describe dict.
                timestamp_describe_dict = copy.deepcopy(
                    describe_dict[f'{field}'])
                timestamp_describe_dict = {
                    f'{field}_timestamp':copy.deepcopy(
                        describe_dict[f'{field}'])}
                timestamp_describe_dict[f'{field}_timestamp'][
                    'dtype'] = 'array'
                timestamp_describe_dict[f'{field}_timestamp']['precision'] = 7
                # add the field_timestamp: stash object pair to stash_objects
                stash_objects[f'{field}_timestamp'] = StashSignal(
                    name=f'{field}_timestamp',
                    describe_dict=timestamp_describe_dict)

        return stash_objects


    # create the list of ophyd objects for stashing values
    spectra_objects = spectra_detectors.get()
    stash_objects=_generate_stash_object(spectra_objects)

    def _per_step(detectors, step, pos_cache):
        '''This triggers multiple spectra at each point in a plan.

        This function is analogous to the `bluesky.plan_stubs.one_nd_step`
        function and should be used instead of that via the kwarg
        `per_step=multi_spectrum` in a call to any default plan except
        count.

        Parameters
        ----------
        detectors : list
            a list of detectors to trigger at each point
        step : dict
            a dictionary mapping motors to values for this point in the
            scan
        pos_cache : dict
            a dictionary mapping motors to their last-set positions.
        '''
        motors = step.keys()
        # move any motors that the outer plan requires to be moved.
        yield from move_per_step(step, pos_cache)

        # set the mode for the specs detector if necessary
        if specs in detectors:
            yield from specs.set_mode('single_point')

        for (edge_name, parameters, settings) in spectra:
            # move the devices in settings into place
            yield from _move_from_dict(settings)

            # reset the photon energy and the feedback loop for the given
            # spectra
            yield from pgm.reset_fbl(
                parameters['alignment_energy'],
                epu_lookup_table=int(parameters['epu_lookup_table']),
                epu_input_offset=parameters['epu_input_offset'],
                fbl_setpoint=parameters['fbl_setpoint'])

            # collect num_spectra individual spectra at this point.
            for num_spectra in range(1, parameters['num_spectra']+1):

                cache_dict={}  # ensure the cache is empty

                #step through each step in the 'spectra'
                for energy in numpy.arange(parameters['low_energy'],
                                           parameters['high_energy'] +
                                           parameters['step_size']/2,
                                           parameters['step_size']):

                    yield from mv(pgm.energy, energy) # move to the new energy

                    # trigger all of the devices and wait for completion
                    grp = _short_uid('trigger')
                    for obj in detectors:
                        yield from trigger(obj, group=grp)
                    yield from wait(group=grp)

                    # read all of the devices to the cache

                    for obj in spectra_objects:
                        data = yield from read(obj)
                        if data: # purely for summarize_plan
                            for k1, reading in data.items():
                                for k2, value in reading.items():
                                    if f'{k1}_{k2}' not in cache_dict.keys():
                                        cache_dict[f'{k1}_{k2}']=[value]
                                    else:
                                        cache_dict[f'{k1}_{k2}'].append(value)

                # move stashed readings to the stashes objects
                for field, sig in stash_objects.items():
                    if field in cache_dict.keys(): # for summarize_plan
                        yield from mv(sig, list(cache_dict[field]))

                # trigger and read the stash_objects Signal objects

                yield from trigger_and_read(
                    list(stash_objects.values())+list(detectors)+list(motors),
                    name=edge_name)

    return _per_step


def load_dictionary(filepath, index_name):
    '''Loads up a dictionary from an Excel file.

    Returns a dictionary loaded from the Excel file found at ``filepath``
    using ``index_name`` to find the index name column in the file.

    Parameters
    ----------
    filepath : str, Path or None
        filepath to load the dictionary data.
    index_name : str
        The name associated with the index column in the file
    '''
    temp_dict = {}

    # extract the information form the file and write it to the dictionary
    f = pandas.read_excel(filepath)
    f = f.set_index(index_name)

    for row_name in f.index:
        temp_dict[row_name] = dict(f.loc[row_name])

    return temp_dict


@dataclass(frozen=True)
class DefaultFileInfo:
    '''A dataclass that holds the default file and plan_factory information.

    This class should be used to define an attribute for ``FileInfo`` which
    stores the name of the plan and the paths to the settings and parameter
    files associated with the instance. These values are made semi-immutable by
    using the ``frozen=True`` kwarg in the ``@dataclass`` decorator above.


    Attributes
    ----------
    settings : string or Path
        The filepath to be used when loading the settings dictionary.
    _settings_index : str
        The name of the column in the settings file that is the index
    parameters : string or Path
        The filepath to be used when loading the parameters dictionary.
    _parameters_index : str
        The name of the column in the parameters file that is the index
    plan_factory : callable
        The callable that generates a plan, or per_step function
    '''

    __slots__ = ('settings', '_settings_index', 'parameters',
                 '_parameters_index', 'plan_factory')
    settings: str
    _settings_index: str
    parameters: str
    _parameters_index: str
    plan_factory: typing.Callable


@dataclass
class FileDataRouter:
    '''A dataclass that holds the file and plan_factory information.

    This class should be used to store the name of the plan and the paths to
    the settings and parameter files associated with the instance. It also
    has a ``reset_defaults`` method for resetting these values to the defaults
    and a efaults attribute for storing the defaults. It can also be called

    NOTE: To make creating instances with the init values of settings,
    parameters and plan_factory saved to the ``self.defaults`` attribute use
    the helper function:

    .. code::

        make_filedatarouter_instance(settings, settings_index,
                                     parameters, parameters_index,
                                     plan_factory, name)

    Call Parameters
    ---------------
    items : str or list
        The item to perform or a list of items to perform  at each step of
        a plan. The items listed here must be present as index keys in
        both files found at the paths ``self.parameters`` and
        ``self.settings``. Using the str 'all' will result in all keys from
        the two files being used provided they both have exactly the same
        keys.

    Attributes
    ----------
    settings : string or Path
        The filepath to be used when loading the settings dictionary.
    parameters : string or Path
        The filepath to be used when loading the parameters dictionary.
    plan_factory : callable
        The callable that generates a plan, or per_step function, associated
    defaults : DefaultFileInfo
        An instance of DefaultFileInfo that stores the default values
    restore_defaults : method
        restores the values of ``self.settings``, ``self.parameters`` and
        ``self.plan_factory`` to the defaults stored in ``self.defaults``
    '''

    __slots__ = ('settings', 'parameters', 'plan_factory', 'defaults', 'name')
    settings: str
    parameters: str
    plan_factory: typing.Callable
    defaults: DefaultFileInfo
    name: str

    def restore_defaults(self):
        '''Restores the other attributes to their default values.'''
        self.settings = self.defaults.settings
        self.parameters = self.defaults.parameters
        self.plan_factory = self.defaults.plan_factory

    def __call__(self, items):
        '''generates a plan using ``self.plan_factory``.

        Returns a plan generated using ``self.plan_factory`` and the data found
        in the files ``self.settings`` and ``self.parameters``.

        Parameters
        ----------
        items : str or list
            The item to perform or a list of items to perform  at each step of
            a plan. The items listed here must be present as index keys in
            both files found at the paths ``self.parameters`` and
            ``self.settings``. Using the str 'all' will result in all keys from
            the two files being used provided they both have exactly the same
            keys.
        '''

        # check that spectra is a list or a str, if a str convert to a list
        if items == 'all':
            items = list(self.settings.keys())
        elif isinstance(items, str):
            items = [items]
        elif not isinstance(items, list):
            raise FileDataRouterValueError(
                f'The items passed to ``{self.name}(items)`` is expected to be'
                f' a str or a list, instead we got {items} which is of type '
                f'{type(items)}.')

        # load the files
        settings = load_dictionary(self.settings,
                                   self.defaults._settings_index)
        parameters = load_dictionary(self.parameters,
                                     self.defaults._parameters_index)

        # check that items are keys in the two dictionaries
        if (set(items) > set(parameters)
                or not set(items) <= set(settings)):

            raise FileDataRouterValueError(
                f'The items passed to {self.name}(items) are not all keys in '
                f'{self.name}.parameters or {self.name}.settings'
                f'\nitems are: \n\t{items}\n{self.name}.'
                f'parameters keys are:\n\t'
                f'{parameters.keys()}\n{self.name}.'
                f'settings keys are:\n\t'
                f'{settings.keys()}')

        # Generate the list of tuples
        tuple_list = [(k, parameters[k], settings[k]) for k in items]

        # Call self.function
        output = self.plan_factory(tuple_list)

        return output  # return the output of self.plan_factory


def make_filedatarouter_instance(settings, settings_index,
                                 parameters, parameters_index,
                                 plan_factory, name):
    '''Returns a ``FileInfo`` instance with the init values as default.

    This function is required to automatically ensure that the init values are
    stored to the default attribute
    '''

    return FileDataRouter(settings, parameters, plan_factory,
                          DefaultFileInfo(settings, settings_index,
                                          parameters, parameters_index,
                                          plan_factory), name)


# define the FileDataRouter for the xps per_step function
xps = make_filedatarouter_instance(
    'test_xps_spectrum_settings.xlsx', 'peak_name',
    'test_xps_spectrum_parameters.xlsx', 'peak_name',
    ios_xps_per_step_factory, 'xps')


# define the FileDataRouter for the xas step per_step function
xas_step = make_filedatarouter_instance(
    'test_xas_step_spectrum_settings.xlsx', 'edge_name',
    'test_xas_step_spectrum_parameters.xlsx', 'edge_name',
    ios_xas_stepspectra_per_step_factory, 'xas_step')


# define the FileDataRouter for the xas fly per_step function
xas_fly = make_filedatarouter_instance(
    'test_xas_fly_spectrum_settings.xlsx', 'edge_name',
    'test_xas_fly_spectrum_parameters.xlsx', 'edge_name',
    ios_xas_flyspectra_per_step_factory, 'xas_fly')


# define the FileDataRouter for the scans
multiscan = make_filedatarouter_instance(
    'test_scan_settings.xlsx', 'scan_name',
    'test_scan_parameters.xlsx', 'scan_name',
    ios_multiscan_plan_factory_wrapper, 'multiscan')



def count_step(detectors, step, pos_cache):
    """Inner loop of a count scan
This conversation was marked as resolved by awalter-bnl
    This is the default function for ``per_step`` in count plans.
    Parameters
    ----------
    detectors : iterable
        devices to read
    step : dict
        maps motors to positions in this step. Not used, included for API
        compatibility with ``bluesky.plan_stubs.one_nd_step``, and similar
        custom ``per_step`` functions only.
    pos_cache : dict
        maps motors to their last-set positions. Not used, included for API
        compatibility with ``bluesky.plan_stubs.one_nd_step``, and similar
        custom ``per_step`` functions only.
    """

    yield from trigger_and_read(list(detectors))


def ios_count(detectors, num=1, delay=None, *, per_step=None, md=None):
    """
    Take one or more readings from detectors.
    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    num : integer, optional
        number of readings to take; default is 1
        If None, capture data until canceled
    delay : iterable or scalar, optional
        Time delay in seconds between successive readings; default is 0.
    per_step : callable, optional
        hook for customizing action of inner loop (messages per step)
        Expected signature:
        ``f(detectors, step, pos_cache) -> plan (a generator)``
        ..note ::
            In this case ``step`` and ``pos_cache`` are provided purely for API
            compatibility with ``bluesky.plan_stubs.one_nd_step`` and similar
            custom ``per_step`` functions, hey will be passed empty dicts.
    md : dict, optional
        metadata
    Notes
    -----
    If ``delay`` is an iterable, it must have at least ``num - 1`` entries or
    the plan will raise a ``ValueError`` during iteration.
    """
    if num is None:
        num_intervals = None
    else:
        num_intervals = num - 1
    _md = {'detectors': [det.name for det in detectors],
           'num_points': num,
           'num_intervals': num_intervals,
           'plan_args': {'detectors': list(map(repr, detectors)), 'num': num},
           'plan_name': 'count',
           'hints': {}
           }
    _md.update(md or {})
    _md['hints'].setdefault('dimensions', [(('time',), 'primary')])

    if per_step is None:
        per_step = count_step

    @stage_decorator(detectors)
    @run_decorator(md=_md)
    def inner_count():
        return (yield from repeat(partial(per_step, detectors, {}, {}),
                                  num=num, delay=delay))

    return (yield from inner_count())
