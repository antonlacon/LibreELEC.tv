#!/bin/sh

# SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

. /etc/profile
oe_setup_addon script.program.steamlink

# Abort if Steam Link is not setup
if [ ! -f "${ADDON_DIR}/prep.ok" ]; then
  exit 0
fi

UDEV_DIR="/lib/udev/rules.d"
UPPER="${ADDON_DIR}/steamlink/udev/rules.d"
WORK="${ADDON_DIR}/steamlink/.overlay"

# Cleanup routine on exit
cleanup() {
  # Unount udev overlay
  if mountpoint -q "${UDEV_DIR}"; then
    umount "${UDEV_DIR}"
    udevadm trigger
  fi

  # Start Kodi if not running
  if ! systemctl is-active --quiet kodi; then
    systemctl start kodi
  fi
}
trap cleanup EXIT

for dir in "${UPPER}" "${WORK}"; do
  if [ ! -d "${dir}" ]; then
    mkdir -p "${dir}" || {
      echo "Error: Failed to create directory: ${dir}" >&2
      exit 1
    }
  fi
done

# Mount overlay if not mounted
if ! mountpoint -q "${UDEV_DIR}"; then
  mount -t overlay overlay \
    -o "lowerdir=${UDEV_DIR},upperdir=${UPPER},workdir=${WORK}" \
    "${UDEV_DIR}"

  udevadm trigger
fi

# Stop Kodi so controller input goes to Steam Link
systemctl stop kodi || echo "Warning: Kodi do not stop cleanly"

# Audio environment for Steam Link
# xxx: assumes ALSA
export PULSE_SERVER="none"
export SDL_AUDIODRIVER="alsa"

# Launch Steam Link
"${ADDON_DIR}/steamlink/steamlink.sh"
STATUS=$?

exit $STATUS
