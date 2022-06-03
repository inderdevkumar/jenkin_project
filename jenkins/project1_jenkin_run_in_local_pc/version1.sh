#!/usr/bin/env bash

echo ======== hostname ======================
echo You are in $HOSTNAME machine
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

