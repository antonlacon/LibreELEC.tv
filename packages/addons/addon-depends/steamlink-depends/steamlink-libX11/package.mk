# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

. $(get_pkg_directory libX11)/package.mk

PKG_NAME="steamlink-libX11"
PKG_LONGDESC="libX11 for steamlink-rpi"
PKG_URL=""
PKG_DEPENDS_TARGET+=" libX11"

unpack() {
  mkdir -p ${PKG_BUILD}
  tar --strip-components=1 -xf ${SOURCES}/${PKG_NAME:10}/${PKG_NAME:10}-${PKG_VERSION}.tar.bz2 -C ${PKG_BUILD}
}

makeinstall-target() {
  :
}
