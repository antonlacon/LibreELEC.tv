# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="steamlink-rpi"
PKG_VERSION="1.0"
PKG_REV="100"
PKG_ARCH="arm"
PKG_ADDON_PROJECTS="RPi2"
PKG_LICENSE="custom"
PKG_SITE="https://support.steampowered.com/kb_article.php?ref=6153-IFGH-6589"
PKG_DEPENDS_TARGET="toolchain steamlink-libjpeg-turbo steamlink-libpng steamlink-libXext steamlink-libX11"
PKG_SECTION="script"
PKG_SHORTDESC="Steam Link App for Raspberry Pi"
PKG_LONGDESC="Installs the Steam Link App for Raspberry Pi 3 or newer from Valve for use in streaming from Steam clients. Addon is not associated with Valve. Steam and the Steam logo are trademarks and/or registered trademarks of Valve Corporation in the U.S. and/or other countries."
PKG_TOOLCHAIN="manual"

PKG_IS_ADDON="yes"
PKG_ADDON_NAME="steamlink-rpi"
PKG_ADDON_TYPE="xbmc.python.script"
PKG_ADDON_PROVIDES="executable"

PKG_STEAMLINK_VERSION="1.1.64.162"
PKG_STEAMLINK_HASH="1ea1c41802bd6cc3efdba7ba258b9d25d5c07cdd1d0ffe9f2d47597588a09155"

make_target() {
  :
}

addon() {
  # Add needed libraries
  mkdir -p ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs

  # libpng
  cp -L $(get_build_dir steamlink-libpng)/.${TARGET_NAME}/.libs/libpng16.so.16 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/

  # libjpeg-turbo
  cp -L $(get_build_dir steamlink-libjpeg-turbo)/.${TARGET_NAME}/libjpeg.so.62 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/

  # libXext
  cp -L $(get_build_dir steamlink-libXext)/.${TARGET_NAME}/src/.libs/libXext.so.6 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/

  # libX11
  cp -L $(get_build_dir steamlink-libX11)/.${TARGET_NAME}/src/.libs/libX11.so.6 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/
  cp -L $(get_build_dir steamlink-libX11)/.${TARGET_NAME}/src/.libs/libX11-xcb.so.1 ${ADDON_BUILD}/${PKG_ADDON_ID}/system-libs/
}

post_install_addon() {
  # Add steamlink version to download to addon
  sed -e "s/@STEAMLINK_VERSION@/${PKG_STEAMLINK_VERSION}/" \
      -e "s/@STEAMLINK_HASH@/${PKG_STEAMLINK_HASH}/" \
      -i ${ADDON_BUILD}/${PKG_ADDON_ID}/default.py
}
