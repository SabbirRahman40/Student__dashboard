import json
import os
import random
import shutil
import copy
from datetime import datetime
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.resources import resource_find
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation

# Plyer integration for Camera, Gallery, and File Picker
try:
    from plyer import camera, filechooser
except ImportError:
    camera = None
    filechooser = None

DATA_FILE_NAME = "student_data.json"

def get_data_file():
    app = App.get_running_app()
    if app is not None:
        return os.path.join(app.user_data_dir, DATA_FILE_NAME)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE_NAME)

DEFAULT_DATA = {
    "users": {},
    "routine": [
        {"id": 1, "day": "Saturday", "time": "1:10-2:10 PM", "subject": "CSE 2391 - Data Structures", "room": "1004", "reminder_min": 30, "reminder_on": True},
        {"id": 2, "day": "Saturday", "time": "2:15-3:15 PM", "subject": "ENG 2203 - Advanced English", "room": "924", "reminder_min": 30, "reminder_on": True},
        {"id": 3, "day": "Sunday", "time": "10:40-11:40 AM", "subject": "EEN 2103 - Circuit Analysis I", "room": "504", "reminder_min": 30, "reminder_on": True},
        {"id": 4, "day": "Sunday", "time": "1:10-2:10 PM", "subject": "CSE 2391 - Data Structures", "room": "1004", "reminder_min": 30, "reminder_on": True},
        {"id": 5, "day": "Sunday", "time": "2:15-3:15 PM", "subject": "ENG 2203 - Advanced English", "room": "924", "reminder_min": 30, "reminder_on": True},
        {"id": 6, "day": "Monday", "time": "8:30-9:30 AM", "subject": "ACC 1305 - Accounting", "room": "501", "reminder_min": 30, "reminder_on": True},
        {"id": 7, "day": "Monday", "time": "10:40-11:40 AM", "subject": "EEN 2103 - Circuit Analysis I", "room": "607", "reminder_min": 30, "reminder_on": True},
        {"id": 8, "day": "Monday", "time": "11:45-12:45 PM", "subject": "EEN 2103 - Circuit Analysis I", "room": "607", "reminder_min": 30, "reminder_on": True},
        {"id": 9, "day": "Monday", "time": "1:10-2:10 PM", "subject": "CSE 2391 - Data Structures", "room": "1004", "reminder_min": 30, "reminder_on": True},
        {"id": 10, "day": "Tuesday", "time": "8:30-9:30 AM", "subject": "ACC 1305 - Accounting", "room": "503", "reminder_min": 30, "reminder_on": True},
        {"id": 11, "day": "Tuesday", "time": "2:15-3:15 PM", "subject": "ENG 2203 - Advanced English", "room": "924", "reminder_min": 30, "reminder_on": True},
        {"id": 12, "day": "Wednesday", "time": "8:30-9:30 AM", "subject": "ACC 1305 - Accounting", "room": "310", "reminder_min": 30, "reminder_on": True},
        {"id": 13, "day": "Wednesday", "time": "10:40-11:40 AM", "subject": "EEN 2104 - Circuit Lab", "room": "EEE lab-01", "reminder_min": 30, "reminder_on": True},
        {"id": 14, "day": "Wednesday", "time": "11:45-12:45 PM", "subject": "EEN 2104 - Circuit Lab", "room": "EEE lab-01", "reminder_min": 30, "reminder_on": True},
        {"id": 15, "day": "Wednesday", "time": "1:10-2:10 PM", "subject": "CSE 2392 - Data Structures Lab", "room": "Com lab-08", "reminder_min": 30, "reminder_on": True},
        {"id": 16, "day": "Wednesday", "time": "2:15-3:15 PM", "subject": "CSE 2392 - Data Structures Lab", "room": "Com lab-08", "reminder_min": 30, "reminder_on": True}
    ],
    "exams": [],
    "tasks": [],
    "photos": [],
    "notes": [],
    "resources": [],
    "cgpa_list": [],
    "theme": "asmani"
}

def _normalize_data(data):
    if not isinstance(data, dict):
        data = {}
    normalized = copy.deepcopy(DEFAULT_DATA)
    normalized.update(data)

    if not isinstance(normalized.get("users"), dict):
        normalized["users"] = {}
    for username, user in list(normalized["users"].items()):
        if isinstance(user, str):
            normalized["users"][username] = {"password": user, "phone": ""}
        elif isinstance(user, dict):
            user.setdefault("password", "")
            user.setdefault("phone", "")
        else:
            normalized["users"].pop(username, None)

    for key in ("routine", "exams", "tasks", "photos", "notes", "resources", "cgpa_list"):
        if not isinstance(normalized.get(key), list):
            normalized[key] = []
    if "theme" not in normalized:
        normalized["theme"] = "asmani"
    return normalized

def load_data():
    data_path = get_data_file()
    data = None
    
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                data = _normalize_data(raw_data)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
            
    if data is None:
        bundled_path = resource_find(DATA_FILE_NAME)
        if not bundled_path:
            bundled_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE_NAME)
        if bundled_path and os.path.isfile(bundled_path):
            try:
                os.makedirs(os.path.dirname(data_path), exist_ok=True)
                shutil.copyfile(bundled_path, data_path)
                with open(data_path, "r", encoding="utf-8") as f:
                    data = _normalize_data(json.load(f))
            except OSError:
                pass
                
    if data is None:
        data = _normalize_data(DEFAULT_DATA)
        
    save_data(data)
    return data

def save_data(data):
    data_path = get_data_file()
    data_dir = os.path.dirname(data_path)
    os.makedirs(data_dir, exist_ok=True)
    temp_path = data_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(temp_path, data_path)

class CardBox(BoxLayout):
    def __init__(self, bg_color=(0.88, 0.93, 0.98, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.padding = dp(10)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(75)
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class ModernAuthBoard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.width = dp(410)
        self.height = dp(510)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[25])
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class BlueSidePanel(BoxLayout):
    def __init__(self, is_right=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(12)
        self.size_hint = (0.44, 1)
        self.bg_color = (0.42, 0.55, 0.90, 1)
        
        with self.canvas.before:
            Color(*self.bg_color)
            radius_list = [0, 25, 25, 0] if is_right else [25, 0, 0, 25]
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=radius_list)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class PrimaryButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.42, 0.55, 0.90, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = '14sp'
        self.bold = True
        self.size_hint_y = None
        self.height = dp(40)

class OutlineButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = '13sp'
        self.bold = True
        self.size_hint_y = None
        self.height = dp(36)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[18])
            Color(0.42, 0.55, 0.90, 1)
            self.inner_rect = RoundedRectangle(size=(self.width-4, self.height-4), pos=(self.x+2, self.y+2), radius=[16])
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
        self.inner_rect.size = (instance.width-4, instance.height-4)
        self.inner_rect.pos = (instance.x+2, instance.y+2)

class AsmaniButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.42, 0.55, 0.90, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = '14sp'
        self.bold = True
        self.size_hint_y = None
        self.height = dp(42)

class AccentButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.15, 0.7, 0.5, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = '14sp'
        self.size_hint_y = None
        self.height = dp(40)

class StudentApp(App):
    def build(self):
        self.title = "Sabbir's Smart Student Dashboard"
        self.data = load_data()
        self.current_user = None
        self.routine_view_mode = "today"
        self.temp_reg_data = {}
        self.temp_forgot_data = {}
        
        if not hasattr(self, "_android_window_configured") and "ANDROID_ARGUMENT" not in os.environ:
            Window.size = (450, 720)
        self.root_layout = FloatLayout()
        
        with self.root_layout.canvas.before:
            self.bg_color_inst = Color(0.90, 0.92, 0.96, 1)
            self.bg_rect = Rectangle(size=(1000, 1000), pos=(0, 0))
        self.root_layout.bind(size=self._update_bg, pos=self._update_bg)

        self.show_login_screen()
        return self.root_layout

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def clear(self):
        self.root_layout.clear_widgets()

    def animate_pop_in(self, widget):
        widget.opacity = 0
        Animation(opacity=1, duration=0.35, t="out_back").start(widget)

    def _create_social_bar(self):
        social_box = BoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None, height=dp(55))
        lbl = Label(text="or login with social platforms", font_size="10sp", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(15), halign='center')
        social_box.add_widget(lbl)
        
        icons_grid = GridLayout(cols=4, spacing=dp(8), size_hint=(None, None), size=(dp(160), dp(32)), pos_hint={'center_x': 0.5})
        for s_name in ["G", "f", "🐙", "in"]:
            btn_s = Button(text=s_name, font_size="11sp", bold=True, background_normal='', background_color=(0.95, 0.95, 0.95, 1), color=(0.2, 0.2, 0.2, 1))
            icons_grid.add_widget(btn_s)
        social_box.add_widget(icons_grid)
        return social_box

    def show_login_screen(self):
        self.clear()
        board = ModernAuthBoard()
        self.animate_pop_in(board)
        
        left_panel = BlueSidePanel(is_right=False)
        left_panel.add_widget(BoxLayout(size_hint_y=0.2))
        
        welcome_lbl = Label(text="Hello, Welcome!", font_size="16sp", bold=True, color=(1, 1, 1, 1), size_hint_y=None, height=dp(30), halign='center')
        welcome_lbl.bind(size=welcome_lbl.setter('text_size'))
        left_panel.add_widget(welcome_lbl)
        
        sub_lbl = Label(text="Don't have an account?", font_size="10sp", color=(0.9, 0.95, 1, 0.9), size_hint_y=None, height=dp(20), halign='center')
        sub_lbl.bind(size=sub_lbl.setter('text_size'))
        left_panel.add_widget(sub_lbl)
        
        btn_goto_reg = OutlineButton(text="Register")
        btn_goto_reg.bind(on_press=lambda x: self.show_register_screen())
        left_panel.add_widget(btn_goto_reg)
        left_panel.add_widget(BoxLayout(size_hint_y=0.3))
        
        board.add_widget(left_panel)
        
        right_panel = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(10), size_hint=(0.56, 1))
        
        title = Label(text="Login", font_size="22sp", bold=True, color=(0.15, 0.15, 0.2, 1), size_hint_y=None, height=dp(40))
        right_panel.add_widget(title)
        
        self.username_input = TextInput(hint_text="Username 👤", multiline=False, size_hint_y=None, height=dp(38), background_color=(0.93, 0.93, 0.95, 1))
        self.password_input = TextInput(hint_text="Password 🔒", password=True, multiline=False, size_hint_y=None, height=dp(38), background_color=(0.93, 0.93, 0.95, 1))
        self.msg_label = Label(text="", color=(0.9, 0.2, 0.2, 1), font_size="10sp", size_hint_y=None, height=dp(18))
        
        right_panel.add_widget(self.username_input)
        right_panel.add_widget(self.password_input)
        right_panel.add_widget(self.msg_label)
        
        btn_forgot = Button(text="Forgot Password?", background_color=(0,0,0,0), color=(0.4, 0.4, 0.5, 1), font_size="10sp", size_hint_y=None, height=dp(20), halign='right')
        btn_forgot.bind(on_press=lambda x: self.show_forgot_screen())
        right_panel.add_widget(btn_forgot)
        
        btn_login = PrimaryButton(text="Login")
        btn_login.bind(on_press=self.handle_login)
        right_panel.add_widget(btn_login)
        
        right_panel.add_widget(self._create_social_bar())
        
        board.add_widget(right_panel)
        self.root_layout.add_widget(board)

    def show_register_screen(self):
        self.clear()
        board = ModernAuthBoard()
        self.animate_pop_in(board)
        
        left_form = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(8), size_hint=(0.56, 1))
        
        title = Label(text="Registration", font_size="20sp", bold=True, color=(0.15, 0.15, 0.2, 1), size_hint_y=None, height=dp(35))
        left_form.add_widget(title)
        
        self.reg_user = TextInput(hint_text="Username 👤", multiline=False, size_hint_y=None, height=dp(36), background_color=(0.93, 0.93, 0.95, 1))
        self.reg_phone = TextInput(hint_text="Email / Phone ✉️", multiline=False, size_hint_y=None, height=dp(36), background_color=(0.93, 0.93, 0.95, 1))
        self.reg_pass = TextInput(hint_text="Password 🔒", password=True, multiline=False, size_hint_y=None, height=dp(36), background_color=(0.93, 0.93, 0.95, 1))
        self.reg_cpass = TextInput(hint_text="Confirm Password 🔒", password=True, multiline=False, size_hint_y=None, height=dp(36), background_color=(0.93, 0.93, 0.95, 1))
        self.reg_msg = Label(text="", color=(0.9, 0.2, 0.2, 1), font_size="10sp", size_hint_y=None, height=dp(18))
        
        left_form.add_widget(self.reg_user)
        left_form.add_widget(self.reg_phone)
        left_form.add_widget(self.reg_pass)
        left_form.add_widget(self.reg_cpass)
        left_form.add_widget(self.reg_msg)
        
        btn_send_otp = PrimaryButton(text="Register")
        btn_send_otp.bind(on_press=self.send_reg_otp)
        left_form.add_widget(btn_send_otp)
        
        left_form.add_widget(self._create_social_bar())
        board.add_widget(left_form)
        
        right_panel = BlueSidePanel(is_right=True)
        right_panel.add_widget(BoxLayout(size_hint_y=0.2))
        
        welcome_lbl = Label(text="Welcome Back!", font_size="16sp", bold=True, color=(1, 1, 1, 1), size_hint_y=None, height=dp(30), halign='center')
        welcome_lbl.bind(size=welcome_lbl.setter('text_size'))
        right_panel.add_widget(welcome_lbl)
        
        sub_lbl = Label(text="Already have an account?", font_size="10sp", color=(0.9, 0.95, 1, 0.9), size_hint_y=None, height=dp(20), halign='center')
        sub_lbl.bind(size=sub_lbl.setter('text_size'))
        right_panel.add_widget(sub_lbl)
        
        btn_goto_login = OutlineButton(text="Login")
        btn_goto_login.bind(on_press=lambda x: self.show_login_screen())
        right_panel.add_widget(btn_goto_login)
        right_panel.add_widget(BoxLayout(size_hint_y=0.3))
        
        board.add_widget(right_panel)
        self.root_layout.add_widget(board)

    def send_reg_otp(self, instance):
        u = self.reg_user.text.strip()
        ph = self.reg_phone.text.strip()
        p = self.reg_pass.text
        cp = self.reg_cpass.text
        
        if not u or not ph or not p:
            self.reg_msg.text = "⚠️ All fields required!"
            return
        if u in self.data["users"]:
            self.reg_msg.text = "⚠️ Username exists!"
            return
        if p != cp:
            self.reg_msg.text = "⚠️ Passwords mismatch!"
            return
            
        otp = str(random.randint(1000, 9999))
        self.temp_reg_data = {"username": u, "phone": ph, "password": p, "otp": otp}
        print(f"\n[SMS OTP] Reg Code: {otp}\n")
        self.show_verify_reg_screen()

    def show_verify_reg_screen(self):
        self.clear()
        board = ModernAuthBoard()
        self.animate_pop_in(board)
        
        panel = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(12), size_hint=(1, 1))
        title = Label(text="🔒 Verify Account", font_size="20sp", bold=True, color=(0.15, 0.15, 0.2, 1), size_hint_y=None, height=dp(35))
        panel.add_widget(title)
        
        info_lbl = Label(text=f"Verification code sent for:\n{self.temp_reg_data.get('phone')}", font_size="12sp", color=(0.3, 0.3, 0.3, 1), size_hint_y=None, height=dp(35), halign='center')
        panel.add_widget(info_lbl)
        
        self.otp_input = TextInput(hint_text="Enter 4-digit OTP", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.93, 0.93, 0.95, 1))
        self.verify_msg = Label(text="", color=(0.9, 0.2, 0.2, 1), font_size="10sp", size_hint_y=None, height=dp(20))
        panel.add_widget(self.otp_input)
        panel.add_widget(self.verify_msg)
        
        btn_confirm = PrimaryButton(text="Confirm & Register")
        btn_confirm.bind(on_press=self.confirm_reg_otp)
        panel.add_widget(btn_confirm)
        
        btn_back = AccentButton(text="🔙 Back")
        btn_back.bind(on_press=lambda x: self.show_register_screen())
        panel.add_widget(btn_back)
        
        board.add_widget(panel)
        self.root_layout.add_widget(board)

    def confirm_reg_otp(self, instance):
        if self.otp_input.text.strip() == self.temp_reg_data.get("otp"):
            u = self.temp_reg_data["username"]
            p = self.temp_reg_data["password"]
            ph = self.temp_reg_data["phone"]
            self.data["users"][u] = {"password": p, "phone": ph}
            save_data(self.data)
            self.show_login_screen()
        else:
            self.verify_msg.text = "❌ Incorrect Verification Code!"

    def show_forgot_screen(self):
        self.clear()
        board = ModernAuthBoard()
        self.animate_pop_in(board)
        
        panel = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(10), size_hint=(1, 1))
        title = Label(text="🔑 Reset Password", font_size="20sp", bold=True, color=(0.15, 0.15, 0.2, 1), size_hint_y=None, height=dp(35))
        panel.add_widget(title)
        
        self.f_user = TextInput(hint_text="Username", multiline=False, size_hint_y=None, height=dp(38), background_color=(0.93, 0.93, 0.95, 1))
        self.f_phone = TextInput(hint_text="Registered Phone / Email", multiline=False, size_hint_y=None, height=dp(38), background_color=(0.93, 0.93, 0.95, 1))
        self.f_pass = TextInput(hint_text="New Password", password=True, multiline=False, size_hint_y=None, height=dp(38), background_color=(0.93, 0.93, 0.95, 1))
        self.f_msg = Label(text="", color=(0.9, 0.2, 0.2, 1), font_size="10sp", size_hint_y=None, height=dp(20))
        
        panel.add_widget(self.f_user)
        panel.add_widget(self.f_phone)
        panel.add_widget(self.f_pass)
        panel.add_widget(self.f_msg)
        
        btn_send_otp = PrimaryButton(text="Send Reset OTP")
        btn_send_otp.bind(on_press=self.send_forgot_otp)
        panel.add_widget(btn_send_otp)
        
        btn_back = AccentButton(text="🔙 Back to Login")
        btn_back.bind(on_press=lambda x: self.show_login_screen())
        panel.add_widget(btn_back)
        
        board.add_widget(panel)
        self.root_layout.add_widget(board)

    def send_forgot_otp(self, instance):
        u = self.f_user.text.strip()
        ph = self.f_phone.text.strip()
        p = self.f_pass.text
        if not u or not ph or not p:
            self.f_msg.text = "⚠️ All fields required!"
            return
        if u not in self.data["users"] or self.data["users"][u]["phone"] != ph:
            self.f_msg.text = "❌ User/Phone mismatch!"
            return
        otp = str(random.randint(1000, 9999))
        self.temp_forgot_data = {"username": u, "password": p, "otp": otp}
        print(f"\n[SMS OTP] Reset Code: {otp}\n")
        self.show_verify_forgot_screen()

    def show_verify_forgot_screen(self):
        self.clear()
        board = ModernAuthBoard()
        self.animate_pop_in(board)
        
        panel = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(12), size_hint=(1, 1))
        title = Label(text="🔒 Verify Reset Code", font_size="20sp", bold=True, color=(0.15, 0.15, 0.2, 1), size_hint_y=None, height=dp(35))
        panel.add_widget(title)
        
        self.f_otp_input = TextInput(hint_text="Enter 4-digit Code", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.93, 0.93, 0.95, 1))
        self.f_verify_msg = Label(text="", color=(0.9, 0.2, 0.2, 1), font_size="10sp", size_hint_y=None, height=dp(20))
        panel.add_widget(self.f_otp_input)
        panel.add_widget(self.f_verify_msg)
        
        btn_confirm = PrimaryButton(text="Confirm New Password")
        btn_confirm.bind(on_press=self.confirm_forgot_otp)
        panel.add_widget(btn_confirm)
        
        btn_back = AccentButton(text="🔙 Back")
        btn_back.bind(on_press=lambda x: self.show_forgot_screen())
        panel.add_widget(btn_back)
        
        board.add_widget(panel)
        self.root_layout.add_widget(board)

    def confirm_forgot_otp(self, instance):
        if self.f_otp_input.text.strip() == self.temp_forgot_data.get("otp"):
            u = self.temp_forgot_data["username"]
            p = self.temp_forgot_data["password"]
            self.data["users"][u]["password"] = p
            save_data(self.data)
            self.show_login_screen()
        else:
            self.f_verify_msg.text = "❌ Incorrect Code!"

    def handle_login(self, instance):
        u = self.username_input.text.strip()
        p = self.password_input.text
        if u in self.data["users"] and self.data["users"][u]["password"] == p:
            self.current_user = u
            self.show_dashboard()
        else:
            self.msg_label.text = "❌ Invalid username or password!"

    # --- BEAUTIFIED GRID DASHBOARD ---
    def show_dashboard(self):
        self.clear()
        dash_layout = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        
        top_layout = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        top_layout.add_widget(Label(text=f"👋 {self.current_user}'s Dashboard", font_size="16sp", bold=True, color=(0.15, 0.25, 0.4, 1)))
        
        btn_logout = Button(text="🚪 Logout", size_hint_x=None, width=dp(70), background_color=(0.8, 0.2, 0.2, 1))
        btn_logout.bind(on_press=lambda x: self.show_login_screen())
        top_layout.add_widget(btn_logout)
        dash_layout.add_widget(top_layout)
        
        # Beautiful 2-column Grid Menu with Large Cards
        nav_layout = GridLayout(cols=2, size_hint_y=None, height=dp(210), spacing=dp(8))
        
        features = [
            ("📅 Class Routine", self.show_routine_screen),
            ("📝 Exams & Countdown", self.show_exam_screen),
            ("📌 Tasks & Syllabus", self.show_task_screen),
            ("📊 CGPA Calculator", self.show_cgpa_screen),
            ("📸 Photo Vault", self.show_photo_screen),
            ("⏱️ Study Timer", self.show_timer_screen),
            ("📁 PDFs & Resources", self.show_resource_screen),
            ("🎨 Themes & Settings", self.show_theme_screen)
        ]
        
        for name, callback in features:
            btn = Button(text=name, background_normal='', background_color=(0.42, 0.55, 0.90, 1), color=(1,1,1,1), font_size='13sp', bold=True)
            btn.bind(on_press=lambda inst, cb=callback: cb())
            nav_layout.add_widget(btn)
            
        dash_layout.add_widget(nav_layout)
        
        toggle_layout = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(5))
        btn_today = Button(text="📅 Today's Classes", background_color=(0.1, 0.6, 0.4, 1) if self.routine_view_mode=="today" else (0.5, 0.5, 0.5, 1))
        btn_today.bind(on_press=lambda x: self.set_routine_view("today"))
        toggle_layout.add_widget(btn_today)
        
        btn_all = Button(text="📚 Full Weekly", background_color=(0.1, 0.6, 0.4, 1) if self.routine_view_mode=="all" else (0.5, 0.5, 0.5, 1))
        btn_all.bind(on_press=lambda x: self.set_routine_view("all"))
        toggle_layout.add_widget(btn_all)
        dash_layout.add_widget(toggle_layout)
        
        current_day_name = datetime.now().strftime("%A")
        header_text = f"🔥 Today's Routine ({current_day_name}):" if self.routine_view_mode=="today" else "📚 Weekly Routine:"
        dash_layout.add_widget(Label(text=header_text, font_size="13sp", bold=True, color=(0.15, 0.25, 0.4, 1), size_hint_y=None, height=dp(24)))
        
        scroll = ScrollView()
        routine_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), padding=dp(2))
        routine_layout.bind(minimum_height=routine_layout.setter('height'))
        
        filtered_routine = self.data["routine"]
        if self.routine_view_mode == "today":
            filtered_routine = [item for item in self.data["routine"] if item['day'].lower() == current_day_name.lower()]
        
        if not filtered_routine:
            routine_layout.add_widget(Label(text="No classes scheduled!", font_size="13sp", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(40)))
        else:
            for item in filtered_routine:
                card = CardBox()
                txt = f"[b]{item['day']}[/b] | {item['time']}\n[color=224466]{item['subject']}[/color]\nRoom: {item['room']} | Reminder: {item.get('reminder_min', 30)}m"
                lbl = Label(text=txt, markup=True, font_size="11sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
                lbl.bind(size=lbl.setter('text_size'))
                card.add_widget(lbl)
                routine_layout.add_widget(card)
            
        scroll.add_widget(routine_layout)
        dash_layout.add_widget(scroll)
        self.root_layout.add_widget(dash_layout)

    def set_routine_view(self, mode):
        self.routine_view_mode = mode
        self.show_dashboard()

    def show_routine_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📅 Routine & Reminders", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.r_day = TextInput(hint_text="Day (Saturday/Sunday...)", multiline=False, size_hint_y=None, height=dp(36))
        self.r_time = TextInput(hint_text="Time (e.g. 1:10-2:10 PM)", multiline=False, size_hint_y=None, height=dp(36))
        self.r_sub = TextInput(hint_text="Subject Name", multiline=False, size_hint_y=None, height=dp(36))
        self.r_room = TextInput(hint_text="Room No", multiline=False, size_hint_y=None, height=dp(36))
        
        for w in [self.r_day, self.r_time, self.r_sub, self.r_room]:
            screen.add_widget(w)
            
        btn_add = AsmaniButton(text="➕ Add Class")
        btn_add.bind(on_press=self.add_class)
        screen.add_widget(btn_add)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=dp(2))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for index, item in enumerate(self.data["routine"]):
            card = CardBox()
            txt = f"[b]{item['day']} ({item['time']})[/b]\n{item['subject']} | Room: {item['room']}"
            lbl = Label(text=txt, markup=True, font_size="11sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            card.add_widget(lbl)
            
            btn_del = Button(text="Delete", size_hint_x=None, width=dp(65), background_color=(0.9, 0.2, 0.2, 1))
            btn_del.bind(on_press=lambda inst, idx=index: self.delete_class(idx))
            card.add_widget(btn_del)
            list_layout.add_widget(card)
            
        scroll.add_widget(list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def add_class(self, instance):
        d, t, s, r = self.r_day.text.strip(), self.r_time.text.strip(), self.r_sub.text.strip(), self.r_room.text.strip()
        if d and t and s:
            self.data["routine"].append({"day": d, "time": t, "subject": s, "room": r, "reminder_min": 30, "reminder_on": True})
            save_data(self.data)
            self.show_routine_screen()

    def delete_class(self, index):
        if 0 <= index < len(self.data["routine"]):
            self.data["routine"].pop(index)
            save_data(self.data)
            self.show_routine_screen()

    def show_exam_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📝 Exams & Countdowns", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.e_type = TextInput(hint_text="Type (Mid / Final / CT)", multiline=False, size_hint_y=None, height=dp(38))
        self.e_sub = TextInput(hint_text="Subject Name", multiline=False, size_hint_y=None, height=dp(38))
        self.e_date = TextInput(hint_text="Date (YYYY-MM-DD)", multiline=False, size_hint_y=None, height=dp(38))
        
        for w in [self.e_type, self.e_sub, self.e_date]:
            screen.add_widget(w)
            
        btn_add = AsmaniButton(text="➕ Add Exam")
        btn_add.bind(on_press=self.add_exam)
        screen.add_widget(btn_add)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=dp(2))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for index, item in enumerate(self.data.get("exams", [])):
            card = CardBox()
            txt = f"[b]{item['type']} : {item['subject']}[/b]\n📅 Date: {item['date']}"
            lbl = Label(text=txt, markup=True, font_size="12sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            card.add_widget(lbl)
            
            btn_del = Button(text="Delete", size_hint_x=None, width=dp(70), background_color=(0.9, 0.2, 0.2, 1))
            btn_del.bind(on_press=lambda inst, idx=index: self.delete_exam(idx))
            card.add_widget(btn_del)
            list_layout.add_widget(card)
            
        scroll.add_widget(list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def add_exam(self, instance):
        t, s, d = self.e_type.text.strip(), self.e_sub.text.strip(), self.e_date.text.strip()
        if t and s:
            self.data["exams"].append({"type": t, "subject": s, "date": d})
            save_data(self.data)
            self.show_exam_screen()

    def delete_exam(self, index):
        if 0 <= index < len(self.data["exams"]):
            self.data["exams"].pop(index)
            save_data(self.data)
            self.show_exam_screen()

    def show_task_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📌 Quick Notes & Tasks", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.t_sub = TextInput(hint_text="Subject / Topic", multiline=False, size_hint_y=None, height=dp(38))
        self.t_text = TextInput(hint_text="Task / Syllabus Checklist Detail", multiline=False, size_hint_y=None, height=dp(38))
        
        for w in [self.t_sub, self.t_text]:
            screen.add_widget(w)
            
        btn_add = AsmaniButton(text="➕ Add Task")
        btn_add.bind(on_press=self.add_task)
        screen.add_widget(btn_add)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=dp(2))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for idx, t in enumerate(self.data["tasks"]):
            card = CardBox()
            txt = f"[b]{t.get('subject', 'General')}[/b]\n• {t.get('text', '')}"
            lbl = Label(text=txt, markup=True, font_size="12sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            card.add_widget(lbl)
            
            btn_done = Button(text="Done", size_hint_x=None, width=dp(70), background_color=(0.2, 0.7, 0.3, 1))
            btn_done.bind(on_press=lambda inst, i=idx: self.delete_task(i))
            card.add_widget(btn_done)
            list_layout.add_widget(card)
            
        scroll.add_widget(list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def add_task(self, instance):
        sub, text = self.t_sub.text.strip(), self.t_text.text.strip()
        if text:
            self.data["tasks"].append({"subject": sub if sub else "General", "text": text})
            save_data(self.data)
            self.show_task_screen()

    def delete_task(self, index):
        if 0 <= index < len(self.data["tasks"]):
            self.data["tasks"].pop(index)
            save_data(self.data)
            self.show_task_screen()

    def show_cgpa_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📊 CGPA & Grade Calculator", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.cg_credit = TextInput(hint_text="Credit Hours (e.g. 3)", multiline=False, size_hint_y=None, height=dp(38))
        self.cg_point = TextInput(hint_text="Grade Point (e.g. 3.75)", multiline=False, size_hint_y=None, height=dp(38))
        self.cg_result = Label(text="Enter your grades to calculate CGPA", font_size="14sp", bold=True, color=(0.1, 0.4, 0.2, 1), size_hint_y=None, height=dp(35))
        
        screen.add_widget(self.cg_credit)
        screen.add_widget(self.cg_point)
        screen.add_widget(self.cg_result)
        
        if "cgpa_list" not in self.data:
            self.data["cgpa_list"] = []
            
        btn_calc = AsmaniButton(text="🧮 Add Subject & Calculate")
        btn_calc.bind(on_press=self.calc_cgpa)
        screen.add_widget(btn_calc)
        
        btn_clear_cg = Button(text="Reset List", size_hint_y=None, height=dp(35), background_color=(0.8,0.2,0.2,1))
        btn_clear_cg.bind(on_press=self.reset_cgpa)
        screen.add_widget(btn_clear_cg)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), padding=dp(2))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        total_cred = sum(x['credit'] for x in self.data["cgpa_list"])
        total_gp = sum(x['credit'] * x['point'] for x in self.data["cgpa_list"])
        cgpa_val = (total_gp / total_cred) if total_cred > 0 else 0.0
        self.cg_result.text = f"Total Credits: {total_cred} | Calculated CGPA: {cgpa_val:.2f}"
        
        for idx, item in enumerate(self.data["cgpa_list"]):
            card = CardBox()
            card.add_widget(Label(text=f"Credit: {item['credit']} | Point: {item['point']}", font_size="12sp", color=(0.15,0.15,0.15,1)))
            list_layout.add_widget(card)
            
        scroll.add_widget(list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def calc_cgpa(self, instance):
        try:
            c = float(self.cg_credit.text.strip())
            p = float(self.cg_point.text.strip())
            if "cgpa_list" not in self.data:
                self.data["cgpa_list"] = []
            self.data["cgpa_list"].append({"credit": c, "point": p})
            save_data(self.data)
            self.show_cgpa_screen()
        except ValueError:
            self.cg_result.text = "⚠️ Please enter valid numbers!"

    def reset_cgpa(self, instance):
        self.data["cgpa_list"] = []
        save_data(self.data)
        self.show_cgpa_screen()

    # --- UPDATED PHOTO VAULT WITH CAMERA & GALLERY ACCESS ---
    def show_photo_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📸 Photo Vault & Document Snaps", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.p_title = TextInput(hint_text="Photo Title / Note", multiline=False, size_hint_y=None, height=dp(38))
        self.p_path = TextInput(hint_text="Selected Photo Path", multiline=False, size_hint_y=None, height=dp(38))
        
        screen.add_widget(self.p_title)
        screen.add_widget(self.p_path)
        
        # Camera & Gallery Picker Buttons
        picker_box = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(40))
        btn_cam = Button(text="📸 Open Camera", background_color=(0.2, 0.6, 0.8, 1))
        btn_cam.bind(on_press=self.take_photo)
        picker_box.add_widget(btn_cam)
        
        btn_gal = Button(text="🖼️ Pick Gallery", background_color=(0.15, 0.7, 0.5, 1))
        btn_gal.bind(on_press=self.pick_gallery_photo)
        picker_box.add_widget(btn_gal)
        screen.add_widget(picker_box)
        
        btn_add = AsmaniButton(text="➕ Save Snap to Vault")
        btn_add.bind(on_press=self.add_photo)
        screen.add_widget(btn_add)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10), padding=dp(2))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for idx, item in enumerate(self.data.get("photos", [])):
            card = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(90), padding=dp(5), spacing=dp(10))
            if item.get('path') and os.path.exists(item['path']):
                card.add_widget(AsyncImage(source=item['path'], size_hint_x=None, width=dp(80)))
            else:
                card.add_widget(Label(text="[Image]", size_hint_x=None, width=dp(80), font_size="10sp"))
            card.add_widget(Label(text=item['title'], font_size="13sp", color=(0.15,0.15,0.15,1)))
            
            btn_del = Button(text="Del", size_hint_x=None, width=dp(50), background_color=(0.9,0.2,0.2,1))
            btn_del.bind(on_press=lambda inst, i=idx: self.delete_photo(i))
            card.add_widget(btn_del)
            list_layout.add_widget(card)
            
        scroll.add_widget(list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def take_photo(self, instance):
        if camera:
            save_filename = os.path.join(App.get_running_app().user_data_dir, f"photo_{int(datetime.now().timestamp())}.jpg")
            try:
                camera.take_picture(filename=save_filename, on_complete=lambda path: setattr(self.p_path, 'text', path))
            except Exception:
                self.p_path.text = save_filename
        else:
            self.p_path.text = "Camera access requires Android app build!"

    def pick_gallery_photo(self, instance):
        if filechooser:
            try:
                filechooser.open_file(on_selection=lambda selection: setattr(self.p_path, 'text', selection[0]) if selection else None)
            except Exception:
                pass
        else:
            self.p_path.text = "Filechooser requires Plyer library!"

    def add_photo(self, instance):
        t, p = self.p_title.text.strip(), self.p_path.text.strip()
        if t:
            self.data["photos"].append({"title": t, "path": p})
            save_data(self.data)
            self.show_photo_screen()

    def delete_photo(self, index):
        if 0 <= index < len(self.data["photos"]):
            self.data["photos"].pop(index)
            save_data(self.data)
            self.show_photo_screen()

    def show_timer_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        screen.add_widget(Label(text="⏱️ Pomodoro Study Timer", font_size="20sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(40)))
        
        self.timer_display = Label(text="25 : 00", font_size="40sp", bold=True, color=(0.1, 0.5, 0.3, 1), size_hint_y=None, height=dp(80))
        screen.add_widget(self.timer_display)
        
        info_lbl = Label(text="Focus for 25 minutes, then take a 5 min break!", font_size="13sp", color=(0.3,0.3,0.3,1), size_hint_y=None, height=dp(30))
        screen.add_widget(info_lbl)
        
        btn_start = AsmaniButton(text="🚀 Start Focus Session")
        btn_start.bind(on_press=lambda x: setattr(self.timer_display, 'text', "Session Running... (25:00)"))
        screen.add_widget(btn_start)
        
        screen.add_widget(BoxLayout())
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    # --- UPDATED RESOURCE SCREEN WITH PDF / FILE PICKER ---
    def show_resource_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📁 Study Resources & PDFs", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.res_name = TextInput(hint_text="Resource / Book Name", multiline=False, size_hint_y=None, height=dp(38))
        self.res_link = TextInput(hint_text="Selected PDF File Path", multiline=False, size_hint_y=None, height=dp(38))
        
        screen.add_widget(self.res_name)
        screen.add_widget(self.res_link)
        
        btn_pick_pdf = Button(text="📁 Choose PDF / File from Storage", size_hint_y=None, height=dp(38), background_color=(0.2, 0.6, 0.8, 1))
        btn_pick_pdf.bind(on_press=self.pick_pdf_file)
        screen.add_widget(btn_pick_pdf)
        
        btn_add = AsmaniButton(text="➕ Save Resource")
        btn_add.bind(on_press=self.add_resource)
        screen.add_widget(btn_add)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=dp(2))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for idx, item in enumerate(self.data.get("resources", [])):
            card = CardBox()
            card.add_widget(Label(text=f"[b]{item['name']}[/b]\nPath: {item['link']}", markup=True, font_size="12sp", color=(0.15,0.15,0.15,1)))
            
            btn_del = Button(text="Del", size_hint_x=None, width=dp(50), background_color=(0.9,0.2,0.2,1))
            btn_del.bind(on_press=lambda inst, i=idx: self.delete_resource(i))
            card.add_widget(btn_del)
            list_layout.add_widget(card)
            
        scroll.add_widget(list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def pick_pdf_file(self, instance):
        if filechooser:
            try:
                filechooser.open_file(on_selection=lambda selection: setattr(self.res_link, 'text', selection[0]) if selection else None)
            except Exception:
                pass
        else:
            self.res_link.text = "Filechooser requires Plyer library!"

    def add_resource(self, instance):
        n, l = self.res_name.text.strip(), self.res_link.text.strip()
        if n:
            self.data["resources"].append({"name": n, "link": l})
            save_data(self.data)
            self.show_resource_screen()

    def delete_resource(self, index):
        if 0 <= index < len(self.data["resources"]):
            self.data["resources"].pop(index)
            save_data(self.data)
            self.show_resource_screen()

    def show_theme_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        screen.add_widget(Label(text="🎨 Custom Dashboard Themes", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        btn_asmani = AsmaniButton(text="💙 Soft Light Theme")
        btn_asmani.bind(on_press=lambda x: self.change_theme((0.90, 0.92, 0.96, 1)))
        screen.add_widget(btn_asmani)
        
        btn_emerald = Button(text="💚 Emerald Dark Theme", background_normal='', background_color=(0.1, 0.5, 0.3, 1), size_hint_y=None, height=dp(42))
        btn_emerald.bind(on_press=lambda x: self.change_theme((0.15, 0.25, 0.2, 1)))
        screen.add_widget(btn_emerald)
        
        btn_sunset = Button(text="🧡 Sunset Orange Theme", background_normal='', background_color=(0.8, 0.4, 0.2, 1), size_hint_y=None, height=dp(42))
        btn_sunset.bind(on_press=lambda x: self.change_theme((0.9, 0.7, 0.5, 1)))
        screen.add_widget(btn_sunset)
        
        btn_raw_json = Button(text="📄 View Raw JSON File", background_color=(0.3, 0.3, 0.5, 1), size_hint_y=None, height=dp(40))
        btn_raw_json.bind(on_press=lambda x: self.show_json_viewer_screen())
        screen.add_widget(btn_raw_json)
        
        screen.add_widget(BoxLayout())
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def show_json_viewer_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📄 Raw JSON File Viewer", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        data_path = get_data_file()
        path_lbl = Label(text=f"Location: {data_path}", font_size="10sp", color=(0.3, 0.3, 0.3, 1), size_hint_y=None, height=dp(30))
        screen.add_widget(path_lbl)
        
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            file_content = f"Could not read json file: {str(e)}"
            
        scroll = ScrollView()
        txt_input = TextInput(text=file_content, readonly=True, multiline=True, font_size="12sp")
        scroll.add_widget(txt_input)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def change_theme(self, color_tuple):
        self.bg_color_inst.rgba = color_tuple
        self.data["theme"] = str(color_tuple)
        save_data(self.data)
        self.show_dashboard()

if __name__ == "__main__":
    StudentApp().run()
