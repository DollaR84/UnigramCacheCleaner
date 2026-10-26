import math
import os
import shutil
import stat
import sys
from typing import Optional

from logHandler import log

from .settings import UCCSettings

from .types import Subfolders


def _norm(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


def _on_rm_error(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


class Cleaner:

    def __init__(self, base_path1: str, base_path2: Optional[str] = None):
        self.base_paths = [base_path1]
        if base_path2 and _norm(base_path2) != _norm(base_path1):
            self.base_paths.append(base_path2)

        self._cache_paths = []

    def run(self) -> str:
        total_size = 0
        self._cache_paths = []
        for folder in self.base_paths:
            if not os.path.exists(folder):
                log.error(f"Error not exists base folder: {folder}")
                continue

            if self._is_dangerous(folder):
                log.error(f"Refusing to clean dangerous folder: {folder}")
                continue

            is_cache = self._is_unigram_cache(folder)
            if is_cache:
                self._cache_paths.append(folder)

            try:
                if not is_cache:
                    total_size += self.clear_folder(folder, remove_dirs=True)
            except Exception as err:
                log.error(f"Error process base folder: {folder}")
                log.error(err, exc_info=True)

            try:
                file_path = os.path.join(folder, "db.sqlite")
                if UCCSettings.get_file_db_setting() and os.path.exists(file_path):
                    size = os.stat(file_path).st_size
                    os.remove(file_path)
                    total_size += size
            except Exception as err:
                log.error(err, exc_info=True)

        for subfolder in Subfolders:
            if not UCCSettings.get_subfolder_setting(subfolder):
                continue

            try:
                total_size += self._process_subfolder(subfolder)
            except Exception as err:
                log.error(f"Error process subfolder: {subfolder.value}")
                log.error(err, exc_info=True)

        return self._process_size(total_size)

    def _is_unigram_cache(self, folder: str) -> bool:
        default_paths = [_norm(UCCSettings.default_cache_path_store), _norm(UCCSettings.default_cache_path_beta)]
        if _norm(folder) in default_paths:
            return True

        try:
            entries = os.listdir(folder)
        except OSError:
            return True
        for name in entries:
            if name.lower().startswith("db.sqlite") and os.path.isfile(os.path.join(folder, name)):
                return True

        known = {s.value.lower() for s in Subfolders}
        found = sum(1 for name in entries if name.lower() in known and os.path.isdir(os.path.join(folder, name)))
        return found >= 2

    def _is_dangerous(self, folder: str) -> bool:
        p = _norm(folder)
        home = _norm(os.path.expanduser("~"))
        return p == os.path.splitdrive(p)[0] + os.sep or p == home

    def _get_dir_size(self, path: str) -> int:
        total = 0
        for root, _, files in os.walk(path):
            for name in files:
                try:
                    total += os.lstat(os.path.join(root, name)).st_size
                except OSError:
                    pass
        return total

    def clear_folder(self, folder: str, remove_dirs: bool = False) -> int:
        total_size = 0
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            try:
                if os.path.islink(path) or os.path.isfile(path):
                    size = os.lstat(path).st_size
                    os.remove(path)
                elif remove_dirs and os.path.isdir(path):
                    size = self._get_dir_size(path)
                    if sys.version_info >= (3, 12):
                        shutil.rmtree(path, onexc=_on_rm_error)
                    else:
                        shutil.rmtree(path, onerror=_on_rm_error)
                else:
                    continue
                total_size += size
            except Exception as err:
                log.error(f"Error remove: {path}")
                log.error(err, exc_info=True)
        return total_size

    def _process_subfolder(self, subfolder: Subfolders) -> int:
        total_size = 0
        for base_path in self._cache_paths:
            folder = os.path.join(base_path, subfolder.value)
            if not os.path.exists(folder):
                continue

            total_size += self.clear_folder(folder)
        return total_size

    def _process_size(self, size: int) -> str:
        suff = ["BB", "KB", "MB", "GB", "TB"]
        if size == 0:
            return f"0 {suff[0]}"

        pwr = min((size.bit_length() - 1) // 10, len(suff) - 1)
        return f"{size / 1024 ** pwr:.2f} {suff[pwr]}"
