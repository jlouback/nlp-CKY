#!/bin/sh
python count_cfg_freq.py parse_train.dat > cfg.counts
python question4.py cfg.counts parse_train.dat
python count_cfg_freq.py parse_train.dat > cfg.counts
python question5.py cfg.counts parse_dev.dat > q5_output
python question6.py cfg_vert.counts parse_dev.dat cfg.counts > q6_output
