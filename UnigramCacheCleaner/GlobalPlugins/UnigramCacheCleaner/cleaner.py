import math
import os

from logHandler import log

from .settings import UCCSettings

from .types import Subfolders


class Cleaner:

    def __init__(self, base_path1: str, base_path2: str):
        self.base_paths = [base_path1]
        if base_path2:
            self.base_paths.append(base_path2)

    def run(self) -> str:
        total_size = 0
        for folder in self.base_paths:
            if not os.path.exists(folder):
                log.error(f"Error not exists base folder: {folder}")
                continue

            try:
                if self.need_clear_base_path(folder):
                    total_size += self.clear_folder(folder)
            except Exception as err:
                log.error(f"Error process base folder: {folder}")
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

    def need_clear_base_path(self, folder: str) -> bool:
        default_paths = [UCCSettings.default_cache_path_store, UCCSettings.default_cache_path_beta]
        if folder in default_paths:
            return False

        subfolders = [subfolder for subfolder in os.listdir(folder) if os.path.isdir(os.path.join(folder, subfolder))]
        if list(set(subfolders) & set([subfolder.value for subfolder in Subfolders])):
            return False

        files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]
        for file in files:
            if "db." in file or "sqlite" in file:
                return False

        return True

    def clear_folder(self, folder: str) -> int:
        total_size = 0
        files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]

        for file in files:
            file_path = os.path.join(folder, file)
            try:
                size = os.stat(file_path).st_size
                os.remove(file_path)
                total_size += size
            except Exception as err:
                log.error(f"Error remove file: {file_path}")
                log.error(err, exc_info=True)

        return total_size

    def _process_subfolder(self, subfolder: Subfolders) -> int:
        total_size = 0
        for base_path in self.base_paths:
            folder = os.path.join(base_path, subfolder.value)
            if not os.path.exists(folder):
                continue

            total_size += self.clear_folder(folder)
        return total_size

    def _process_size(self, size: int) -> str:
        suff = ["BB", "KB", "MB", "GB", "TB"]
        if size == 0:
            return f"0 {suff[0]}"

        pwr = math.floor(math.log(size, 1024))
        return f"{size / 1024 ** pwr:.2f} {suff[pwr]}"
