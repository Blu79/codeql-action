from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import threading
from datetime import datetime

class RaiBaiApp(App):
    def build(self):
        self.is_running = False
        self.client = None

        layout = BoxLayout(orientation='vertical', padding=15, spacing=12)

        title = Label(text='🚀 Rải Bài App Nhỏ', font_size='24sp', size_hint_y=None, height=60)
        layout.add_widget(title)

        self.api_id = TextInput(hint_text='API ID', input_filter='int', multiline=False)
        self.api_hash = TextInput(hint_text='API Hash', password=True, multiline=False)
        self.source = TextInput(hint_text='Source Channel (ví dụ: mychannel)', multiline=False)

        layout.add_widget(self.api_id)
        layout.add_widget(self.api_hash)
        layout.add_widget(self.source)

        btn_layout = BoxLayout(size_hint_y=None, height=110, spacing=10)

        login_btn = Button(text='🔑 Đăng Nhập', background_color=(0.2, 0.5, 1, 1))
        login_btn.bind(on_press=self.login)
        btn_layout.add_widget(login_btn)

        self.start_btn = Button(text='▶️ BẮT ĐẦU', background_color=(0.1, 0.7, 0.1, 1))
        self.start_btn.bind(on_press=self.start_forward)
        btn_layout.add_widget(self.start_btn)

        self.stop_btn = Button(text='⏹️ DỪNG', background_color=(0.8, 0.1, 0.1, 1), disabled=True)
        self.stop_btn.bind(on_press=self.stop_forward)
        btn_layout.add_widget(self.stop_btn)

        layout.add_widget(btn_layout)

        self.log_label = Label(text='App sẵn sàng...\n1. Nhập API ID + Hash\n2. Bấm Đăng Nhập\n', size_hint_y=None, halign='left')
        self.log_label.bind(size=self.log_label.setter('text_size'))
        scroll = ScrollView()
        scroll.add_widget(self.log_label)
        layout.add_widget(scroll)

        return layout

    def log(self, msg):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_label.text += f"[{time_str}] {msg}\n"

    def login(self, instance):
        try:
            api_id = int(self.api_id.text.strip())
            api_hash = self.api_hash.text.strip()

            if not api_id or not api_hash:
                self.log("❌ Nhập đủ API ID và API Hash!")
                return

            self.log("Đang đăng nhập...")

            def do_login():
                try:
                    self.client = TelegramClient('rai_app_session', api_id, api_hash)
                    asyncio.run(self.client.start(phone=lambda: input("Nhập số điện thoại (+84...): ")))
                    self.log("✅ Đăng nhập thành công!\nBây giờ bấm BẮT ĐẦU")
                except Exception as e:
                    self.log(f"❌ Lỗi: {str(e)}")

            threading.Thread(target=do_login, daemon=True).start()

        except Exception as e:
            self.log(f"Lỗi: {str(e)}")

    def start_forward(self, instance):
        if not self.client:
            self.log("❌ Hãy đăng nhập trước!")
            return
        if not self.source.text.strip():
            self.log("❌ Nhập Source Channel!")
            return

        self.is_running = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.log(f"🚀 Đang theo dõi: {self.source.text.strip()}")

        source = self.source.text.strip()

        @events.register(events.NewMessage(chats=[source]))
        async def handler(event):
            if not self.is_running: return
            try:
                self.log("🆕 Phát hiện bài mới → Forwarding...")
                await asyncio.sleep(5)
            except Exception as e:
                self.log(f"Lỗi: {str(e)}")

        self.client.add_event_handler(handler)

    def stop_forward(self, instance):
        self.is_running = False
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.log("⏹️ Đã dừng.")

if __name__ == '__main__':
    RaiBaiApp().run()
