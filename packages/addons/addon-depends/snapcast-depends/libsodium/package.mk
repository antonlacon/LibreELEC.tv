# SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) 2022-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="libsodium"
PKG_VERSION="1.0.22"
PKG_SHA256="dce1986e63c3e14e3a7d1db62f350614284862d4e57dec5d9263d10549e35250"
PKG_LICENSE="ISC"
PKG_SITE="https://libsodium.org/"
PKG_URL="https://download.libsodium.org/libsodium/releases/libsodium-${PKG_VERSION}-stable.tar.gz"
PKG_DEPENDS_TARGET="toolchain"
PKG_LONGDESC="A modern, portable, easy to use crypto library"

PKG_CONFIGURE_OPTS_TARGET="--disable-shared"
