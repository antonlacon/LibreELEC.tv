# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2016 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2018-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="binutils-or1k"
PKG_VERSION="$(get_pkg_version binutils)"
PKG_LICENSE="GPL"
PKG_URL=""
PKG_DEPENDS_HOST="toolchain:host"
PKG_LONGDESC="A GNU collection of binary utilities for OpenRISC 1000."
PKG_DEPENDS_UNPACK+=" binutils"
PKG_PATCH_DIRS+=" $(get_pkg_directory binutils)/patches"

PKG_CONFIGURE_OPTS_HOST="--target=or1k-none-elf \
                         --with-sysroot=${TOOLCHAIN}/or1k-none-elf/sysroot \
                         --without-ppl \
                         --enable-static \
                         --without-cloog \
                         --disable-werror \
                         --disable-multilib \
                         --disable-libada \
                         --disable-libssp \
                         --enable-version-specific-runtime-libs \
                         --enable-plugins \
                         --enable-gold \
                         --enable-ld=default \
                         --enable-lto \
                         --disable-nls"

unpack() {
  mkdir -p ${PKG_BUILD}
  tar --strip-components=1 -xf ${SOURCES}/binutils/binutils-${PKG_VERSION}.tar.xz -C ${PKG_BUILD}
}

pre_configure_host() {
  unset CPPFLAGS
  unset CFLAGS
  unset CXXFLAGS
  unset LDFLAGS
}

make_host() {
  make configure-host
  # override the makeinfo binary with true - this does not build the documentation
  make MAKEINFO=true
}

makeinstall_host() {
  # override the makeinfo binary with true - this does not build the documentation
  make MAKEINFO=true install
}
