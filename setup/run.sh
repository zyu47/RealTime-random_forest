#!/usr/bin/env bash

gnome-terminal -x bash -c "./start.sh;bash;" &
python ../fusion/fusion_server.py --mode brandeis
