from kivy.base import ExceptionHandler, ExceptionManager
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

# -*- coding: utf-8 -*-
"""CASSINELLI CLIENTES - app de clientes (Kivy)."""
import os
import re
import json
import time
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line, Triangle
from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import escape_markup

# ---------------------------------------------------------------- paleta
VERDE = (0.043, 0.384, 0.200, 1)
VERDE_OSC = (0.027, 0.290, 0.149, 1)
MENTA = (0.894, 0.961, 0.910, 1)
BLANCO = (1, 1, 1, 1)
TEXTO = (0.063, 0.208, 0.125, 1)
GRIS = (0.42, 0.50, 0.45, 1)
GRIS_C = (0.62, 0.68, 0.64, 1)
BORDE = (0.78, 0.87, 0.81, 1)
FONDO = (0.957, 0.980, 0.961, 1)
ORO = (1.0, 0.82, 0.18, 1)
ROJO = (0.78, 0.18, 0.18, 1)
INACTIVO = (0.66, 0.72, 0.68, 1)

Window.clearcolor = FONDO
Window.softinput_mode = "below_target"

CENTRO = {"center_y": 0.5}


# ---------------------------------------------------------------- utilidades
def hoy():
    return datetime.now().strftime("%d/%m/%Y")


def parse_monto(t):
    try:
        return float(str(t).replace(",", ".").strip())
    except Exception:
        return None


def parse_fecha(t):
    n = re.findall(r"\d+", str(t))
    if len(n) != 3:
        return None
    d, m, a = int(n[0]), int(n[1]), int(n[2])
    if a < 100:
        a += 2000
    try:
        return datetime(a, m, d).strftime("%d/%m/%Y")
    except ValueError:
        return None


def filtro_fecha(s, deshacer):
    return "".join(ch for ch in s if ch in "0123456789/ ")


def soles(x):
    return "S/ %.2f" % float(x)


def esc(t):
    return escape_markup(str(t))


def buscar_img(*claves):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes")
    try:
        archivos = sorted(os.listdir(base))
    except Exception:
        return None
    for k in claves:
        for a in archivos:
            b = a.lower()
            if k in b and b.endswith((".png", ".jpg", ".jpeg", ".webp")):
                return os.path.join(base, a)
    return None


def normalizar(c):
    c.setdefault("compras", 0)
    c.setdefault("pagos", 0)
    cr = c.setdefault("credito", {})
    cr.setdefault("estado", "ninguno")
    cr.setdefault("monto", 0)
    cr.setdefault("fecha", "")
    c.setdefault("deuda", 0)
    c.setdefault("socio", False)
    c.setdefault("socio_pedido", False)
    c.setdefault("socio_monto", "")
    c.setdefault("socio_fecha", "")
    c.setdefault("creado", hoy())


# ---------------------------------------------------------------- widgets base
def T(texto, tam=14, color=TEXTO, bold=False, halign="left", italic=False, **kw):
    """Texto que se ajusta en varias líneas y crece en alto."""
    l = Label(text=texto, font_size=sp(tam), color=color, bold=bold,
              italic=italic, halign=halign, valign="middle", markup=True,
              size_hint_y=None, **kw)
    l.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
    l.bind(texture_size=lambda i, s: setattr(i, "height", s[1] + dp(2)))
    return l


def P(texto, tam=14, color=TEXTO, bold=False, halign="left", **kw):
    """Texto que llena el espacio que le dan (para filas de alto fijo)."""
    l = Label(text=texto, font_size=sp(tam), color=color, bold=bold,
              halign=halign, valign="middle", markup=True, **kw)
    l.bind(size=lambda i, s: setattr(i, "text_size", (s[0], s[1])))
    return l


class Caja(BoxLayout):
    def __init__(self, fondo=BLANCO, radio=14, borde=None, **kw):
        super().__init__(**kw)
        if isinstance(radio, (list, tuple)):
            self._rad = [dp(x) for x in radio]
            self._lin = None
        else:
            self._rad = [dp(radio)]
            self._lin = dp(radio)
        self._borde = borde if (borde and self._lin) else None
        with self.canvas.before:
            self._col = Color(*fondo)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=self._rad)
            if self._borde:
                Color(*self._borde)
                self._bl = Line(rounded_rectangle=(self.x, self.y, self.width,
                                                   self.height, self._lin),
                                width=dp(1))
        self.bind(pos=self._act, size=self._act)

    def _act(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size
        if self._borde:
            self._bl.rounded_rectangle = (self.x, self.y, self.width,
                                          self.height, self._lin)

    def pintar(self, color):
        self._col.rgba = color


def V(fondo=None, radio=14, borde=None, pad=0, sp_=8, **kw):
    """Columna que crece según su contenido."""
    padding = dp(pad) if not isinstance(pad, (list, tuple)) else [dp(x) for x in pad]
    if fondo is None:
        c = BoxLayout(orientation="vertical", size_hint_y=None,
                      padding=padding, spacing=dp(sp_), **kw)
    else:
        c = Caja(fondo=fondo, radio=radio, borde=borde, orientation="vertical",
                 size_hint_y=None, padding=padding, spacing=dp(sp_), **kw)
    c.bind(minimum_height=c.setter("height"))
    return c


def H(alto, **kw):
    kw.setdefault("spacing", dp(10))
    return BoxLayout(orientation="horizontal", size_hint_y=None,
                     height=dp(alto), **kw)


def scroll(contenido):
    sv = ScrollView(do_scroll_x=False, bar_width=dp(3))
    sv.add_widget(contenido)
    return sv


class Ico(Widget):
    """Iconos dibujados (no dependen de ninguna fuente)."""

    def __init__(self, kind="persona", color=VERDE, fondo=None, detalle=BLANCO, **kw):
        super().__init__(**kw)
        self.kind = kind
        self.color = color
        self.fondo = fondo
        self.detalle = detalle
        self.bind(pos=self._d, size=self._d)
        self._d()

    def _d(self, *a):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        s = min(w, h)
        if s <= 0:
            return
        cx, cy = x + w / 2.0, y + h / 2.0
        k = self.kind
        with self.canvas:
            if self.fondo is not None:
                Color(*self.fondo)
                Ellipse(pos=(cx - s / 2.0, cy - s / 2.0), size=(s, s))
                s = s * 0.60
            lw = max(dp(1.3), s * 0.075)

            def X(f):
                return cx + f * s

            def Y(f):
                return cy + f * s

            Color(*self.color)
            if k == "persona":
                Ellipse(pos=(X(-0.17), Y(0.04)), size=(0.34 * s, 0.34 * s))
                RoundedRectangle(pos=(X(-0.3), Y(-0.36)), size=(0.6 * s, 0.34 * s),
                                 radius=[0.3 * s, 0.3 * s, 0, 0])
            elif k == "telefono":
                RoundedRectangle(pos=(X(-0.18), Y(-0.36)), size=(0.36 * s, 0.72 * s),
                                 radius=[0.08 * s])
                Color(*self.detalle)
                Rectangle(pos=(X(-0.12), Y(-0.2)), size=(0.24 * s, 0.46 * s))
                Ellipse(pos=(X(-0.04), Y(-0.32)), size=(0.08 * s, 0.08 * s))
            elif k == "escudo":
                Rectangle(pos=(X(-0.3), Y(-0.02)), size=(0.6 * s, 0.36 * s))
                Triangle(points=[X(-0.3), Y(-0.02), X(0.3), Y(-0.02), X(0), Y(-0.40)])
                Color(*self.detalle)
                Line(points=[X(-0.14), Y(0.05), X(-0.03), Y(-0.07), X(0.16), Y(0.17)],
                     width=lw * 1.4)
            elif k == "tarjeta":
                RoundedRectangle(pos=(X(-0.36), Y(-0.23)), size=(0.72 * s, 0.46 * s),
                                 radius=[0.06 * s])
                Color(*self.detalle)
                Rectangle(pos=(X(-0.36), Y(0.04)), size=(0.72 * s, 0.08 * s))
                Rectangle(pos=(X(-0.27), Y(-0.15)), size=(0.2 * s, 0.05 * s))
            elif k == "check":
                Line(points=[X(-0.3), Y(0.0), X(-0.1), Y(-0.2), X(0.3), Y(0.22)],
                     width=lw * 1.6)
            elif k == "check_c":
                Ellipse(pos=(X(-0.5), Y(-0.5)), size=(s, s))
                Color(*self.detalle)
                Line(points=[X(-0.24), Y(0.0), X(-0.07), Y(-0.17), X(0.26), Y(0.17)],
                     width=lw * 1.5)
            elif k == "trofeo":
                RoundedRectangle(pos=(X(-0.2), Y(-0.02)), size=(0.4 * s, 0.38 * s),
                                 radius=[0, 0, 0.2 * s, 0.2 * s])
                Rectangle(pos=(X(-0.04), Y(-0.2)), size=(0.08 * s, 0.2 * s))
                Rectangle(pos=(X(-0.17), Y(-0.28)), size=(0.34 * s, 0.08 * s))
                Line(ellipse=(X(-0.37), Y(0.1), 0.2 * s, 0.2 * s), width=lw)
                Line(ellipse=(X(0.17), Y(0.1), 0.2 * s, 0.2 * s), width=lw)
            elif k == "apreton":
                Line(circle=(X(-0.13), cy, 0.25 * s), width=lw * 1.3)
                Line(circle=(X(0.13), cy, 0.25 * s), width=lw * 1.3)
            elif k == "grupo":
                Ellipse(pos=(X(-0.1), Y(0.08)), size=(0.2 * s, 0.2 * s))
                RoundedRectangle(pos=(X(-0.2), Y(-0.28)), size=(0.4 * s, 0.3 * s),
                                 radius=[0.2 * s, 0.2 * s, 0, 0])
                Ellipse(pos=(X(-0.37), Y(0.06)), size=(0.15 * s, 0.15 * s))
                Ellipse(pos=(X(0.22), Y(0.06)), size=(0.15 * s, 0.15 * s))
                RoundedRectangle(pos=(X(-0.42), Y(-0.28)), size=(0.2 * s, 0.22 * s),
                                 radius=[0.1 * s, 0.1 * s, 0, 0])
                RoundedRectangle(pos=(X(0.22), Y(-0.28)), size=(0.2 * s, 0.22 * s),
                                 radius=[0.1 * s, 0.1 * s, 0, 0])
            elif k == "corona":
                Rectangle(pos=(X(-0.32), Y(-0.2)), size=(0.64 * s, 0.13 * s))
                Triangle(points=[X(-0.32), Y(-0.07), X(-0.32), Y(0.26), X(-0.04), Y(-0.07)])
                Triangle(points=[X(-0.2), Y(-0.07), X(0), Y(0.34), X(0.2), Y(-0.07)])
                Triangle(points=[X(0.04), Y(-0.07), X(0.32), Y(0.26), X(0.32), Y(-0.07)])
            elif k == "calendario":
                Line(rounded_rectangle=(X(-0.3), Y(-0.28), 0.6 * s, 0.52 * s, 0.05 * s),
                     width=lw)
                Rectangle(pos=(X(-0.3), Y(0.12)), size=(0.6 * s, 0.12 * s))
                for i in range(3):
                    for j in range(2):
                        Rectangle(pos=(X(-0.2 + i * 0.17), Y(-0.19 + j * 0.14)),
                                  size=(0.09 * s, 0.07 * s))
            elif k == "moneda":
                Ellipse(pos=(X(-0.32), Y(-0.32)), size=(0.64 * s, 0.64 * s))
                Color(*self.detalle)
                Line(circle=(cx, cy, 0.21 * s), width=lw)
                Line(points=[cx, Y(0.1), cx, Y(-0.1)], width=lw)
            elif k == "lupa":
                Line(circle=(X(-0.08), Y(0.06), 0.2 * s), width=lw * 1.2)
                Line(points=[X(0.07), Y(-0.09), X(0.27), Y(-0.29)], width=lw * 1.4)
            elif k == "menu":
                for j in (-0.2, 0.0, 0.2):
                    Line(points=[X(-0.28), Y(j), X(0.28), Y(j)], width=lw * 1.3)
            elif k == "flecha":
                Line(points=[X(0.24), cy, X(-0.24), cy], width=lw * 1.4)
                Line(points=[X(-0.04), Y(0.2), X(-0.24), cy, X(-0.04), Y(-0.2)],
                     width=lw * 1.4)
            elif k == "flecha_der":
                Line(points=[X(-0.24), cy, X(0.24), cy], width=lw * 1.4)
                Line(points=[X(0.04), Y(0.2), X(0.24), cy, X(0.04), Y(-0.2)],
                     width=lw * 1.4)
            elif k == "casa":
                Triangle(points=[X(-0.34), Y(0.02), X(0.34), Y(0.02), X(0), Y(0.34)])
                Rectangle(pos=(X(-0.23), Y(-0.3)), size=(0.46 * s, 0.32 * s))
            elif k == "ventas":
                Line(rounded_rectangle=(X(-0.25), Y(-0.33), 0.5 * s, 0.6 * s, 0.05 * s),
                     width=lw)
                Rectangle(pos=(X(-0.12), Y(0.24)), size=(0.24 * s, 0.1 * s))
                Line(points=[X(-0.12), Y(0.06), X(0.12), Y(0.06)], width=lw)
                Line(points=[X(-0.12), Y(-0.08), X(0.12), Y(-0.08)], width=lw)
                Line(points=[X(-0.12), Y(-0.22), X(0.04), Y(-0.22)], width=lw)
            elif k == "mas":
                for j in (-0.24, 0.0, 0.24):
                    Ellipse(pos=(X(j) - 0.06 * s, cy - 0.06 * s), size=(0.12 * s, 0.12 * s))


class BotonIco(ButtonBehavior, Ico):
    def __init__(self, kind="persona", **kw):
        super().__init__(kind=kind, **kw)


class Boton(ButtonBehavior, BoxLayout):
    def __init__(self, texto, relleno=True, icono=None, der=False, alto=52,
                 color=VERDE, tam=16, **kw):
        super().__init__(orientation="horizontal", size_hint_y=None,
                         height=dp(alto), spacing=dp(10),
                         padding=[dp(14), 0, dp(14), 0], **kw)
        self.relleno = relleno
        self.base = color
        with self.canvas.before:
            self._col = Color(*(color if relleno else BLANCO))
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(12)])
            if not relleno:
                self._col2 = Color(*color)
                self._lin = Line(rounded_rectangle=(self.x, self.y, self.width,
                                                    self.height, dp(12)),
                                 width=dp(1.6))
        self.bind(pos=self._act, size=self._act)
        fg = BLANCO if relleno else color
        det = color if relleno else BLANCO
        self.lbl = P(texto, tam, fg, True, "center")
        if icono and not der:
            self.add_widget(Ico(icono, color=fg, detalle=det, size_hint=(None, None),
                                size=(dp(30), dp(30)), pos_hint=CENTRO))
        self.add_widget(self.lbl)
        if icono and der:
            self.add_widget(Ico(icono, color=fg, detalle=det, size_hint=(None, None),
                                size=(dp(26), dp(26)), pos_hint=CENTRO))

    def _act(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size
        if not self.relleno:
            self._lin.rounded_rectangle = (self.x, self.y, self.width,
                                           self.height, dp(12))

    def activo(self, si):
        self.disabled = not si
        c = self.base if si else GRIS_C
        if self.relleno:
            self._col.rgba = c
        else:
            self._col2.rgba = c
            self.lbl.color = c

    def on_press(self):
        self.opacity = 0.8

    def on_release(self):
        self.opacity = 1


class Campo(Caja):
    def __init__(self, icono, hint, prefijo="", filtro=None, **kw):
        super().__init__(fondo=BLANCO, radio=10, borde=BORDE,
                         orientation="horizontal", size_hint_y=None,
                         height=dp(48), padding=[dp(12), 0, dp(10), 0],
                         spacing=dp(10), **kw)
        if icono:
            self.add_widget(Ico(icono, color=VERDE, size_hint=(None, None),
                                size=(dp(24), dp(24)), pos_hint=CENTRO))
        if prefijo:
            self.add_widget(Label(text=prefijo, color=TEXTO, bold=True,
                                  font_size=sp(15), size_hint_x=None, width=dp(26)))
        self.inp = TextInput(hint_text=hint, multiline=False,
                             background_normal="", background_active="",
                             background_color=(0, 0, 0, 0),
                             foreground_color=TEXTO, hint_text_color=GRIS_C,
                             cursor_color=VERDE, font_size=sp(15),
                             padding=[0, dp(13), 0, dp(13)], input_filter=filtro,
                             write_tab=False)
        self.add_widget(self.inp)

    @property
    def valor(self):
        return self.inp.text.strip()


class FilaBtn(ButtonBehavior, Caja):
    pass


class Tab(ButtonBehavior, Caja):
    pass


class Hero(ButtonBehavior, FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*VERDE_OSC)
            self._r1 = Rectangle(pos=self.pos, size=self.size)
            Color(*VERDE)
            self._e1 = Ellipse(pos=self.pos, size=(10, 10))
        self.bind(pos=self._act, size=self._act)

    def _act(self, *a):
        self._r1.pos = self.pos
        self._r1.size = self.size
        w, h = self.size
        self._e1.size = (w * 1.3, h * 1.1)
        self._e1.pos = (self.x - w * 0.15, self.y + h * 0.25)


def barra(n, total):
    b = H(10, spacing=0)
    f = max(0.02, min(1.0, float(n) / total))
    b.add_widget(Caja(fondo=VERDE, radio=5, size_hint_x=f))
    if f < 1:
        b.add_widget(Caja(fondo=MENTA, radio=5, size_hint_x=1 - f))
    return b


# ---------------------------------------------------------------- aplicación
class ClientesApp(App):
    title = "CASSINELLI CLIENTES"

    # ----- datos
    def build(self):
        self.ruta_datos = os.path.join(self.user_data_dir, "cassinelli_clientes.json")
        self.cargar()
        self.pila = []
        self.modal = None
        self._toques = []
        self.adm_tab = "inicio"
        self.adm_det = None
        self.reparto = {}
        self.sm = ScreenManager(transition=SlideTransition(duration=0.18))
        for n in ("inicio", "c1", "c2", "socio", "diez", "admin"):
            self.sm.add_widget(Screen(name=n))
        self.constructores = {
            "inicio": self.v_inicio,
            "c1": lambda: self.v_credito(1),
            "c2": lambda: self.v_credito(2),
            "socio": self.v_socio,
            "diez": self.v_diez,
        }
        self.refrescar()
        Window.bind(on_keyboard=self._tecla)
        return self.sm

    def on_pause(self):
        return True

    def cargar(self):
        try:
            with open(self.ruta_datos, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            d = {}
        d.setdefault("clientes", [])
        d.setdefault("ventas", [])
        d.setdefault("actual", None)
        cfg = d.setdefault("config", {})
        cfg.setdefault("pin", "1234")
        cfg.setdefault("porcentaje", 10)
        for c in d["clientes"]:
            normalizar(c)
        self.d = d

    def guardar(self):
        try:
            tmp = self.ruta_datos + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.d, f, ensure_ascii=False, indent=1)
            os.replace(tmp, self.ruta_datos)
        except Exception as e:
            print("No se pudo guardar:", e)

    def cliente(self, cid):
        return next((c for c in self.d["clientes"] if c["id"] == cid), None)

    def actual(self):
        return self.cliente(self.d.get("actual"))

    def nuevo_cliente(self, nombre, tel):
        cid = max([c["id"] for c in self.d["clientes"]] + [0]) + 1
        c = {"id": cid, "nombre": nombre, "telefono": tel}
        normalizar(c)
        self.d["clientes"].append(c)
        return c

    def estado_socio(self, c):
        if c["socio"]:
            return "Activo"
        return "Pendiente" if c["compras"] >= 10 else "No aplica"

    # ----- navegación
    def refrescar(self):
        n = self.sm.current
        if n == "admin":
            self.adm_ir(self.adm_tab, self.adm_det)
            return
        scr = self.sm.get_screen(n)
        scr.clear_widgets()
        scr.add_widget(self.constructores[n]())

    def ir(self, nombre, volver=False):
        if nombre != "admin":
            scr = self.sm.get_screen(nombre)
            scr.clear_widgets()
            scr.add_widget(self.constructores[nombre]())
        actual = self.sm.current
        if not volver and actual != nombre:
            self.pila.append(actual)
        self.sm.transition.direction = "right" if volver else "left"
        self.sm.current = nombre

    def atras(self):
        if self.pila:
            self.ir(self.pila.pop(), volver=True)

    def _tecla(self, *a):
        if len(a) < 2 or a[1] != 27:
            return False
        if self.modal is not None:
            self.modal.dismiss()
            return True
        if self.sm.current == "admin":
            if self.adm_det is not None:
                self.adm_ir(self.adm_tab)
            elif self.adm_tab != "inicio":
                self.adm_ir("inicio")
            else:
                self.salir_admin()
            return True
        if self.pila:
            self.atras()
            return True
        return False

    # ----- diálogos
    def dialogo(self, titulo, widgets, ok="Guardar", cb=None, cancelar=True):
        mv = ModalView(size_hint=(0.9, None), height=dp(260), background="",
                       background_color=(0, 0, 0, 0), overlay_color=(0, 0, 0, 0.55),
                       auto_dismiss=False)
        caja = V(fondo=BLANCO, radio=16, pad=16, sp_=10)
        caja.add_widget(T(titulo, 19, TEXTO, True))
        for w in widgets:
            caja.add_widget(w)
        fila = H(48)
        if cancelar:
            b0 = Boton("Cancelar", relleno=False, alto=48, tam=15)
            b0.bind(on_release=lambda *a: mv.dismiss())
            fila.add_widget(b0)
        b1 = Boton(ok, alto=48, tam=15)

        def aceptar(*a):
            if cb is None or cb() is not False:
                mv.dismiss()
        b1.bind(on_release=aceptar)
        fila.add_widget(b1)
        caja.add_widget(fila)
        caja.bind(height=lambda i, h: setattr(mv, "height", h))
        mv.add_widget(caja)
        self.modal = mv
        mv.bind(on_dismiss=lambda *a: setattr(self, "modal", None))
        mv.open()

    def aviso(self, titulo, texto, ok="Aceptar"):
        self.dialogo(titulo, [T(esc(texto), 15, TEXTO)], ok, None, cancelar=False)

    # ----- cabecera de las pantallas del cliente
    def cabecera(self, atras=True):
        h = Caja(fondo=VERDE_OSC, radio=0, orientation="horizontal",
                 size_hint_y=None, height=dp(84),
                 padding=[dp(8), dp(8), dp(8), dp(8)])
        if atras:
            b = BotonIco("flecha", color=BLANCO, size_hint=(None, None),
                         size=(dp(44), dp(44)), pos_hint=CENTRO)
            b.bind(on_release=lambda *a: self.atras())
            h.add_widget(b)
        else:
            h.add_widget(Widget(size_hint_x=None, width=dp(44)))
        col = BoxLayout(orientation="vertical")
        col.add_widget(P("CASSINELLI", 27, BLANCO, True, "center", size_hint_y=0.62))
        col.add_widget(P("productos de limpieza", 13, BLANCO, False, "center",
                         size_hint_y=0.38))
        h.add_widget(col)
        h.add_widget(Widget(size_hint_x=None, width=dp(44)))
        return h

    # ================================================== PANTALLA 1: inicio
    def v_inicio(self):
        c = self.actual()
        raiz = FloatLayout()
        hero = Hero(pos_hint={"top": 1}, size_hint=(1, 0.58))
        hero.bind(on_release=lambda *a: self.toque_logo())
        src_hero = buscar_img("portada", "inicio", "bienvenida", "fondo",
                              "banner", "hero", "splash", "pantalla")
        src_logo = buscar_img("logo", "cassinelli")
        if src_hero:
            try:
                im = Image(source=src_hero, fit_mode="cover")
            except TypeError:
                im = Image(source=src_hero, allow_stretch=True, keep_ratio=False)
            hero.add_widget(im)
        else:
            col = BoxLayout(orientation="vertical", size_hint=(0.92, 0.62),
                            pos_hint={"center_x": 0.5, "center_y": 0.62})
            if src_logo:
                col.add_widget(Image(source=src_logo))
            else:
                col.add_widget(P("CASSINELLI", 40, BLANCO, True, "center",
                                 size_hint_y=0.4))
                col.add_widget(P("productos de limpieza", 19, BLANCO, False,
                                 "center", size_hint_y=0.2))
            col.add_widget(P("Limpieza y bienestar\nen tu hogar", 19, BLANCO, False,
                             "center", italic=True, size_hint_y=0.4))
            hero.add_widget(col)
        raiz.add_widget(hero)

        card = Caja(fondo=BLANCO, radio=[30, 30, 0, 0], orientation="vertical",
                    pos_hint={"y": 0}, size_hint=(1, 0.5),
                    padding=[dp(20), dp(18), dp(20), dp(14)], spacing=dp(10))
        card.add_widget(T("¡Bienvenido a\nCASSINELLI!", 24, TEXTO, True, "center"))
        card.add_widget(T("Para empezar, registra tus datos", 14, TEXTO, False, "center"))
        cn = Campo("persona", "Nombres y Apellidos")
        ct = Campo("telefono", "Número de teléfono", filtro="int")
        if c:
            cn.inp.text = c["nombre"]
            ct.inp.text = c["telefono"]
        card.add_widget(cn)
        card.add_widget(ct)
        b = Boton("Siguiente", icono="flecha_der", der=True)
        b.bind(on_release=lambda *a: self.registrar(cn.valor, ct.valor))
        card.add_widget(b)
        card.add_widget(Widget())
        raiz.add_widget(card)
        return raiz

    def registrar(self, nombre, tel):
        nombre = " ".join(nombre.split())
        tel = re.sub(r"\D", "", tel)
        if len(nombre) < 3:
            self.aviso("Falta tu nombre", "Escribe tus nombres y apellidos.")
            return
        if len(tel) < 9:
            self.aviso("Revisa tu teléfono", "Escribe tu número de 9 dígitos.")
            return
        c = next((x for x in self.d["clientes"] if x["telefono"] == tel), None)
        if c is None:
            c = self.nuevo_cliente(nombre, tel)
        else:
            c["nombre"] = nombre
        self.d["actual"] = c["id"]
        self.guardar()
        self.ir("c1")

    def toque_logo(self):
        ahora = time.time()
        self._toques = [t for t in self._toques if ahora - t < 3] + [ahora]
        if len(self._toques) >= 5:
            self._toques = []
            self.pedir_pin()

    def pedir_pin(self):
        cp = Campo(None, "PIN de administrador", filtro="int")
        cp.inp.password = True

        def ok():
            if cp.valor == str(self.d["config"]["pin"]):
                self.abrir_admin()
                return True
            cp.inp.text = ""
            cp.inp.hint_text = "PIN incorrecto, intenta de nuevo"
            return False
        self.dialogo("Modo administrador", [cp], "Entrar", ok)

    # ============================================ PANTALLAS 2 y 3: crédito
    def texto_credito(self, c, nivel):
        cr = c["credito"]
        if nivel == 1 and c["pagos"] >= 1:
            return "Este nivel ya está completo. Sigue con el siguiente.", False
        if nivel == 2 and c["pagos"] < 1:
            return "Se habilita cuando hayas realizado tu primer pago.", False
        est = cr["estado"]
        if est == "pendiente":
            return "Solicitud enviada el %s. Queda a la espera de aprobación." % cr["fecha"], False
        if est == "aprobado":
            return "Aprobado: %s disponibles. Se descuentan en tu próxima compra." % soles(cr["monto"]), False
        if est == "debe":
            return "Tienes un pago pendiente de %s. Págalo para pedir más crédito." % soles(c["deuda"]), False
        return "Disponible para solicitar.", True

    def v_credito(self, nivel):
        c = self.actual()
        monto = 10 if nivel == 1 else 20
        txt_estado, activo = self.texto_credito(c, nivel)
        raiz = BoxLayout(orientation="vertical")
        raiz.add_widget(self.cabecera(True))
        cont = V(pad=14, sp_=12)
        tarjeta = V(fondo=BLANCO, pad=14, sp_=12)
        fila = H(66)
        fila.add_widget(Ico("escudo", color=VERDE, detalle=BLANCO,
                            size_hint=(None, None), size=(dp(62), dp(62)),
                            pos_hint=CENTRO))
        col = BoxLayout(orientation="vertical")
        col.add_widget(P("Crédito Autorizado", 21, TEXTO, True, size_hint_y=0.58))
        col.add_widget(P("¡Gracias por tu confianza!" if nivel == 1 else "¡Sigues avanzando!",
                         13, GRIS, size_hint_y=0.42))
        fila.add_widget(col)
        tarjeta.add_widget(fila)
        caja = Caja(fondo=MENTA, radio=12, orientation="vertical",
                    size_hint_y=None, height=dp(104), padding=dp(10))
        caja.add_widget(P("Monto disponible", 15, TEXTO, True, "center", size_hint_y=0.34))
        caja.add_widget(P(soles(monto), 40, TEXTO, True, "center", size_hint_y=0.66))
        tarjeta.add_widget(caja)
        b = Boton("Solicitar crédito autorizado", icono="tarjeta", alto=66)
        b.activo(activo)
        b.bind(on_release=lambda *a: self.solicitar(nivel))
        tarjeta.add_widget(b)
        tarjeta.add_widget(T(esc(txt_estado), 13, GRIS, False, "center"))
        cont.add_widget(tarjeta)
        cont.add_widget(T("Condiciones:", 15, TEXTO, True))
        for txt, alto in (("Disponible para tus compras.", 28),
                          ("Se descuenta en tu próxima compra.", 28),
                          ("Puedes solicitar más crédito cuando hayas realizado un pago.", 44)):
            f = H(alto, spacing=dp(8))
            f.add_widget(Ico("check", color=VERDE, size_hint=(None, None),
                             size=(dp(22), dp(22)), pos_hint=CENTRO))
            f.add_widget(P(txt, 13, TEXTO))
            cont.add_widget(f)
        sig = Boton("Siguiente", icono="flecha_der", der=True)
        sig.bind(on_release=lambda *a: self.ir("c2" if nivel == 1 else "socio"))
        cont.add_widget(sig)
        raiz.add_widget(scroll(cont))
        return raiz

    def solicitar(self, nivel):
        c = self.actual()
        txt, ok = self.texto_credito(c, nivel)
        if not ok:
            self.aviso("Todavía no disponible", txt)
            return
        monto = 10 if nivel == 1 else 20
        c["credito"] = {"estado": "pendiente", "monto": monto, "fecha": hoy()}
        self.guardar()
        self.aviso("Solicitud enviada",
                   "Pediste %s de crédito. Queda registrada para que Cassinelli la apruebe." % soles(monto))
        self.refrescar()

    # ================================================ PANTALLA 4: socio
    def v_socio(self):
        pct = self.d["config"]["porcentaje"]
        raiz = BoxLayout(orientation="vertical")
        raiz.add_widget(self.cabecera(True))
        cont = V(pad=16, sp_=14)
        cont.add_widget(Widget(size_hint_y=None, height=dp(6)))
        fila = H(96)
        fila.add_widget(Widget())
        fila.add_widget(Ico("apreton", color=BLANCO, fondo=VERDE,
                            size_hint=(None, None), size=(dp(92), dp(92))))
        fila.add_widget(Widget())
        cont.add_widget(fila)
        cont.add_widget(T("¡Ya eres el socio de la empresa!", 26, TEXTO, True, "center"))
        cont.add_widget(T("Recibirás el %s%% del dinero de las ganancias de la empresa, "
                          "repartidos en todos los socios por compras." % pct,
                          15, TEXTO, False, "center"))
        tarj = Caja(fondo=MENTA, radio=14, orientation="horizontal",
                    size_hint_y=None, height=dp(88), padding=dp(12), spacing=dp(12))
        tarj.add_widget(Ico("grupo", color=BLANCO, fondo=VERDE, size_hint=(None, None),
                            size=(dp(60), dp(60)), pos_hint=CENTRO))
        tarj.add_widget(P("Si ya tuviste más de 10 compras registradas, "
                          "ya eres socio de Cassinelli.", 14, TEXTO))
        cont.add_widget(tarj)
        sig = Boton("Siguiente", icono="flecha_der", der=True)
        sig.bind(on_release=lambda *a: self.ir("diez"))
        cont.add_widget(sig)
        raiz.add_widget(scroll(cont))
        return raiz

    # ======================================== PANTALLA 5: 10 compras y pago
    def v_diez(self):
        c = self.actual()
        n = c["compras"]
        listo = n >= 10
        raiz = BoxLayout(orientation="vertical")
        raiz.add_widget(self.cabecera(True))
        cont = V(pad=14, sp_=12)
        fila = H(84)
        fila.add_widget(Ico("trofeo", color=BLANCO, fondo=VERDE, size_hint=(None, None),
                            size=(dp(68), dp(68)), pos_hint=CENTRO))
        col = BoxLayout(orientation="vertical")
        if listo:
            col.add_widget(P("¡Ya tienes 10 compras registradas!", 18, TEXTO, True,
                             size_hint_y=0.62))
            col.add_widget(P("Ahora puedes acceder al pago para socio.", 13, GRIS,
                             size_hint_y=0.38))
        else:
            col.add_widget(P("Llevas %d de 10 compras" % n, 18, TEXTO, True,
                             size_hint_y=0.6))
            col.add_widget(P("Te faltan %d para acceder al pago para socio." % (10 - n),
                             13, GRIS, size_hint_y=0.4))
        fila.add_widget(col)
        cont.add_widget(fila)
        if not listo:
            cont.add_widget(barra(n, 10))
        b = Boton("Presionar aquí", icono="moneda", alto=62)
        b.activo(listo)
        b.bind(on_release=lambda *a: self.presionar())
        cont.add_widget(b)

        form = V(fondo=MENTA, radio=14, pad=14, sp_=10)
        t = H(34)
        t.add_widget(Ico("corona", color=VERDE, size_hint=(None, None),
                         size=(dp(34), dp(34)), pos_hint=CENTRO))
        t.add_widget(P("Pago para socio", 18, TEXTO, True))
        form.add_widget(t)
        form.add_widget(T("Monto a recibir:", 15, TEXTO))
        cm = Campo("moneda", "Ingrese el monto (S/)", filtro="float")
        form.add_widget(cm)
        form.add_widget(T("Fecha de cobro:", 15, TEXTO))
        cf = Campo("calendario", "dd / mm / aaaa", filtro=filtro_fecha)
        form.add_widget(cf)
        if c["socio_monto"]:
            cm.inp.text = c["socio_monto"]
        if c["socio_fecha"]:
            cf.inp.text = c["socio_fecha"]
        g = Boton("Guardar", icono="check_c", alto=54)
        g.bind(on_release=lambda *a: self.guardar_pago(c, cm.valor, cf.valor, True))
        form.add_widget(g)
        cont.add_widget(form)
        raiz.add_widget(scroll(cont))
        return raiz

    def presionar(self):
        c = self.actual()
        if c["compras"] < 10:
            self.aviso("Aún no", "Te faltan %d compras para acceder al pago para socio." % (10 - c["compras"]))
            return
        c["socio_pedido"] = True
        self.guardar()
        self.aviso("Solicitud registrada",
                   "Ahora escribe el monto a recibir y la fecha de cobro, y toca Guardar.")

    def guardar_pago(self, c, monto_txt, fecha_txt, desde_cliente):
        if desde_cliente and not c["socio_pedido"]:
            self.aviso("Primero presiona «Presionar aquí»",
                       "Necesitas registrar tu solicitud de socio antes de guardar el pago.")
            return False
        m = parse_monto(monto_txt)
        f = parse_fecha(fecha_txt)
        if m is None or m <= 0:
            self.aviso("Revisa el monto", "Escribe un monto mayor a 0, por ejemplo 150.00")
            return False
        if f is None:
            self.aviso("Revisa la fecha", "Usa el formato dd/mm/aaaa, por ejemplo 25/10/2026.")
            return False
        c["socio_monto"] = "%.2f" % m
        c["socio_fecha"] = f
        self.guardar()
        self.aviso("Guardado", "Pago para socio: %s, fecha de cobro %s." % (soles(m), f))
        return True

    # ================================================== ADMINISTRADOR
    def abrir_admin(self):
        scr = self.sm.get_screen("admin")
        scr.clear_widgets()
        self.adm_raiz = BoxLayout(orientation="vertical")
        scr.add_widget(self.adm_raiz)
        self.pila = []
        self.adm_ir("inicio")
        self.ir("admin")

    def salir_admin(self):
        self.pila = []
        self.ir("inicio", volver=True)

    def adm_ir(self, tab, det=None):
        self.adm_tab = tab
        self.adm_det = det
        self.adm_raiz.clear_widgets()
        titulos = {"inicio": "Panel de Cassinelli", "clientes": "Clientes",
                   "socios": "Socios", "ventas": "Ventas", "mas": "Más"}
        titulo = titulos[tab] if det is None else "Clientes - Socios"
        self.adm_raiz.add_widget(self.adm_cabecera(titulo))
        if det is not None:
            cuerpo = self.a_detalle(det)
        else:
            cuerpo = {"inicio": self.a_inicio, "clientes": self.a_clientes,
                      "socios": self.a_socios, "ventas": self.a_ventas,
                      "mas": self.a_mas}[tab]()
        self.adm_raiz.add_widget(cuerpo)
        self.adm_raiz.add_widget(self.adm_nav())

    def adm_cabecera(self, titulo):
        h = Caja(fondo=VERDE, radio=0, orientation="horizontal", size_hint_y=None,
                 height=dp(58), padding=[dp(8), dp(6)], spacing=dp(6))
        izq = BotonIco("flecha" if self.adm_det is not None else "menu", color=BLANCO,
                       size_hint=(None, None), size=(dp(44), dp(44)), pos_hint=CENTRO)
        if self.adm_det is not None:
            izq.bind(on_release=lambda *a: self.adm_ir(self.adm_tab))
        else:
            izq.bind(on_release=lambda *a: self.adm_ir("mas"))
        h.add_widget(izq)
        h.add_widget(P(titulo, 19, BLANCO, True, "center"))
        der = BotonIco("lupa", color=BLANCO, size_hint=(None, None),
                       size=(dp(44), dp(44)), pos_hint=CENTRO)
        der.bind(on_release=lambda *a: self.adm_ir("clientes"))
        h.add_widget(der)
        return h

    def adm_nav(self):
        nav = Caja(fondo=BLANCO, radio=0, size_hint_y=None, height=dp(66),
                   padding=[dp(6), dp(5)], spacing=dp(4))
        for tid, nombre, ico in (("inicio", "Inicio", "casa"),
                                 ("clientes", "Clientes", "persona"),
                                 ("socios", "Socios", "corona"),
                                 ("ventas", "Ventas", "ventas"),
                                 ("mas", "Más", "mas")):
            act = tid == self.adm_tab
            t = Tab(fondo=MENTA if act else BLANCO, radio=12, orientation="vertical",
                    padding=[0, dp(4), 0, dp(2)])
            col = VERDE if act else INACTIVO
            t.add_widget(Ico(ico, color=col, size_hint=(1, 0.62)))
            t.add_widget(P(nombre, 10, col, act, "center", size_hint_y=0.38))
            t.bind(on_release=lambda i, tid=tid: self.adm_ir(tid))
            nav.add_widget(t)
        return nav

    # ---- inicio del panel
    def a_inicio(self):
        cs = self.d["clientes"]
        cont = V(pad=12, sp_=12)
        grid = GridLayout(cols=2, size_hint_y=None, height=dp(176), spacing=dp(10))
        socios = len([c for c in cs if c["socio"]])
        total_v = sum(v["monto"] for v in self.d["ventas"])
        for num, et in ((str(len(cs)), "Clientes"), (str(socios), "Socios activos"),
                        (str(sum(c["compras"] for c in cs)), "Compras registradas"),
                        (soles(total_v), "Ventas totales")):
            k = Caja(fondo=MENTA, radio=12, orientation="vertical", padding=dp(8))
            k.add_widget(P(num, 24, TEXTO, True, "center", size_hint_y=0.6))
            k.add_widget(P(et, 12, GRIS, False, "center", size_hint_y=0.4))
            grid.add_widget(k)
        cont.add_widget(grid)

        cont.add_widget(T("Solicitudes de crédito", 17, TEXTO, True))
        pend = [c for c in cs if c["credito"]["estado"] == "pendiente"]
        if not pend:
            cont.add_widget(T("No hay solicitudes pendientes.", 14, GRIS))
        for c in pend:
            cont.add_widget(self.fila_accion(
                c, soles(c["credito"]["monto"]), "Aprobar",
                lambda i, c=c: self.aprobar(c)))
        cont.add_widget(T("Cobros pendientes", 17, TEXTO, True))
        debe = [c for c in cs if c["credito"]["estado"] == "debe"]
        if not debe:
            cont.add_widget(T("Nadie tiene pagos pendientes.", 14, GRIS))
        for c in debe:
            cont.add_widget(self.fila_accion(
                c, soles(c["deuda"]), "Registrar pago",
                lambda i, c=c: self.pago_cliente(c)))
        return scroll(cont)

    def fila_accion(self, c, detalle, texto_btn, cb):
        f = Caja(fondo=BLANCO, radio=12, borde=BORDE, orientation="horizontal",
                 size_hint_y=None, height=dp(68), padding=dp(8), spacing=dp(8))
        col = BoxLayout(orientation="vertical")
        col.add_widget(P(esc(c["nombre"]), 15, TEXTO, True, size_hint_y=0.55))
        col.add_widget(P("%s  ·  %s" % (esc(c["telefono"]), detalle), 12, GRIS,
                         size_hint_y=0.45))
        f.add_widget(col)
        b = Boton(texto_btn, alto=44, tam=13)
        b.size_hint_x = None
        b.width = dp(112)
        b.pos_hint = CENTRO
        b.bind(on_release=cb)
        f.add_widget(b)
        return f

    def aprobar(self, c):
        c["credito"]["estado"] = "aprobado"
        self.guardar()
        self.adm_ir(self.adm_tab, self.adm_det)

    def pago_cliente(self, c):
        if c["credito"]["estado"] != "debe":
            self.aviso("Sin pagos pendientes", "Este cliente no tiene crédito por cobrar.")
            return
        monto = c["deuda"]

        def ok():
            c["pagos"] += 1
            c["credito"] = {"estado": "ninguno", "monto": 0, "fecha": ""}
            c["deuda"] = 0
            self.guardar()
            self.adm_ir(self.adm_tab, self.adm_det)
        self.dialogo("Registrar pago",
                     [T("%s paga %s. Después podrá pedir más crédito (hasta S/ 20)." %
                        (esc(c["nombre"]), soles(monto)), 15, TEXTO)], "Confirmar", ok)

    # ---- clientes
    def a_clientes(self):
        cont = V(pad=12, sp_=10)
        nuevo = Boton("Nuevo cliente", alto=48, tam=15, icono="persona")
        nuevo.bind(on_release=lambda *a: self.dlg_nuevo_cliente())
        cont.add_widget(nuevo)
        busc = Campo("lupa", "Buscar por nombre o teléfono")
        cont.add_widget(busc)
        lista = V(sp_=8)
        cont.add_widget(lista)
        self.llenar(lista, "", False)
        busc.inp.bind(text=lambda i, t: self.llenar(lista, t, False))
        return scroll(cont)

    def llenar(self, lista, txt, solo_socios):
        lista.clear_widgets()
        q = txt.strip().lower()
        cs = [c for c in self.d["clientes"]
              if (not solo_socios or c["socio"] or c["compras"] >= 10)
              and (not q or q in c["nombre"].lower() or q in c["telefono"])]
        cs.sort(key=lambda c: c["nombre"].lower())
        if not cs:
            lista.add_widget(T("No hay resultados. Los clientes aparecen aquí cuando se "
                               "registran o los agregas con «Nuevo cliente».", 14, GRIS))
        for c in cs:
            lista.add_widget(self.fila_cliente(c))

    def fila_cliente(self, c):
        f = FilaBtn(fondo=BLANCO, radio=12, borde=BORDE, orientation="horizontal",
                    size_hint_y=None, height=dp(68), padding=dp(8), spacing=dp(10))
        f.add_widget(Ico("persona", color=VERDE, fondo=MENTA, size_hint=(None, None),
                         size=(dp(48), dp(48)), pos_hint=CENTRO))
        col = BoxLayout(orientation="vertical")
        col.add_widget(P(esc(c["nombre"]), 16, TEXTO, True, size_hint_y=0.55))
        col.add_widget(P(esc(c["telefono"]), 13, GRIS, size_hint_y=0.45))
        f.add_widget(col)
        extra = self.reparto.get(c["id"])
        if extra is not None:
            txt = "[b]%s[/b]" % soles(extra)
        elif c["socio"]:
            txt = "[b]Socio[/b]"
        else:
            txt = "%d compras" % c["compras"]
        f.add_widget(P(txt, 13, VERDE if c["socio"] else GRIS, False, "right",
                       size_hint_x=None, width=dp(96)))
        f.bind(on_release=lambda i, cid=c["id"]: self.adm_ir(self.adm_tab, cid))
        return f

    def dlg_nuevo_cliente(self):
        cn = Campo("persona", "Nombres y Apellidos")
        ct = Campo("telefono", "Número de teléfono", filtro="int")

        def ok():
            nombre = " ".join(cn.valor.split())
            tel = re.sub(r"\D", "", ct.valor)
            if len(nombre) < 3 or len(tel) < 9:
                cn.inp.hint_text = "Escribe el nombre completo"
                ct.inp.hint_text = "Teléfono de 9 dígitos"
                return False
            if any(x["telefono"] == tel for x in self.d["clientes"]):
                ct.inp.text = ""
                ct.inp.hint_text = "Ese teléfono ya está registrado"
                return False
            self.nuevo_cliente(nombre, tel)
            self.guardar()
            self.adm_ir(self.adm_tab)
        self.dialogo("Nuevo cliente", [cn, ct], "Guardar", ok)

    # ---- detalle (pantalla 6 del diseño)
    def a_detalle(self, cid):
        c = self.cliente(cid)
        if c is None:
            return self.a_clientes()
        cont = V(pad=12, sp_=12)
        tj = Caja(fondo=VERDE, radio=12, orientation="horizontal", size_hint_y=None,
                  height=dp(80), padding=dp(12), spacing=dp(12))
        tj.add_widget(Ico("persona", color=BLANCO, size_hint=(None, None),
                          size=(dp(44), dp(44)), pos_hint=CENTRO))
        col = BoxLayout(orientation="vertical")
        col.add_widget(P(esc(c["nombre"]), 17, BLANCO, True, size_hint_y=0.55))
        tel = BoxLayout(size_hint_y=0.45, spacing=dp(6))
        tel.add_widget(Ico("telefono", color=BLANCO, size_hint=(None, None),
                           size=(dp(16), dp(16)), pos_hint=CENTRO))
        tel.add_widget(P(esc(c["telefono"]), 13, BLANCO))
        col.add_widget(tel)
        tj.add_widget(col)
        ins = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(66))
        ins.add_widget(Ico("corona", color=ORO, size_hint_y=0.62))
        ins.add_widget(P("Socio" if c["socio"] else "Cliente", 12, ORO, True, "center",
                         size_hint_y=0.38))
        tj.add_widget(ins)
        cont.add_widget(tj)

        datos = V(fondo=MENTA, radio=12, pad=12, sp_=8)
        datos.add_widget(T("Datos de socio", 16, TEXTO, True))
        interior = V(fondo=BLANCO, radio=10, pad=[10, 6], sp_=0)
        for et, val in (("Compras registradas:", str(c["compras"])),
                        ("Porcentaje de ganancia:", "%s%%" % self.d["config"]["porcentaje"]),
                        ("Estado:", self.estado_socio(c))):
            f = H(32)
            f.add_widget(P(et, 14, TEXTO))
            f.add_widget(P(val, 14, TEXTO, True, "right"))
            interior.add_widget(f)
        datos.add_widget(interior)
        cont.add_widget(datos)

        pago = V(fondo=MENTA, radio=12, pad=12, sp_=8)
        pago.add_widget(T("Pago para socio", 16, TEXTO, True))
        pago.add_widget(T("Monto:", 14, TEXTO))
        cm = Campo(None, "0.00", prefijo="S/", filtro="float")
        cm.inp.text = c["socio_monto"]
        pago.add_widget(cm)
        pago.add_widget(T("Fecha de cobro:", 14, TEXTO))
        cf = Campo("calendario", "dd / mm / aaaa", filtro=filtro_fecha)
        cf.inp.text = c["socio_fecha"]
        pago.add_widget(cf)
        g = Boton("Guardar", icono="check_c", alto=52)
        g.bind(on_release=lambda *a: self.guardar_pago(c, cm.valor, cf.valor, False))
        pago.add_widget(g)
        cont.add_widget(pago)

        acc = V(fondo=BLANCO, radio=12, borde=BORDE, pad=12, sp_=8)
        acc.add_widget(T("Acciones", 16, TEXTO, True))
        cr = c["credito"]
        nombres = {"ninguno": "sin crédito", "pendiente": "solicitado", "aprobado": "aprobado",
                   "debe": "usado, por cobrar"}
        acc.add_widget(T("Crédito: %s %s" % (soles(cr["monto"]) if cr["monto"] else "",
                                             nombres[cr["estado"]]), 14, GRIS))
        if cr["estado"] == "pendiente":
            b = Boton("Aprobar crédito %s" % soles(cr["monto"]), alto=46, tam=14)
            b.bind(on_release=lambda *a: self.aprobar(c))
            acc.add_widget(b)
        elif cr["estado"] == "aprobado":
            b = Boton("Cancelar crédito aprobado", relleno=False, alto=46, tam=14)
            b.bind(on_release=lambda *a: self.cancelar_credito(c))
            acc.add_widget(b)
        elif cr["estado"] == "debe":
            b = Boton("Registrar pago (%s)" % soles(c["deuda"]), alto=46, tam=14)
            b.bind(on_release=lambda *a: self.pago_cliente(c))
            acc.add_widget(b)
        b2 = Boton("Registrar compra", relleno=False, alto=46, tam=14)
        b2.bind(on_release=lambda *a: self.dlg_compra(c))
        acc.add_widget(b2)
        b3 = Boton("Quitar socio" if c["socio"] else "Activar como socio",
                   relleno=False, alto=46, tam=14)
        b3.bind(on_release=lambda *a: self.alternar_socio(c))
        acc.add_widget(b3)
        b4 = Boton("Eliminar cliente", relleno=False, alto=46, tam=14, color=ROJO)
        b4.bind(on_release=lambda *a: self.dlg_eliminar(c))
        acc.add_widget(b4)
        cont.add_widget(acc)
        return scroll(cont)

    def cancelar_credito(self, c):
        c["credito"] = {"estado": "ninguno", "monto": 0, "fecha": ""}
        self.guardar()
        self.adm_ir(self.adm_tab, self.adm_det)

    def alternar_socio(self, c):
        if not c["socio"] and c["compras"] < 10:
            self.aviso("Faltan compras",
                       "%s tiene %d compras. Para ser socio necesita 10." % (c["nombre"], c["compras"]))
            return
        c["socio"] = not c["socio"]
        self.guardar()
        self.adm_ir(self.adm_tab, self.adm_det)

    def dlg_eliminar(self, c):
        def ok():
            self.d["clientes"] = [x for x in self.d["clientes"] if x["id"] != c["id"]]
            if self.d.get("actual") == c["id"]:
                self.d["actual"] = None
            self.guardar()
            self.adm_ir(self.adm_tab)
        self.dialogo("Eliminar cliente",
                     [T("Se borrarán los datos de %s. Esta acción no se puede deshacer." %
                        esc(c["nombre"]), 15, TEXTO)], "Eliminar", ok)

    # ---- compras / ventas
    def registrar_venta(self, c, monto, usar):
        neto, usado = monto, 0.0
        cr = c["credito"]
        if usar and cr["estado"] == "aprobado":
            usado = min(monto, float(cr["monto"]))
            neto = monto - usado
            c["credito"] = {"estado": "debe", "monto": cr["monto"], "fecha": cr["fecha"]}
            c["deuda"] = usado
        c["compras"] += 1
        self.d["ventas"].append({"cid": c["id"], "nombre": c["nombre"], "monto": monto,
                                 "credito": usado, "neto": neto, "fecha": hoy()})
        self.guardar()
        return neto, usado

    def dlg_compra(self, c):
        cm = Campo("moneda", "Monto de la compra (S/)", filtro="float")
        widgets = [cm]
        estado = [False]
        tog = None
        if c["credito"]["estado"] == "aprobado":
            tog = Boton("Descontar crédito: No", relleno=False, alto=46, tam=14)

            def cambiar(*a):
                estado[0] = not estado[0]
                tog.lbl.text = "Descontar crédito: %s" % ("Sí" if estado[0] else "No")
            tog.bind(on_release=cambiar)
            widgets.append(tog)

        def ok():
            m = parse_monto(cm.valor)
            if m is None or m <= 0:
                cm.inp.text = ""
                cm.inp.hint_text = "Escribe un monto mayor a 0"
                return False
            neto, usado = self.registrar_venta(c, m, estado[0])
            self.adm_ir(self.adm_tab, self.adm_det)
            self.aviso("Compra registrada",
                       "Total %s. Crédito descontado %s. Cobrar %s. Compras de %s: %d." %
                       (soles(m), soles(usado), soles(neto), c["nombre"], c["compras"]))
        self.dialogo("Registrar compra", widgets, "Guardar", ok)

    def a_ventas(self):
        cont = V(pad=12, sp_=10)
        cont.add_widget(T("Registrar una venta", 17, TEXTO, True))
        cs = sorted(self.d["clientes"], key=lambda c: c["nombre"].lower())
        mapa = {"%s - %s" % (c["nombre"], c["telefono"]): c for c in cs}
        marco = Caja(fondo=BLANCO, radio=10, borde=BORDE, size_hint_y=None, height=dp(48))
        sp_cli = Spinner(text="Elige un cliente" if cs else "Primero agrega clientes",
                         values=list(mapa.keys()), background_normal="",
                         background_color=(0, 0, 0, 0), color=TEXTO, font_size=sp(15))
        marco.add_widget(sp_cli)
        cont.add_widget(marco)
        cm = Campo("moneda", "Monto de la venta (S/)", filtro="float")
        cont.add_widget(cm)
        usar = [False]
        tog = Boton("Descontar crédito aprobado: No", relleno=False, alto=46, tam=14)

        def cambiar(*a):
            usar[0] = not usar[0]
            tog.lbl.text = "Descontar crédito aprobado: %s" % ("Sí" if usar[0] else "No")
        tog.bind(on_release=cambiar)
        cont.add_widget(tog)
        g = Boton("Guardar venta", icono="check_c", alto=54)

        def guardar_venta(*a):
            c = mapa.get(sp_cli.text)
            m = parse_monto(cm.valor)
            if c is None:
                self.aviso("Falta el cliente", "Elige a quién le vendiste.")
                return
            if m is None or m <= 0:
                self.aviso("Revisa el monto", "Escribe un monto mayor a 0.")
                return
            neto, usado = self.registrar_venta(c, m, usar[0])
            self.adm_ir("ventas")
            self.aviso("Venta registrada",
                       "Total %s. Crédito descontado %s. Cobrar %s. Compras de %s: %d." %
                       (soles(m), soles(usado), soles(neto), c["nombre"], c["compras"]))
        g.bind(on_release=guardar_venta)
        cont.add_widget(g)
        cont.add_widget(T("Últimas ventas", 17, TEXTO, True))
        ult = list(reversed(self.d["ventas"]))[:15]
        if not ult:
            cont.add_widget(T("Todavía no hay ventas registradas.", 14, GRIS))
        for v in ult:
            f = Caja(fondo=BLANCO, radio=10, borde=BORDE, orientation="horizontal",
                     size_hint_y=None, height=dp(56), padding=dp(8))
            col = BoxLayout(orientation="vertical")
            col.add_widget(P(esc(v["nombre"]), 14, TEXTO, True, size_hint_y=0.55))
            col.add_widget(P(v["fecha"], 12, GRIS, size_hint_y=0.45))
            f.add_widget(col)
            f.add_widget(P(soles(v["monto"]), 15, VERDE, True, "right",
                           size_hint_x=None, width=dp(90)))
            cont.add_widget(f)
        return scroll(cont)

    # ---- socios y reparto
    def a_socios(self):
        cont = V(pad=12, sp_=10)
        pct = self.d["config"]["porcentaje"]
        cont.add_widget(T("Reparto de ganancias (%s%%)" % pct, 17, TEXTO, True))
        cg = Campo("moneda", "Ganancias del periodo (S/)", filtro="float")
        cont.add_widget(cg)
        b = Boton("Calcular reparto", icono="grupo", alto=50, tam=15)
        cont.add_widget(b)
        b2 = Boton("Guardar reparto como monto de pago", relleno=False, alto=48, tam=14)
        cont.add_widget(b2)
        lista = V(sp_=8)
        cont.add_widget(lista)

        def calcular(*a):
            g = parse_monto(cg.valor)
            if g is None or g <= 0:
                self.aviso("Revisa las ganancias", "Escribe cuánto ganó la empresa en el periodo.")
                return
            activos = [c for c in self.d["clientes"] if c["socio"]]
            total = sum(c["compras"] for c in activos)
            if not activos or total <= 0:
                self.aviso("Sin socios activos", "Activa al menos un socio con compras para repartir.")
                return
            pozo = g * pct / 100.0
            self.reparto = {c["id"]: pozo * c["compras"] / total for c in activos}
            self.llenar(lista, "", True)
            self.aviso("Reparto calculado",
                       "Se reparten %s entre %d socios, según sus compras." % (soles(pozo), len(activos)))

        def aplicar(*a):
            if not self.reparto:
                self.aviso("Primero calcula", "Toca «Calcular reparto» para ver cuánto le toca a cada socio.")
                return
            for cid, m in self.reparto.items():
                c = self.cliente(cid)
                if c:
                    c["socio_monto"] = "%.2f" % m
            self.guardar()
            self.aviso("Guardado", "El reparto quedó como monto de pago de cada socio. "
                                   "Falta poner la fecha de cobro en cada uno.")
        b.bind(on_release=calcular)
        b2.bind(on_release=aplicar)
        self.llenar(lista, "", True)
        return scroll(cont)

    # ---- más
    def a_mas(self):
        cont = V(pad=12, sp_=12)
        c1 = V(fondo=BLANCO, radio=12, borde=BORDE, pad=12, sp_=8)
        c1.add_widget(T("Porcentaje para socios", 16, TEXTO, True))
        cp = Campo("moneda", "Porcentaje (ej. 10)", filtro="float")
        cp.inp.text = str(self.d["config"]["porcentaje"])
        c1.add_widget(cp)
        b1 = Boton("Guardar porcentaje", alto=48, tam=15)

        def gp(*a):
            p = parse_monto(cp.valor)
            if p is None or not (0 < p <= 100):
                self.aviso("Revisa el porcentaje", "Escribe un número entre 1 y 100.")
                return
            self.d["config"]["porcentaje"] = int(p) if p == int(p) else p
            self.guardar()
            self.aviso("Guardado", "Los socios recibirán el %s%% de las ganancias." % self.d["config"]["porcentaje"])
        b1.bind(on_release=gp)
        c1.add_widget(b1)
        cont.add_widget(c1)

        c2 = V(fondo=BLANCO, radio=12, borde=BORDE, pad=12, sp_=8)
        c2.add_widget(T("Cambiar PIN de administrador", 16, TEXTO, True))
        cn = Campo(None, "Nuevo PIN (4 a 8 dígitos)", filtro="int")
        cn.inp.password = True
        c2.add_widget(cn)
        b2 = Boton("Guardar PIN", alto=48, tam=15)

        def gpin(*a):
            if not (4 <= len(cn.valor) <= 8):
                self.aviso("PIN muy corto", "Usa entre 4 y 8 dígitos.")
                return
            self.d["config"]["pin"] = cn.valor
            self.guardar()
            cn.inp.text = ""
            self.aviso("PIN cambiado", "Desde ahora entras con el PIN nuevo.")
        b2.bind(on_release=gpin)
        c2.add_widget(b2)
        cont.add_widget(c2)

        c3 = V(fondo=BLANCO, radio=12, borde=BORDE, pad=12, sp_=8)
        c3.add_widget(T("Datos de este teléfono", 16, TEXTO, True))
        c3.add_widget(T("Los clientes, compras y ventas se guardan en este teléfono, en el archivo:\n%s"
                        % esc(self.ruta_datos), 12, GRIS))
        cont.add_widget(c3)

        sal = Boton("Salir del modo administrador", relleno=False, alto=52)
        sal.bind(on_release=lambda *a: self.salir_admin())
        cont.add_widget(sal)
        return scroll(cont)


if __name__ == "__main__":
    ClientesApp().run()
