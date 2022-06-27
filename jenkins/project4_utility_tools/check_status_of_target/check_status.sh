#!/usr/bin/env bash

echo ========================
echo Test if Target is fine
echo ========================

ssh_signature_file=/home/gui_pd_access/inder/test_files/id_ed25519_mgu22

echo Please enter the target you want to flash. padi/idc/mgu?
read target_connected

echo Turning off power supply
export PYTHONPATH=/home/gui_pd_access/inder/test_files/psu/
cd /home/gui_pd_access/inder/test_files/psu/
sudo /home/gui_pd_access/inder/test_files/psu/psu.sh False


if [ "${target_connected^^}" == "IDC" ]; then
    target_ip=160.48.199.99
    echo Turning on Power supply
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True
    echo Sleep for 30s to make ECU Alive back
    sleep 30
    echo Read ECU mode
    python3 /home/gui_pd_access/inder/test_files/hsfz-send/read_ecu_mode.py --ip-addr $target_ip --diag-addr 0x63
    echo Read ECU UID 
    python3 /home/gui_pd_access/inder/test_files/hsfz-send/read_ecu_uid.py --ip-addr $target_ip --diag-addr 0x63
    echo Keygen -f 160.48.199.99
    ssh-keygen -f "/root/.ssh/known_hosts" -R "160.48.199.99"
    echo IOC version is
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "ls /usr/lib/libffp_ioc.so.* | head -n 1 | xargs -I{} ffptool {} sw-version 0 | grep 'SW version'"
    echo Checking application mode Status
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "systemctl is-active application.target"
    echo Checking Flashing mode Status
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "systemctl is-active flashing.target"
    echo Rebooting Target in Application mode
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "nsm_control --r 7" > /dev/null
    echo Sleep again for 30s
    sleep 30
    echo Checking application mode status aftre reboot
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "systemctl is-active application.target"
    echo Serial Number of Target
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "grim xdata read CRIN -d bin"
    echo
    echo MAC Address of Target in Small and capital
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "grim status | grep "SOC-MAC" | tr " " :"
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "grim status | grep "SOC-MAC" | tr " " : | tr [:lower:] [:upper:]"

elif [ "${target_connected^^}" == "MGU" ]; then
    target_ip=160.48.199.99
    echo Turning on Power supply
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True
    echo Sleep for 30s to make ECU Alive back
    sleep 30
    echo Read ECU mode
    python3 /home/gui_pd_access/inder/test_files/hsfz-send/read_ecu_mode.py --ip-addr $target_ip --diag-addr 0x63
    echo Read ECU UID 
    python3 /home/gui_pd_access/inder/test_files/hsfz-send/read_ecu_uid.py --ip-addr $target_ip --diag-addr 0x63
    echo Keygen -f 160.48.199.99
    ssh-keygen -f "/root/.ssh/known_hosts" -R "160.48.199.99"
    echo IOC version is
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "ls /usr/lib/libffp_ioc.so.* | head -n 1 | xargs -I{} ffptool {} sw-version 0 | grep 'SW version'"
    echo Checking application mode Status
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "systemctl is-active application.target"
    echo Checking Flashing mode Status
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "systemctl is-active flashing.target"
    echo Rebooting Target in Application mode
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "nsm_control --r 7" > /dev/null
    echo Sleep again for 30s
    sleep 30
    echo Checking application mode status aftre reboot
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "systemctl is-active application.target"
    echo Serial Number of Target
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "grim xdata read CRIN -d bin"
    echo
    echo MAC Address of Target in Small and capital
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "grim status | grep "SOC-MAC" | tr " " :"
    ssh -o StrictHostKeyChecking=no -i $ssh_signature_file root@$target_ip "grim status | grep "SOC-MAC" | tr " " : | tr [:lower:] [:upper:]" 

elif [ "${target_connected^^}" == "PADI" ]; then
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True 

else
    echo Please eneter idc/mgu/padi

fi
