#!/usr/bin/env bash

echo ========================
echo Modemamanger should be stopped
echo SW4 switch should be in right side ie in qdl mode manually
echo Build is already downloaded and saved locally
echo ========================

echo Checking status for  Modemamanger
sudo service ModemManager status | grep "Active"

echo It should be disabled. So any way I am stoping It
sudo systemctl stop ModemManager
echo Checking again the status for  Modemamanger
sudo service ModemManager status | grep "Active"


echo PLease make sure above things are meeting before flashing
echo Please enter the target you want to flash. padi/idc/mgu?
read target_connected

export PYTHONPATH=/home/gui_pd_access/inder/test_files/psu/
cd /home/gui_pd_access/inder/test_files/psu/
sudo /home/gui_pd_access/inder/test_files/psu/psu.sh False


if [ "${target_connected^^}" == "IDC" ]; then
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True 
    cd /home/gui_pd_access/inder/gui_pd_access_nuc_worker/recover_broken_idc_with_uart/dev_flash_idc/mgu22-MGU22_22w12.5-1-21-mgu22-images/mgu22
    sudo ./flash_all.sh idc23_high

elif [ "${target_connected^^}" == "MGU" ]; then
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True 
   cd /home/gui_pd_access/inder/gui_pd_access_nuc_worker/recover_broken_idc_with_uart/dev_flash_idc/mgu22-MGU22_22w12.5-1-21-mgu22-images/mgu22
   #cd /home/gui_pd_access/mgu22-MGU22_D450S_22w24.3-1-4-mgu22-images/mgu22
   sudo ./flash_all.sh mgu22_highf

elif [ "${target_connected^^}" == "PADI" ]; then
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True 
    cd /home/gui_pd_access/inder/mgu22-MGU22_22w12.5-1-21-mgu22-images/mgu22
    sudo ./flash_all.sh

else
    echo Please eneter idc/mgu/padi

fi
