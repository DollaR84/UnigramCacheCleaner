import os

import addonHandler
import config
import gui
from gui.settingsDialogs import SettingsPanel

import wx

from .types import CleaningPeriod


addonHandler.initTranslation()


LOCALAPPDATA = os.environ.get("LOCALAPPDATA")
UNIGRAM_CACHE_PATH = os.path.join(LOCALAPPDATA, r"Packages\38833FF26BA1D.UnigramPreview_g9c9v27vpyspw\LocalState\0")


confspec = {
    "unigram_cache_path1": f"string(default='{UNIGRAM_CACHE_PATH}')",
    "unigram_cache_path2": "string(default='')",
    "cleaning_period": "string(default='day')",
    "date_last_clean": "string(default='')",
}
config.conf.spec["UnigramCacheCleaner"] = confspec


class UCCSettings(SettingsPanel):
    title = "UnigramCacheCleaner"

    localisation_cleaning_period = {
        CleaningPeriod.DAY.value: _("cleaning once a day"),
        CleaningPeriod.WEEK.value: _("cleaning once a week"),
        CleaningPeriod.MONTH.value: _("cleaning once a month"),
    }

    def makeSettings(self, settingsSizer):
        settings_sizer_helper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        self.cleaning_period = settings_sizer_helper.addLabeledControl(
            _("cleaning period:"), wx.Choice,
            choices=list(self.localisation_cleaning_period.values())
        )
        self.cleaning_period.SetStringSelection(
            self.localisation_cleaning_period[config.conf["UnigramCacheCleaner"].get("cleaning_period")]
        )

        browse_text = _("Browse...")
        dir_dialog_title = _("Select a directory")
        _unigram_cache_path_default = UNIGRAM_CACHE_PATH

        for index in range(1, 3):
            group_sizer = wx.StaticBoxSizer(
                wx.VERTICAL, self,
                label=" ".join([_("Path to cache unigram folder"), str(index)]),
            )
            group_box = group_sizer.GetStaticBox()
            group_helper = settings_sizer_helper.addItem(gui.guiHelper.BoxSizerHelper(self, sizer=group_sizer))

            directory_path_helper = gui.guiHelper.PathSelectionHelper(group_box, browse_text, dir_dialog_title)
            directory_entry_control = group_helper.addItem(directory_path_helper)

            setattr(self, f"unigram_cache_path{index}", directory_entry_control.pathControl)
            getattr(self, f"unigram_cache_path{index}").Value = config.conf["UnigramCacheCleaner"].get(
                f"unigram_cache_path{index}", _unigram_cache_path_default
            )
            _unigram_cache_path_default = ""

    def get_key(self, data: dict, select_value: str):
        for key, value in data.items():
            if value == select_value:
                return key

    def onSave(self):
        config.conf["UnigramCacheCleaner"]["unigram_cache_path1"] = self.unigram_cache_path1.GetValue()
        config.conf["UnigramCacheCleaner"]["unigram_cache_path2"] = self.unigram_cache_path2.GetValue()
        config.conf["UnigramCacheCleaner"]["cleaning_period"] = self.get_key(
            self.localisation_cleaning_period, self.cleaning_period.GetStringSelection()
        )
