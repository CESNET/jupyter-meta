#!/bin/bash

image='jupyterhubdockercppkrb-pbs'
containerPort='443'
servicePort='443'

containerAPIPort='8082'
serviceAPIPort='8082'

outputFile='' #>/dev/null

RED='\033[0;31m'
NC='\033[0m' # No Color
#printf "I ${RED}love${NC} Stack Overflow\n"

CYAN='\033[0;36m'
LCYAN='\033[1;36m'
GREEN='\033[0;32m'

echo -e "${LCYAN}Building docker image $image...${NC}"
docker image build --network host -t $image .
echo -e "${LCYAN}Done${NC} \$?=$?"

if [ $? -ne 0 ]
then
  exit -1
fi

echo -e "${LCYAN}Deleting old container $image...${NC}"
kubectl delete -n default  deployment $image
kubectl delete pods $image --grace-period=0 --force
echo -e "${LCYAN}Done${NC} \$?=$?"

OldPortForwardPID="$(ps aux | grep port-forward | grep "$image" | awk '{print $2}')"

echo Killing old port forwarding processes with PID $OldPortForwardPID...
#kill $OldPortForwardPID
systemctl stop jupyter-port-forwarding-pbs
echo -e "${LCYAN}Done${NC} \$?=$?"

echo -e "${LCYAN}Starting container $image on port $containerPort...${NC}"
kubectl create -f pod.yml
#kubectl run $image \
#--image="$image" \
#--port=$servicePort \
#--image-pull-policy='Never' \
#--env="HOSTNAME=jupyter.cloud.metacentrum.cz"
#--overrides='{"spec":{"containers[]":{"volumeMounts":{"mountPath":"/storage",}}}}'
#--overrides='{"spec":{"containers[]":{"securityContext":{"capabilities":{"add":"CAP_SYS_ADMIN"}}}}}'
#--overrides='{"spec": {"hostname":"jupyter.cloud.metacentrum.cz"}}'

#docker run -d -p 8000:8000 $image --network host start

#sleep 10
while [ -z "$(kubectl get pods | grep $image | grep "Running")" ]
do
  echo -n "..." && sleep 1
done
echo "..."

podId="$(kubectl get pods | grep $image | grep "Running" | cut  -d' ' -f1)"
echo -e "${LCYAN}Exposing pod $podId${NC}"
kubectl expose pod $podId --type=LoadBalancer
echo -e "${LCYAN}Done${NC} \$?=$?"

#sleep 5
echo -e "${LCYAN}Port-forwarding address 0.0.0.0 pod $podId hostPort:containerPort $servicePort:$containerPort $(($servicePort+1)):$(($containerPort+1)) $serviceAPIPort:$containerAPIPort  ${NC}"
#nohup kubectl port-forward --address 0.0.0.0 $podId $servicePort:$containerPort $outputFile &
#nohup kubectl port-forward --address 0.0.0.0 $podId $(($servicePort+1)):$(($containerPort+1)) $outputFile &
#nohup kubectl port-forward --address 0.0.0.0 $podId $serviceAPIPort:$containerAPIPort $outputFile &
systemctl start jupyter-port-forwarding-pbs
systemctl start jupyter-port-forwarding-cloud
echo -e "${LCYAN}Done${NC} \$?=$?"
echo -e "${GREEN}RERUN FINISHED${NC}"

echo -e -n "\e[0m"
