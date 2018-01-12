from databroker import Broker

# move to /etc/databroker/csx2.yml
config = {
    'description' : "CSX2 raw data",
    'metadatastore':
        {'module' : 'databroker.headersource.mongo',
         'class' : 'MDS',
         'config' : {
            'host':'xf23id-ca.cs.nsls2.local',
            'database': 'datastore-23id2', 
	        'port': 27017, 
            'timezone': 'US/Eastern',
            'auth' : False}
        },
    'assets' : {
        'module' : 'databroker.assets.mongo',
        'class' : 'Registry',
        'config' : {
            'host':'xf23id-ca.cs.nsls2.local',
			'port': 27017,
            'database':'filestore'
        }
    },
}

db = Broker.from_config(config)

import nslsii
nslsii.configure_base(get_ipython().user_ns, db)


# Make ophyd listen to pyepics.
from ophyd import setup_ophyd
setup_ophyd()


# TODO not need this
from epics import caget, caput
from amostra.client.commands import SampleReference, ContainerReference
# from metadataclient.mds import MDS

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
# RE.subscribe_lossless('all', metadatastore.commands.insert)


# Optional: set any metadata that rarely changes.
# RE.md['beamline_id'] = 'YOUR_BEAMLINE_HERE'

# convenience imports

def ensure_proposal_id(md):
   if 'proposal_id' not in md:
       raise ValueError("Please run user_checkin() first")



from time import sleep
import numpy as np

sample_reference = SampleReference(host='xf23id-ca.cs.nsls2.local', port=7772)
container_reference = ContainerReference(host='xf23id-ca.cs.nsls2.local', port=7772)

from bluesky.callbacks.mpl_plotting import plot_peak_stats


# Set up default metadata.
RE.md['group'] = ''
RE.md['config'] = {}
RE.md['beamline_id'] = 'CSX-2'


# Add a callback that prints scan IDs at the start of each scan.
def print_scan_ids(name, start_doc):
    print("Transient Scan ID: {0}".format(start_doc['scan_id']))
    print("Persistent Unique Scan ID: '{0}'".format(start_doc['uid']))

RE.subscribe('start', print_scan_ids)

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
nslsii.configure_olog(get_ipython().user_ns, callback=cb)

#this is no longer supported by bluesky
class gs:
    DETS=[]
