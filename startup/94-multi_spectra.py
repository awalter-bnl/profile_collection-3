from bluesky.plan_stubs import move_per_step, trigger_and_read, mv
from IPython import get_ipython
import numpy
ip = get_ipython()


class MultiSpectraValueError(ValueError):
    ...


test_spectrum_parameters = {
    'C1s': {'low_energy': 285, 'high_energy': 300, 'step_size': 5},
    'O1s': {'low_energy': 525, 'high_energy': 540, 'step_size': 5}}


test_spectrum_settings = {
    'C1s': {'det.gain': 2, 'det.decade': 1},
    'O1s': {'det.gain': 3, 'det.decade': 2}}


test_scan_map = {
    'test_scan1': {'detectors': 'det', 'spectra_type': 'xps',
                   'interesting_edges': 'C1s',
                   'plan': 'scan', 'arguments': 'motor,0,5,4',
                   'hw.motor2.x': 100},
    'test_scan2': {'spectra_type': 'xps',
                   'interesting_edges': 'C1s,O1s',
                   'plan': 'count', 'arguments': 2,
                   'hw.motor2.x': 200}}


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
    for attr in attrs.split('.'):
        if attr != '':
            obj = getattr(obj, attr)
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
    move_dict, dict
        A dictionary mapping ``ophyd.Device``s to be moved to positions
        to move to. See above for a description of this dictionary.
    '''
    settings_list = []
    for key, value in move_dict.items():
        obj = _str_to_obj(key)
        settings_list.extend([obj, value])

    yield from mv(*settings_list)


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
    def __init__(self, name):
        self.dictionary = {}
        self._default_filepath = ''
        self.filepath = ''

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
        ...  # TODO: write the part that loads the data from the file

    def reset_defaults(self):
        '''Resets ``self.filepath`` to the default value and reloads the dict.
        '''
        self.filepath = self._default_filepath
        self.load()


class MultiScan():
    '''A class to be used for sequencing a scan list at IOS.

    This class is intended to store and perform a scan, or a list of scans, as
    referenced in  ``self.scanmap``. ``self.scanmap`` must have the keys
    'dets', 'spectra_type' and 'interesting_edges', it may also contain the
    keys 'plan' and 'arguments' to indicate a particular plan to call and what
    args to include. Finally it may also contain keys which relate to any
    'settable' ``ophyd.device`` (like 'manip.x') and a value to set it to.
    These values will be set prior to the scan being performed.

    Call Parameters
    ---------------
    scans : list or string
        A scan, or list of scans, to execute. The scan_names must be a key in
        ``self.scan_map``.

    Initialization Parameters
    -------------------------
    scan_arguments : dict
        A dictionary that maps scan types (count, scan,...) to the arguments
        that each scan requires (kwargs assume default values, except for
        ``per_step`` which is internally set.) This dictionary is set at
        initialization time.
    default_map_filepath : string or Path
        The default filepath for the file containing the scan_map information.

    Attributes
    ----------
    scanmap : FileDict
        A FileDict object that has an attribute, dictionary, that maps
        scan names to scan types and parameters related to each scan to be
        performed. It also has attributes for loading information into the dict
        from a file.
    scan_arguments : dict
        A dictionary that maps scan types (count, scan,...) to an ordereddict
        that maps the arguments that each scan requires to a type. Types can be
        any ``type`` object or 'obj'. For all types but 'obj' the input will be
        converted using the type (eg. str(val) ). For obj the val will be
        passed to ``_str_2_obj``. Kwargs assume default values, except for
        ``per_step`` which is internally set. This dictionary is set at
        initialization time.
    validate : func
        A function that validates that a proposed scan can occur with the
        currently loaded dictionaries.
    '''
    scanmap = FileDict('scanmap')

    def __init__(self, scan_arguments, default_map_filepath, name):
        self.scan_arguments = scan_arguments
        self.name = name
        self.scanmap._default_filepath = default_map_filepath
        self.scanmap.reset_defaults()

    def _convert_arguments(self, plan, arguments):
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
        for i, (key, val) in enumerate(self.scan_arguments[plan].items()):
            if type(val) == type:
                args.append(val(arguments[i]))
            elif type(val) == str and val == 'obj':
                args.append(_str_to_obj(arguments[i]))
            else:
                raise MultiSpectraValueError(
                    f'The value found in {self.name}.detectors[{key}] is not a'
                    f' valid value. Valid values are any ``type`` object or '
                    f'the string "obj"')
        return args

    def __call__(self, scans):
        # check that scans is a list or a str, if a str convert to a list
        if type(scans) == str:
            scans = [scans]
        elif type(scans) != list:
            raise MultiSpectraValueError(
                f'when calling ``{self.name}(scans)`` `scans` is expected'
                f' to be a str or a list, instead we got {scans} which is of'
                f' type {type(scans)}.')
        # step through each of the requested scans and perform it.
        for scan in scans:
            scaninfo = self.scanmap.dictionary[scan]
            dets = [_str_to_obj(det)
                    for det in scaninfo['detectors'].split(',')]
            args = self._convert_arguments(scaninfo['plan'],
                                           scaninfo['arguments'].split(','))
            per_step = ip.user_ns[scaninfo['spectra_type']](
                scaninfo['interesting_edges'].split(','))
            yield from ip.user_ns[scaninfo['plan']](dets, *args,
                                                    per_step=per_step)


class MultiSpectra():
    '''A class that is used for the acquisition of 'spectra' at IOS

    This class is intended to store a set of dictionaries associated with
    scans where multiple 'spectra' need to be taken at each step in a 'plan'.
    It also is a callable function that returns a ``per_step`` function,
    analogous to ``bluesky.plan_stubs.one_nd_step``. This plan can be used with
    the ``per_step`` kwarg in any plan that accepts ``per_step`` kwargs.

    An instance of this class will have the following parameters and
    attributes:

    Call Parameters
    ---------------
    spectra, str or list
        The spectrum to perform, or a list of spectra to perform, at each
        step of a scan. The names listed here must be present as keys in both
        the ``self.parameters`` and ``self.settings`` dictionaries.

    Initialization Parameters
    -------------------------
    detectors : dict
        A dictionary that maps the detectors associated with this scan type to
        a value that indicates if the detector is a '0D' detector, where
        each trigger returns a single float or int, or a '1D' detector, where
        each trigger returns a full spectrum. This dictionary is defined at
        initialization time.
    default_parameters_filepath : str or Path
        The default filepath for the spectrum 'parameters' file.
    default_settings_filepath : str or Path
        The default filepath for the spectrum 'settings' file.
    name : str, optional
        The name of the instantiated version of this class.

    Attributes
    ----------
    parameters : FileDict
        A FileDict object with an attribute dictionary that maps spectrum names
        (like 'C1s') to the parameters that define the spectrum, which are by
        definition 'low_energy', 'high_energy' and 'step_size'.
    settings : FileDict
        A FileDict object with an attribute dictionary that maps spectrum names
        (like 'C1s') to the parameters that need to be defined differently for
        each spectrum. Examples might include items like 'det1.gain' or
        'det1.exposure_time', but can include any 'settable' ``ophyd`` object.
    detectors : dict
        A dictionary that maps the detectors associated with this scan type to
        an attribute associated with the keys from the ``self.parameters``
        dict. For point-detectors (a single value for trigger) there should be
        a single key in the detector sub-dictionary called 'spectra_axis' that
        indicates the axis (eg. photon energy) for bluesky to scan with the
        values from ``self.parameters``. This dictionary is defined at
        instantiation time.
    validate : func
        A function that validates that a proposed scan can occur with the
        currently loaded dictionaries.
    '''

    parameters = FileDict('parameters')
    settings = FileDict('settings')

    def __init__(self, detectors, default_parameters_filepath,
                 default_settings_filepath, name):
        self.detectors = detectors
        self.name = name
        self.parameters._default_filepath = default_parameters_filepath
        self.settings._default_filepath = default_settings_filepath
        self.parameters.reset_defaults()
        self.settings.reset_defaults()

    def __call__(self, spectra):
        # check that spectra is a list or a str, if a str convert to a list
        if type(spectra) == str:
            spectra = [spectra]
        elif type(spectra) != list:
            raise MultiSpectraValueError(
                f'when calling ``{self.name}(spectra)`` `spectra` is expected'
                f' to be a str or a list, instead we got {spectra} which is of'
                f' type {type(spectra)}.')

        # define the plan that results in a single 'spectra' being taken.
        def _spectrum(detectors, motors, axis, stream_name):
            '''returns a plan that will perform a single spectra.

            This steps through each value defined in ``self.parameters`` under
            the key 'stream_name' along the axis defined in
            'axis'.

            Parameters
            ----------
            detectors, list
                A list of detectors to trigger and read at each step.
            motors : list
                A list of the motors involved in the outer 'scan'.
            axis : object
                ``ophyd.Device`` object that defines the 'axis' to scan the
                spectra over.
            stream_name, str
                The stream_name to use in trigger_and_read, also the name of
                the key in ``self.settings`` and ``self.parameters``.
            '''

            parameters = self.parameters.dictionary[stream_name]

            # set the required values in self.settings for this spectra

            yield from _move_from_dict(self.settings.dictionary[stream_name])

            # step through each step in the 'spectra' and record the results
            for spectra_pos in numpy.arange(parameters['low_energy'],
                                            (parameters['high_energy'] +
                                             parameters['step_size']/2),
                                            parameters['step_size']):
                yield from mv(axis, spectra_pos)
                yield from trigger_and_read(
                    list(detectors) + list(motors) + [axis], name=stream_name)

        # define the `per_step` function that is to be returned.
        def _multi_spectrum(detectors, step, pos_cache):
            '''This function is used to trigger multiple spectra at each point
            in a scan.

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
            # move to the required position
            yield from move_per_step(step, pos_cache)

            # determine if the each of the specifed detectors that are also in
            # self.detectors take a spectra with a trigger or not:
            spectra_dets = set(detectors).intersection(set(self.detectors))
            if all('spectra_axis' in self.detectors[det].keys()
                   for det in spectra_dets):  # if all spectra_dets are 0D
                spectra_axes = [self.detectors[det]['spectra_axis']
                                for det in spectra_dets]
                spectra_axis = spectra_axes[0]
                if all(val == spectra_axis for val in spectra_axes):
                    for spectrum in spectra:  # step through + acquire spectra
                        yield from _spectrum(detectors, motors,
                                             spectra_axis, spectrum)
                else:
                    raise MultiSpectraValueError(
                        f'The "spectra_axis" kwarg in {self.name}.detectors '
                        f'returns {spectra_axes} for the detectors '
                        f'{spectra_dets}. However, the "spectra_axis" should '
                        f'be the same for all.')
            elif all('low_energy' in self.detectors[det].keys()
                     for det in spectra_dets):  # if all spectra_dets are 1D
                for spectrum in spectra:  # step through and acquire spectra
                    # set the required values in self.settings for this spectra
                    yield from _move_from_dict(
                        self.settings.dictionary[spectrum])
                    # set the required values in self.detectors[det]
                    for det in spectra_dets:
                        yield from _move_from_dict(
                            {self.detectors[det].get(k, k): v
                             for k, v in self.parameters.dictionary.items()})
                    # trigger and read each spectra.
                    yield from trigger_and_read(list(detectors)+list(motors),
                                                name=spectrum)
            else:
                spectra_det_keys = {det.name: self.detectors[det].keys()
                                    for det in spectra_dets}
                raise MultiSpectraValueError(
                    f'In ``multispectra._multi_spectrum`` it is expected that '
                    f' each of the requested detectors that are included in '
                    f'{self.name}.detectors also have either "spectra_axis" '
                    f'or the group ["low_energy", "high_energy", "step_size"] '
                    f'as keys. The detectors fitting this description have the'
                    f' the following keys: {spectra_det_keys}')

        return _multi_spectrum  # return the `per_step` function
