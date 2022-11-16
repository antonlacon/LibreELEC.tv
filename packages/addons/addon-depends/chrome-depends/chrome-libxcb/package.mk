# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2018-2021 Team LibreELEC (https://libreelec.tv)

. $(get_pkg_directory libxcb)/package.mk

PKG_NAME="chrome-libxcb"
PKG_LONGDESC="libxcb for chrome"
PKG_URL=""
PKG_DEPENDS_UNPACK+=" libxcb"
PKG_BUILD_FLAGS="-sysroot"

PKG_CONFIGURE_OPTS_TARGET="${PKG_CONFIGURE_OPTS_TARGET} \
                           --disable-static \
                           --enable-shared"

unpack() {
  mkdir -p ${PKG_BUILD}
  tar --strip-components=1 -xf ${SOURCES}/${PKG_NAME:7}/${PKG_NAME:7}-${PKG_VERSION}.tar.xz -C ${PKG_BUILD}
}
