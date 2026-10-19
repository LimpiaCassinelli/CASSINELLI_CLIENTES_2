from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget

VERDE = (0, 0.55, 0.30, 1)
VERDE_CLARO = (0.25, 0.90, 0.55, 1)
VERDE_OSCURO = (0.02, 0.16, 0.10, 1)
BLANCO = (1, 1, 1, 1)
AMARILLO = (1, 0.75, 0.15, 1)

Window.clearcolor = VERDE_OSCURO


class CassinelliClientes(App):
    def build(self):
        self.title = "CASSINELLI CLIENTES"

        raiz = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(24), dp(24), dp(20)],
            spacing=dp(15)
        )

        raiz.add_widget(Widget(size_hint_y=0.35))

        titulo = Label(
            text="[b]CASSINELLI[/b]",
            markup=True,
            font_size=sp(34),
            color=VERDE_CLARO,
            size_hint_y=None,
            height=dp(55),
            halign="center"
        )
        raiz.add_widget(titulo)

        subtitulo = Label(
            text="[b]PRODUCTOS DE LIMPIEZA[/b]",
            markup=True,
            font_size=sp(17),
            color=BLANCO,
            size_hint_y=None,
            height=dp(35)
        )
        raiz.add_widget(subtitulo)

        bienvenida = Label(
            text="¡Bienvenido!",
            font_size=sp(25),
            color=AMARILLO,
            size_hint_y=None,
            height=dp(50)
        )
        raiz.add_widget(bienvenida)

        explicacion = Label(
            text="Registra tus datos para continuar",
            font_size=sp(16),
            color=BLANCO,
            size_hint_y=None,
            height=dp(35)
        )
        raiz.add_widget(explicacion)

        raiz.add_widget(Widget(size_hint_y=None, height=dp(8)))

        self.nombre = TextInput(
            hint_text="Escribe tu nombre y apellido",
            multiline=False,
            font_size=sp(17),
            size_hint_y=None,
            height=dp(56),
            padding=[dp(14), dp(16)],
            background_normal="",
            background_active="",
            background_color=BLANCO,
            foreground_color=VERDE_OSCURO,
            cursor_color=VERDE
        )
        raiz.add_widget(self.nombre)

        self.telefono = TextInput(
            hint_text="Número de teléfono",
            multiline=False,
            input_filter="int",
            input_type="number",
            font_size=sp(17),
            size_hint_y=None,
            height=dp(56),
            padding=[dp(14), dp(16)],
            background_normal="",
            background_active="",
            background_color=BLANCO,
            foreground_color=VERDE_OSCURO,
            cursor_color=VERDE
        )
        raiz.add_widget(self.telefono)

        self.mensaje = Label(
            text="",
            font_size=sp(14),
            color=AMARILLO,
            size_hint_y=None,
            height=dp(35)
        )
        raiz.add_widget(self.mensaje)

        siguiente = Button(
            text="[b]SIGUIENTE  ➜[/b]",
            markup=True,
            font_size=sp(19),
            size_hint_y=None,
            height=dp(58),
            background_normal="",
            background_down="",
            background_color=VERDE,
            color=BLANCO
        )
        siguiente.bind(on_release=self.continuar)
        raiz.add_widget(siguiente)

        raiz.add_widget(Widget(size_hint_y=0.5))

        pie = Label(
            text="Limpieza y desinfección al precio justo",
            font_size=sp(13),
            color=VERDE_CLARO,
            size_hint_y=None,
            height=dp(30)
        )
        raiz.add_widget(pie)

        return raiz

    def continuar(self, boton):
        nombre = self.nombre.text.strip()
        telefono = self.telefono.text.strip()

        if len(nombre.split()) < 2:
            self.mensaje.text = "Escribe tu nombre y apellido."
            return

        if len(telefono) != 9:
            self.mensaje.text = "Escribe un teléfono peruano de 9 dígitos."
            return

        self.mensaje.text = "Datos verificados. Continuaremos."


if __name__ == "__main__":
    CassinelliClientes().run()
