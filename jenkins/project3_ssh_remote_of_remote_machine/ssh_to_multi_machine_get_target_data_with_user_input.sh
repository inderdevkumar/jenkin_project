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
sshpass -p "BHUasampleTest14" scp -r  /home/gui_pd_access/inder/test_files tf_admin@$worker_name.$with_network:/home/tf_admin/

echo -e "\n\n======== Taking SSH to ONe REmote MACHINE ==================== ====================== ======================"

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@$worker_name.$with_network << EOF
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

echo -e "\n\n=========== creatre folder in tmp folder for data backup in /tmp/$worker_name ===================="
mkdir $worker_name

echo -e "\n\n======== Prec check for  SSH to Target connected to NUC ================== ====================== ======================="
echo -e "\n\n======== Running VCAR Script ===================="

python /home/tf_admin/test_files/hu-keepalive.py > /home/tf_admin/test_files/vcar_log.txt 2>&1 &
echo -e "\n\n======== Toggling POwer of 12V ===================="

/opt/utils/psu/manage_zd.py -s on

echo -e "\n\n======== ping to target ===================="
if [[ "$target_connected_to_worker"  == "mgu" || "$target_connected_to_worker" == "idc" ]] ;then
        ping 160.48.199.99 -c 10
	echo -e "\n\n======== Chaning correct mode to ssh key  ===================="
	chmod 400 /home/tf_admin/test_files/id_ed25519_mgu22

	if [[ "$variant_connected"  == "c" ]] ; then
                echo -e "\n\n =========Selected target is c type. Checking for csrs under sysfunc folder ====================="
                ls -al /var/sys/sysfunc
        
                echo -e "\n\n ========= moving files from hu/idc to NUC /tmp folder ========================"
                scp -o StrictHostKeyChecking=no -i /home/tf_admin/test_files/id_ed25519_mgu22 -r -v root@160.48.199.99:/var/sys/sysfunc $worker_name/
                
        else
                echo -e "\n\n ========= Check for csrs under sysfunc folder ====================="
                ls -al /var/sys/sysfunc
                echo -e "\n\n ========= Selected target is d type. Checking for trustzone_data and sys under var folder ====================="
                ls -al /var
        
                echo -e "\n\n ========= moving files from hu/idc to NUC home/$worker_name folder ========================"
                scp -o StrictHostKeyChecking=no -i /home/tf_admin/test_files/id_ed25519_mgu22 -r -v root@160.48.199.99:/var/sys/ root@160.48.199.99:/var/trustzone_data $worker_name/
        fi

	echo -e "\n\n======== Taking ssh to target  ===================="
	ssh -o StrictHostKeyChecking=no -i /home/tf_admin/test_files/id_ed25519_mgu22 root@160.48.199.99 '
	echo ======== grim status  ======================
	grim status
        echo -e "\n\n========= ECU UID from grim status  ======================"
        grim status | grep "ECU-UID"
	grim status | grep "ECU-UID" | tr -d " "
	grim status | grep "ECU-UID" | tr -d " " | tr [:lower:] [:upper:]
	echo ======== MAC Address from grim status  ======================
        grim status | grep "SOC-MAC"
	grim status | grep "SOC-MAC" | tr " " :
	grim status | grep "SOC-MAC" | tr " " : | tr [:lower:] [:upper:]
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

	'

else
	ping 160.48.199.40 -c 10
	echo -e "\n\n======== Chaning correct mode to ssh key  ===================="
        chmod 400 /home/tf_admin/test_files/id_ed25519_mgu22

        if [[ "$variant_connected"  == "c" ]] ; then
                echo -e "\n\n =========Selected target is c type. Checking for csrs under sysfunc folder ====================="
                ls -al /var/sys/sysfunc
        
                echo -e "\n\n ========= moving files from padi to NUC home/$worker_name folder ========================"
                scp -o StrictHostKeyChecking=no -i /home/tf_admin/test_files/id_ed25519_mgu22 -r -v root@160.48.199.40:/var/sys/sysfunc $worker_name/
                
        else
                echo -e "\n\n ========= Check for csrs under sysfunc folder ====================="
                ls -al /var/sys/sysfunc
                echo -e "\n\n ========= Selected target is d type. Checking for trustzone_data and sys under var folder ====================="
                ls -al /var
        
                echo -e "\n\n ========= moving files from padi to NUC home/$worker_name folder ========================"
                scp -o StrictHostKeyChecking=no -i /home/tf_admin/test_files/id_ed25519_mgu22 -r -v root@160.48.199.40:/var/sys/ root@160.48.199.99:/var/trustzone_data $worker_name/
        fi

        echo -e "\n\n======== Taking ssh to target  ===================="
        ssh -o StrictHostKeyChecking=no -i /home/tf_admin/test_files/id_ed25519_mgu22 root@160.48.199.99 '
        echo ======== grim status  ======================
        grim status
        echo -e "\n\n========= ECU UID from grim status  ======================"
        grim status | grep "ECU-UID"
        grim status | grep "ECU-UID" | tr -d " "
        grim status | grep "ECU-UID" | tr -d " " | tr [:lower:] [:upper:]
	echo ======== MAC Address from grim status  ======================
        grim status | grep "SOC-MAC"
        grim status | grep "SOC-MAC" | tr " " :
        grim status | grep "SOC-MAC" | tr " " : | tr [:lower:] [:upper:]
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

        '
fi
EOF

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@$worker_name.$with_network << EOF
 echo ======== Back to Worker ====================== ====================== ====================== ======================
hostname
echo -e "\n\n======= listing files in tf_admkin and tmp folder ===================="
ls
ls /tmp

echo -e "\n\n======= Deleting unwanted test_files folder  ===================="
sudo -S rm -rf test_files
BHUasampleTest14

echo -e "\n\n======= Rebooting worker  ===================="
sudo reboot
EOF

echo -e "\n\n======= worker is rebooted waiting for 15s to re login=================="
sleep 15

sshpass -p "BHUasampleTest14" ssh -o StrictHostKeyChecking=no tf_admin@$worker_name.$with_network << EOF
echo -e "\n\n======= Back to worker   ===================="
hostname
echo -e "\n\n======= to confirm reboot is done  uptime  ===================="
uptime
echo -e "\n\n======= Now moving files from $worker_name to tmp folder. BUt PLan is to MOving files from remote machine to LOcal window machine  ==================="
#scp -r  /tmp/sys tf_admin@lnt_testbench.$with_network:/home/tf_admin/inder/
#scp -r  /tmp/var tf_admin@lnt_testbench.$with_network:/home/tf_admin/inder/
mv $worker_name /tmp
echo -e "\n\n======= to check if test_files folder and /tmp/$worker_name is removed or not  ===================="
ls
ls al /tmp/$worker_name
echo   ========================================================================================================================
EOF

