# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2011 Anthony Nash (nash.ant@gmail.com)
# Copyright (C) 2009-2016 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2016-2022 Team LibreELEC (https://libreelec.tv)

PKG_NAME="vdr"
PKG_VERSION="2.6.1"
PKG_SHA256="4717616da8e5320dceb7b44db1e4fa1b01e1d356a73717ec21225387020999c6"
PKG_LICENSE="GPL"
PKG_SITE="http://www.tvdr.de"
PKG_URL="http://git.tvdr.de/?p=vdr.git;a=snapshot;h=refs/tags/${PKG_VERSION};sf=tbz2"
PKG_SOURCE_NAME="${PKG_NAME}-${PKG_VERSION}.tar.bz2"
PKG_DEPENDS_TARGET="toolchain bzip2 fontconfig freetype libcap libiconv libjpeg-turbo"
PKG_LONGDESC="A DVB TV server application."
PKG_TOOLCHAIN="manual"

post_unpack() {
  rm -rf ${PKG_BUILD}/PLUGINS/src/skincurses
}

pre_configure_target() {
  export LDFLAGS="$(echo ${LDFLAGS} | sed -e "s|-Wl,--as-needed||") -L${SYSROOT_PREFIX}/usr/lib/iconv"
}

pre_make_target() {
  cat > Make.config <<EOF
  PLUGINLIBDIR = /usr/lib/vdr
  PREFIX = /usr
  VIDEODIR = /storage/videos
  CONFDIR = /storage/.config/vdr
  LOCDIR = ./locale
  LIBS += -liconv
  NO_KBD=yes
  VDR_USER=root
EOF
}

make_target() {
  make vdr vdr.pc
  make LOCDIR=./dummylocale install-i18n
  make include-dir
}
