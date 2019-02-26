from bluesky.plan_stubs import move_per_step, trigger_and_read, mv
from IPython import get_ipython
import numpy
from ophyd import Device
ip=get_ipython()

class MultiSpectraValueError(ValueError):
    ...


test_spectrum_parameters = {
    'C1s': {'low_energy': 285, 'high_energy': 300, 'step_size': 0.2},
    'O1s': {'low_energy': 525, 'high_energy': 540, 'step_size': 0.2}}


test_spectrum_settings = {
    'C1s': {'det.gain': 2, 'det.decade': 1},
    'O1s': {'det.gain': 3, 'det.decade': 2}}


test_scan_map = {
    'test_scan1': {'spectra_type': 'xps', 'interesting_edges': ['C1s'],
                   'plan': 'scan', 'arguments': 'num_points,start1,stop1',
                   'hw.motor2.x': 100},
    'test_scan2': {'spectra_type': 'xps',
                   'interesting_edges': ['C1s', 'O1s'],
                   'plan': 'count', 'arguments': 'num_points',
                   'hw.motor2.x': 200}}


class MultiScan():
    '''A class to be used for sequencing a scan list at IOS.

    This class is intended to store and perform a list of scans as referenced
    in order.


    Attributes
    ----------
    scan_map : dict
        A dictionary that maps scan names to scan types and parameters related
        to the each scan to be performed.
    '''
    ...


class MultiSpectra():
    '''A class that is used for the acquisition of 'spectra' at IOS

    This class is intended to store a set of dictionaries associated with
    scans where multiple 'spectra' need to be taken at each step in a 'plan'.
    It also is a callable function that returns a ``per_step`` function,
    analagous to ``bluesky.plan_stubs.one_nd_step``. This plan can be used with
    the ``per_step`` kwarg in any plan that accepts ``per_step`` kwargs.

    An instance of this class will have the following parameters and
    attributes:

    Call Parameters
    ---------------
    spectra, str or list
        The spectrum to perform, or a list of spectrum to perform, at each
        step of a scan. The names listed here must be present as keys in both
        the ``self.parameters`` and ``self.settings`` dictionaries.

    Initialization Parameters
    -------------------------
    detectors : dict
        A dictionary that maps the detectors associated with this scan type to
        a value that indicates if the detector is a '0D' detector, where
        each trigger returns a single float ot int, or a '1D' detector, where
        each trigger returns a full spectra. This dictionary is defined at
        instantiation time.
    default_parameters_filepath : str or Path
        The default filepath for the spectrum 'parameters' file.
    default_settings_filepath : str or Path
        The default filepath for the spectrum 'settings' file.
    name : str, optional
        The name of the instantiated version of this class.

    Attributes
    ----------
    parameters : dict
        A dictionary that maps spectrum names (like 'C1s') to the parameters
        that define the spectrum, which are by definition 'low_energy',
        'high_energy' and 'step_size'.
    settings : dict
        A dictionary that maps spectrum names (like 'C1s') to the parameters
        that need to be defined differently for each spectrum. Examples might
        include items like 'det1_gain' or 'det1_exposure_time', but can include
        any 'settable' ``ophyd`` object.
    parameters_filepath : str or Path
        The filepath for the spectrum parameters Office Excel/LibreOffice Calc
        file.
    settings_filepath : str or Path
        The filepath for the spectrum settings Office Excel/LibreOffice Calc
        file.
    detectors : dict
        A dictionary that maps the detectors associated with this scan type to
        an attribute associated with the keys from the ``self.parameters``
        dict. For point-detecotors (a single value for trigger) their should be
        a single key in the detector sub-dictionary called 'spectra_axis' that
        indicates the axis(eg. photon energy) for bluesky to scan with the
        values from ``self.parameters``. This dictionary is defined at
        instantiation time.
    load_dicts : func
        A function that loads the parameters from excell files and records them
        in the dictionaries above.
    reset_dicts : func
        A function that resets the parameter and settings dictionaries, and
        filepaths back to the default values.
    validate : func
        A function that validates that a proposed scan can occur with the
        currently loaded dictionaries.
    '''

    def __init__(self, detectors, default_parameters_filepath,
                 default_settings_filepath, name=''):
        self.detectors = detectors
        self._default_parameters_filepath = default_parameters_filepath
        self._default_settings_filepath = default_settings_filepath
        self.parameters_filepath = default_parameters_filepath
        self.settings_filepath = default_settings_filepath
        self.settings = {}
        self.parameters = {}
        self.name = name

    def __call__(self, spectra):
        # check that spectra is a list or a str, if a str convert to a list
        if type(spectra) == str:
            spectra = []
        elif type(spectra) != list:
            raise MultiSpectraValueError(
                f'when calling ``{self.name}(spectra)`` `spectra` is expected'
                f' to be a str or a list, instead we got {spectra} which is of'
                f' type {type(spectra)}.')

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
                A dictionary mapping ``ophyd.Device``s to be moved to postions
                to move to. See above for a description of of this dictionary.
            '''
            settings_list = []
            for key, value in move_dict.items():
                parent, _, attrs = key.partition('.')
                obj = ip.user_ns[parent]
                for attr in attrs.split('.'):
                    obj=getattr(obj,attr)
                settings_list.extend([obj, value])

            yield from mv(*settings_list)

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

            parameters = self.parameters[stream_name]

            # set the required values in self.settings for this spectra

            yield from _move_from_dict(self.settings[stream_name])

            # step through each step in the 'spectra' and record the results
            for spectra_pos in numpy.arange(parameters['low_energy'],
                                            (parameters['high_energy']+
                                             parameters['step_size']/2),
                                            parameters['step_size']):
                yield from mv(axis, spectra_pos)
                yield from trigger_and_read(
                    list(detectors)+list(motors)+[axis], name=stream_name)

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
                        f'{spectra_dets} However, the "spectra_axis" should be'
                        f' the same for all.')
            elif all('low_energy' in self.detectors[det].keys()
                     for det in spectra_dets):  # if all spectra_dets are 1D
                for spectrum in spectra:  # step through and acquire spectra
                    # set the required values in self.settings for this spectra
                    yield from _move_from_dict(self.settings(spectrum))
                    # trigger and read each spectra.
                    yield from trigger_and_read(list(detectors)+list(motors),
                                                name=spectrum)

        return _multi_spectrum # return the `per_step` function
