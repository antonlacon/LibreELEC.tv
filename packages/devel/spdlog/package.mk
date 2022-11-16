# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2017-2022 Team LibreELEC (https://libreelec.tv)

PKG_NAME="spdlog"
PKG_VERSION="1.10.0"
PKG_SHA256="697f91700237dbae2326b90469be32b876b2b44888302afbc7aceb68bcfe8224"
PKG_LICENSE="MIT"
PKG_SITE="https://github.com/gabime/spdlog"
PKG_URL="https://github.com/gabime/spdlog/archive/v${PKG_VERSION}.tar.gz"
PKG_DEPENDS_TARGET="toolchain libfmt"
PKG_LONGDESC="Very fast, header only, C++ logging library."

PKG_CMAKE_OPTS_TARGET="-DCMAKE_CXX_STANDARD=14 \
                       -DCMAKE_CXX_EXTENSIONS:BOOL=OFF \
                       -DSPDLOG_BUILD_SHARED=ON \
                       -DSPDLOG_FMT_EXTERNAL=ON \
                       -DSPDLOG_BUILD_EXAMPLE=OFF \
                       -DSPDLOG_BUILD_TESTS=OFF"
