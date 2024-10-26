import os

import addonHandler
import config
import gui
from gui.settingsDialogs import SettingsPanel

import wx

from .types import CleaningPeriod, Subfolders


addonHandler.initTranslation()


class UCCSettings(SettingsPanel):
    title = "UnigramCacheCleaner"

    localisation_cleaning_period = {
        CleaningPeriod.DAY.value: _("cleaning once a day"),
        CleaningPeriod.WEEK.value: _("cleaning once a week"),
        CleaningPeriod.MONTH.value: _("cleaning once a month"),
    }

    local_appdata = os.environ.get("LOCALAPPDATA")

    @classmethod
    @property
    def default_cache_path_store(cls) -> str:
        return os.path.join(cls.local_appdata, r"Packages\38833FF26BA1D.UnigramPreview_g9c9v27vpyspw\LocalState\0")

    @classmethod
    @property
    def default_cache_path_beta(cls) -> str:
        return os.path.join(cls.local_appdata, r"Packages\TelegramFZ-LLC.Unigram_1vfw5zm9jmzqy\LocalState\0")

    @classmethod
    def get_subfolder_setting(cls, subfolder: Subfolders) -> bool:
        return config.conf["UnigramCacheCleaner"].get(f"subfolder_{subfolder.value}", True)

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

        for index, default_path in zip(range(1, 3), (self.default_cache_path_store, self.default_cache_path_beta,)):
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
                f"unigram_cache_path{index}", default_path
            )

        group_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Subdirectories to clean up:"))
        group_box = group_sizer.GetStaticBox()
        group_helper = settings_sizer_helper.addItem(gui.guiHelper.BoxSizerHelper(self, sizer=group_sizer))

        self.subfolder_controls = {}
        for subfolder in Subfolders:
            subfolder_ctrl = group_helper.addItem(wx.CheckBox(self, label=subfolder.value))
            subfolder_ctrl.SetValue(self.get_subfolder_setting(subfolder))
            self.subfolder_controls[subfolder] = subfolder_ctrl

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

        for subfolder in Subfolders:
            subfolder_ctrl = self.subfolder_controls.get(subfolder)
            if not subfolder_ctrl:
                continue

            config.conf["UnigramCacheCleaner"][f"subfolder_{subfolder.value}"] = subfolder_ctrl.IsChecked()


confspec = {
    "unigram_cache_path1": f"string(default='{UCCSettings.default_cache_path_store}')",
    "unigram_cache_path2": f"string(default='{UCCSettings.default_cache_path_beta}')",
    "cleaning_period": "string(default='day')",
    "date_last_clean": "string(default='')",
}

for subfolder in Subfolders:
    confspec[f"subfolder_{subfolder.value}"] = "boolean(default=True)"

config.conf.spec["UnigramCacheCleaner"] = confspec
