#!/usr/bin/env bash

echo ======== HOstname from where you are running Jenkin  ====================== ====================== ======================
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

echo -e "\n\n======== Taking SSH to ONe REmote MACHINE ==================== ====================== ======================"

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

ping 160.48.199.99 -c 10
echo -e "\n\n======== Chaning correct mode to ssh key  ===================="

chmod 400 /home/tf_admin/test_files/id_ed25519_mgu22
echo -e "\n\n======== Taking ssh to target  ===================="

ssh -o StrictHostKeyChecking=no -i /home/tf_admin/test_files/id_ed25519_mgu22 root@160.48.199.99

 echo ======== grim status  ======================
grim status
echo -e "\n\n ========= Check for csrs ========================"
ls /var/sys/sysfunc
echo -e "\n\n=========== Check for IOC version  ==================="
ls /usr/lib/libffp_ioc.so.* | head -n 1 | xargs -I{} ffptool {} sw-version 0
echo -e "\n\n============ CHeck for HW Variant ============================"
cat /run/etc/variant.env
echo -e "\n\n=========== Check for SW Version ===================="
cat /etc/os-release
echo -e "\n\n =========== Check for Serial NUmber ================"
grim xdata read CRIN -d bin
echo -e "\n\n======== Check for Numeric Serial NUmber ===================="
grim xdata read ECU_SN -d bin
echo -e "\n\n======= socnet to confirm mac address  ===================="
ifconfig | grep "socnet0"
echo -e "\n\n======= exiting from target with nsm_control --r 7  ==================== ====================== ======================"
nsm_control --r 7 | grep "closing connection to"


EOF

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@tf-worker-mgu-315.bmw-carit.intra << EOF
 echo ======== Back to Worker ====================== ====================== ====================== ======================
hostname
echo -e "\n\n======= listing files  ===================="
ls
echo -e "\n\n======= Back to Worker  ===================="
sudo -S mkdir test_files/test_dir
BHUasampleTest14
echo -e "\n\n======= Deleting unwanted files  ===================="
sudo rm -rf test_files
BHUasampleTest14
echo -e "\n\n======= Rebooting worker  ===================="
sudo reboot
EOF

echo -e "\n\n======= worker is rebooted waiting for 15s to re login=================="
sleep 15

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@tf-worker-mgu-315.bmw-carit.intra << EOF
echo -e "\n\n======= Back to worker   ===================="
hostname
echo -e "\n\n======= to confirm reboot is done  uptime  ===================="
uptime
echo -e "\n\n======= to check if test_files folder is removed or not  ===================="
ls
echo   ========================================================================================================================
EOF
