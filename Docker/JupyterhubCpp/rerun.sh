#!/bin/bash

image='jupyterhubdockercppkrb'
containerPort='8010'
servicePort='8010'

RED='\033[0;31m'
NC='\033[0m' # No Color
#printf "I ${RED}love${NC} Stack Overflow\n"

CYAN='\033[0;36m'
LCYAN='\033[1;36m'

echo -e "${LCYAN}Deleting old container $image...${NC}"
kubectl delete -n default  deployment $image
echo -e "${LCYAN}$? Done${NC}"

OldPortForwardPID="$(ps aux | grep port-forward | grep "$image" | awk '{print $2}')"

echo Killing old port forwarding process...
kill $OldPortForwardPID
echo -e "${LCYAN}$? Done${NC}"

echo -e "${LCYAN}Building docker image $image...${NC}"
docker image build --network host -t $image .
echo -e "${LCYAN}$? Done${NC}"

echo -e "${LCYAN}Starting container $image on port $containerPort...${NC}"
kubectl run $image --image="$image" --port=$containerPort  --image-pull-policy='Never'

sleep 5
podId="$(kubectl get pods | grep $image | grep Running | cut  -d' ' -f1)"

echo -e "${LCYAN}Exposing pod $podId${NC}"
kubectl expose pod $podId --type=NodePort
echo -e "${LCYAN}$? Done${NC}"

sleep 5
echo -e "${LCYAN}Port-forwarding address 0.0.0.0 pod $podId hostPort:containerPort $servicePort:$containerPort${NC}"
kubectl port-forward --address 0.0.0.0 $podId $servicePort:$containerPort &
echo -e "${LCYAN}$? Done${NC}"

echo -e -n "\e[0m"
