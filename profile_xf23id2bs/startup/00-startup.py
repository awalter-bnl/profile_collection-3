# Make ophyd listen to pyepics.
from ophyd import setup_ophyd
setup_ophyd()

import warnings
with warnings.catch_warnings():
    from databroker import Broker
    import databroker.databroker
    from databroker.core import register_builtin_handlers

# TODO not need this
from epics import caget, caput
from filestore.fs import FileStore
from metadatastore.mds import MDS
from amostra.client.commands import SampleReference, ContainerReference
# from metadataclient.mds import MDS

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
from bluesky.global_state import gs
# gs.RE.subscribe_lossless('all', metadatastore.commands.insert)

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()

# Optional: set any metadata that rarely changes.
# RE.md['beamline_id'] = 'YOUR_BEAMLINE_HERE'

# convenience imports
from ophyd.commands import *
from bluesky.callbacks import *
from bluesky.spec_api import *
from bluesky.global_state import gs, abort, stop, resume
# from databroker import (DataBroker as db, get_events, get_images,
#                        get_table, get_fields, restream, process)

def ensure_proposal_id(md):
   if 'proposal_id' not in md:
       raise ValueError("Please run user_checkin() first")



from time import sleep
import numpy as np

RE = gs.RE  # convenience alias
mds = MDS({'host':'xf23id-ca.cs.nsls2.local','database': 'datastore-23id2', 
	   'port': 27017, 'timezone': 'US/Eastern'}, auth=False)
sample_reference = SampleReference(host='xf23id-ca.cs.nsls2.local', port=7772)
container_reference = ContainerReference(host='xf23id-ca.cs.nsls2.local', port=7772)

# mds = MDS({'host':http://xf23-ca.cs.nsls2.local, 'port': 7770})
db = Broker(mds, FileStore({'host':'xf23id-ca.cs.nsls2.local',
			    'port': 27017, 'database':'filestore'}))
#RE.md_validator = ensure_proposal_id
register_builtin_handlers(db.fs)
RE.subscribe('all', mds.insert)


from bluesky.callbacks.scientific import plot_peak_stats

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

from functools import partial
from pyOlog import SimpleOlogClient
from bluesky.callbacks.olog import logbook_cb_factory

# Set up the logbook. This configures bluesky's summaries of
# data acquisition (scan type, ID, etc.).

LOGBOOKS = ['Data Acquisition']  # list of logbook names to publish to
simple_olog_client = SimpleOlogClient()
generic_logbook_func = simple_olog_client.log
configured_logbook_func = partial(generic_logbook_func, logbooks=LOGBOOKS)
desc_template = """
{{- start.plan_name }} ['{{ start.uid[:6] }}'] (scan num: {{ start.scan_id }})
Scan Plan
---------
{{ start.plan_type }}
{%- for k, v in start.plan_args | dictsort %}
    {{ k }}: {{ v }}
{%-  endfor %}
{% if 'signature' in start -%}
Call:
    {{ start.signature }}
{% endif %}
Metadata
--------
{% for k, v in start.items() -%}
{%- if k not in ['plan_type', 'plan_args'] -%}{{ k }} : {{ v }}
{% endif -%}
{%- endfor -%}"""

desc_dispatch = {'edge_ascan': """
{{- start.name }} [{{ start.plan_name }} '{{ start.uid[:6] }}'] (scan num: {{ start.scan_id }})"""}

cb = logbook_cb_factory(configured_logbook_func, desc_template=desc_template,
                        desc_dispatch=desc_dispatch)
RE.subscribe('start', cb)

logbook = simple_olog_client
