# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

. $(get_pkg_directory libXext)/package.mk

PKG_NAME="steamlink-libXext"
PKG_LONGDESC="libXext for steamlink-rpi"
PKG_URL=""
PKG_DEPENDS_TARGET+=" libXext"
PKG_BUILD_FLAGS+=" -sysroot"

unpack() {
  mkdir -p ${PKG_BUILD}
  tar --strip-components=1 -xf ${SOURCES}/${PKG_NAME:10}/${PKG_NAME:10}-${PKG_VERSION}.tar.bz2 -C ${PKG_BUILD}
}
