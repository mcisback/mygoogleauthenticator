import os

from CLI import ConfigManager
from GoogleAuth import generate_code_from_time, generate_otp_uri

os.environ['KIVY_NO_ARGS'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')

from kivymd.app import MDApp
from kivy.lang import Builder

from kivy.properties import StringProperty
from kivymd.uix.list import ThreeLineAvatarIconListItem, OneLineAvatarListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.snackbar import Snackbar

from kivy.clock import Clock
from kivymd.utils import asynckivy
from kivy.core.clipboard import Clipboard

from kivy_garden.qrcode import QRCodeWidget

class CardItem(ThreeLineAvatarIconListItem):
    headline = StringProperty()
    otp = StringProperty()
    time = StringProperty()

class MyGoogleAuthApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = "MyGoogleAuth"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        self.cards = []
        self.dialog = False

    def set_config(self, cli_config: ConfigManager):
        self.cli_config = cli_config

        return  self

    def build(self):
        self.screen = Builder.load_file("GUI/mainwindow.kv")

        self.entries = self.cli_config.list_entries()
        self.set_list()

        Clock.schedule_interval(self.refresh_callback, 1)

        return self.screen

    def set_list(self):
        async def set_list():
            if len(self.entries) <= 0:
                self.screen.ids.refresh_layout.add_widget(
                    OneLineAvatarListItem(text=f"DB Empty. Add One Entry")
                )
            else:
                for entry in self.entries.items():
                    otp = generate_code_from_time(entry[1])

                    time_remaining = str(otp[1]) + "s remaining"
                    otp_code = str(otp[0])

                    print(f"{otp_code}:{time_remaining}")

                    await asynckivy.sleep(0)
                    card = CardItem(headline=entry[0], otp=otp_code, time=time_remaining)
                    self.cards.append(card)
                    self.screen.ids.box.add_widget(card)

        asynckivy.start(set_list())

    def on_start(self):
        # self.entries = self.cli_config.list_entries()
        # self.set_list()
        pass
    def show_qrcode_dialog(self, card_item):
        print("Dialog Data: ", card_item)

        if not self.dialog:
            # qrcodedialog = QrCodeDialog().set_data("Hello, World !")
            # qrcodedialog.set_data("Hello, World !")
            qrcodedata = generate_otp_uri(card_item.headline, self.cli_config.get_entry_by_key(card_item.headline))

            print("QrCodeData is: ", qrcodedata)

            self.dialog = MDDialog(
                type="custom",
                size_hint=(.7, .6),
                content_cls=QrCodeDialog().set_data(qrcodedata)
                )

        self.dialog.set_normal_height()
        self.dialog.open()

    def close_dialog(self, inst=None):
        print("Called MyGoogleAuthApp.close_dialog")

        self.dialog.dismiss()

    def refresh_callback(self, *args):
        for card in self.cards:
            otp = generate_code_from_time(self.cli_config.get_entry_by_key(card.headline))

            time_remaining = str(otp[1]) + "s remaining"
            otp_code = str(otp[0])

            card.otp = otp_code
            card.time = time_remaining
    def copy_icon_on_press(self, card_item):
        otp = card_item.otp

        print(f"Copying OTP: {card_item.headline}:{otp}")

        Clipboard.copy(otp)

        Snackbar(
            text="Copied to Clipboard !"
        ).show()

    def edit_icon_on_press(self, card_item):
        print("Editing: ", card_item.headline)

    def add_button_on_press(self):
        print("Clicked Add Button")

    def settings_button_on_press(self):
        print("Clicked Settings Button")

class QrCodeDialog(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def set_data(self, data):
        self.ids.qr.data = data

        return self
