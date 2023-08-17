from kivy.app import App
from kivy.uix.label import Label


class Main(App):
    def build(self):
        return Label(text='Hello World')


Main().run()