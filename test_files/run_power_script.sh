#!/usr/bin/env bash

export PYTHONPATH=/home/gui_pd_access/inder/test_files/psu/
cd /home/gui_pd_access/inder/test_files/psu/
sudo /home/gui_pd_access/inder/test_files/psu/psu.sh False
sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True
python /home/gui_pd_access/inder/test_files/hu-keepalive.py

