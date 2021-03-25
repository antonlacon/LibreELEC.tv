# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2021-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="btrfs-progs"
PKG_VERSION="5.10.1"
PKG_SHA256="69788461f7076951f7235b87d0a5615683151dfbfaaa93f645279bf757e85769"
PKG_LICENSE="GPLv2"
PKG_SITE="https://btrfs.wiki.kernel.org/index.php/Main_Page"
PKG_URL="https://github.com/kdave/btrfs-progs/archive/refs/tags/v${PKG_VERSION}.tar.gz"
PKG_DEPENDS_TARGET="toolchain util-linux lzo zlib zstd"
PKG_DEPENDS_INIT="${PKG_DEPENDS_TARGET}"
PKG_LONGDESC="tools for the btrfs filesystem"
PKG_TOOLCHAIN="configure"


PKG_CONFIGURE_OPTS_TARGET="--disable-backtrace \
                           --disable-convert \
                           --disable-documentation \
                           --disable-python \
                           --disable-shared \
                           --enable-zstd"

PKG_CONFIGURE_OPTS_INIT="${PKG_CONFIGURE_OPTS_TARGET}"


pre_configure_target() {
  ./autogen.sh
}


#post_makeinstall_target() {
#}

makeinstall_init() {
  mkdir -p ${INSTALL}/usr/sbin
    cp fsck.btrfs ${INSTALL}/usr/sbin

  if [ ${INITRAMFS_PARTED_SUPPORT} = "yes" ]; then
    cp mkfs.btrfs ${INSTALL}/usr/sbin
  fi
}
