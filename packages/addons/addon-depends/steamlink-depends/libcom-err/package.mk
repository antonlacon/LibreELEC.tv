# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2016 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2018-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="libcom-err"
PKG_VERSION="1.47.1"
PKG_SHA256="5a33dc047fd47284bca4bb10c13cfe7896377ae3d01cb81a05d406025d99e0d1"
PKG_LICENSE="GPL"
PKG_SITE="http://e2fsprogs.sourceforge.net/"
PKG_URL="https://www.kernel.org/pub/linux/kernel/people/tytso/e2fsprogs/v${PKG_VERSION}/e2fsprogs-${PKG_VERSION}.tar.xz"
PKG_DEPENDS_TARGET="autotools:host gcc:host"
PKG_LONGDESC="Common error-handing library"
PKG_BUILD_FLAGS="-parallel -cfg-libs -sysroot"

post_unpack() {
  # Increase minimal inode size to avoid:
  # "ext4 filesystem being mounted at xxx supports timestamps until 2038 (0x7fffffff)"
  sed -i 's/inode_size = 128/inode_size = 256/g' ${PKG_BUILD}/misc/mke2fs.conf.in
}

pre_configure() {
  PKG_CONFIGURE_OPTS_TARGET="BUILD_CC=${HOST_CC} \
                           --disable-blkid-debug \
                           --disable-bsd-shlibs \
                           --disable-debugfs \
                           --disable-e2initrd-helper \
                           --enable-elf-shlibs \
                           --disable-fsck \
                           --disable-fuse2fs \
                           --disable-imager \
                           --disable-jbd-debug \
                           --disable-libblkid \
                           --disable-libuuid \
                           --disable-nls \
                           --disable-profile \
                           --enable-resizer \
                           --disable-rpath \
                           --disable-subset \
                           --disable-symlink-build \
                           --disable-symlink-install \
                           --disable-testio-debug \
                           --enable-tls \
                           --disable-uuidd \
                           --enable-verbose-makecmds \
                           --with-crond-dir=no \
                           --without-pthread \
                           --with-systemd-unit-dir=no \
                           --with-udev-rules-dir=no"
}

post_makeinstall_target() {
  make -C lib/et LIBMODE=644 DESTDIR=${SYSROOT_PREFIX} install

  rm -rf ${INSTALL}/usr/sbin/badblocks
  rm -rf ${INSTALL}/usr/sbin/blkid
  rm -rf ${INSTALL}/usr/sbin/dumpe2fs
  rm -rf ${INSTALL}/usr/sbin/e2freefrag
  rm -rf ${INSTALL}/usr/sbin/e2undo
  rm -rf ${INSTALL}/usr/sbin/e4defrag
  rm -rf ${INSTALL}/usr/sbin/filefrag
  rm -rf ${INSTALL}/usr/sbin/fsck
  rm -rf ${INSTALL}/usr/sbin/logsave
  rm -rf ${INSTALL}/usr/sbin/mklost+found
}
