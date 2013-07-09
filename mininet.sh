#!/bin/bash

sudo ~/sdx-platform/mininet/mn -c
sudo ~/sdx-platform/mininet/mn --custom $HOME/sdx-platform/mininet/extra-topos.py --controller remote --mac $@
