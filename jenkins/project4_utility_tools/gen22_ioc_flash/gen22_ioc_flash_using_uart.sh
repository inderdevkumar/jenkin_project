#!/usr/bin/env bash

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@$worker_name.$with_network << EOF
 echo ======== hostname ======================
hostname
echo -e "\n\n=========== Check Memory Size ==================="
df -h | egrep 'Filesystem|/dev/nvme0n1p2'
echo -e "\n\n============uptime ============================"
uptime
echo -e "\n\n============ UART IOC	 flash procedure start here  ============================"
echo -e "\n\n============ Build is downloading  ============================"

if [[ -d /home/tf_admin/inder/$target_connected_to_worker ]]
then
    echo "/home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*  folder exist"
    if [[ -d /home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*/mgu22/ioc/b2/DevFBL_B2 ]]
    then
        cd /home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*/mgu22/ioc/b2
        ls -al
        cd DevFBL_B2/Linux
        /opt/utils/psu/manage_zd.py -s on & ./DEV_BL_pcclient_B2 -p /dev/ttyIOC -v 4M -wv /home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*/mgu22/ioc/b2/bmw_idc_m7_4m*.srec
    else
        cd /home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*/mgu22/ioc/b2
        7z x ioc_*_idc_DevFBL_B2
        ls -al
        cd DevFBL_B2/Linux
        ls -al
        echo chmod 777 DEV_BL_pcclient_B2
        chmod 777 DEV_BL_pcclient_B2
        /opt/utils/psu/manage_zd.py -s on & ./DEV_BL_pcclient_B2 -p /dev/ttyIOC -v 4M -wv /home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*/mgu22/ioc/b2/bmw_idc_m7_4m*.srec
    fi
    
else
   mkdir $target_connected_to_worker
   cd /home/tf_admin/inder/$target_connected_to_worker
   wget --user inderdevyadavpartner --password Koderma@123# $build_link
   ls
   tar -xzvf bmw_idc23*
   ls
   cd /home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*/mgu22
   ls
   /opt/utils/psu/manage_zd.py -m qdl & ./flash_all.sh idc23_high
fi
EOF
