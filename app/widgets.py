from __future__ import annotations

import calendar
from datetime import date

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from app.helpers import display_date


# Mobil görünüm için tek merkezden yönetilen renk paleti
PRIMARY = (0.05, 0.09, 0.18, 1)        # lacivert
PRIMARY_LIGHT = (0.10, 0.16, 0.30, 1)
ACCENT = (0.13, 0.45, 0.95, 1)         # canlı mavi
ACCENT_SOFT = (0.88, 0.94, 1.00, 1)
DANGER = (0.88, 0.18, 0.18, 1)
DANGER_SOFT = (1.00, 0.92, 0.92, 1)
SUCCESS = (0.08, 0.62, 0.36, 1)
SUCCESS_SOFT = (0.90, 0.98, 0.94, 1)
WARNING = (0.96, 0.62, 0.12, 1)
WARNING_SOFT = (1.00, 0.96, 0.88, 1)
BG = (0.94, 0.96, 0.99, 1)
CARD_BG = (1, 1, 1, 1)
CARD_BORDER = (0.86, 0.89, 0.94, 1)
TEXT = (0.06, 0.08, 0.14, 1)
MUTED = (0.40, 0.44, 0.53, 1)
WHITE = (1, 1, 1, 1)
INPUT_BG = (0.97, 0.98, 1, 1)


class RoundedBox(BoxLayout):
    def __init__(
        self,
        bg_color=CARD_BG,
        radius=18,
        border_color=CARD_BORDER,
        border_width=1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = dp(radius)
        self.border_color = border_color
        self.border_width = border_width
        with self.canvas.before:
            self._bg_color_instruction = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_color_instruction = Color(*self.border_color)
            self._border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius),
                width=dp(self.border_width),
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *_args):
        self._bg_color_instruction.rgba = self.bg_color
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self.radius]
        self._border_color_instruction.rgba = self.border_color
        self._border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)


class RoundedButton(Button):
    def __init__(self, bg_color=PRIMARY, fg_color=WHITE, radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.color = fg_color
        self.radius = dp(radius)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.font_size = self.font_size or dp(14)
        self.bold = True
        with self.canvas.before:
            self._bg_color_instruction = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._state_changed)

    def _state_changed(self, *_args):
        if self.state == "down":
            self._bg_color_instruction.rgba = (
                max(self.bg_color[0] - 0.04, 0),
                max(self.bg_color[1] - 0.04, 0),
                max(self.bg_color[2] - 0.04, 0),
                self.bg_color[3],
            )
        else:
            self._bg_color_instruction.rgba = self.bg_color

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self.radius]


class StyledSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = INPUT_BG
        self.color = TEXT
        self.font_size = dp(14)
        self.option_cls = "SpinnerOption"
        self.halign = "left"
        self.valign = "middle"
        self.padding = [dp(12), 0]
        self.bind(size=self._update_text_size)
        self._update_text_size()

    def _update_text_size(self, *_args):
        self.text_size = (max(self.width - dp(24), 1), self.height)


class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_active = ""
        self.background_color = INPUT_BG
        self.foreground_color = TEXT
        self.hint_text_color = (0.55, 0.59, 0.68, 1)
        self.cursor_color = ACCENT
        self.font_size = dp(15)
        self.padding = [dp(12), dp(11), dp(12), dp(8)]


def label(text: str, size=15, bold=False, color=TEXT, halign="left", height=None):
    w = Label(
        text=text,
        font_size=dp(size),
        bold=bold,
        color=color,
        halign=halign,
        valign="middle",
        markup=True,
    )
    if height:
        w.size_hint_y = None
        w.height = dp(height)
    w.bind(size=lambda inst, _value: setattr(inst, "text_size", (inst.width, None)))
    return w


def title_label(text: str):
    return label(text, size=19, bold=True, color=TEXT, height=38)


def section_title(text: str):
    box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(42), padding=[dp(2), dp(8), dp(2), dp(4)])
    box.add_widget(label(text, size=16, bold=True, color=TEXT, height=28))
    return box


def small_label(text: str):
    return label(text, size=12, color=MUTED, height=24)


def btn(text: str, on_press=None, bg=PRIMARY, fg=WHITE, height=44):
    b = RoundedButton(
        text=text,
        size_hint_y=None,
        height=dp(height),
        bg_color=bg,
        fg_color=fg,
        font_size=dp(13),
    )
    if on_press:
        b.bind(on_press=on_press)
    return b


def ghost_btn(text: str, on_press=None, height=44):
    return btn(text, on_press=on_press, bg=ACCENT_SOFT, fg=PRIMARY, height=height)


def form_input(hint="", text="", multiline=False, input_filter=None):
    ti = StyledTextInput(
        text=str(text or ""),
        hint_text=hint,
        multiline=multiline,
        size_hint_y=None,
        height=dp(96 if multiline else 48),
        input_filter=input_filter,
    )
    return ti


def form_spinner(values, text=None):
    sp = StyledSpinner(
        text=text or (values[0] if values else "Seçiniz"),
        values=values,
        size_hint_y=None,
        height=dp(48),
    )
    return sp


def card(orientation="vertical", padding=14, spacing=8, bg_color=CARD_BG):
    box = RoundedBox(
        orientation=orientation,
        padding=[dp(padding)] * 4,
        spacing=dp(spacing),
        size_hint_y=None,
        bg_color=bg_color,
        radius=18,
    )
    box.bind(minimum_height=box.setter("height"))
    return box


def metric_card(title: str, value: str, subtitle: str = "", tone: str = "neutral"):
    colors = {
        "neutral": (CARD_BG, TEXT),
        "blue": (ACCENT_SOFT, PRIMARY),
        "green": (SUCCESS_SOFT, SUCCESS),
        "red": (DANGER_SOFT, DANGER),
        "orange": (WARNING_SOFT, WARNING),
        "dark": (PRIMARY, WHITE),
    }
    bg, fg = colors.get(tone, colors["neutral"])
    box = card(padding=10, spacing=2, bg_color=bg)
    box.add_widget(label(title, size=11, color=WHITE if tone == "dark" else MUTED, height=22))
    box.add_widget(label(value, size=17, bold=True, color=fg, height=30))
    if subtitle:
        box.add_widget(label(subtitle, size=10, color=WHITE if tone == "dark" else MUTED, height=18))
    return box


def chip(text: str, tone: str = "blue"):
    tones = {
        "blue": (ACCENT_SOFT, PRIMARY),
        "green": (SUCCESS_SOFT, SUCCESS),
        "red": (DANGER_SOFT, DANGER),
        "orange": (WARNING_SOFT, WARNING),
        "gray": ((0.92, 0.94, 0.97, 1), MUTED),
        "dark": (PRIMARY_LIGHT, WHITE),
    }
    bg, fg = tones.get(tone, tones["blue"])
    box = RoundedBox(size_hint_y=None, height=dp(30), padding=[dp(10), 0, dp(10), 0], bg_color=bg, radius=15, border_color=bg)
    box.add_widget(label(text, size=11, bold=True, color=fg, halign="center"))
    return box


def scroll_container():
    scroll = ScrollView(size_hint=(1, 1))
    # Alt menü sabit kaldığı için içerik sonuna ekstra nefes payı veriyoruz.
    content = BoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(12), dp(8), dp(12), dp(82)], size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))
    scroll.add_widget(content)
    return scroll, content


def make_choice(row, title_field):
    return f"{row['id']} | {row[title_field]}"


def choice_id(text):
    if not text or "|" not in text:
        return None
    try:
        return int(text.split("|", 1)[0].strip())
    except ValueError:
        return None


def set_spinner_by_id(spinner: Spinner, row_id, title: str | None = None):
    if not row_id:
        return
    prefix = f"{row_id} |"
    for value in spinner.values:
        if value.startswith(prefix):
            spinner.text = value
            return
    if title:
        spinner.text = f"{row_id} | {title}"


def show_message(title: str, message: str):
    layout = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
    layout.add_widget(label(message, size=15))
    close = btn("Tamam", bg=PRIMARY)
    layout.add_widget(close)
    popup = Popup(title=title, content=layout, size_hint=(0.90, None), height=dp(240))
    close.bind(on_press=popup.dismiss)
    popup.open()


def confirm(title: str, message: str, on_yes):
    layout = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
    layout.add_widget(label(message, size=15))
    row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    no = btn("Vazgeç", bg=PRIMARY_LIGHT)
    yes = btn("Evet", bg=DANGER)
    row.add_widget(no)
    row.add_widget(yes)
    layout.add_widget(row)
    popup = Popup(title=title, content=layout, size_hint=(0.9, None), height=dp(240))
    no.bind(on_press=popup.dismiss)

    def _yes(_btn):
        popup.dismiss()
        on_yes()

    yes.bind(on_press=_yes)
    popup.open()


class DateButton(RoundedButton):
    def __init__(self, date_value=None, **kwargs):
        super().__init__(**kwargs)
        self.date_value = date_value or date.today().isoformat()
        self.size_hint_y = None
        self.height = dp(48)
        self.bg_color = ACCENT_SOFT
        self.color = PRIMARY
        self.font_size = dp(14)
        self.update_text()
        self.bind(on_press=self.open_picker)

    def set_date(self, value):
        self.date_value = value or date.today().isoformat()
        self.update_text()

    def update_text(self):
        self.text = display_date(self.date_value) or "Tarih seç"

    def open_picker(self, *_args):
        DatePickerPopup(self.date_value, self.set_date).open()


class DatePickerPopup(Popup):
    def __init__(self, selected_date, callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Tarih Seç"
        self.size_hint = (0.96, 0.82)
        self.callback = callback
        try:
            parts = [int(x) for x in str(selected_date).split("-")]
            self.current = date(parts[0], parts[1], 1)
            self.selected_day = parts[2]
        except Exception:
            today = date.today()
            self.current = date(today.year, today.month, 1)
            self.selected_day = today.day
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.content = self.root_box
        self.render()

    def render(self):
        self.root_box.clear_widgets()
        header = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        header.add_widget(btn("‹", self.prev_month, bg=PRIMARY_LIGHT))
        header.add_widget(label(f"{self.current.month:02d}/{self.current.year}", size=18, bold=True, halign="center"))
        header.add_widget(btn("›", self.next_month, bg=PRIMARY_LIGHT))
        self.root_box.add_widget(header)

        names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        grid = GridLayout(cols=7, spacing=dp(4), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for name in names:
            grid.add_widget(label(name, size=12, bold=True, halign="center", height=30))

        cal = calendar.Calendar(firstweekday=0)
        for day in cal.itermonthdays(self.current.year, self.current.month):
            if day == 0:
                grid.add_widget(label("", height=42))
            else:
                b = btn(
                    str(day),
                    bg=ACCENT if day == self.selected_day else (0.90, 0.92, 0.96, 1),
                    fg=WHITE if day == self.selected_day else TEXT,
                    height=42,
                )
                b.bind(on_press=lambda _b, d=day: self.select_day(d))
                grid.add_widget(b)
        self.root_box.add_widget(grid)
        self.root_box.add_widget(btn("Bugün", self.select_today, bg=SUCCESS))
        self.root_box.add_widget(btn("Kapat", lambda _b: self.dismiss(), bg=PRIMARY_LIGHT))

    def prev_month(self, *_args):
        year = self.current.year
        month = self.current.month - 1
        if month == 0:
            month = 12
            year -= 1
        self.current = date(year, month, 1)
        self.selected_day = min(self.selected_day, calendar.monthrange(year, month)[1])
        self.render()

    def next_month(self, *_args):
        year = self.current.year
        month = self.current.month + 1
        if month == 13:
            month = 1
            year += 1
        self.current = date(year, month, 1)
        self.selected_day = min(self.selected_day, calendar.monthrange(year, month)[1])
        self.render()

    def select_day(self, day):
        self.callback(date(self.current.year, self.current.month, day).isoformat())
        self.dismiss()

    def select_today(self, *_args):
        self.callback(date.today().isoformat())
        self.dismiss()
