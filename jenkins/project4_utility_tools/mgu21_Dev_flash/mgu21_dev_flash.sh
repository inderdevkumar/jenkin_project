#!/usr/bin/env bash

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@$worker_name.$with_network << EOF
 echo ======== hostname ======================
hostname
echo -e "\n\n=========== Check Memory Size ==================="
df -h | egrep 'Filesystem|/dev/nvme0n1p2'
echo -e "\n\n============uptime ============================"
uptime
echo -e "\n\n============ dev flash procedure start here  ============================"
echo -e "\n\n============ Build is downloadin"
echo -e "\n\n======== Copying  test_files folder from local to Remote ===================="
sshpass -p "BHUasampleTest14" scp -r  /home/gui_pd_access/inder/test_files tf_admin@$worker_name.$with_network:/home/tf_admin/
cp /home/tf_admin/test_files/netrc/.netrc /home/tf_admin
sudo -S chmod 666 /home/tf_admin/.netrc
mv /home/tf_admin/test_files/ssh_files_for_mgu /tmp/ssh_files_for_mgu

echo -e "\n\n======== DHCP server running ===================="
sudo ssh -F /tmp/ssh_files_for_mgu/config-loopback -t -t localhost "sudo dnsmasq --log-queries --keep-in-foreground --log-facility=/home/tf_admin/test_files/dnsmasq.log --interface=eth0 --dhcp-range=192.168.0.0,static --dhcp-host=$mac_address,192.168.0.24"
echo -e "\n\n======== SWitching the target to ELK Mode  ===================="
echo -e "\n\n======== DEv Flash start  ===================="

echo -e "\n\n======== DEv Flash start  ===================="
EOF

