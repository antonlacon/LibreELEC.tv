#!/bin/sh

# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2021-present Team LibreELEC (https://libreelec.tv)

CURRENT_IMG="${1}"
UPGRADE_IMG="${2}"

# Allow upgrades between arm and arm64 - binary addons will be broken
if [ "${CURRENT_IMG}" = "RPi3.arm" -o "${CURRENT_IMG}" = "RPi3.aarch64" ]; then
  exit 0
# Allow upgrade from RPi2.arm to RPi3.arm if an RPi3 B, B+ or A+
elif [ "${CURRENT_IMG}" = "RPi2.arm" -a "${UPGRADE_IMG}" = "RPi3.arm" ]; then
  RPI_REVISION=$(hexdump -ve '1/1 "%.2x"' /sys/firmware/devicetree/base/system/linux,revision)
  RPI_TYPE=${RPI_REVISION:6:1}
  if [ "${RPI_TYPE}" = "8" -o "${RPI_TYPE}" = "d" -o "${RPI_TYPE}" = "e" ]; then
    exit 0
  else
    exit 1
  fi
else
  exit 1
fi
