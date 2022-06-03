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
echo -e "\n\n======== Copying  test_files folder from local to Remote ===================="
sshpass -p "BHUasampleTest14" scp -r  /home/gui_pd_access/inder/test_files tf_admin@tf-worker-mgu-315.bmw-carit.intra:/home/tf_admin/


echo -e "\n\n======== Taking SSH to ONe REmote MACHINE ===================="

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@tf-worker-mgu-315.bmw-carit.intra << EOF
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
echo -e "\n\n======== Taking SSH to Target connected to NUC ================== ====================== ======================="
echo -e "\n\n======== Running VCAR Script ===================="

python /home/tf_admin/test_files/hu-keepalive.py > /home/tf_admin/test_files/vcar_log.txt 2>&1 &
echo -e "\n\n======== Toggling POwer of 12V ===================="

/opt/utils/psu/manage_zd.py -s on
#echo -e "\n\n======== Sleep for 10s ===================="
#sleep 10
echo -e "\n\n======== ping to target ===================="
ping 160.48.199.99 -c 10 > /home/tf_admin/test_files/ping_to_target.txt
cat /home/tf_admin/test_files/ping_to_target.txt

echo -e "\n\n======== soc logs  ==================="
picocom -b 115200 /dev/ttySOCHU > /home/tf_admin/test_files/soc_logs.txt 2>&1 &
cat /home/tf_admin/test_files/soc_logs.txt

echo -e "\n\n======== ioc logs  ==================="
picocom -b 115200 /dev/ttyIOC > /home/tf_admin/test_files/ioc_logs.txt 2>&1 &
cat /home/tf_admin/test_files/ioc_logs.txt

echo -e "\n\n======= Back to Worker  ===================="
sudo -S mkdir test_files/test_dir
BHUasampleTest14
echo -e "\n\n======= Rebooting worker  ===================="
sudo reboot

EOF
