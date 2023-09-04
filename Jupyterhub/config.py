import os
import socket
import batchspawner    # Even though not used, needed to register batchspawner interface

c = get_config()

c.PAMAuthenticator.admin_users = {'nikl','ruda'}

c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 443
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8082
c.JupyterHub.hub_connect_ip = 'jupyter.cloud.metacentrum.cz'

#c.KubeSpawner.image = 'jupyterhub/singleuser:1.0'
c.KubeSpawner.storage_pvc_ensure = False

c.JupyterHub.template_vars = {'announcement_login': "Jupyterhub webserver for spawning Jupyter notebooks onto PBS nodes (last updated on Aug 24, 2023). For general usage information and potential problem solutions please see wiki at https://wiki.metacentrum.cz/wiki/Jupyter_for_MetaCentrum_users"}
#c.JupyterHub.template_vars = {'announcement_spawn': "In near future users will be able to choose submitting options separately"}

c.JupyterHub.allow_named_servers=True

c.JupyterHub.spawner_class = 'wrapspawner.ProfilesSpawner'
#c.JupyterHub.spawner_class = 'batchspawner.PBSSpawner'
c.Spawner.http_timeout = 3600
c.Spawner.start_timeout = 36000

#c.HubAuth.api_url = 'http://jupyter.cloud.metacentrum.cz:8082/hub/api'

c.JupyterHub.debug_db = False
c.Spawner.debug = False

c.PBSSpawner.state_exechost_re = r'exec_host2 = ([\w\._-]+):'

c.PBSSpawner.batch_query_cmd = './qstat-merge.sh {job_id}'

#&& rm -rf .jupyterhub_api_token_{job_id} \
#&& rm -rf JUPYTERHUB_API_TOKEN_FILE \

c.PBSSpawner.batch_submit_cmd = 'echo {username} > /dev/null \
&& export JUPYTERHUB_API_TOKEN_FILE=.jupyterhub_api_token_$(date +%s | md5sum | head -c 32) \
&& echo $JUPYTERHUB_API_TOKEN > $JUPYTERHUB_API_TOKEN_FILE \
&& sudo -E -u {username} KRB5CCNAME=/tmp/krb5cc_$(id -u {username}) \
scp -o StrictHostKeyChecking=no $JUPYTERHUB_API_TOKEN_FILE \
{username}@storage-brno12-cerit.metacentrum.cz:/nfs4/home/{username} \
&& sudo -E -u {username} qsub -v JUPYTERHUB_API_TOKEN_FILE,PATH,JUPYTERHUB_CLIENT_ID,JUPYTERHUB_API_TOKEN,JUPYTERHUB_HOST,JUPYTERHUB_OAUTH_CALLBACK_URL,JUPYTERHUB_USER,JUPYTERHUB_SERVER_NAME,JUPYTERHUB_API_URL,JUPYTERHUB_ACTIVITY_URL,JUPYTERHUB_BASE_URL,JUPYTERHUB_SERVICE_PREFIX \
-o {homedir} -e {homedir}'

#------------------------------------------------------------------------------
# BatchSpawnerBase configuration
#    These are simply setting parameters used in the job script template below
#------------------------------------------------------------------------------
#c.BatchSpawnerBase.req_nprocs = '1'
#c.BatchSpawnerBase.req_queue = 'gpu'
c.BatchSpawnerBase.req_host = 'meta-pbs.metacentrum.cz'
#c.BatchSpawnerBase.req_runtime = '00:10:00'
#c.BatchSpawnerBase.req_memory = '400mb'
c.JupyterHub.extra_handlers = [(r"/api/batchspawner", 'batchspawner.api.BatchSpawnerAPIHandler')]

#------------------------------------------------------------------------------
# PBS spawner submit script configuration
#------------------------------------------------------------------------------
c.PBSSpawner.batch_script = '''#!/bin/sh
#PBS -q {queue}@{host}
#PBS -l select=1:ncpus={nprocs}:ngpus={partition}:mem={memory}
#PBS -l walltime={runtime}
#PBS -N jupyter-ntb-singleuser

export MODULEPATH+=:/software/jupyterhub-1.2/modules:/software/jupyterhub-1.1/modules
module load jupyterhub-1.1 clang-10.0.1 cling-0.7 #note: python-3.6.2-gcc module is also loaded

# root folder where your notebook server initiates
#export NOTEBOOK_DIR="/storage/brno2/home/$PBS_O_LOGNAME"
export NOTEBOOK_DIR={ntbdir}

# due to security reasons the API token is transferred via file instead of via #PBS -v variable
export JPY_TOKEN_PATH="/storage/brno12-cerit/home/$PBS_O_LOGNAME/$JUPYTERHUB_API_TOKEN_FILE"
#export JUPYTERHUB_API_TOKEN="$(cat $JPY_TOKEN_PATH)"
export JPY_API_TOKEN=$JUPYTERHUB_API_TOKEN

rm -rf $JPY_TOKEN_PATH

# adjust your own environment
export JUPYTER_BASHRC={options}
#/storage/brno2/home/$PBS_O_LOGNAME/.jupyter_bashrc

if [ -s "$JUPYTER_BASHRC" ]
then
  source $JUPYTER_BASHRC
fi

echo "JUPYTERHUB_API_TOKEN"  $JUPYTERHUB_API_TOKEN

{prologue}
$SINGULARITY_JUPYTER_PREFIX {cmd} --notebook-dir=$NOTEBOOK_DIR
{epilogue}

'''

from optionsspawner.forms import (
    TextInputField,
    SelectField,
)

c.JupyterHub.spawner_class = 'optionsspawner.OptionsFormSpawner'
c.OptionsFormSpawner.child_class = 'batchspawner.PBSSpawner'
c.OptionsFormSpawner.child_config = {}

options_spawner = SelectField('c.OptionsFormSpawner.child_class',
    label='Spawn notebook server on a PBS node (recommended) or locally on a cloud',
    attr_required=True,
    choices=[(1.0, 'PBS'), (2.0, 'cloud (ignore the PBS parameters bellow and press Start')],
    default=1.0
)

options_queue = SelectField('req_queue',
    label='PBS Queue (aka qsub -q X),     @@@### for higher RAM requirements use special queues     @@@###',
    attr_required=True,
    choices=[('gpu_jupyter', 'gpu_jupyter (nvidia A40)'), ('gpu_jupyter', 'default'),  ('gpu', 'gpu (random nvidia gpu)'), ('large_mem', 'large RAM 500+ GB')],
    default='gpu_jupyter'

)

options_nprocs = TextInputField('req_nprocs',
    label="PBS Number of Processor Cores (aka qsub -l nprocs=X)",
    attr_value='1',
    attr_required=True
)

options_ngpus = TextInputField('req_partition',
    label="PBS Number of GPUs (aka qsub -l ngpus=X, increase only when a gpu queue is selected)",
    attr_value='0',
    attr_required=True
)

options_memory = TextInputField('req_memory',
    label="PBS Memory (aka qsub -l mem=X)",
    attr_value='4gb',
    attr_required=True
)

options_runtime = TextInputField('req_runtime',
    label="PBS Walltime (aka qsub -l walltime=X), use 10 hours max, after that the MetaCentrum kerberos login ticket expires",
    attr_value='10:00:00',
    attr_required=True
)

options_bashrc = TextInputField('req_options',
    label="[Optional] Path and name of your .jupyter_bashrc file (see wiki to properly prepare your jupyter notebooks' environment)",
    attr_value='/storage/brno2/home/$PBS_O_LOGNAME/.jupyter_bashrc',
    attr_required=True
)

options_homedir = TextInputField('req_homedir',
    label="Directory where PBS saves job's stdout and stderr files (aka qsub -o X -e X)",
    attr_value='skirit.ics.muni.cz:/tmp',
    attr_required=True
)

options_ntbdir = TextInputField('req_ntbdir',
    label="Directory where Notebook creates and accesses .ipynb source files (aka ./notebook --notebook-dir=X)",
    attr_value='/storage/brno2/home/$PBS_O_LOGNAME',
    attr_required=True
)

options_prologue = TextInputField('req_prologue',
    label="[Optional] Commands executed just before the notebook server starts (equivalent to using .jupyter_bashrc)",
    attr_value='',
    attr_required=False
)

options_epilogue = TextInputField('req_epilogue',
    label="[Optional] Commands executed just after the notebook server ends unexpectedly",
    attr_value='',
    attr_required=False
)

c.OptionsFormSpawner.form_fields = [
    options_spawner,
    options_queue,
    options_nprocs,
    options_ngpus,
    options_memory,
    options_runtime,
    options_bashrc,
    options_homedir,
    options_ntbdir,
    options_prologue,
    options_epilogue
]


c.ProfilesSpawner.profiles = [
   ('MetaCentrum PBS (CPU) - 1 core, 1 GB RAM, 1 hour', 'jup1c0g1m1h', 'batchspawner.PBSSpawner',
      dict(req_nprocs='1', req_queue='default', req_runtime='1:00:00', req_memory='1gb')),
   ('MetaCentrum PBS (CPU) - 4 cores, 4 GB RAM, 8 hours', 'jup4c0g4m8h', 'batchspawner.PBSSpawner',
      dict(req_nprocs='4', req_queue='default', req_runtime='8:00:00', req_memory='4gb')),
   ('MetaCentrum PBS (CPU) - 8 cores, 16 GB RAM, 8 hours', 'jup8c0g16m8h', 'batchspawner.PBSSpawner',
      dict(req_nprocs='8', req_queue='default', req_runtime='8:00:00', req_memory='16gb')),
   ('MetaCentrum PBS (CPU) - 16 cores, 128 GB RAM, 8 hours', 'jup16c0g128m8h', 'batchspawner.PBSSpawner',
      dict(req_nprocs='16', req_queue='default', req_runtime='8:00:00', req_memory='128gb')),
   ('MetaCentrum PBS (GPU T4) - 1 core, 1 GPU, 1 GB RAM, 1 hour', 'jup1c1g1m1h', 'batchspawner.PBSSpawner',
      dict(req_nprocs='1:ngpus=1', req_queue='gpu_jupyter', req_runtime='1:00:00', req_memory='1gb')),
   ('MetaCentrum PBS (GPU T4) - 1 core, 1 GPU, 8 GB RAM, 8 hours', 'jup1c1g8m8h', 'batchspawner.PBSSpawner',
      dict(req_nprocs='1:ngpus=1', req_queue='gpu_jupyter', req_runtime='8:00:00', req_memory='8gb')),
   ('MetaCentrum PBS (GPU T4) - 1 core, 2 GPUs, 16 GB RAM, 8 hours', 'jup1c2g16m8h', 'batchspawner.PBSSpawner',
      dict(req_nprocs='1:ngpus=2', req_queue='gpu_jupyter', req_runtime='8:00:00', req_memory='16gb')),
   ('OpenStack Cloud (CPU)', 'cloud', 'jupyterhub.spawner.LocalProcessSpawner', {'ip':'0.0.0.0'} )
   ]

