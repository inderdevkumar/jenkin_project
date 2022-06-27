#!/usr/bin/env bash
echo Enter worker name
read WORKER_NAME
echo Enter full path from where u want to copy
read FROM
echo Enter the full path where you want to paste
read DESTINATION
sudo scp -r tf_admin@$WORKER_NAME:$FROM $DESTINATION
