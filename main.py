from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager


class WindowManager(ScreenManager):
    pass

class TestApp(App):
    def build(self):
        return Builder.load_file('main.kv')  # this method can be eliminated if `main.kv` is renamed to `test.kv`

if __name__ == '__main__':
    TestApp().run()