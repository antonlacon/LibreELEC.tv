# SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

import shutil
import tarfile
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

import xbmcaddon
import xbmcgui


STEAMLINK_VERSION = "@STEAMLINK_VERSION@"
STEAMLINK_HASH = "@STEAMLINK_HASH@"
STEAMLINK_TARBALL_NAME = f"steamlink-rpi-trixie-arm64-{STEAMLINK_VERSION}.tar.gz"
STEAMLINK_URL = f"http://media.steampowered.com/steamlink/rpi/trixie/arm64/{STEAMLINK_TARBALL_NAME}"


# -----------------------------
# Data structs
# -----------------------------

@dataclass
class SteamlinkPaths:
    addon: Path
    steamlink: Path
    libs: Path
    prep_flag: Path
    version_file: Path
    bin: Path

    @classmethod
    def from_addon(cls, addon_dir: Path):
        return cls(
            addon=addon_dir,
            steamlink=addon_dir / "steamlink",
            libs=addon_dir / "system-libs",
            prep_flag=addon_dir / "prep.ok",
            version_file=addon_dir / "steamlink" / "version.txt",
            bin=addon_dir / "bin"
        )

# -----------------------------
# Utility helpers
# -----------------------------

def execute(cmd: list[str]) -> str:
    """Run a command and return stdout, raising on failure."""
    result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False
        )
    return result.stdout.decode()


def read_text(path: Path) -> str:
    """Read entire file as text."""
    return path.read_text()


def safe_extract_tar(tar_path: Path, target_dir: Path):
    """Safely extract tarball without allowing path traversal, preserving modes and links."""
    with tarfile.open(tar_path) as tar:
        safe_members = []
        base = target_dir.resolve()

        for member in tar.getmembers():
            name = member.name

            # Skip absolute paths or Windows drive prefixes
            if name.startswith("/") or ":" in name:
                continue

            dest = (target_dir / name).resolve()
            if str(dest).startswith(str(base)):
                safe_members.append(member)

        # Pre-create parent directories once
        dirs = set()
        for m in safe_members:
            d = (target_dir / m.name).parent
            dirs.add(d)
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        buf = bytearray(131072)
        view = memoryview(buf)

        for member in safe_members:
            # Hoist attributes
            name = member.name
            mode = member.mode
            is_dir = member.isdir()
            is_sym = member.issym()
            is_hard = member.islnk()
            linkname = member.linkname if (is_sym or is_hard) else None

            out_path = target_dir / name

            # Directories
            if is_dir:
                out_path.mkdir(parents=True, exist_ok=True)
                try:
                    out_path.chmod(mode)
                except OSError:
                    pass
                continue

            # Symlinks
            if is_sym:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                if out_path.exists() or out_path.is_symlink():
                    out_path.unlink()
                out_path.symlink_to(linkname)
                continue

            # Hardlinks
            if is_hard:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                target = target_dir / linkname
                if out_path.exists():
                    out_path.unlink()
                os.link(target, out_path)
                continue

            # Regular files
            src = tar.extractfile(member)
            if src is None:
                continue

            out_path.parent.mkdir(parents=True, exist_ok=True)

            with out_path.open("wb") as out:
                readinto = src.readinto
                write = out.write

                while True:
                    chunk = readinto(buf)
                    if not chunk:
                        break
                    write(view[:chunk])

            try:
                out_path.chmod(mode)
            except OSError:
                pass


def sha256_file(path: Path) -> str:
    """Compute SHA256 hash of a file in 32KB chunks."""
    hasher = sha256()
    buf = bytearray(32768)
    view = memoryview(buf)
    with path.open("rb") as f:
        readinto = f.readinto
        while True:
            chunk = readinto(buf)
            if not chunk:
                break
            hasher.update(view[:chunk])
    return hasher.hexdigest()


# -----------------------------
# UI helpers
# -----------------------------

def notify(title: str, message:str, level=xbmcgui.NOTIFICATION_INFO, duration=5000):
    xbmcgui.Dialog().notification(title, message, level, duration)


@contextmanager
def progress(title: str, message: str):
    bar = xbmcgui.DialogProgress()
    bar.create(title, message)
    try:
        yield bar
    finally:
        bar.close()


# -----------------------------
# Download
# -----------------------------

def download_file(url: str, dest: Path, expected_hash: str):
    """Download a file with progress and verify its hash."""
    if len(expected_hash) != 64:
        notify("Steam Link", "Invalid SHA256 hash format", xbmcgui.NOTIFICATION_ERROR)
        return False


    with progress("File Download", f"Downloading {dest.name}...") as bar:
        buf = bytearray(32768)
        view = memoryview(buf)
        last_pct = -1

        def progress_hook(downloaded, total_size):
            nonlocal last_pct
            if total_size <= 0:
                bar.update(0, "Filesize Unknown")
                return
            pct = int(downloaded * 100 / total_size)
            # Update progress bar every 5%
            if pct // 5 != last_pct // 5:
                last_pct = pct
                bar.update(pct)

        try:
            with urlopen(url) as response, dest.open("wb") as out:
                total = response.length or -1
                downloaded = 0

                readinto = response.readinto
                write = out.write

                while True:
                    chunk = readinto(buf)
                    if not chunk:
                        break
                    write(view[:chunk])
                    downloaded += chunk
                    progress_hook(downloaded, total)

        except Exception:
            notify("Steam Link", "Download failed", xbmcgui.NOTIFICATION_ERROR)
            return False

    # Verify hash
    actual_hash = sha256_file(dest)
    if actual_hash != expected_hash:
        notify("Steam Link", "Download file failed integrity check", xbmcgui.NOTIFICATION_ERROR)
        if dest.exists():
            dest.unlink()
        return False

    return True


# -----------------------------
# Steamlink preparation
# -----------------------------

def get_install_state(paths: SteamlinkPaths) -> str:
    if not paths.prep_flag.exists():
        return "missing"
    if not paths.version_file.exists():
        return "missing"

    try:
        installed = read_text(paths.version_file).strip()
    except Exception:
        return "corrupt"

    if installed != STEAMLINK_VERSION:
        return "outdated"

    return "current"


def prepare_steamlink(paths: SteamlinkPaths):
    """Prepare system libraries and flags before launching Steam Link."""
    if not paths.libs.is_dir():
        raise RuntimeError("Missing system-libs directory")

    paths.steamlink.mkdir(parents=True, exist_ok=True)
    lib_target = paths.steamlink / "lib"
    lib_target.mkdir(parents=True, exist_ok=True)

    for file in paths.libs.iterdir():
        link = lib_target / file.name
        if not link.exists():
            link.symlink_to(file)

    (paths.steamlink / ".ignore_arch").touch()
    paths.prep_flag.touch()


# -----------------------------
# Main launcher
# -----------------------------

def start_steamlink():
    paths = SteamlinkPaths.from_addon(Path(xbmcaddon.Addon().getAddonInfo("path")))
    state = get_install_state(paths)

    if state in ("missing", "corrupt", "outdated"):
        shutil.rmtree(paths.steamlink, ignore_errors=True)
        paths.prep_flag.unlink(missing_ok=True)

        # Download steamlink package
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tarball = tmp_path / STEAMLINK_TARBALL_NAME

            dl_result = download_file(STEAMLINK_URL, tarball, STEAMLINK_HASH)
            if not dl_result:
                return

            try:
                safe_extract_tar(tarball, paths.addon)
            except Exception:
                notify("Steam Link", "Failed to extract Steam Link package", xbmcgui.NOTIFICATION_ERROR)
                return

            try:
                prepare_steamlink(paths)
            except Exception:
                notify("Steam Link", "Failed to prepare Steam Link", xbmcgui.NOTIFICATION_ERROR)

    # Launch Steam Link
    notify("Steam Link", "Starting Steam Link")
    try:
        execute(["systemd-run", str(paths.bin / "steamlink-start.sh")])
    except subprocess.CalledProcessError as e:
        notify("Steam Link", "Failed to start Steam Link")


start_steamlink()
