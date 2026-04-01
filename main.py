from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from db import crear_tabla_ventas
from tpv import TPVScreen
from caja import CajaScreen
from pedidos import PedidosScreen

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')


from kivy.uix.label import Label


from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import shutil
from kivy.app import App
import os

def copiar_db_inicial():
    import shutil
    from kivy.app import App
    import os

    app = App.get_running_app()

    origen = os.path.join(os.path.dirname(__file__), "inventario.db")
    destino = os.path.join(app.user_data_dir, "inventario.db")

    print("ORIGEN:", origen)
    print("DESTINO:", destino)

    # 🔥 SI NO EXISTE O ESTÁ VACÍO → copiar
    if not os.path.exists(destino) or os.path.getsize(destino) < 1000:
        shutil.copy(origen, destino)
        print("📦 Inventario COPIADO BIEN")
    else:
        print("✅ Inventario ya existe")


class MenuScreen(Screen):

    def ir_tpv(self, instance):
        self.manager.current = "tpv"

    def ir_caja(self, instance):
        self.manager.current = "caja"

    def ir_pedidos(self, instance):
        self.manager.current = "pedidos"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical")

        # 🧾 TÍTULO
        titulo = Label(
            text="RULIÑA",
            font_size=28,
            size_hint_y=0.2
        )

        root.add_widget(titulo)

        # 🎨 BOTONES FULL SCREEN
        btn_pedidos = Button(
            text="PEDIDOS",
            font_size=22,
            size_hint_y=0.26,
            background_color=(0.7, 0.5, 0.9, 1),
            background_normal=""
        )
        btn_pedidos.bind(on_press=self.ir_pedidos)

        btn_tpv = Button(
            text="TPV",
            font_size=22,
            size_hint_y=0.26,
            background_color=(1, 0.6, 0.75, 1),
            background_normal=""
        )
        btn_tpv.bind(on_press=self.ir_tpv)

        btn_caja = Button(
            text="CAJA",
            font_size=22,
            size_hint_y=0.26,
            background_color=(0.2, 0.8, 0.4, 1),
            background_normal=""
        )
        btn_caja.bind(on_press=self.ir_caja)

        root.add_widget(btn_pedidos)
        root.add_widget(btn_tpv)
        root.add_widget(btn_caja)

        self.add_widget(root)

from caja import CajaScreen

class MyApp(App):
    def build(self):
        copiar_db_inicial()
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(PedidosScreen(name="pedidos"))
        sm.add_widget(TPVScreen(name="tpv"))
        sm.add_widget(CajaScreen(name="caja"))
        crear_tabla_ventas() 
        return sm


if __name__ == "__main__":
    MyApp().run()