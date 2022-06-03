#!/usr/bin/env bash

echo ======== hostname ======================
hostname
echo -e "\n\n ========= CHeck Ubunto Version ========================"
lsb_release -a
echo -e "\n\n=========== Check Memory Size ==================="
df -h | egrep 'Filesystem|/dev/nvme0n1p2'
echo -e "\n\n============uptime ============================"
uptime
echo -e "\n\n=========== ip of my machine ===================="
ip a s eno1 | egrep -o 'inet [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut -d' ' -f2
echo -e "\n\n =========== who am I ================"
whoami
echo -e "\n\n======== Current date time ===================="
date

for IP in $(cat /home/gui_pd_access/inder/jenkins/project2_ssh_remote_machine/host_name.txt)
do 
echo -e "\n\n======== Taking SSH to $IP REmote MACHINE ===================="

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@$IP << EOF
 echo ======== hostname ======================
hostname
echo -e "\n\n ========= CHeck Ubunto Version ========================"
lsb_release -a
echo -e "\n\n=========== Check Memory Size ==================="
df -h | egrep 'Filesystem|/dev/nvme0n1p2'
echo -e "\n\n============uptime ============================"
uptime
echo -e "\n\n=========== ip of my machine ===================="
ip a s eno1 | egrep -o 'inet [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut -d' ' -f2
echo -e "\n\n =========== who am I ================"
whoami
echo -e "\n\n======== Current date time ===================="
date

EOF
done
