from enum import Enum
from ophyd.areadetector.base import EpicsSignalWithRBV, ADComponent
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.detectors import DetectorBase
from ophyd.areadetector.filestore_mixins import FileStorePluginBase, FileStoreIterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin, StatsPlugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
from ophyd.device import Staged
from ophyd.ophydobj import Kind
from ophyd.signal import EpicsSignalRO, EpicsSignal
import time as ttime


class SpecsDetectorCam(CamBase):
    '''This is a class that defines the cam class for a SPECS detector
    '''

    # Controls
    connect = ADComponent(EpicsSignal, 'CONNECTED_RBV', write_pv='CONNECT', kind=Kind.omitted, name='connect' )
    status_message = ADComponent(EpicsSignalRO, 'StatusMessage_RBV', string=True, kind=Kind.omitted, name='status_message')
    server_name = ADComponent(EpicsSignalRO, 'SERVER_NAME_RBV', string=True, kind=Kind.omitted, name='server_name')
    protocol_version = ADComponent(EpicsSignalRO, 'PROTOCOL_VERSION_RBV', string=True, kind=Kind.omitted, name='protocol_version')

    # Energy Controls
    pass_energy = ADComponent(EpicsSignalWithRBV, 'PASS_ENERGY', name='pass_energy')
    low_energy = ADComponent(EpicsSignalWithRBV, 'LOW_ENERGY', name='low_energy')
    high_energy = ADComponent(EpicsSignalWithRBV, 'HIGH_ENERGY', name='high_energy')
    energy_width = ADComponent(EpicsSignalRO, 'ENERGY_WIDTH_RBV', name='energy_width')
    kinetic_energy = ADComponent(EpicsSignalWithRBV, 'KINETIC_ENERGY', name='kinetic_energy')
    retarding_ratio = ADComponent(EpicsSignalWithRBV, 'RETARDING_RATIO', name='retarding_ratio')
    step_size = ADComponent(EpicsSignalWithRBV, 'STEP_SIZE', name='step_size')
    fat_values = ADComponent(EpicsSignalWithRBV, 'VALUES', name='fat_values')
    samples = ADComponent(EpicsSignalWithRBV, 'SAMPLES', name='samples')

    # Configuration
    scan_range = ADComponent(EpicsSignalWithRBV, 'SCAN_RANGE', kind=Kind.config, name='scan_range')
    acquire_mode = ADComponent(EpicsSignalWithRBV, 'ACQ_MODE', kind=Kind.config, name='acquire_mode')
    define_spectrum = ADComponent(EpicsSignalWithRBV, 'DEFINE_SPECTRUM', kind=Kind.config, name='define_spectrum')
    validate_spectrum = ADComponent(EpicsSignalWithRBV, 'VALIDATE_SPECTRUM', kind=Kind.config, name='validate_spectrum')
    safe_state = ADComponent(EpicsSignalWithRBV, 'SAFE_STATE', kind=Kind.config, name='safe_state')
    pause_acq = ADComponent(EpicsSignalWithRBV, 'PAUSE_RBV', kind=Kind.config, name='pause_acq')

    #Data Progress
    current_point = ADComponent(EpicsSignalRO, 'CURRENT_POINT_RBV', kind=Kind.omitted, name='current_point')
    current_channel = ADComponent(EpicsSignalRO, 'CURRENT_CHANNEL_RBV', kind=Kind.omitted, name='current_channel')
    region_time_left = ADComponent(EpicsSignalRO, 'REGION_TIME_LEFT_RBV', kind=Kind.omitted, name='region_time_left')
    region_progress = ADComponent(EpicsSignalRO, 'REGION_PROGRESS_RBV', kind=Kind.omitted, name='region_progress')
    total_time_left = ADComponent(EpicsSignalRO, 'TOTAL_TIME_LEFT_RBV', kind=Kind.omitted, name='total_tiem_left')
    progress = ADComponent(EpicsSignalRO, 'PROGRESS_RBV', kind=Kind.omitted, name='progress')
    total_points_iteration = ADComponent(EpicsSignalRO, 'TOTAL_POINTS_ITERTION_RBV', kind=Kind.omitted, name='total_points_iteration')
    total_points = ADComponent(EpicsSignalRO, 'TOTAL_POINTS_RBV', kind=Kind.omitted, name='total_points')


class FileStoreHDF5Single(FileStorePluginBase):
    '''This FileStore mixin is used when running the AreaDetector hdf5 plugin
    in `Single` mode (ie. one hdf5 file per trigger).
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = 'AD_HDF5_SINGLE'  # spec name stored in res. doc

        self.stage_sigs.update([('file_template', '%s%s_%6.6d.h5'),
                                ('file_write_mode', 'Single'),
                                ])
        # 'Single' file_write_mode means one image : one file.
        # It does NOT mean that 'num_images' is ignored.

    def get_frames_per_point(self):
        return self.parent.cam.num_images.get()

    def stage(self):
        super().stage()
        # this over-rides the behavior is the base stage
        self._fn = self._fp

        resource_kwargs = {'template': self.file_template.get(),
                           'filename': self.file_name.get(),
                           'frame_per_point': self.get_frames_per_point()}
        self._generate_resource(resource_kwargs)


class FileStoreHDF5SingleIterativeWrite(FileStoreHDF5Single, FileStoreIterativeWrite):
    pass


class SpecsHDF5Plugin(HDF5Plugin, FileStoreHDF5SingleIterativeWrite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the filestore_spec name
        self.filestore_spec = 'SPECS_HDF5_SINGLE_DATAFRAME'

    # Add some parameters required to retrieve the data as a pandas dataframe
    key = '/entry/data/data'
    column_names = ('spectrum',)

    # write a new stage method that adds `column_names` and `key` to
    # resource_kwargs.
    def stage(self):
        super().stage()
        # this over-rides the behavior is the base stage
        self._fn = self._fp

        resource_kwargs = {'template': self.file_template.get(),
                           'filename': self.file_name.get(),
                           'key': self.key,
                           'column_names': self.column_names,
                           'frame_per_point': self.get_frames_per_point()}
        self._generate_resource(resource_kwargs)


class SpecsSingleTrigger(SingleTrigger):
    '''SIngleTrigger class for the specs analyzer

    Modifies the trigger class so that the name associated with the measured spectrum is spectrum, it also
    ensures that the hdf5 data is only generated if ``self.acquisition_mode == 'spectrum'``
    '''

    def trigger(self):
        if self._staged != Staged.yes:
            raise RunTimeError(f'The {self.name} detector is not ready to trigger, call ``{self.name}.stage()`` prior to'
                               'triggering')

        self._status = self._status_type(self)
        self.cam.acquire.put(1,wait=False)
        # Here we do away weith the `dispatch` method used in `SingleTrigger as that
        # gives the same field to multiple datafioles which DB can't handle
        if self.acquisition_mode == 'spectrum':
            self.hdf1.generate_datum('spectrum', ttime.time(), {})
        return self._status


class SPECSmode(Enum):
    spectrum = 'spectrum'
    single_count = 'single_count'



class SpecsDetector(SpecsSingleTrigger, DetectorBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs.update({self.cam.safe_state: 0})
   
        self.count.kind = Kind.hinted
 
    cam = ADComponent(SpecsDetectorCam, 'cam1:')
    hdf1 = ADComponent(SpecsHDF5Plugin,
                       name='hdf1',
                       suffix='HDF1:',
                       write_path_template='/GPFS/xf23id/xf23id2/data/specs/%Y/%m/%d/',
                       root='/GPFS/xf23id/xf23id2/')
    
    count = ADComponent(EpicsSignalRO, 'Stats5:Total_RBV', kind=Kind.hinted, name='count')

    acquisition_mode = None 

    def set_mode(self, mode):
        '''This method returns a plan that swaps between 'single_count' mode and 'spectrum' mode.

        This method sets a range of parameters in order to run the detector in either 'single_count'
        mode, where a single value is read at each trigger, and 'spectrum' mode, where a spectrum is
        read at each trigger.

        Parameters
        ----------
        mode : str or SPECSmode enum
            The mode to use for the data acquisition, the options are 'single_point' and 'spectrum'.
        '''

        if type(mode) == str:
            try:
                mode = SPECSmode(mode)
            except ValueError:
                raise ValueError(f'The value provided via `mode` in {self.name}.set_mode does not have'
                                 f' the correct value type (should be "single_count", "spectrum", '
                                 f'SPECSmode.single_count or SPECSmode.spectrum')
        elif type(mode) is not SPECSmode:
            raise TypeError(f'the mode supplied in {self.name}.set_mode is not of type `string` or'
                            f' type SPECSmode, set was not performed')

        if mode is SPECSmode.single_count:
            yield from mv(self.cam.acquire_mode, 3,
                          self.hdf1.enable, 0)
        elif mode == SPECSmode.spectrum:
            yield from mv(self.cam.acquire_mode, 0,
                          self.hdf1.enable, 1)
            self.hdf1.kind=Kind.normal
        else:
            raise ValueError(f'The value provided via `mode` in {self.name}.set_mode does not have'
                             f' the correct value type (should be "single_count", "spectrum", '
                             f'SPECSmode.single_count or SPECSmode.spectrum')
        self.acquisition_mode = mode

specs = SpecsDetector('XF:23ID2-ES{SPECS}', name = 'specs')
