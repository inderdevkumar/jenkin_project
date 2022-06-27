#!/usr/bin/env bash

#put .netrc file in /home/tf_admin
#and give correct access: sudo chmod 666 /home/tf_admin/.netrc

sudo chmod 666 /home/gui_pd_access/.netrc
echo Please enter the target you want to flash. mgu18/mgu21/rse18?
read target_connected

export PYTHONPATH=/home/gui_pd_access/inder/test_files/psu/
cd /home/gui_pd_access/inder/test_files/psu/
sudo /home/gui_pd_access/inder/test_files/psu/psu.sh False


if [ "${target_connected^^}" == "MGU18" ]; then
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True 
    sudo ssh -F /tmp/ssh_files_for_mgu/config-loopback -t -t localhost "sudo dnsmasq --log-queries --keep-in-foreground --log-facility=/home/tf_admin/mgu18/dnsmasq.log --interface=eth0 --dhcp-range=192.168.0.0,static --dhcp-host=00:1C:D7:BF:64:61,192.168.0.24" & sudo /home/tf_admin/rse/mgu-N18_22w15.2-1-4-mgu-high-images/scripts/flashIntel.sh -r 192.168.0.25 -i -e e -f -d -D D
    sudo ./flash_all.sh idc23_high

elif [ "${target_connected^^}" == "MGU21" ]; then
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True 
   cd /home/gui_pd_access/inder/gui_pd_access_nuc_worker/recover_broken_idc_with_uart/dev_flash_idc/mgu22-MGU22_22w12.5-1-21-mgu22-images/mgu22
   #cd /home/gui_pd_access/mgu22-MGU22_D450S_22w24.3-1-4-mgu22-images/mgu22
   sudo ./flash_all.sh mgu22_highf

elif [ "${target_connected^^}" == "RSE18" ]; then
    sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True 
    
    sudo ./flash_all.sh

else
    echo Please eneter idc/mgu/padi

fi