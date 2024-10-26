from enum import Enum


class CleaningPeriod(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class Subfolders(Enum):
    Animations = "animations"
    Documents = "documents"
    Music = "music"
    Passport = "passport"
    Photos = "photos"
    ProfilePhotos = "profile_photos"
    Secret = "secret"
    SecretThumbnails = "secret_thumbnails"
    Stickers = "stickers"
    Stories = "stories"
    Temp = "temp"
    Thumbnails = "thumbnails"
    VideoNotes = "video_notes"
    Videos = "videos"
    Voice = "voice"
    Wallpapers = "wallpapers"
