#!/usr/bin/env bash

echo ========================
echo Modemamanger should be stopped
echo SW4 switch should be in right side ie in qdl mode manually
echo Build is already downloaded and saved locally
echo ========================
echo Please enter the target you want to flash. padi/idc/mgu?
read target_connected

export PYTHONPATH=/home/gui_pd_access/inder/test_files/psu/
cd /home/gui_pd_access/inder/test_files/psu/
sudo /home/gui_pd_access/inder/test_files/psu/psu.sh False
sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True

if [ "${target_connected^^}" == "IDC" ]; then
	echo Sleep for 30s to get ECU alive
	sleep 30
	echo ECU MOde of Traget is
	python3 /home/gui_pd_access/inder/test_files/hsfz-send/read_ecu_mode.py --ip-addr 160.48.199.99 --diag-addr 0x63
	echo ECU MOde of Traget is
        python3 /home/gui_pd_access/inder/test_files/hsfz-send/read_ecu_uid.py --ip-addr 160.48.199.99 --diag-addr 0x63
	echo Download Enginerring mode token for this sample and press any key to continue
	read user_input
	echo Installing Engineering Mode token 
	python3 /home/gui_pd_access/inder/test_files/hsfz-send/sfa_write_token.py --ip-addr 160.48.199.99 --diag-addr 0x63 --stk-file /home/gui_pd_access/Downloads/token*.stk
	echo REmove token from download folder
	rm -rf /home/gui_pd_access/Downloads/token*
	echo Rechecking ECU MOde of Traget is
        python3 /home/gui_pd_access/inder/test_files/hsfz-send/read_ecu_mode.py --ip-addr 160.48.199.99 --diag-addr 0x63
elif [ "${target_connected^^}" == "MGU" ]; then
	echo In MGU
elif [ "${target_connected^^}" == "PADI" ]; then
	echo in padi
else
    echo Please eneter idc/mgu/padi

fi
