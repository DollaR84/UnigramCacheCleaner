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
    "unigram_cache_path": f"string(default='{UNIGRAM_CACHE_PATH}')",
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

        group_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Path to cache unigram folder"))
        group_box = group_sizer.GetStaticBox()
        group_helper = settings_sizer_helper.addItem(gui.guiHelper.BoxSizerHelper(self, sizer=group_sizer))

        browse_text = _("Browse...")
        dir_dialog_title = _("Select a directory")
        directory_path_helper = gui.guiHelper.PathSelectionHelper(group_box, browse_text, dir_dialog_title)
        directory_entry_control = group_helper.addItem(directory_path_helper)
        
        self.unigram_cache_path = directory_entry_control.pathControl
        self.unigram_cache_path.Value = config.conf["UnigramCacheCleaner"].get("unigram_cache_path", UNIGRAM_CACHE_PATH)

    def get_key(self, data: dict, select_value: str):
        for key, value in data.items():
            if value == select_value:
                return key

    def onSave(self):
        config.conf["UnigramCacheCleaner"]["unigram_cache_path"] = self.unigram_cache_path.GetValue()
        config.conf["UnigramCacheCleaner"]["cleaning_period"] = self.get_key(
            self.localisation_cleaning_period, self.cleaning_period.GetStringSelection()
        )
