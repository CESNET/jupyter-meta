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

c.JupyterHub.template_vars = {'announcement_login': "Please see wiki at https://wiki.metacentrum.cz/wiki/Jupyter_for_MetaCentrum_users"}
#c.JupyterHub.template_vars = {'announcement_spawn': "In near future users will be able to choose submitting options separately"}

c.JupyterHub.allow_named_servers=True

c.JupyterHub.spawner_class = 'wrapspawner.ProfilesSpawner'
#c.JupyterHub.spawner_class = 'batchspawner.PBSSpawner'
c.Spawner.http_timeout = 3600
c.Spawner.start_timeout = 3600

#c.HubAuth.api_url = 'http://jupyter.cloud.metacentrum.cz:8082/hub/api'

c.JupyterHub.debug_db = False
c.Spawner.debug = False

c.PBSSpawner.state_exechost_re = r'exec_host2 = ([\w\._-]+):'

c.PBSSpawner.batch_query_cmd = './qstat-merge.sh {job_id}'

#&& rm -rf .jupyterhub_api_token_{job_id} \

c.PBSSpawner.batch_submit_cmd = 'echo {username} > /dev/null \
&& export JUPYTERHUB_API_TOKEN_FILE=.jupyterhub_api_token_$(date +%s | md5sum | head -c 32) \
&& echo $JUPYTERHUB_API_TOKEN > $JUPYTERHUB_API_TOKEN_FILE \
&& sudo -E -u {username} KRB5CCNAME=/tmp/krb5cc_$(id -u {username}) \
scp -o StrictHostKeyChecking=no $JUPYTERHUB_API_TOKEN_FILE \
{username}@storage-brno6.metacentrum.cz:/home/fsbrno2/home/{username} \
&& rm -rf JUPYTERHUB_API_TOKEN_FILE \
&& sudo -E -u {username} qsub -v JUPYTERHUB_API_TOKEN_FILE,PATH,LANG,LC_ALL,JUPYTERHUB_CLIENT_ID,JUPYTERHUB_HOST,JUPYTERHUB_OAUTH_CALLBACK_URL,JUPYTERHUB_USER,JUPYTERHUB_SERVER_NAME,JUPYTERHUB_API_URL,JUPYTERHUB_ACTIVITY_URL,JUPYTERHUB_BASE_URL,JUPYTERHUB_SERVICE_PREFIX'

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
#PBS -l select=1:ncpus={nprocs}:mem={memory}
#PBS -l walltime={runtime}
#PBS -N jupyter-ntb-singleuser
#PBS -o skirit.ics.muni.cz:/storage/brno2/home/{username}
#PBS -e skirit.ics.muni.cz:/storage/brno2/home/{username}

export MODULEPATH+=:/software/jupyterhub-1.2/modules:/software/jupyterhub-1.1/modules
module load jupyterhub-1.1 clang-10.0.1 cling-0.7 #note: python-3.6.2-gcc module is also loaded

# root folder where your notebook server initiates
export NOTEBOOK_DIR="/storage/brno2/home/$PBS_O_LOGNAME"

# due to security reasons the API token is transferred via file instead of via #PBS -v variable
export JUPYTERHUB_API_TOKEN="$(cat $NOTEBOOK_DIR/$JUPYTERHUB_API_TOKEN_FILE)"
export JPY_API_TOKEN=$JUPYTERHUB_API_TOKEN

rm -rf $NOTEBOOK_DIR/$JUPYTERHUB_API_TOKEN_FILE

# adjust your own environment
export JUPYTER_BASHRC=/storage/brno2/home/$PBS_O_LOGNAME/.jupyter_bashrc

if [ -s "$JUPYTER_BASHRC" ]
then
  source $JUPYTER_BASHRC
fi

$SINGULARITY_JUPYTER_PREFIX {cmd} --notebook-dir=$NOTEBOOK_DIR

'''

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

