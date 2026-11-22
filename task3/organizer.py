"""Organize a directory by file extension with a preview mode."""

import argparse
import logging
import os
import stat
from pathlib import Path

EXTENSIONS = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".xls", ".xlsx", ".csv", ".pptx", ".odt"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".heic", ".tiff"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"},
    "Archives": {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz", ".tar.gz", ".tar.bz2", ".tar.xz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".json", ".sql", ".ps1", ".sh"},
}
CATEGORY = {extension: name for name, extensions in EXTENSIONS.items()
            for extension in extensions}
CATEGORY_NAMES = {name.casefold() for name in EXTENSIONS}
LOG = logging.getLogger(__name__)


def category_for(path):
    suffix = "".join(path.suffixes[-2:]).lower()
    if suffix in CATEGORY:
        return CATEGORY[suffix], suffix
    suffix = path.suffix.lower()
    return CATEGORY.get(suffix), suffix


def is_reparse_point(info):
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def move_without_overwriting(source, destination):
    # Windows rename fails on existing destinations. POSIX rename can replace
    # them, so reserve the destination atomically by creating a hard link.
    if os.name == "nt":
        source.rename(destination)
        return
    os.link(source, destination, follow_symlinks=False)
    try:
        source.unlink()
    except OSError:
        destination.unlink()
        raise


def place_file(source, folder, suffix, apply, reserved):
    if apply:
        folder.mkdir(exist_ok=True)
    if os.path.lexists(folder):
        info = folder.lstat()
        if is_reparse_point(info) or not stat.S_ISDIR(info.st_mode):
            raise OSError(f"Category path must be a real directory: {folder}")
    stem = source.name[:-len(suffix)]
    extension = source.name[-len(suffix):]
    index = 0
    while True:
        name = source.name if index == 0 else f"{stem} ({index}){extension}"
        destination = folder / name
        index += 1
        if destination in reserved or os.path.lexists(destination):
            continue
        if apply:
            try:
                move_without_overwriting(source, destination)
            except FileExistsError:
                continue
        else:
            reserved.add(destination)
        return destination


def organize(root, recursive, apply):
    relocated = skipped = failed = 0
    pending = [root]
    reserved = set()
    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as entries:
                children = sorted(entries, key=lambda entry: entry.name.casefold())
        except OSError as error:
            LOG.error("Cannot scan %s: %s", directory, error)
            failed += 1
            continue

        for entry in children:
            source = Path(entry.path)
            try:
                info = entry.stat(follow_symlinks=False)
                if is_reparse_point(info):
                    skipped += 1
                    LOG.info("Skipped link or junction %s", source)
                    continue
                if stat.S_ISDIR(info.st_mode):
                    if recursive and entry.name.casefold() not in CATEGORY_NAMES:
                        pending.append(source)
                    continue
                category, suffix = category_for(source)
                if not stat.S_ISREG(info.st_mode) or not category or source == Path(__file__).resolve():
                    skipped += 1
                    LOG.info("Skipped %s", source)
                    continue
                destination = place_file(source, directory / category, suffix, apply, reserved)
                LOG.info("%s %s -> %s", "Moved" if apply else "Would move", source, destination)
                relocated += 1
            except OSError as error:
                LOG.error("Cannot process %s: %s", source, error)
                failed += 1

    print(f"{'Moved' if apply else 'Would move'}: {relocated} | Skipped: {skipped} | Errors: {failed}")
    return int(failed > 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--recursive", action="store_true", help="Organize nested directories in place")
    parser.add_argument("--apply", action="store_true", help="Move files. The default previews changes")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        directory = args.directory.absolute()
        if is_reparse_point(directory.lstat()) or not directory.is_dir():
            parser.error("Provide a real directory, without a link or junction at the target.")
        return organize(directory.resolve(), args.recursive, args.apply)
    except OSError as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
