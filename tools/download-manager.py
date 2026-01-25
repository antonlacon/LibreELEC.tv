#! /usr/bin/env python3

#SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) 2023-present Ian Leonard (antonlacon@gmail.com)

'''
This generates a list of URLs of every file used by the selected image build.

The script may be invoked in one of three ways:

  ./tools/download-manager.py --clean
  ./tools/download-manager.py --mirror
  ./tools/download-manager.py --sync

--clean lists stale packages in the sources directory.
    Add --delete to also delete these files.

--mirror will output of files that should be downloaded to create a sources mirror.
    Add --export to write the list to a file.

--sync will run --clean and then run --mirror.

For each option:
    Add --all to have it consider every project/device/arch/uboot_system in builds_all.
    Add --builddirs to filter builds_all to just ones with a build directory.

    Use PROJECT=W DEVICE=X ARCH=Y UBOOT_SYSTEM=Z ./download-manager.py to run against
    the specified project/device/arch on the CLI.

Examples:
    Clean files in the sources dir not needed to build RPi5.aarch64 images:
    PROJECT=RPi DEVICE=RPi5 ARCH=aarch64 tools/download-manager --clean

    Write the list of files needed to build a mirror for every image to a file:
    ./tools/download-manager.py --mirror --all --export file.txt
'''


import argparse
import os
import subprocess
import shutil
import sys

from concurrent.futures import ThreadPoolExecutor


DISTRO_NAME = 'LibreELEC'


# project, device, arch, uboot_system
builds_all = [
    ['Allwinner', 'A64', 'aarch64', 'oranagepi-win'],
    ['Allwinner', 'A64', 'aarch64', 'pine64'],
    ['Allwinner', 'A64', 'aarch64', 'pine64-lts'],
    ['Allwinner', 'A64', 'aarch64', 'pine64-plus'],
    ['Allwinner', 'H3', 'arm', 'banana-m2p'],
    ['Allwinner', 'H3', 'arm', 'beelink-x2'],
    ['Allwinner', 'H3', 'arm', 'libretech-h3'],
    ['Allwinner', 'H3', 'arm', 'nanopi-m1'],
    ['Allwinner', 'H3', 'arm', 'orangepi-2'],
    ['Allwinner', 'H3', 'arm', 'orangepi-pc'],
    ['Allwinner', 'H3', 'arm', 'orangepi-pc-plus'],
    ['Allwinner', 'H3', 'arm', 'orangepi-pc-plus2e'],
    ['Allwinner', 'H5', 'aarch64', 'tritium-h5'],
    ['Allwinner', 'H6', 'aarch64', 'beelink-gs1'],
    ['Allwinner', 'H6', 'aarch64', 'orangepi-3'],
    ['Allwinner', 'H6', 'aarch64', 'orangepi-3-lts'],
    ['Allwinner', 'H6', 'aarch64', 'oranagepi-lite2'],
    ['Allwinner', 'H6', 'aarch64', 'orangepi-one-plus'],
    ['Allwinner', 'H6', 'aarch64', 'pine-h64'],
    ['Allwinner', 'H6', 'aarch64', 'pine-h64-model-b'],
    ['Allwinner', 'H6', 'aarch64', 'tanix-tx6'],
    ['Allwinner', 'R40', 'arm', 'banana-m2u'],
    ['Amlogic', 'AMLGX', 'aarch64', 'bananapi-m2-pro'],
    ['Amlogic', 'AMLGX', 'aarch64', 'bananapi-m2s'],
    ['Amlogic', 'AMLGX', 'aarch64', 'bananapi-m5'],
    ['Amlogic', 'AMLGX', 'aarch64', 'box'],
    ['Amlogic', 'AMLGX', 'aarch64', 'khadas-vim'],
    ['Amlogic', 'AMLGX', 'aarch64', 'khadas-vim2'],
    ['Amlogic', 'AMLGX', 'aarch64', 'khadas-vim3'],
    ['Amlogic', 'AMLGX', 'aarch64', 'khadas-vim3l'],
    ['Amlogic', 'AMLGX', 'aarch64', 'lafrite'],
    ['Amlogic', 'AMLGX', 'aarch64', 'lepotato'],
    ['Amlogic', 'AMLGX', 'aarch64', 'nanopi-k2'],
    ['Amlogic', 'AMLGX', 'aarch64', 'odroid-c2'],
    ['Amlogic', 'AMLGX', 'aarch64', 'odroid-c4'],
    ['Amlogic', 'AMLGX', 'aarch64', 'odroid-hc4'],
    ['Amlogic', 'AMLGX', 'aarch64', 'odroid-n2'],
    ['Amlogic', 'AMLGX', 'aarch64', 'radxa-zero'],
    ['Amlogic', 'AMLGX', 'aarch64', 'radxa-zero2'],
    ['Amlogic', 'AMLGX', 'aarch64', 'wetek-core2'],
    ['Amlogic', 'AMLGX', 'arm', 'wetek-hub'],
    ['Amlogic', 'AMLGX', 'aarch64', 'wetek-play2'],
    ['Generic', 'Generic', 'x86_64', None],
    ['Generic', 'Generic-legacy', 'x86_64', None],
    ['RPi', 'RPi2', 'arm', None],
    ['RPi', 'RPi4', 'aarch64', None],
    ['RPi', 'RPi5', 'aarch64', None],
    ['Samsung', 'Exynos', 'arm', 'odroid-xu3'],
    ['Samsung', 'Exynos', 'arm', 'odroid-xu4'],
    ['Rockchip', 'RK3288', 'arm', 'miqi'],
    ['Rockchip', 'RK3288', 'arm', 'tinker'],
    ['Rockchip', 'RK3328', 'aarch64', 'a1'],
    ['Rockchip', 'RK3328', 'aarch64', 'roc-cc'],
    ['Rockchip', 'RK3328', 'aarch64', 'rock64'],
    ['Rockchip', 'RK3399', 'aarch64', 'hugsun-x99'],
    ['Rockchip', 'RK3399', 'aarch64', 'khadas-edge'],
    ['Rockchip', 'RK3399', 'aarch64', 'nanopc-t4'],
    ['Rockchip', 'RK3399', 'aarch64', 'nanopi-m4'],
    ['Rockchip', 'RK3399', 'aarch64', 'orangepi'],
    ['Rockchip', 'RK3399', 'aarch64', 'roc-pc'],
    ['Rockchip', 'RK3399', 'aarch64', 'roc-pc-plus'],
    ['Rockchip', 'RK3399', 'aarch64', 'rock-pi-4'],
    ['Rockchip', 'RK3399', 'aarch64', 'rock-pi-4-plus'],
    ['Rockchip', 'RK3399', 'aarch64', 'rock-pi-n10'],
    ['Rockchip', 'RK3399', 'aarch64', 'rock960'],
    ['Rockchip', 'RK3399', 'aarch64', 'rockpro64'],
    ['Rockchip', 'RK3399', 'aarch64', 'sapphire'],
]
# no test builds
#    ['RPi', 'RPi', 'arm', None],
#    ['NXP', 'iMX6', 'arm', 'cubox'],
#    ['NXP', 'iMX6', 'arm', 'udoo'],
#    ['NXP', 'iMX6', 'arm', 'wandboard'],
#    ['NXP', 'iMX8', 'aarch64', 'mq-evk'],
#    ['NXP', 'iMX8', 'aarch64', 'pico-mq'],
#    ['Qualcomm', 'Dragonboard', 'aarch64', '410c'],


def execute(command):
    '''Run shell commands.'''
    try:
        cmd_status = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f'Command failed: {command}')
        print(f'Executed command: {e.cmd}')
        print(f'START COMMAND OUTPUT:\n{e.stdout.decode()}\nEND COMMAND OUTPUT')
        return None
    return cmd_status.stdout.decode()


def parse_distro_version():
    '''Read distro version settings from file.'''
    distro_version = None
    os_version = None
    with open(f'{os.getcwd()}/distributions/{DISTRO_NAME}/version', mode='r', encoding='utf-8') as data:
        content = data.read()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('DISTRO_VERSION'):
            distro_version = line.partition('=')[2].strip('\"')
        elif line.startswith('OS_VERSION'):
            os_version = line.partition('=')[2].strip('\"')
        if distro_version and os_version:
            break
    return distro_version, os_version


def parse_distro_options():
    '''Read distro options settings from file.'''
    distro_mirror = None
    with open(f'{os.getcwd()}/distributions/{DISTRO_NAME}/options', mode='r', encoding='utf-8') as data:
        content = data.read()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('DISTRO_MIRROR'):
            distro_mirror = line.partition('=')[2].strip('\"')
            break
    return distro_mirror


def parse_builder_options(file):
    '''Read builder settings from file.'''
    with open(file, mode='r', encoding='utf-8') as data:
        content = data.read()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('SOURCES_DIR'):
            return line.partition('=')[2].strip('\"')
    return None


def get_packages(build_setup):
    pkg_list = []
    cmd_build = f'PROJECT={build_setup[0]} DEVICE={build_setup[1]} ARCH={build_setup[2]}'
    if build_setup[3]:
        cmd_build = f'{cmd_build} UBOOT_SYSTEM={build_setup[3]}'
    cmd_result = execute(f'{cmd_build} scripts/pkgjson | scripts/genbuildplan.py --hide-header --list-packages --build image')
    if cmd_result:
        for item in cmd_result.splitlines():
            pkg_url = None
            # get package details
            pkg_details = execute(f'{cmd_build} tools/pkginfo --strip {item}').strip()
            for line in pkg_details.splitlines():
                if line.startswith('PKG_URL'):
                    pkg_url = line.partition('=')[2].strip('"')
                    break
            # add package and filename to project list if not present
            if pkg_url and [item, pkg_url] not in pkg_list:
                pkg_list.append([item, pkg_url])
    return pkg_list


# build list of packages with desired versions to keep
def get_git_package_list():
    '''Create list of packages, their source package filenames, and URL to download for every setup in builds'''
    distro_mirror = parse_distro_options()
    if args.all:
        builds = builds_all
    elif args.builddirs:
        distro_version, os_version = parse_distro_version()
        builds = builds_all
        # remove entries without a build directory
        for build in list(builds):
            if not os.path.isdir(f'{os.getcwd()}/build.{DISTRO_NAME}-{build[1]}.{build[2]}-{os_version}-{distro_version}'):
                builds.remove(build)
    else:
        project = os.getenv('PROJECT')
        device = os.getenv('DEVICE')
        arch = os.getenv('ARCH')
        uboot_system = os.getenv('UBOOT_SYSTEM') if os.getenv('UBOOT_SYSTEM') else None
        if project and device and arch:
            builds = [[project, device, arch, uboot_system]]
        else:
            print('Error: Unknown build. Set PROJECT, DEVICE, ARCH and, if needed, UBOOT_SYSTEM or invoke with --all')
            sys.exit(1)

    pkg_list = []
    # this returns a list of lists with all the desired packages and URLs
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(get_packages, builds))
    if results:
        for pkg_set in results:
            for package in pkg_set:
                if package not in pkg_list:
                    pkg_list.append([package[0], package[1], f'{distro_mirror}/{package[0]}/{package[1]}'])
    return pkg_list


def generate_delete_list():
    '''Compare files in source dir against desired files for packages in git tree'''
    files_to_delete = ''
    # compare packages in sources directory against files in git tree
    if os.path.isdir(SOURCES_DIR) and PKG_LIST:
        # each directory is a package
        for package in os.listdir(SOURCES_DIR):
            active_pkg_list = ''
            if os.path.isdir(f'{SOURCES_DIR}/{package}'):
                for file in os.listdir(f'{SOURCES_DIR}/{package}'):
                    # skip auxilliary files
                    if file.endswith(('.url', '.sha256')):
                        continue
                    # test for file in use by git tree
                    for tree_entry in PKG_LIST:
                        if tree_entry[0] not in active_pkg_list:
                            active_pkg_list = f'{active_pkg_list} {tree_entry[0]}'
                        if package == tree_entry[0] and file != tree_entry[1]:
                            file_path = f'{SOURCES_DIR}/{package}/{file}'
                            if file_path not in files_to_delete:
                                files_to_delete = f'{files_to_delete}\n{file_path}' if files_to_delete else file_path
                            if os.path.isfile(f'{file_path}.url') and f'{file_path}.url' not in files_to_delete:
                                files_to_delete = f'{files_to_delete}\n{file_path}.url'
                            if os.path.isfile(f'{file_path}.sha256') and f'{file_path}.sha256' not in files_to_delete:
                                files_to_delete = f'{files_to_delete}\n{file_path}.sha256'
                            # end loop after package's source dir is evaluated
                            break
                # downloaded packages that are no longer in tree
                if package not in active_pkg_list:
                    file_path = f'{SOURCES_DIR}/{package}'
                    if file_path not in files_to_delete:
                        files_to_delete = f'{files_to_delete}\n{file_path}' if files_to_delete else file_path
    return files_to_delete


def prune_source_dir(verbose=True):
    purge_filepaths = generate_delete_list()
    if purge_filepaths:
        for file in purge_filepaths.splitlines():
            if verbose:
                print(file)
            if args.delete:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                else:
                    os.remove(file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='download-manager.py',
    description="""
    When invoked with clean, this prints a list of package names to delete.
    When invoked with mirror, this prints a list of package names and URLs to be added to a sources mirror.

    Each command considers one, some, or all project builds in determining these lists.
    Specify PROJECT=W DEVICE=X ARCH=Y UBOOT_SYSTEM=Z like other build commands to mirror to a single
    project build's files. Specify other options listed below to consider more than one project build.
    """)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-c', '--clean', action='store_true', \
                       help='Remove files from sources if no longer in the package tree.')
    mode.add_argument('-m', '--mirror', action='store_true', \
                       help='Output file list for adding to sources to match package tree requirements.')
    mode.add_argument('-s', '--sync', action='store_true', \
                       help='Run --clean and --mirror.')
    parser.add_argument('-a', '--all', action='store_true', \
                       help='Consider all project/devices when determining what files to keep in sources directory.')
    parser.add_argument('-b', '--builddirs', action='store_true', \
                       help='Filter build list used by --all to only include builds with a present project/device/arch build directory.')
    parser.add_argument('-e', '--export', action='store', nargs='?', \
                       help='Export list of package source files to keep to file.')
    parser.add_argument('-d', '--delete', action='store_true', \
                       help='Delete files in addition to listing them.')
    args = parser.parse_args()


    # generate list of current packages for comparison
    PKG_LIST = get_git_package_list()


    # CLEAN
    if args.clean or args.sync:
        # sources directory
        SOURCES_DIR = None
        # in tree git controlled options that may contain SOURCES_DIR
        if os.path.isfile(f'{os.getcwd()}/.libreelec/options'):
            SOURCES_DIR = parse_build_options(f'{os.getcwd()}/.libreelec/options')
        # global options in home may contain SOURCES_DIR
        if os.path.isfile(f'{os.getenv("HOME")}/.libreelec/options'):
            SOURCES_DIR = parse_builder_options(f'{os.getenv("HOME")}/.libreelec/options')
        # default SOURCES
        if not SOURCES_DIR:
            SOURCES_DIR = f'{os.getcwd()}/sources'
        # expands ~ to home dir
        SOURCES_DIR = os.path.expanduser(SOURCES_DIR)
        # expands $HOME to home dir
        SOURCES_DIR = os.path.expandvars(SOURCES_DIR)

        if not os.path.isdir(SOURCES_DIR):
            print(f'Error: Abort: Unable to find directory: {SOURCES_DIR}')
            sys.exit(1)

        if args.sync:
            prune_source_dir(verbose=False)
        else:
            prune_source_dir(verbose=True)


    # MIRROR
    if args.mirror or args.sync:
        # sanity check
        if args.export:
            export_path = args.export if args.export.startswith('/') else os.path.join(os.getcwd(), args.export)
            if os.path.isfile(export_path):
                print(f'Error: Export file already exists: {export_path}')
                sys.exit(1)


        # get package details to build a source repository mirror
        if args.export:
            if not os.path.isfile(export_path):
                with open(export_path, mode='w', encoding='utf-8') as export_file:
                    for package in PKG_LIST:
                        export_file.write(f'{package[0]} {package[1]} {package[2]}\n')
                print(f'Exported list of files to: {export_path}')
        else:
            for package in PKG_LIST:
                print(f'{package[0]} {package[1]} {package[2]}')
