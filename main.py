#Kivy 2.0.1
#KivyMD 1.1.0
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from  kivy.core.window import Window




class WindowManager(ScreenManager):
    pass

#App window size
Window.size = (700, 700)

class TestApp(MDApp):
    def build(self):
        self.title = "MY GARAGE"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = 'Gray'
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file('main.kv')

if __name__ == '__main__':
    TestApp().run()