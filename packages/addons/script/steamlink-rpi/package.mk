# SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="steamlink-rpi"
PKG_VERSION="1.0"
PKG_REV="0"
PKG_ARCH="aarch64"
PKG_ADDON_PROJECTS="RPi5"
PKG_LICENSE="custom"
PKG_SITE="https://support.steampowered.com/kb_article.php?ref=6153-IFGH-6589"
PKG_DEPENDS_TARGET="steamlink-ffmpeg steamlink-libepoxy steamlink-libpng"
PKG_SECTION="script"
PKG_SHORTDESC="Steam Link App for Raspberry Pi"
PKG_LONGDESC="Installs the Steam Link App for Raspberry Pi 3 or newer from Valve for use in streaming from Steam clients. Addon is not associated with Valve. Steam and the Steam logo are trademarks and/or registered trademarks of Valve Corporation in the U.S. and/or other countries."
PKG_TOOLCHAIN="manual"

PKG_IS_ADDON="yes"
PKG_ADDON_NAME="steamlink-rpi"
PKG_ADDON_TYPE="xbmc.python.script"
PKG_ADDON_PROVIDES="executable"

PKG_STEAMLINK_VERSION="1.3.13.281"
PKG_STEAMLINK_HASH="6773437c2659a93e7b8d4e9c5069315f7dbf701c168a29ac1119f7b69dd7b72e"

addon() {
  # Add needed libraries
  mkdir -p ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs

  # ffmpeg
  cp -L $(get_install_dir steamlink-ffmpeg)/usr/lib/libavcodec.so.59 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/
  cp -L $(get_install_dir steamlink-ffmpeg)/usr/lib/libavutil.so.57 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/

  # libepoxy
  cp -L $(get_install_dir steamlink-libepoxy)/usr/lib/libepoxy.so.0 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/

  # libpng
  cp -L $(get_install_dir steamlink-libpng)/usr/lib/libpng16.so.16 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/
}

post_install_addon() {
  # Add steamlink version to download to addon
  sed -e "s/@STEAMLINK_VERSION@/${PKG_STEAMLINK_VERSION}/" \
      -e "s/@STEAMLINK_HASH@/${PKG_STEAMLINK_HASH}/" \
      -i ${ADDON_BUILD}/${PKG_ADDON_ID}/default.py
}
