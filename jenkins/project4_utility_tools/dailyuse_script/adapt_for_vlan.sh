#!/usr/bin/env bash
ssh_signature_file=/home/gui_pd_access/inder/test_files/id_ed25519_mgu22

cat /etc/network/interfaces.d/usb-eth0
echo Use hu for MGU, idc for IDC and padi for PADI as argument. And run the script with sudo 
echo your connected target to worker is $1
echo ====================================
if [ "$1" == "hu" ] || [ "$1" == "idc" ]; then
	echo configuring VLAN for $1
	echo ping to $1 before change in VLAN
	ping -c 6 160.48.199.99
	sed -i 's/160.48.199.99/160.48.199.40/g' /etc/network/interfaces.d/usb-eth0
	sudo service network-manager restart
	ssh-keygen -f "/home/gui_pd_access/.ssh/known_hosts" -R "160.48.199.99"
	echo ping to $1 after change in VLAN
	ping -c 6 160.48.199.99
	target_ip=160.48.199.99
	ssh -i $ssh_signature_file root@$target_ip "systemctl is-active application.target"
	ssh -i $ssh_signature_file root@$target_ip "systemctl is-active flashing.target"
	ssh -i $ssh_signature_file root@$target_ip "systemctl is-active rsu.target"
	ssh -i $ssh_signature_file root@$target_ip "nsm_control --r 7"
	sleep 10
	ssh -i $ssh_signature_file root@$target_ip "systemctl is-active application.target"
elif [ "$1" == "padi" ]; then
	echo configuring VLAN for $1
	echo ping to $1 before change in VLAN
	ping -c 6 160.48.199.40
	sed -i 's/160.48.199.40/160.48.199.99/g' /etc/network/interfaces.d/usb-eth0
	sudo service network-manager restart
	echo ping to $1 after change in VLAN
	ssh-keygen -f "/home/gui_pd_access/.ssh/known_hosts" -R "160.48.199.40"
	ping -c 6 160.48.199.40
fi

cat /etc/network/interfaces.d/usb-eth0

