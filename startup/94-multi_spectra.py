from bluesky.plan_stubs import move_per_step, trigger_and_read, mv
from bluesky.preprocessors import stub_wrapper
from IPython import get_ipython
import numpy
from ophyd.signal import Signal
import pandas
ip = get_ipython()


# Define ``ophyd.Signal``'s that we can use to track which spectra, group and
# step we are at in the scan when necessary.
spectra_num = Signal(name='spectra_num')
group_num = Signal(name='group_num')
step_num = Signal(name='step_num')


class MultiSpectraValueError(ValueError):
    ...


class PlanSchedulerValueError(ValueError):
    ...


# This section is some temporary test objects
from ophyd.sim import hw
from bluesky.plans import count, scan
from bluesky.simulators import summarize_plan


def ERamp(dets, start, stop, velocity, streamname='primary'):
    yield from count(dets)


hw = hw()
specs = hw.det2
specs.name = 'specs'
specs.gain = Signal(name='specs_gain')
specs.decade = Signal(name='specs_decade')
specs.low_energy = Signal(name='specs_low_energy')
specs.high_energy = Signal(name='specs_high_energy')
specs.step_size = Signal(name='specs_step_size')


def _set_mode(val):
    yield from mv(specs.acquisition_mode, val)


specs.set_mode = _set_mode
specs.acquisition_mode = Signal(name='specs_acquisition_mode')
specs.num_acquisitions = Signal(name='specs_num_acquisitions')
vortex = hw.det1
vortex.name = 'vortex'
vortex.gain = Signal(name='vortex_gain')
vortex.decade = Signal(name='vortex_decade')


class Pgm():
    def __init__(self, name):
        self.energy = Signal(name='pgm_energy')
        self.name = name


pgm = Pgm('pgm')
motor = hw.motor
motor1 = hw.motor1
motor2 = hw.motor2
det = hw.det


def _str_to_obj(str_ref):
    '''Converts a string ref to an ``ophyd.Device`` object to an reference.

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


# define the plan that results in multiple 'scans' being performed at each step
def ios_multiscan_plan_factory(scans):
    '''returns a plan that will perform multiple scans in order.

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

    # Below is a dictionary that maps scan types (count, scan,...) to a
    # dictionary that maps the arguments that each scan requires to a type.
    # Types can be any ``type`` object or 'obj'. For all types but 'obj' the
    # input will be converted using the type (eg. str(val) ). For obj the val
    # will be passed to ``_str_2_obj``. Kwargs assume default values.
    plan_arguments = {
        'scan': {'motor1': 'obj', 'start1': float, 'stop1': float, 'num': int},
        'count': {}}

    def _convert_arguments(plan, arguments):
        '''converts the arguments value in scanmap to a useable list

        Parameters
        ----------
        plan : str
            The key to extract the type information from ``self.detectors``
        arguments : list
            The list of arguments extracted from ``self.scanmap.dictionary``

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
                raise PlanSchedulerValueError(
                    f'The value found from plan_arguments[{key}] in '
                    f'"ios_multi_scan_plan_factory" is not a valid value.'
                    f'Valid values are any ``type`` object or the string "obj"'
                    )
        return args

    # step through each of the requested scans and perform it.
    for (scan_name, parameters, settings) in scans:
        # check if a plan and arguments are given, use 'count' if not.
        plan = parameters.get('plan', 'count')
        arguments = parameters.get('arguments', [])

        # move to the predefined positions for this scan
        yield from _move_from_dict(settings)

        # convert detectors to a list of ``ophyd.Device`` objects.
        dets = [_str_to_obj(det)
                for det in parameters['detectors'].split(',')]
        # convert the arguments basd on the plan type
        args = _convert_arguments(plan, arguments)
        # extract the per_step function from the 'spectra_type' parameter
        spectra_obj = ip.user_ns[parameters['spectra_type']]
        spectra_list = parameters['interesting_spectra'].split(',')
        # define a function that loops over each spectra group 'group_num'
        # times
        _per_step = spectra_obj(spectra_list)

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
                yield from _per_step(detectors+extra_dets, step, pos_cache)

        # extract out the spectra meta-data
        md = {'spectra': {}}
        md['spectra'] = {
            k: {'parameters': spectra_obj.parameters.dictionary[k],
                'settings': spectra_obj.settings.dictionary[k]}
            for k in spectra_list}
        md['scan'] = {'settings': settings, 'parameters': parameters}
        # yield from the required plan, num_scans times.
        for scan_num in range(parameters['num_scans']):
            yield from ip.user_ns[plan](dets, *args, per_step=_group_step,
                                        md=md)


# define the plan that results in multiple 'xps' spectra being taken per_step.
def ios_xps_per_step_factory(spectra):
    '''returns a per_step function that will perform multiple XPS spectra.

    This yields a per_step function that will set each value required to
    generate an XPS spectra using the specs detector at IOS and then triggers
    the detector (and any ancillary detectors) which executes the spectra for
    each spectra in `spectra`.

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

        This function is analagous to the `bluesky.plan_stubs.one_nd_step`
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

        for (peak_name, parameters, settings) in spectra:
            # move the devices in settings into place
            yield from _move_from_dict(settings)

            # set the parameters for the scan
            yield from mv(specs.low_energy, parameters['low_energy'],
                          specs.high_energy, parameters['high_energy'],
                          specs.step_size, parameters['step_size'],
                          specs.num_acquisitions, parameters['num_spectra'],
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
    '''returns a per_step function that will perform multiple XAS spectra.

    This yields a per_step function that will set each value required to
    generate an XAS spectra by fly scanning over the energy axis at IOS for
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

    def _per_step(detectors, step, pos_cache):
        '''This triggers multiple spectra at each point in a plan.

        This function is analagous to the `bluesky.plan_stubs.one_nd_step`
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
            extra_dets = []
            # add ``spectra_num`` to the extra_dets list if needed
            if parameters['num_spectra'] is None:
                parameters['num_spectra'] = 1
            elif parameters['num_spectra'] > 1:
                extra_dets.append(spectra_num)
            # collect num_spectra individual spectra at this point.
            for num_spectra in range(1, parameters['num_spectra']+1):
                if spectra_num in extra_dets:  # update spectra_num if needed
                    yield from mv(spectra_num, num_spectra)
                # perform the fly scan
                yield from stub_wrapper(
                    ERamp(list(detectors)+list(motors)+[pgm.energy]+extra_dets,
                          parameters['low_energy'],
                          parameters['high_energy'],
                          parameters['velocity'],
                          streamname=edge_name))
    return _per_step


# define the plan that results in multiple 'xas_step' spectra being taken
# per_step.
def ios_xas_stepspectra_per_step_factory(spectra):
    '''returns a per_step function that will perform multiple XAS spectra.

    This returns a per_step function, and a metadata dict that will set each
    value required to generate an XAS step spectra using the specs detector at
    IOS and then steps through each energy point and triggers and reads the
    detector (and any ancillary detectors) for each `spectra`.

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

    def _per_step(detectors, step, pos_cache):
        '''This triggers multiple spectra at each point in a plan.

        This function is analagous to the `bluesky.plan_stubs.one_nd_step`
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

        for (edge_name, parameters, settings) in spectra:
            # move the devices in settings into placd
            yield from _move_from_dict(settings)
            extra_dets = []
            # add ``spectra_num`` to the extra_dets list if needed
            if parameters['num_spectra'] is None:
                parameters['num_spectra'] = 1
            elif parameters['num_spectra'] > 1:
                extra_dets.append(spectra_num)
            # collect num_spectra individual spectra at this point.
            for num_spectra in range(1, parameters['num_spectra']+1):
                if spectra_num in extra_dets:  # update spectra_num if needed
                    yield from mv(spectra_num, num_spectra)
                for energy in numpy.arange(parameters['low_energy'],
                                           parameters['high_energy'] +
                                           parameters['step_size']/2,
                                           parameters['step_size']):
                    yield from mv(pgm.energy, energy)
                    yield from trigger_and_read(
                        list(detectors)+list(motors)+[pgm.energy]+extra_dets,
                        name=edge_name)

    return _per_step


class FileDict():
    '''A class used for dictionaries loaded from Excel files.

    This class should be used to define an attribute for dictionaries loaded
    from Office Excel/LibreOffice Calc files and the assoicated attributes for
    the dictionary.

    Parameters
    ----------
    name : str
        The name of this attribute.

    Attributes
    ----------
    dictionary : dict
        The dictionary containing the loaded information.
    filepath : string or Path
        The filepath to be used when loading the dictionary.
    load : func
        A function that loads a dictionary using the file found at the
        ``filepath`` attribute.
    reset_defaults : func
        A function that resets the dictionary and the filepath to the default
        values.
    '''
    def __init__(self, name, default_filepath, index_name):
        self.name = name
        self.dictionary = {}
        self._default_filepath = default_filepath
        self.filepath = default_filepath
        self._index_name = index_name  # The name used as the index in the file
        self.reset_defaults()

    def load(self, filepath=None):
        '''Loads up a dictionary from a file

        Loads a dictionary from the file found at ``self.filepath``, or found
        using the optional 'filepath' kwarg. If using the optional 'filepath'
        kwarg it also updates ``self.filepath``

        Parameters
        ----------
        filepath : str, Path or None
            filepath to load the dictionary data from, if the default
            ``filepath=None`` is used it uses the value found in
            ``self.filepath``.
        '''
        # if filepath = None use ``self.filepath`` otherwise update
        # ``self.filepath``
        if filepath is None:
            filepath = self.filepath
        else:
            self.filepath = filepath

        temp_dict = {}

        # extract the information form the file and write it to the dictionary
        f = pandas.read_excel(filepath)
        f = f.set_index(self._index_name)

        for row_name in f.index:
            temp_dict[row_name] = dict(f.loc[row_name])

        self.dictionary = temp_dict

    def reset_defaults(self):
        '''Resets ``self.filepath`` to the default value and reloads the dict.
        '''
        self.filepath = self._default_filepath
        self.load()


class PlanSchedular():
    '''A class that is used to schedule many plans and returns a single plan.

    This class is intended to store a set of dictionaries associated with
    multiple ``self.plan_factory`` function call. When called an instance of
    this class takes in a list of 'items' and returns a plan that does the
    following:

    1. generate a list of ``(item, self.parameters.dictionary[item],
        self.settings.dictionary[item])`` tuples from list `items`.
    3. Calls ``self.function`` passing in the tuple list
    4. Return the output plan.

    An instance of this class will have the following parameters and
    attributes:

    Call Parameters
    ---------------
    items : str or list
        The item to perform or a list of items to perform  at each step of a
        plan. The items listed here must be present as keys in both the
        ``self.parameters.dictionary`` and ``self.settings,dictionary``. Using
        the str 'all' will result in all keys from the two dictionaries being
        used provided they both have exactly the same keys.

    Initialization Parameters
    -------------------------
    name : str
        The name of the instantiated version of this class.
    default_parameters_filepath : str or Path
        The default filepath for the spectrum 'parameters' file.
    default_settings_filepath : str or Path
        The default filepath for the spectrum 'settings' file.
    parameters_index_name : str
        The column name that indicates the 'index' in the parameters file,
        default is 'edge_name'.
    settings_index_name : str
        The column name that indicates the 'index' in the settings file,
        default is 'edge_name'.

    Attributes
    ----------
    parameters : FileDict
        A FileDict object with an attribute dictionary that maps spectrum names
        (like 'C1s') to the parameters that define the spectrum, which are by
        definition 'low_energy', 'high_energy' and 'step_size'.
    settings : FileDict
        A FileDict object with an attribute dictionary that maps 'items' to a
        dictionary mapping the ``ophyd.Device``'s that need to be set for each
        'item' to the value to set it to. Examples might include items like
        'det1.gain' or 'det1.exposure_time', but can include any 'settable'
        ``ophyd.Device`` object.
    function : func
        A function that is to be called at step 2 above.
    validate : method
        A method that validates that a proposed 'item' can be used with the
        currently loaded dictionaries.
    '''

    def __init__(self, name, function,
                 default_parameters_filepath, parameters_index_name,
                 default_settings_filepath, settings_index_name):
        self.name = name
        self.function = function
        self.parameters = FileDict('parameters', default_parameters_filepath,
                                   parameters_index_name)
        self.settings = FileDict('settings', default_settings_filepath,
                                 settings_index_name)

    def __call__(self, items):
        # check that spectra is a list or a str, if a str convert to a list
        if items == 'all':
            items = list(self.settings.keys())
        elif isinstance(items, str):
            items = [items]
        elif not isinstance(items, list):
            raise PlanSchedulerValueError(
                f'The items passed to ``{self.name}(items)`` is expected to be'
                f' a str or a list, instead we got {items} which is of type '
                f'{type(items)}.')

        # check that items are keys in the two dictionaries
        if (not set(items) <= set(self.parameters.dictionary)
                or not set(items) <= set(self.settings.dictionary)):
            raise PlanSchedulerValueError(
                f'The items passed to {self.name}(items) are not all keys in '
                f'{self.name}.parameters.dictionary or {self.name}.settings.'
                f'dictionary\nitems are: \n\t{items}\n{self.name}.'
                f'parameters.dictionary keys are:\n\t'
                f'{self.parameters.dictionary.keys()}\n{self.name}.'
                f'settings.dictionary keys are:\n\t'
                f'{self.settings.dictionary.keys()}')

        # Generate the list of tuples
        tuple_list = [(k, self.parameters.dictionary[k],
                       self.settings.dictionary[k]) for k in items]

        # Call self.function
        output = self.function(tuple_list)

        return output  # return the output of self.function


# define the PlanSchedular for the xps per_step function
xps = PlanSchedular('xps', ios_xps_per_step_factory,
                    'test_spectrum_parameters.xlsx', 'peak_name',
                    'test_spectrum_settings.xlsx', 'peak_name')


# define the PlanSchedular for the xas step per_step function
xas_step = PlanSchedular('xas_step', ios_xas_stepspectra_per_step_factory,
                         'test_xas_spectrum_parameters.xlsx', 'edge_name',
                         'test_xas_spectrum_settings.xlsx', 'edge_name')


# define the PlanSchedular for the xas fly per_step function
xas_fly = PlanSchedular('xas_fly', ios_xas_flyspectra_per_step_factory,
                        'test_xas_fly_spectrum_parameters.xlsx', 'edge_name',
                        'test_xas_fly_spectrum_settings.xlsx', 'edge_name')


# define the PlanScheduler for the scans
multiscan = PlanSchedular('multiscan', ios_multiscan_plan_factory,
                          'test_scan_parameters.xlsx', 'scan_name',
                          'test_scan_settings.xlsx', 'scan_name')
