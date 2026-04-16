from __future__ import annotations

from aqt import mw
from aqt.qt import QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget
from aqt.utils import showInfo

from .theme_core import (
    GLOBAL_STYLING_THEME_CHOICE_ATTR,
    build_dialog_stylesheet,
    is_theme_enabled,
    normalize_theme_id,
    theme_label,
    theme_presets,
)


def _addon_name() -> str:
    return __name__.split(".", 1)[0]


def _load_config() -> dict[str, object]:
    config = mw.addonManager.getConfig(_addon_name()) or {}
    if "theme_preset" not in config:
        config["theme_preset"] = "off"
    return config


class GlobalStylingConfigDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent or mw)
        self.setWindowTitle("Global Styling")
        self.resize(620, 280)

        self._config = _load_config()
        self._preset_combo = QComboBox(self)
        self._description = QLabel(self)
        self._description.setWordWrap(True)
        self._preview = QLabel(self)
        self._preview.setWordWrap(True)
        self._preview.setMargin(14)

        layout = QVBoxLayout(self)
        intro = QLabel(
            "Choose a shared visual style for your Moritz add-ons. "
            "Add-ons that support Global Styling will use this theme automatically, "
            "while add-ons without support keep their normal local styling."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self._preset_combo)
        layout.addWidget(self._description)
        layout.addWidget(self._preview)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        for preset in theme_presets():
            self._preset_combo.addItem(preset.label, preset.theme_id)
        current_theme = normalize_theme_id(str(self._config.get("theme_preset") or "off"))
        self._preset_combo.setCurrentIndex(max(0, self._preset_combo.findData(current_theme)))
        self._preset_combo.currentIndexChanged.connect(self._refresh_preview)

        self._refresh_preview()

    def _refresh_preview(self) -> None:
        theme_id = normalize_theme_id(self._preset_combo.currentData())
        preset = next(p for p in theme_presets() if p.theme_id == theme_id)
        self._description.setText(preset.description)
        self._preview.setText(
            f"<b>{preset.label}</b><br>"
            "Dialogs, settings panes, and supported home-screen widgets will use this shared look."
        )
        if is_theme_enabled(theme_id):
            self.setStyleSheet(build_dialog_stylesheet(theme_id, self.palette()))
        else:
            self.setStyleSheet("")

    def _save(self) -> None:
        theme_id = normalize_theme_id(self._preset_combo.currentData())
        self._config["theme_preset"] = theme_id
        mw.addonManager.writeConfig(_addon_name(), self._config)
        setattr(mw, GLOBAL_STYLING_THEME_CHOICE_ATTR, theme_id)
        if is_theme_enabled(theme_id):
            message = f"Global Styling theme set to {theme_label(theme_id)}."
        else:
            message = "Global Styling turned off. Supported add-ons will use their own local styling again."
        showInfo(message, parent=self)
        self.accept()


def open_config_dialog() -> None:
    dialog = GlobalStylingConfigDialog(parent=mw)
    dialog.exec()
