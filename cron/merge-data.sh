#!/bin/bash
source /root/miniconda3/bin/activate api
cd /root/chileanfires/cron
/root/miniconda3/envs/api/bin/python /root/chileanfires/cron/merge-data.py