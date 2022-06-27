#!/usr/bin/env bash



echo -e "\n\n======== Taking SSH to Target connected to NUC ================== ====================== ======================="



chmod 400 /home/gui_pd_access/inder/test_files/id_ed25519_mgu22
echo -e "\n\n======== ECU UID of  target  ===================="
python3 /home/gui_pd_access/inder/test_files/hsfz-send/read_ecu_uid.py --ip-addr 160.48.199.99 --diag-addr 0x63
echo -e "\n\n======== Taking ssh to target  ===================="

ssh -o StrictHostKeyChecking=no -i /home/gui_pd_access/inder/test_files/id_ed25519_mgu22 root@160.48.199.99

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

