import calendar
from datetime import datetime, timedelta
import logging
import os

import config
import addonHandler
import globalPluginHandler
import gui
import scriptHandler
import ui

import wx

from .cleaner import Cleaner

from .settings import UCCSettings, UNIGRAM_CACHE_PATH

from .types import CleaningPeriod


addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "UnigramCacheCleaner"

    size_suff = {
        "BB": _("bytes"),
        "KB": _("kilobytes"),
        "MB": _("megabytes"),
        "GB": _("gigabytes"),
        "TB": _("terabytes"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(UCCSettings)

        unigram_cache_path = config.conf["UnigramCacheCleaner"].get("unigram_cache_path", UNIGRAM_CACHE_PATH)
        self.cleaner = Cleaner(unigram_cache_path)

        self.process = wx.CallLater(60 * 1000, self.start_checker)

    def start_checker(self):
        if self.check_need_clear():
            self.run()
            self.save_date_last_clean()
        self.process = None

    def run(self):
        size_suff = self.cleaner.run()
        size, suff = size_suff[:-3], self.size_suff.get(size_suff[-2:], "")
        message = " ".join([_("cleared from unigram cache"), size, suff])
        ui.message(message)

    def check_need_clear(self):
        cleaning_period = config.conf["UnigramCacheCleaner"].get("cleaning_period", CleaningPeriod.DAY.value)
        date_last_clean = config.conf["UnigramCacheCleaner"].get("date_last_clean", "")

        if not date_last_clean:
            return True

        now = datetime.now()
        date_last_clean = datetime.strptime(date_last_clean, "%d.%m.%Y")
        date_passed = now - date_last_clean

        if CleaningPeriod.DAY.value == cleaning_period:
            return date_passed.days > 0

        if CleaningPeriod.WEEK.value == cleaning_period:
            return date_passed.days >= 7

        if CleaningPeriod.MONTH.value == cleaning_period:
            month_days = calendar.monthrange(date_last_clean.year, date_last_clean.month)[1]
            date_clean = date_last_clean + timedelta(days=month_days)
            return date_clean > now

        return False

    def save_date_last_clean(self):
        now = datetime.now()
        now_str = now.strftime("%d.%m.%Y")
        config.conf["UnigramCacheCleaner"]["date_last_clean"] = now_str

    @scriptHandler.script(
        description=_("Manual clean cache"),
        gesture="kb:NVDA+SHIFT+C"
    )
    def script_manual_clean(self, gesture):
        self.run()
