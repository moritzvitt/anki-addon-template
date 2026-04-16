from __future__ import annotations

from aqt import mw
from aqt.qt import QWidget

from .config_dialog import open_config_dialog
from .theme_core import (
    GLOBAL_STYLING_PROVIDER_ATTR,
    GLOBAL_STYLING_THEME_CHOICE_ATTR,
    build_dialog_stylesheet,
    build_web_theme_css,
    is_theme_enabled,
    normalize_theme_id,
)
from . import shared_menu


ADDON_MENU_NAME = "Global Styling"


class GlobalStylingProvider:
    def theme_id(self) -> str | None:
        if mw is None:
            return None
        config = mw.addonManager.getConfig(__name__) or {}
        theme_id = normalize_theme_id(str(config.get("theme_preset") or None))
        if not is_theme_enabled(theme_id):
            return None
        return theme_id

    def apply_dialog_theme(self, widget: QWidget) -> None:
        theme_id = self.theme_id()
        if theme_id is None:
            widget.setStyleSheet("")
            return
        widget.setStyleSheet(build_dialog_stylesheet(theme_id, widget.palette()))

    def build_web_theme_css(self, widget: QWidget, selector: str) -> str:
        return build_web_theme_css(self.theme_id(), widget.palette(), selector)


def _install_provider() -> None:
    provider = GlobalStylingProvider()
    setattr(mw, GLOBAL_STYLING_PROVIDER_ATTR, provider)
    setattr(mw, GLOBAL_STYLING_THEME_CHOICE_ATTR, provider.theme_id())


def register() -> None:
    if mw is None:
        return

    _install_provider()
    shared_menu.add_action_to_addon_menu(
        addon_name=ADDON_MENU_NAME,
        action_text="Settings",
        callback=open_config_dialog,
    )
    mw.addonManager.setConfigAction(__name__, open_config_dialog)
