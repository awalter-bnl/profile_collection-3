import logging
from ophyd.commands import *

from databroker import DataBroker as db, get_events, get_images, get_table, process

import bluesky.qt_kicker  # make matplotlib qt backend play nice with bluesky asyncio

import asyncio
from functools import partial
from functools import partial
from bluesky.standard_config import *
from bluesky.global_state import abort, stop, resume, all_is_well, panic
from bluesky.plans import *
from bluesky.callbacks import *
from bluesky.broker_callbacks import *
from bluesky.scientific_callbacks import plot_peak_stats
from bluesky.hardware_checklist import *
from bluesky import qt_kicker   # provides the libraries for live plotting
qt_kicker.install_qt_kicker()    # installs the live plotting libraries

# Set up default metadata.
gs.RE.md['group'] = ''
gs.RE.md['config'] = {}
gs.RE.md['beamline_id'] = 'CSX-2'


# alias
RE = gs.RE


# Add a callback that prints scan IDs at the start of each scan.
def print_scan_ids(name, start_doc):
    print("Transient Scan ID: {0}".format(start_doc['scan_id']))
    print("Persistent Unique Scan ID: '{0}'".format(start_doc['uid']))

gs.RE.subscribe('start', print_scan_ids)
