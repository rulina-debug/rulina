from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen

from db import obtener_productos, obtener_variantes, guardar_venta


class CardProducto(ButtonBehavior, BoxLayout):
    pass


class TPVScreen(Screen):

    def volver_menu(self, instance):
        self.manager.current = "menu"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.carrito = []

        layout_root = FloatLayout()
        self.add_widget(layout_root)

        # 🔙 botón volver
        btn_back = Button(
            text="VOLVER",
            size_hint=(None, None),
            size=(60, 60),
            pos_hint={"x": 0.02, "top": 0.98},
            background_color=(0.2, 0.2, 0.2, 1)
        )
        btn_back.bind(on_press=self.volver_menu)

        # ================= PRODUCTOS =================

        self.grid = GridLayout(
            cols=3,
            spacing=10,
            padding=10,
            size_hint_y=None,
            row_default_height=200,
            row_force_default=True
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.grid)

        # ================= CARRITO =================

        self.btn_carrito = Button(
            text="CARRITO 0",
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={"right": 0.98, "top": 0.98}
        )
        self.btn_carrito.bind(on_press=self.abrir_carrito)

        layout_root.add_widget(scroll)
        layout_root.add_widget(self.btn_carrito)
        layout_root.add_widget(btn_back)

    # 🚀 cargar productos cuando entras
    def on_enter(self):
        self.cargar_productos()

    def cargar_productos(self):
        self.grid.clear_widgets()

        productos = obtener_productos()
        print("Productos cargados:", productos)

        for ref, nombre, precio, stock, imagen in productos:

            box = BoxLayout(orientation="vertical")

            img = Image(
                source=imagen,
                size_hint_y=0.7,
                allow_stretch=True
            )

            btn = Button(
                text=f"{nombre}\n{precio}€",
                size_hint_y=0.3
            )

            btn.bind(on_press=lambda x, n=nombre: self.ver_variantes(n))

            box.add_widget(img)
            box.add_widget(btn)

            self.grid.add_widget(box)

    # ---------------- VARIANTES ----------------

    def seleccionar_variante(self, ref, nombre, precio, popup):
        self.add_carrito(ref, nombre, precio)
        popup.dismiss()

    def ver_variantes(self, nombre):

        variantes = obtener_variantes(nombre)

        contenedor = GridLayout(cols=2, spacing=10, padding=10, size_hint_y=None)
        contenedor.bind(minimum_height=contenedor.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(contenedor)

        btn_cerrar = Button(text="Cerrar", size_hint_y=None, height=50)
        contenedor.add_widget(btn_cerrar)

        if len(variantes) == 1:
            ref, nombre_var, v1, v2, precio, stock = variantes[0]
            nombre_final = f"{nombre_var} {v1 or ''} {v2 or ''}".strip()
            self.add_carrito(ref, nombre_final, precio)
            return

        popup = Popup(title="Selecciona variante", content=scroll, size_hint=(0.9, 0.9))
        btn_cerrar.bind(on_press=popup.dismiss)

        for ref, nombre_var, v1, v2, precio, stock in variantes:

            nombre_final = f"{nombre_var} {v1 or ''} {v2 or ''}".strip()

            btn = Button(
                text=f"{nombre_final}\n{precio}€",
                size_hint_y=None,
                height=70
            )

            btn.bind(
                on_press=lambda x, r=ref, n=nombre_final, p=precio:
                self.seleccionar_variante(r, n, p, popup)
            )

            contenedor.add_widget(btn)

        popup.open()

    # ---------------- CARRITO ----------------

    def add_carrito(self, ref, nombre, precio):

        for item in self.carrito:
            if item["ref"] == ref:
                item["cantidad"] += 1
                self.actualizar_carrito()
                return

        self.carrito.append({
            "ref": ref,
            "nombre": nombre,
            "precio": float(precio),
            "cantidad": 1
        })

        self.actualizar_carrito()

    def actualizar_carrito(self):
        total_items = sum(item["cantidad"] for item in self.carrito)
        self.btn_carrito.text = f"CARRITO {total_items}"

    def abrir_carrito(self, instance):

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        total = 0

        self.popup_carrito = Popup(
            title="Carrito",
            size_hint=(0.9, 0.9)
        )

        popup = self.popup_carrito

        # 🔴 CERRAR
        btn_cerrar = Button(
            text="Cerrar",
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        btn_cerrar.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(btn_cerrar)

        # 🧾 ITEMS
        for item in self.carrito:

            total_item = item["precio"] * item["cantidad"]
            total += total_item

            fila = BoxLayout(size_hint_y=None, height=60)

            lbl = Label(text=f"{item['nombre']} x{item['cantidad']} = {total_item:.2f}€")
            btn_del = Button(text="X", size_hint_x=0.2)

            btn_del.bind(on_press=lambda x, item=item: self.eliminar(item, popup))

            fila.add_widget(lbl)
            fila.add_widget(btn_del)

            layout.add_widget(fila)

        # 💰 TOTAL
        layout.add_widget(Label(text=f"TOTAL: {total:.2f}€"))

        # 💳 BOTONES PAGO
        btn_efectivo = Button(
            text="Efectivo",
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.8, 0.3, 1)
        )

        btn_tarjeta = Button(
            text="Tarjeta",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.9, 1)
        )

        btn_efectivo.bind(on_press=lambda x: self.teclado_efectivo(total))
        btn_tarjeta.bind(on_press=lambda x: self.pago_tarjeta(total))

        layout.add_widget(btn_efectivo)
        layout.add_widget(btn_tarjeta)

        popup.content = layout
        popup.open()

    def pagar(self, total, popup):

        guardar_venta(self.carrito)

        self.carrito.clear()
        self.actualizar_carrito()

        popup.dismiss()

        Popup(
            title="Pago",
            content=Label(text="Venta realizada"),
            size_hint=(0.6, 0.4)
        ).open()

    def teclado_efectivo(self, total):

        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label

        layout = BoxLayout(orientation="vertical", spacing=15, padding=15)

        self.importe_recibido = 0

        lbl_total = Label(text=f"TOTAL: {total:.2f}€", font_size=20)
        self.lbl_pago = Label(text="Recibido: 0€", font_size=18)

        layout.add_widget(lbl_total)
        layout.add_widget(self.lbl_pago)

        # 💸 BOTONES RÁPIDOS
        fila_rapida = GridLayout(cols=5, spacing=10, size_hint_y=None, height=60)

        colores = [
            (0.6,0.8,0.6,1),
            (0.9,0.4,0.4,1),
            (0.4,0.6,0.9,1),
            (0.9,0.7,0.3,1)
        ]

        valores = [5,10,20,50]

        for i, v in enumerate(valores):
            btn = Button(text=f"{v}€", background_color=colores[i])
            btn.bind(on_press=lambda x, val=v: self.set_importe(val))
            fila_rapida.add_widget(btn)

        btn_exacto = Button(text="Exacto", background_color=(0.6,0.9,0.6,1))
        btn_exacto.bind(on_press=lambda x: self.set_importe(total))
        fila_rapida.add_widget(btn_exacto)

        layout.add_widget(fila_rapida)

        # 🔢 TECLADO
        teclado = GridLayout(cols=3, spacing=10, size_hint_y=None, height=300)

        botones = [
            "7","8","9",
            "4","5","6",
            "1","2","3",
            "0",".","⌫"
        ]

        for num in botones:

            btn = Button(
                text=num,
                font_size=22,
                background_color=(0.9, 0.6, 0.7, 1)
            )

            if num == "⌫":
                btn.bind(on_press=lambda x: self.borrar_digito())

            elif num == ".":
                btn.bind(on_press=lambda x: self.sumar_pago("."))

            else:
                btn.bind(on_press=lambda x, n=num: self.sumar_pago(n))

            teclado.add_widget(btn)

        layout.add_widget(teclado)

        # 💰 COBRAR
        btn_ok = Button(
            text="COBRAR",
            size_hint_y=None,
            height=70,
            font_size=20,
            background_color=(0.3, 0.8, 0.3, 1)
        )

        btn_ok.bind(on_press=lambda x: self.confirmar_pago(total))

        layout.add_widget(btn_ok)

        self.popup_pago = Popup(
            title="Pago en efectivo",
            content=layout,
            size_hint=(0.9, 0.9)
        )

        self.popup_pago.open()

    def sumar_pago(self, numero):

        texto = self.lbl_pago.text.replace("Recibido: ", "").replace("€", "").strip()

        # 🧠 evitar doble punto
        if numero == "." and "." in texto:
            return

        # 🧠 iniciar correctamente
        if texto == "0":
            if numero == ".":
                nuevo = "0."
            else:
                nuevo = numero
        else:
            nuevo = texto + numero

        self.lbl_pago.text = f"Recibido: {nuevo}€"

        try:
            self.importe_recibido = float(nuevo)
        except:
            self.importe_recibido = 0

    def borrar_digito(self):

        texto = self.lbl_pago.text.replace("Recibido: ", "").replace("€", "").strip()

        if len(texto) <= 1:
            texto = "0"
        else:
            texto = texto[:-1]

        self.lbl_pago.text = f"Recibido: {texto}€"

        try:
            self.importe_recibido = float(texto)
        except:
            self.importe_recibido = 0


    def confirmar_pago(self, total):

        if self.importe_recibido < total:
            self.lbl_pago.text = "X Falta dinero"
            return

        cambio = self.importe_recibido - total

        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from db import guardar_venta

        # 💾 guardar venta
        guardar_venta(self.carrito)

        self.carrito.clear()
        self.actualizar_carrito()

        self.popup_pago.dismiss()

        layout = BoxLayout(orientation="vertical", spacing=20, padding=20)

        layout.add_widget(Label(
            text=f"💰 Cambio: {cambio:.2f}€",
            font_size=24
        ))

        btn_cerrar = Button(
            text="Cerrar",
            size_hint_y=None,
            height=60,
            background_color=(0.3, 0.8, 0.3, 1)
        )

        popup_final = Popup(
            title="Pago completado",
            content=layout,
            size_hint=(0.7, 0.5)
        )

        def cerrar_popup(x):
            popup_final.dismiss()
            # 🔥 vuelve limpio al TPV
            self.manager.current = "tpv"

        btn_cerrar.bind(on_press=cerrar_popup)

        layout.add_widget(btn_cerrar)

        popup_final.open()  


    def pago_tarjeta(self, total):

        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from db import guardar_venta

        guardar_venta(self.carrito)

        self.carrito.clear()
        self.actualizar_carrito()

        Popup(
            title="Pago",
            content=Label(text="Pago con tarjeta OK"),
            size_hint=(0.6, 0.4)
        ).open()    


    def set_importe(self, valor):
        self.importe_recibido = float(valor)
        self.lbl_pago.text = f"Recibido: {valor}€"