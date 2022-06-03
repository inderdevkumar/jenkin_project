#!/usr/bin/env bash

echo ======== hostname ======================
hostname
echo -e "\n\n=========== Check Memory Size ==================="
df -h | egrep 'Filesystem|/dev/nvme0n1p2'
echo -e "\n\n============uptime ============================"
uptime
echo -e "\n\n=========== ip of my machine ===================="
ip a s eno1 | egrep -o 'inet [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut -d' ' -f2

echo List of worker are: $list_of_workers

for WORKER in $(echo "$list_of_workers" | tr "," "\n");
do 
echo -e "\n\n======== Taking SSH to $WORKER REmote MACHINE ============================================================"

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@$WORKER.$network_used << EOF
 echo ======== hostname ======================
hostname
echo -e "\n\n=========== Check Memory Size ==================="
df -h | egrep 'Filesystem|/dev/nvme0n1p2'
echo -e "\n\n============uptime ============================"
uptime
echo -e "\n\n=========== ip of my machine ===================="
ip a s eno1 | egrep -o 'inet [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut -d' ' -f2
echo -e "\n\n======== ========================= ============================ ============================ ============="
EOF
done

