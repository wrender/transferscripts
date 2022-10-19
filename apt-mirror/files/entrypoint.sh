#!/bin/bash
# Refresh mirror every X hours
while true;
do
  apt-mirror
  echo "Start sleep 12h..."
  sleep 12h
done