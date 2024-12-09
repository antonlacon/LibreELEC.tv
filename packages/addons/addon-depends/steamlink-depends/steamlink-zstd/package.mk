# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2017-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="steamlink-zstd"
PKG_VERSION="1.5.6"
PKG_SHA256="4aa8dd1c1115c0fd6b6b66c35c7f6ce7bd58cc1dfd3e4f175b45b39e84b14352"
PKG_LICENSE="BSD/GPLv2"
PKG_SITE="http://www.zstd.net"
PKG_URL="https://github.com/facebook/zstd/releases/download/v${PKG_VERSION}/zstd-${PKG_VERSION}.tar.zst"
PKG_DEPENDS_TARGET="ccache:host meson:host ninja:host gcc:host"
PKG_LONGDESC="A fast real-time compression algorithm."
# Override toolchain as meson and ninja are not built yet
# and zstd is a dependency of ccache
PKG_TOOLCHAIN="meson"
PKG_BUILD_FLAGS="-sysroot"

configure_package() {
  PKG_MESON_SCRIPT="${PKG_BUILD}/build/meson/meson.build"
}

PKG_MESON_OPTS_TARGET="-Dlegacy_level=0 \
                       -Dbin_programs=false \
                       -Dlz4=disabled \
                       -Dlzma=disabled \
                       -Dzlib=disabled"
