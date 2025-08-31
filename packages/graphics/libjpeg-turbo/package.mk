# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2016 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2018-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="libjpeg-turbo"
PKG_VERSION="3.1.1"
PKG_SHA256="aadc97ea91f6ef078b0ae3a62bba69e008d9a7db19b34e4ac973b19b71b4217c"
PKG_LICENSE="GPL"
PKG_SITE="https://libjpeg-turbo.org/"
PKG_URL="https://github.com/libjpeg-turbo/libjpeg-turbo/releases/download/${PKG_VERSION}/${PKG_NAME}-${PKG_VERSION}.tar.gz"
PKG_DEPENDS_HOST="cmake:host ninja:host"
PKG_DEPENDS_TARGET="cmake:host ninja:host gcc:host"
PKG_LONGDESC="A JPEG image codec that uses SIMD instructions."
PKG_BUILD_FLAGS="+pic +pic:host"

PKG_CMAKE_OPTS_HOST="-DENABLE_STATIC=ON \
                     -DENABLE_SHARED=OFF \
                     -DWITH_JPEG8=OFF \
                     -DWITH_SIMD=OFF"

PKG_CMAKE_OPTS_TARGET="-DENABLE_STATIC=OFF \
                       -DENABLE_SHARED=ON \
                       -DWITH_JPEG8=OFF"

if target_has_feature "(neon|sse)"; then
  PKG_CMAKE_OPTS_TARGET+=" -DWITH_SIMD=ON"
else
  PKG_CMAKE_OPTS_TARGET+=" -DWITH_SIMD=OFF"
fi

if [ ${TARGET_ARCH} = "x86_64" ]; then
  PKG_DEPENDS_HOST+=" nasm:host"
  PKG_DEPENDS_TARGET+=" nasm:host"
fi

post_makeinstall_target() {
  rm -rf ${INSTALL}/usr/bin
}
