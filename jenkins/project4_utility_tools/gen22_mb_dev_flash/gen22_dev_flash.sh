#!/usr/bin/env bash

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@$worker_name.$with_network << EOF
 echo ======== hostname ======================
hostname
echo -e "\n\n=========== Check Memory Size ==================="
df -h | egrep 'Filesystem|/dev/nvme0n1p2'
echo -e "\n\n============uptime ============================"
uptime
echo -e "\n\n============ dev flash procedure start here  ============================"
echo -e "\n\n============ Build is downloading  ============================"
cd /home/tf_admin/inder
if [[ -d /home/tf_admin/inder/$target_connected_to_worker ]]
then
    echo "/home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*  folder exist"
    cd /home/tf_admin/inder/$target_connected_to_worker/bmw_idc23*/mgu22
    ls
    ./flash_all.sh idc23_high
    /opt/utils/psu/manage_zd.py -m qdl & ./flash_all.sh idc23_high
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

