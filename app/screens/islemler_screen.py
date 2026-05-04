from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

from app.helpers import is_official_document, kdv_ayir, money, number_for_input, to_float, today_str, ui_label, ui_options, ui_value
from app.repositories import (
    add_belge_dosyasi,
    delete_islem,
    insert_islem,
    list_belge_dosyalari,
    list_cariler,
    list_islemler,
    list_kasalar,
    list_kategoriler_by_tip,
    update_islem,
)
from app.screens.base import RefreshableScreen
from app.widgets import (
    ACCENT,
    ACCENT_SOFT,
    DANGER,
    DANGER_SOFT,
    MUTED,
    PRIMARY,
    PRIMARY_LIGHT,
    SUCCESS,
    SUCCESS_SOFT,
    TEXT,
    WARNING,
    WARNING_SOFT,
    WHITE,
    DateButton,
    btn,
    card,
    chip,
    choice_id,
    confirm,
    form_input,
    form_spinner,
    label,
    make_choice,
    scroll_container,
    set_spinner_by_id,
    show_message,
    small_label,
    title_label,
)

ISLEM_TIPLERI = ["gelir", "gider", "tahsilat", "odeme"]
BELGE_TURLERI = ui_options("belge_turu")
ODEME_DURUMLARI = ui_options("odeme_durumu")

TIP_BASLIK = {
    "gelir": "Gelir",
    "gider": "Gider",
    "tahsilat": "Tahsilat",
    "odeme": "Ödeme",
}

TIP_FORM_BASLIK = {
    "gelir": "Gelir Kaydı",
    "gider": "Gider Kaydı",
    "tahsilat": "Tahsilat Kaydı",
    "odeme": "Ödeme Kaydı",
}

TIP_ACIKLAMA = {
    "gelir": "Satış, hizmet geliri veya müşteriye kesilen belge takibi.",
    "gider": "Fişli, faturalı veya belgesiz masraf takibi.",
    "tahsilat": "Müşteriden alınan ödeme / banka girişi.",
    "odeme": "Tedarikçiye, personele veya başka bir yere yapılan ödeme.",
}

TIP_TONE = {
    "gelir": "green",
    "gider": "red",
    "tahsilat": "blue",
    "odeme": "orange",
}

TIP_ACTIVE_COLOR = {
    "gelir": SUCCESS,
    "gider": DANGER,
    "tahsilat": ACCENT,
    "odeme": WARNING,
}

TIP_SOFT_COLOR = {
    "gelir": SUCCESS_SOFT,
    "gider": DANGER_SOFT,
    "tahsilat": ACCENT_SOFT,
    "odeme": WARNING_SOFT,
}

TIP_DEFAULTS = {
    "gelir": {"belge_turu": "belgesiz", "kdv_orani": "0", "odeme_durumu": "odendi"},
    "gider": {"belge_turu": "belgesiz", "kdv_orani": "0", "odeme_durumu": "odendi"},
    "tahsilat": {"belge_turu": "dekont", "kdv_orani": "0", "odeme_durumu": "odendi"},
    "odeme": {"belge_turu": "dekont", "kdv_orani": "0", "odeme_durumu": "odendi"},
}


class IslemlerScreen(RefreshableScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.edit_id = None
        self.active_tip = "gider"
        self.tab_buttons = {}
        self.scroll, self.content = scroll_container()
        self.add_widget(self.scroll)
        self._build()

    def on_pre_enter(self, *_args):
        self.reload_options()
        self.reload_list()

    def _build(self):
        self.content.clear_widgets()
        self.content.add_widget(title_label("İşlem Kayıtları"))
        self.content.add_widget(small_label("Önce işlem türünü seç, sonra formu doldur. Liste seçili türe göre süzülür."))
        self._build_type_tabs()
        self._build_form()
        self._build_list_area()
        self.apply_type_view(reset_fields=True)

    def _build_type_tabs(self):
        tabs_card = card(padding=10, spacing=8)
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(104))
        for tip in ISLEM_TIPLERI:
            b = btn(TIP_BASLIK[tip], lambda _b, t=tip: self.select_tip(t), bg=TIP_SOFT_COLOR[tip], fg=TIP_ACTIVE_COLOR[tip], height=48)
            self.tab_buttons[tip] = b
            grid.add_widget(b)
        tabs_card.add_widget(grid)
        self.content.add_widget(tabs_card)

    def _build_form(self):
        self.form_card = card(padding=12, spacing=8)
        self.form_title = label("", size=18, bold=True, color=TEXT, height=34)
        self.form_hint = small_label("")
        self.form_card.add_widget(self.form_title)
        self.form_card.add_widget(self.form_hint)

        self.tarih = DateButton(today_str())
        self.baslik = form_input("Başlık")
        self.toplam_tutar = form_input("Toplam Tutar")
        self.kdv_orani = form_spinner(["0", "1", "8", "10", "18", "20"], "0")
        self.belge_turu = form_spinner(BELGE_TURLERI, ui_label("belge_turu", "belgesiz"))
        self.belge_no = form_input("Belge No")
        self.odeme_durumu = form_spinner(ODEME_DURUMLARI, ui_label("odeme_durumu", "odendi"))
        self.kasa = form_spinner(["Seçiniz"], "Seçiniz")
        self.cari = form_spinner(["Seçiniz"], "Seçiniz")
        self.kategori = form_spinner(["Seçiniz"], "Seçiniz")
        self.aciklama = form_input("Açıklama", multiline=True)

        fields = [
            ("Tarih", self.tarih),
            ("Başlık", self.baslik),
            ("Toplam Tutar", self.toplam_tutar),
            ("KDV Oranı", self.kdv_orani),
            ("Belge Türü", self.belge_turu),
            ("Belge No", self.belge_no),
            ("Ödeme Durumu", self.odeme_durumu),
            ("Kasa / Banka", self.kasa),
            ("Cari", self.cari),
            ("Kategori", self.kategori),
            ("Açıklama", self.aciklama),
        ]
        for caption, widget in fields:
            self.form_card.add_widget(label(caption, size=13, color=MUTED, height=24))
            self.form_card.add_widget(widget)

        row = BoxLayout(size_hint_y=None, height=44, spacing=8)
        row.add_widget(btn("Kaydet", self.save, bg=SUCCESS))
        row.add_widget(btn("Yeni", lambda *_: self.clear_form(), bg=PRIMARY_LIGHT))
        self.form_card.add_widget(row)
        self.content.add_widget(self.form_card)

    def _build_list_area(self):
        self.records_title = title_label("Kayıtlar")
        self.content.add_widget(self.records_title)
        self.list_box = card(padding=0, spacing=8)
        self.content.add_widget(self.list_box)

    def select_tip(self, tip: str, reset_fields: bool = True, reload_records: bool = True):
        if tip not in ISLEM_TIPLERI:
            tip = "gider"
        self.active_tip = tip
        self.edit_id = None if reset_fields else self.edit_id
        self.apply_type_view(reset_fields=reset_fields)
        self.on_type_change()
        if reload_records:
            self.reload_list()

    def apply_type_view(self, reset_fields: bool = False):
        self._paint_tabs()
        self.form_title.text = TIP_FORM_BASLIK[self.active_tip]
        self.form_hint.text = TIP_ACIKLAMA[self.active_tip]
        self.records_title.text = f"{TIP_BASLIK[self.active_tip]} Kayıtları"

        self.baslik.hint_text = f"{TIP_BASLIK[self.active_tip]} başlığı"
        self.toplam_tutar.hint_text = "Toplam tutar"
        self.belge_no.hint_text = "Belge / dekont / referans no"

        if reset_fields:
            defaults = TIP_DEFAULTS[self.active_tip]
            self.tarih.set_date(today_str())
            self.baslik.text = ""
            self.toplam_tutar.text = ""
            self.kdv_orani.text = defaults["kdv_orani"]
            self.belge_turu.text = ui_label("belge_turu", defaults["belge_turu"])
            self.belge_no.text = ""
            self.odeme_durumu.text = ui_label("odeme_durumu", defaults["odeme_durumu"])
            self.kasa.text = "Seçiniz"
            self.cari.text = "Seçiniz"
            self.kategori.text = "Seçiniz"
            self.aciklama.text = ""

    def _paint_tabs(self):
        for tip, button in self.tab_buttons.items():
            is_active = tip == self.active_tip
            button.bg_color = TIP_ACTIVE_COLOR[tip] if is_active else TIP_SOFT_COLOR[tip]
            button.color = WHITE if is_active else TIP_ACTIVE_COLOR[tip]
            button.text = f"✓ {TIP_BASLIK[tip]}" if is_active else TIP_BASLIK[tip]
            if hasattr(button, "_bg_color_instruction"):
                button._bg_color_instruction.rgba = button.bg_color

    def reload_options(self):
        self.kasa_rows = list_kasalar()
        self.cari_rows = list_cariler()
        self.kasa.values = ["Seçiniz"] + [make_choice(r, "kasa_adi") for r in self.kasa_rows]
        self.cari.values = ["Seçiniz"] + [make_choice(r, "unvan") for r in self.cari_rows]
        if self.kasa.text not in self.kasa.values:
            self.kasa.text = "Seçiniz"
        if self.cari.text not in self.cari.values:
            self.cari.text = "Seçiniz"
        self.on_type_change()

    def on_type_change(self):
        kategori_tip = "gelir" if self.active_tip in ("gelir", "tahsilat") else "gider"
        self.kategori_rows = list_kategoriler_by_tip(kategori_tip)
        self.kategori.values = ["Seçiniz"] + [make_choice(r, "kategori_adi") for r in self.kategori_rows]
        if self.kategori.text not in self.kategori.values:
            self.kategori.text = "Seçiniz"

    def clear_form(self):
        self.edit_id = None
        self.apply_type_view(reset_fields=True)
        self.on_type_change()

    def collect(self):
        baslik = self.baslik.text.strip()
        if not baslik:
            raise ValueError("Başlık zorunlu.")
        toplam = to_float(self.toplam_tutar.text)
        if toplam <= 0:
            raise ValueError("Toplam tutar 0'dan büyük olmalı.")

        kdv_orani = 0 if self.active_tip in ("tahsilat", "odeme") else to_float(self.kdv_orani.text)
        tutar, kdv_tutari = kdv_ayir(toplam, kdv_orani)
        belge_turu = ui_value("belge_turu", self.belge_turu.text)
        odeme_durumu = ui_value("odeme_durumu", self.odeme_durumu.text)
        resmi_kayit = 1 if is_official_document(belge_turu) else 0
        return {
            "islem_tipi": self.active_tip,
            "cari_id": choice_id(self.cari.text),
            "kasa_id": choice_id(self.kasa.text),
            "kategori_id": choice_id(self.kategori.text),
            "tarih": self.tarih.date_value,
            "belge_turu": belge_turu,
            "belge_no": self.belge_no.text.strip(),
            "belge_tarihi": self.tarih.date_value,
            "baslik": baslik,
            "aciklama": self.aciklama.text.strip(),
            "tutar": tutar,
            "kdv_orani": kdv_orani,
            "kdv_tutari": kdv_tutari,
            "toplam_tutar": toplam,
            "odeme_durumu": odeme_durumu,
            "resmi_kayit": resmi_kayit,
        }

    def save(self, *_args):
        try:
            data = self.collect()
            if data["odeme_durumu"] == "odendi" and not data["kasa_id"]:
                raise ValueError("Ödendi seçiliyse kasa/banka seçmelisin.")
            if self.edit_id:
                update_islem(self.edit_id, data)
                show_message("Tamam", "İşlem güncellendi.")
            else:
                self.edit_id = insert_islem(data)
                show_message("Tamam", "İşlem eklendi. Belge eklemek istersen listeden Belge butonunu kullan.")
            self.clear_form()
            self.reload_list()
            self.manager.app_refresh_all()
        except Exception as exc:
            show_message("Hata", str(exc))

    def edit(self, row):
        self.edit_id = row["id"]
        self.select_tip(row["islem_tipi"] or "gider", reset_fields=False, reload_records=False)
        self.tarih.set_date(row["tarih"])
        self.baslik.text = row["baslik"] or ""
        self.toplam_tutar.text = number_for_input(row["toplam_tutar"])
        self.kdv_orani.text = number_for_input(row["kdv_orani"])
        self.belge_turu.text = ui_label("belge_turu", row["belge_turu"] or TIP_DEFAULTS[self.active_tip]["belge_turu"])
        self.belge_no.text = row["belge_no"] or ""
        self.odeme_durumu.text = ui_label("odeme_durumu", row["odeme_durumu"] or "odendi")
        self.reload_options()
        set_spinner_by_id(self.kasa, row["kasa_id"], row["kasa_adi"])
        set_spinner_by_id(self.cari, row["cari_id"], row["cari_unvan"])
        set_spinner_by_id(self.kategori, row["kategori_id"], row["kategori_adi"])
        self.aciklama.text = row["aciklama"] or ""
        self.scroll.scroll_y = 1

    def detail(self, row):
        docs = list_belge_dosyalari(row["id"])
        doc_text = "\n".join([f"- {d['dosya_adi']}" for d in docs]) or "Belge yok"
        message = (
            f"Başlık: {row['baslik']}\n"
            f"Tarih: {row['tarih']}\n"
            f"Tip: {TIP_BASLIK.get(row['islem_tipi'], row['islem_tipi'])}\n"
            f"Tutar: {money(row['toplam_tutar'])}\n"
            f"KDV: {money(row['kdv_tutari'])}\n"
            f"Belge: {ui_label('belge_turu', row['belge_turu'])} {row['belge_no'] or ''}\n"
            f"Kasa: {row['kasa_adi'] or '-'}\n"
            f"Cari: {row['cari_unvan'] or '-'}\n"
            f"Kategori: {row['kategori_adi'] or '-'}\n\n"
            f"Ekler:\n{doc_text}"
        )
        show_message("İşlem Detayı", message)

    def delete(self, row):
        confirm("Sil", f"{row['baslik']} kaydı silinsin mi?", lambda: self._delete(row["id"]))

    def _delete(self, islem_id):
        delete_islem(islem_id)
        self.clear_form()
        self.reload_list()
        self.manager.app_refresh_all()

    def attach(self, row):
        AttachmentPopup(row["id"], on_done=lambda: self.reload_list()).open()

    def reload_list(self):
        if not hasattr(self, "list_box"):
            return
        self.list_box.clear_widgets()
        rows = [row for row in list_islemler() if row["islem_tipi"] == self.active_tip]

        if not rows:
            empty = card(padding=14, spacing=4, bg_color=TIP_SOFT_COLOR[self.active_tip])
            empty.add_widget(label(f"Henüz {TIP_BASLIK[self.active_tip]} kaydı yok.", size=15, bold=True, color=TIP_ACTIVE_COLOR[self.active_tip], height=30))
            empty.add_widget(small_label("Yeni kayıt eklemek için üstteki formu doldurup Kaydet'e bas."))
            self.list_box.add_widget(empty)
            return

        for row in rows:
            box = card(padding=10, spacing=5)
            top = BoxLayout(size_hint_y=None, height=32, spacing=6)
            type_chip = chip(TIP_BASLIK.get(row["islem_tipi"], row["islem_tipi"]), TIP_TONE.get(row["islem_tipi"], "gray"))
            type_chip.size_hint_x = None
            type_chip.width = dp(96)
            top.add_widget(type_chip)
            top.add_widget(label(money(row["toplam_tutar"]), size=15, bold=True, color=TIP_ACTIVE_COLOR[self.active_tip], halign="right", height=32))
            box.add_widget(top)

            box.add_widget(label(f"[b]{row['baslik']}[/b]", size=15, height=28))
            meta = f"{row['tarih']} • {ui_label('belge_turu', row['belge_turu'])} • {ui_label('odeme_durumu', row['odeme_durumu'])}"
            box.add_widget(label(meta, size=12, color=MUTED, height=24))
            if row["cari_unvan"] or row["kasa_adi"]:
                box.add_widget(label(f"{row['cari_unvan'] or '-'} / {row['kasa_adi'] or '-'}", size=12, color=MUTED, height=22))

            actions1 = BoxLayout(size_hint_y=None, height=40, spacing=6)
            actions1.add_widget(btn("Düzenle", lambda _b, r=row: self.edit(r), bg=PRIMARY))
            actions1.add_widget(btn("Detay", lambda _b, r=row: self.detail(r), bg=ACCENT))
            box.add_widget(actions1)
            actions2 = BoxLayout(size_hint_y=None, height=40, spacing=6)
            actions2.add_widget(btn(f"Belge ({row['belge_sayisi']})", lambda _b, r=row: self.attach(r), bg=PRIMARY_LIGHT))
            actions2.add_widget(btn("Sil", lambda _b, r=row: self.delete(r), bg=DANGER))
            box.add_widget(actions2)
            self.list_box.add_widget(box)


class AttachmentPopup(Popup):
    def __init__(self, islem_id, on_done=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Belge Ekle"
        self.islem_id = islem_id
        self.on_done = on_done
        self.size_hint = (0.96, 0.88)
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(label("Fiş/fatura/dekont dosya yolunu yazabilir veya aşağıdan dosya seçebilirsin.", size=13, height=46))
        self.path_input = form_input("/storage/emulated/0/Download/fis.jpg")
        root.add_widget(self.path_input)
        row = BoxLayout(size_hint_y=None, height=42, spacing=8)
        row.add_widget(btn("Ekle", self.add_manual, bg=SUCCESS))
        row.add_widget(btn("Kapat", lambda *_: self.dismiss(), bg=PRIMARY_LIGHT))
        root.add_widget(row)
        try:
            self.filechooser = FileChooserListView(path=str(Path.home()))
            root.add_widget(self.filechooser)
            root.add_widget(btn("Seçili Dosyayı Ekle", self.add_selected, bg=PRIMARY))
        except Exception:
            pass
        self.content = root

    def add_selected(self, *_args):
        selected = getattr(self, "filechooser", None).selection if hasattr(self, "filechooser") else []
        if not selected:
            show_message("Eksik", "Dosya seçilmedi.")
            return
        self._add_path(selected[0])

    def add_manual(self, *_args):
        self._add_path(self.path_input.text.strip())

    def _add_path(self, path):
        try:
            add_belge_dosyasi(self.islem_id, path)
            show_message("Tamam", "Belge eklendi.")
            if self.on_done:
                self.on_done()
            self.dismiss()
        except Exception as exc:
            show_message("Hata", str(exc))
