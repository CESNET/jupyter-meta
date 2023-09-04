To start Jupyterhub, run

sudo ./rerun.sh

which will rebuild dockerimage, delete old jupyterhub pod and remove port forwarding, start jupyterhub pod and port forwarding between pod and host
Port forwarding is currently done via systemctl service, because simple 'nohup ... &' kept crashing within minutes or hours.
But for testing purposes you can comment 'systemctl start ...' and uncomment forwarding lines, where ports 443 and 8082 are bridged between the pod and host
If no major errors appear, jupyterhub should be running and available to users

dockerfile
==========
This file contains instructions in docker format to build the dockerimage. Note that it coppies files from this folder
to the pod when being created, like pbs.conf, pbs folder, kerberosPAM.py (for jupyterhub to properly flush kerberos tickets into /tmp), etc...

config.py
=========
Configuration of Jupyterhub, which is appended to jupyter_config.py during docker image building

rerun.py
========
Deletes old jupyterhub pod and port forwarding, builds docker image, starts kubernetes pod with jupyterhub and starts port-forwarding

Other files
===========
The rest of the files are necessary to enable proper functioning of the hub.

kerberosPAM.py - fixes kerberos ticket flushing into /tmp/krb5cc_{uid} when loggin into jupyterhub  

pbs/ - folder with necessary deb packages to allow using PBS and submitting jobs, I did not find an easy way 
       to just run apt install pbs-client or similar, so in dockerfile .deb packages from pbs/ are installed instead

pod.yml - pod description for kubernetes
krb5.conf - kerberos configuration for metacentrum
pbs.conf - PBS configuration for metacentrum
qstat-merge.sh - usage ./qstat-merge.sh {job_id}, outputs job info even if the job was moved

