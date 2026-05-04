from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy.uix.screenmanager import NoTransition, ScreenManager
from kivy.uix.scrollview import ScrollView

from app import config
from app.database import init_db
from app.screens.cariler_screen import CarilerScreen
from app.screens.dashboard_screen import DashboardScreen
from app.screens.islemler_screen import IslemlerScreen
from app.screens.kasalar_screen import KasalarScreen
from app.screens.kategoriler_screen import KategorilerScreen
from app.screens.raporlar_screen import RaporlarScreen
from app.screens.yedek_screen import YedekScreen
from app.widgets import BG, PRIMARY, PRIMARY_LIGHT, WHITE, ACCENT, RoundedBox, btn, label


class AppScreenManager(ScreenManager):
    def app_refresh_all(self):
        for screen in self.screens:
            if hasattr(screen, "reload"):
                try:
                    screen.reload()
                except Exception:
                    pass


class YNBOnMuhasebeMobileApp(App):
    title = config.APP_NAME
    icon = str(config.ICON_PATH)

    def build(self):
        config.set_data_dir(Path(self.user_data_dir))
        init_db()

        Window.clearcolor = BG
        root = BoxLayout(orientation="vertical", spacing=0)
        root.add_widget(self._header())

        self.manager = AppScreenManager(transition=NoTransition())
        self.manager.add_widget(DashboardScreen(name="dashboard"))
        self.manager.add_widget(IslemlerScreen(name="islemler"))
        self.manager.add_widget(CarilerScreen(name="cariler"))
        self.manager.add_widget(KasalarScreen(name="kasalar"))
        self.manager.add_widget(KategorilerScreen(name="kategoriler"))
        self.manager.add_widget(RaporlarScreen(name="raporlar"))
        self.manager.add_widget(YedekScreen(name="yedek"))
        root.add_widget(self.manager)
        root.add_widget(self._nav())
        return root

    def _header(self):
        # Android'de bazı cihazlarda içerik status bar'a fazla yaklaşabiliyor.
        # Üst güvenli boşluk + daha büyük ikon ile başlık alanı toparlandı.
        safe_top = dp(10) if platform == "android" else 0
        outer = BoxLayout(
            size_hint_y=None,
            height=dp(104) + safe_top,
            padding=[dp(14), safe_top + dp(8), dp(14), dp(8)],
        )
        box = RoundedBox(
            orientation="horizontal",
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(12),
            bg_color=PRIMARY,
            border_color=PRIMARY,
            radius=20,
        )

        # Geniş logo telefonda küçülüyordu. Burada daha okunaklı kare ikon kullanıyoruz.
        logo_source = str(config.ICON_PATH if config.ICON_PATH.exists() else config.LOGO_PATH)
        if Path(logo_source).exists():
            box.add_widget(
                Image(
                    source=logo_source,
                    size_hint=(None, None),
                    width=dp(58),
                    height=dp(58),
                    allow_stretch=True,
                    keep_ratio=True,
                )
            )

        title_box = BoxLayout(orientation="vertical", spacing=dp(2))
        title_box.add_widget(label("YNB Ön Muhasebe", size=20, bold=True, color=WHITE, height=34))
        title_box.add_widget(label("Gelir • Gider • Cari • Kasa Takibi", size=12, color=(0.80, 0.87, 1, 1), height=24))
        box.add_widget(title_box)
        outer.add_widget(box)
        return outer

    def _nav(self):
        # Alt menü artık ekrana sığacak şekilde 5 ana butona indirildi.
        # Kategori/Rapor/Yedek, Diğer menüsü altından açılır.
        outer = BoxLayout(size_hint_y=None, height=dp(62), padding=[dp(8), dp(5), dp(8), dp(6)])
        shell = RoundedBox(
            orientation="horizontal",
            bg_color=WHITE,
            border_color=(0.86, 0.89, 0.94, 1),
            radius=22,
            padding=[dp(6), dp(5), dp(6), dp(5)],
            spacing=dp(5),
        )
        items = [
            ("Ana", "dashboard"),
            ("İşlem", "islemler"),
            ("Cari", "cariler"),
            ("Kasa", "kasalar"),
        ]
        for text, screen in items:
            b = btn(text, lambda _b, s=screen: self.go(s), bg=PRIMARY_LIGHT, fg=WHITE, height=42)
            b.size_hint_x = 1
            shell.add_widget(b)

        more_btn = btn("Diğer", lambda _b: self._open_more_menu(), bg=PRIMARY_LIGHT, fg=WHITE, height=42)
        more_btn.size_hint_x = 1
        shell.add_widget(more_btn)

        outer.add_widget(shell)
        return outer

    def _open_more_menu(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(14), dp(14), dp(14), dp(14)])
        popup = Popup(
            title="Diğer Menü",
            content=content,
            size_hint=(0.86, None),
            height=dp(270),
            auto_dismiss=True,
        )
        for text, screen in [("Kategoriler", "kategoriler"), ("Raporlar", "raporlar"), ("Yedek", "yedek")]:
            b = btn(text, lambda _b, s=screen, p=popup: (p.dismiss(), self.go(s)), bg=PRIMARY_LIGHT, fg=WHITE, height=48)
            content.add_widget(b)
        popup.open()

    def go(self, screen_name):
        self.manager.current = screen_name


if __name__ == "__main__":
    YNBOnMuhasebeMobileApp().run()
