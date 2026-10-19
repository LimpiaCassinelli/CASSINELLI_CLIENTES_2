bloque = '''from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import traceback

class ManejadorErrores(ExceptionHandler):
    def handle_exception(self, inst):
        txt = "".join(traceback.format_exception(type(inst), inst, inst.__traceback__))[-700:]
        def mostrar(dt):
            Popup(title="ERROR", content=Label(text=txt, font_size="11sp"),
                  size_hint=(0.95, 0.8)).open()
        Clock.schedule_once(mostrar, 0)
        return ExceptionManager.PASS

ExceptionManager.add_handler(ManejadorErrores())

'''
s = open("main.py", encoding="utf-8").read()
if "ManejadorErrores" in s:
    print("Ya estaba aplicado")
else:
    open("main.py", "w", encoding="utf-8").write(bloque + s)
    print("Parche aplicado")
