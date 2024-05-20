import logging
import math
import os


class Cleaner:

    _subfolders = [
        "animations", "documents",
        "music", "passport",
        "photos", "profile_photos",
        "secret", "secret_thumbnails",
        "stickers", "stories",
        "temp", "thumbnails",
        "video_notes", "videos",
        "voice", "wallpapers",
    ]

    def __init__(self, base_path: str):
        self.base_path = base_path

    def run(self) -> str:
        total_size = 0
        for subfolder in self._subfolders:
            try:
                size = self._process_subfolder(subfolder)
                total_size += size
            except Exception as err:
                logger = logging.getLogger()
                logger.error(f"Error process subfolder: {subfolder}")
                logger.error(err, exc_info=True)
        return self._process_size(total_size)

    def _process_subfolder(self, subfolder: str) -> int:
        total_size = 0
        folder = os.path.join(self.base_path, subfolder)
        if not os.path.exists(folder):
            return total_size

        files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]

        for file in files:
            file_path = os.path.join(folder, file)
            try:
                size = os.stat(file_path).st_size
                os.remove(file_path)
                total_size += size
            except Exception as err:
                logger = logging.getLogger()
                logger.error(f"Error remove file: {file_path}")
                logger.error(err, exc_info=True)

        return total_size

    def _process_size(self, size: int) -> str:
        suff = ["BB", "KB", "MB", "GB", "TB"]
        if size == 0:
            return f"0 {suff[0]}"

        pwr = math.floor(math.log(size, 1024))
        return f"{size / 1024 ** pwr:.2f} {suff[pwr]}"
