#!/bin/sh
ulimit -s unlimited
ulimit -n 100000
xvfb-run python3 main.py > err.log