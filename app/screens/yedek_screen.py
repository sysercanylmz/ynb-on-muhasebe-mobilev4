from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from app import config
from app.backup import BackupError, create_backup, list_backup_files, restore_backup
from app.screens.base import RefreshableScreen
from app.widgets import DANGER, PRIMARY, PRIMARY_LIGHT, SUCCESS, btn, card, confirm, form_input, form_spinner, label, scroll_container, show_message, title_label


class YedekScreen(RefreshableScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll, self.content = scroll_container()
        self.add_widget(self.scroll)
        self.backup_spinner = None
        self.path_input = None

    def on_pre_enter(self, *_args):
        self.reload()

    def reload(self):
        self.content.clear_widgets()
        self.content.add_widget(title_label("Yedekleme"))

        info = card(padding=10, spacing=4)
        info.add_widget(label("[b]Bu ekran neyi yedekler?[/b]", size=15, height=28))
        info.add_widget(label("Veritabanı, gelir/gider kayıtları, cariler, kasalar, kategoriler ve belge/fiş/fatura dosyaları ZIP olarak yedeklenir.", size=13, height=56))
        info.add_widget(label(f"Uygulama veri yolu:\n{config.DATA_DIR}", size=11, height=54))
        self.content.add_widget(info)

        self.content.add_widget(btn("Yedek Al", self._backup_now, bg=SUCCESS, height=48))

        note = card(padding=10, spacing=4)
        note.add_widget(label("Yedek mümkünse telefonun [b]Download/YNB_On_Muhasebe_Yedek[/b] klasörüne kaydedilir. Oraya yazılamazsa uygulama içi yedek klasörüne kaydedilir.", size=13, height=72))
        self.content.add_widget(note)

        self.content.add_widget(title_label("Yedekten Geri Yükle"))

        backups = [str(path) for path in list_backup_files()]
        if backups:
            self.backup_spinner = form_spinner(backups, text=backups[0])
        else:
            self.backup_spinner = form_spinner(["Yedek bulunamadı"], text="Yedek bulunamadı")
        self.content.add_widget(self.backup_spinner)

        self.path_input = form_input("Yedek dosyası yolu", text=backups[0] if backups else "")
        self.content.add_widget(self.path_input)

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        row.add_widget(btn("Listeyi Yenile", lambda _b: self.reload(), bg=PRIMARY_LIGHT, height=46))
        row.add_widget(btn("Yolu Forma Al", self._copy_selected_to_input, bg=PRIMARY, height=46))
        self.content.add_widget(row)

        self.content.add_widget(btn("Seçili Yedeği Geri Yükle", self._restore_selected, bg=DANGER, height=48))

        warn = card(padding=10, spacing=4)
        warn.add_widget(label("[b]Dikkat:[/b] Geri yükleme mevcut verinin yerine geçer. Sistem önce mevcut veritabanının güvenlik kopyasını uygulama klasörüne alır.", size=13, height=70))
        self.content.add_widget(warn)

    def _backup_now(self, *_args):
        try:
            path = create_backup()
            show_message("Yedek Alındı", f"Yedek başarıyla oluşturuldu:\n\n{path}")
            self.reload()
        except BackupError as exc:
            show_message("Yedek Hatası", str(exc))

    def _copy_selected_to_input(self, *_args):
        if not self.path_input or not self.backup_spinner:
            return
        if self.backup_spinner.text and self.backup_spinner.text != "Yedek bulunamadı":
            self.path_input.text = self.backup_spinner.text

    def _restore_selected(self, *_args):
        if not self.path_input:
            return
        path = self.path_input.text.strip()
        if not path or path == "Yedek bulunamadı":
            show_message("Yedek Seçilmedi", "Geri yüklenecek ZIP yedeğini seç veya dosya yolunu yaz.")
            return

        def do_restore():
            try:
                restore_backup(Path(path))
                show_message("Geri Yükleme Tamam", "Yedek geri yüklendi. Ana sayfaya dönüp ekranları yenileyebilirsin.")
                app = self.manager
                if hasattr(app, "app_refresh_all"):
                    app.app_refresh_all()
            except BackupError as exc:
                show_message("Geri Yükleme Hatası", str(exc))

        confirm("Yedeği Geri Yükle", "Mevcut kayıtların yerine bu yedek yüklenecek. Devam edilsin mi?", do_restore)
