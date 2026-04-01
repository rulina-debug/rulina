from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


class PedidosScreen(Screen):

    def volver_menu(self, instance):
        self.nuevo_pedido(None)
        self.manager.current = "menu"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.productos = []

        root = BoxLayout(orientation="vertical")

        scroll = ScrollView()
        layout = BoxLayout(orientation="vertical", spacing=5, padding=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))

        scroll.add_widget(layout)
        root.add_widget(scroll)

        self.add_widget(root)

        # 🔙 volver
        btn_back = Button(text="VOLVER", size_hint_y=None, height=50)
        btn_back.bind(on_press=self.volver_menu)
        layout.add_widget(btn_back)

        # 👤 CLIENTE

        layout.add_widget(Label(text="--- CLIENTE ---", size_hint_y=None, height=30))

        self.nombre = TextInput(
            hint_text="Nombre cliente",
            size_hint_y=None,
            height=50,
            multiline=False
        )

        self.telefono = TextInput(
            hint_text="Teléfono",
            size_hint_y=None,
            height=50,
            multiline=False,
            input_filter="int"
        )

        layout.add_widget(self.nombre)
        layout.add_widget(self.telefono)

        # 📅 FECHAS
        self.fecha_pedido = TextInput(
            text=datetime.now().strftime("%Y-%m-%d"),
            size_hint_y=None,
            height=50
        )

        self.fecha_entrega = TextInput(
            hint_text="Fecha entrega",
            size_hint_y=None,
            height=50
        )

        layout.add_widget(self.fecha_pedido)
        layout.add_widget(self.fecha_entrega)

        # 📦 LISTA PRODUCTOS
        layout.add_widget(Label(text="--- PEDIDO ---", size_hint_y=None, height=10))

        self.scroll = ScrollView(size_hint_y=None, height=100)
        self.lista = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.lista.bind(minimum_height=self.lista.setter("height"))

        self.scroll.add_widget(self.lista)
        layout.add_widget(self.scroll)

        # ➕ añadir producto
        btn_add = Button(text="+ Añadir producto", size_hint_y=None, height=50)
        btn_add.bind(on_press=self.add_producto)
        layout.add_widget(btn_add)

        btn_del = Button(text="- Borrar último", size_hint_y=None, height=50)
        btn_del.bind(on_press=self.borrar_producto)
        layout.add_widget(btn_del)

        # 💰 TOTAL
        self.lbl_total = Label(text="TOTAL: 0€", size_hint_y=None, height=40)
        layout.add_widget(self.lbl_total)

        # 💳 ESTADO PAGO
        layout.add_widget(Label(text="--- PAGO ---", size_hint_y=None, height=30))

        self.estado_pago = "pendiente"
        self.metodo_pago = ""

        fila_pago = BoxLayout(size_hint_y=None, height=50, spacing=10)

        btn_pendiente = Button(
            text="PENDIENTE PAGO",
            background_color=(1, 0.6, 0, 1)  # naranja
        )

        btn_pagado = Button(
            text="PAGADO",
            background_color=(0.2, 0.6, 1, 1)  # azul
        )

        btn_pendiente.bind(on_press=lambda x: self.set_pago("pendiente"))
        btn_pagado.bind(on_press=lambda x: self.set_pago("pagado"))

        fila_pago.add_widget(btn_pendiente)
        fila_pago.add_widget(btn_pagado)

        layout.add_widget(fila_pago)

        # métodos pago
        self.metodos_layout = BoxLayout(size_hint_y=None, height=50)

        for metodo in ["Efectivo", "Tarjeta", "Bizum"]:
            btn = Button(text=metodo)
            btn.bind(on_press=lambda x, m=metodo: self.set_metodo(m))
            self.metodos_layout.add_widget(btn)

        layout.add_widget(self.metodos_layout)
        self.metodos_layout.opacity = 0  # oculto al inicio


        fila_acciones = BoxLayout(size_hint_y=None, height=60, spacing=10)

        layout.add_widget(Label(text="--- Generar Ticket ---", size_hint_y=None, height=30))
        btn_pdf = Button(
            text="PDF",
            background_color=(0.3, 0.8, 0.3, 1)
        )

        btn_email = Button(
            text="Email",
            background_color=(0.6, 0.3, 0.8, 1)
        )

        btn_pdf.bind(on_press=self.generar_pdf_pedido)
        btn_email.bind(on_press=self.enviar_email)

        fila_acciones.add_widget(btn_pdf)
        fila_acciones.add_widget(btn_email)

        layout.add_widget(fila_acciones)


        btn_nuevo = Button(text="Nuevo pedido", size_hint_y=None, height=50)
        btn_nuevo.bind(on_press=self.nuevo_pedido)
        layout.add_widget(btn_nuevo)

    # ---------------- PRODUCTOS ----------------

    def add_producto(self, instance):

        fila = BoxLayout(size_hint_y=None, height=35, spacing=3)

        nombre = TextInput(hint_text="Producto", size_hint_x=2)
        v1 = TextInput(hint_text="Var1")
        v2 = TextInput(hint_text="Var2")
        cantidad = TextInput(hint_text="Cant", input_filter="int", size_hint_x=0.7)
        precio = TextInput(hint_text="€", input_filter="float", size_hint_x=0.8)

        fila.add_widget(nombre)
        fila.add_widget(v1)
        fila.add_widget(v2)
        fila.add_widget(cantidad)
        fila.add_widget(precio)

        self.lista.add_widget(fila)

        self.productos.append((nombre, v1, v2, cantidad, precio))

        # recalcular al escribir
        for campo in [cantidad, precio]:
            campo.bind(text=lambda x, y: self.calcular_total())

    def borrar_producto(self, instance):

        if self.productos:
            self.productos.pop()
            self.lista.remove_widget(self.lista.children[0])
            self.calcular_total()

    # ---------------- TOTAL ----------------

    def calcular_total(self):

        total = 0

        for n, v1, v2, c, p in self.productos:
            try:
                total += int(c.text) * float(p.text)
            except:
                pass

        self.lbl_total.text = f"TOTAL: {round(total,2)}€"

    # ---------------- PAGO ----------------

    def set_pago(self, estado):
        self.estado_pago = estado

        if estado == "pagado":
            self.metodos_layout.opacity = 1
        else:
            self.metodos_layout.opacity = 0
            self.metodo_pago = ""

    def set_metodo(self, metodo):
        self.metodo_pago = metodo
        print("Método:", metodo)


    # ---------------- PDF ---------------- 

    def generar_pdf_pedido(self, instance):

        nombre = self.nombre.text
        telefono = self.telefono.text
        fecha_pedido = self.fecha_pedido.text
        fecha_entrega = self.fecha_entrega.text

        # 🕒 nombre archivo único
        ahora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archivo = f"pedido_{nombre}_{ahora}.pdf".replace(" ", "_")

        doc = SimpleDocTemplate(archivo)
        styles = getSampleStyleSheet()

        elementos = []

        # 🧾 CABECERA
        elementos.append(Paragraph("RULIÑA - PEDIDO CLIENTE", styles["Title"]))
        elementos.append(Paragraph("------------------------------", styles["Normal"]))
        elementos.append(Spacer(1, 10))

        elementos.append(Paragraph(f"Cliente: {nombre}", styles["Normal"]))
        elementos.append(Paragraph(f"Teléfono: {telefono}", styles["Normal"]))
        elementos.append(Paragraph(f"Fecha pedido: {fecha_pedido}", styles["Normal"]))
        elementos.append(Paragraph(f"Fecha entrega: {fecha_entrega}", styles["Normal"]))

        elementos.append(Spacer(1, 15))

        # 📦 PRODUCTOS
        total = 0

        for n, v1, v2, c, p in self.productos:
            try:
                cantidad = int(c.text)
                precio = float(p.text)
                total_linea = cantidad * precio

                texto = f"{n.text} {v1.text} {v2.text} x{cantidad} = {total_linea:.2f}€"
                elementos.append(Paragraph(texto, styles["Normal"]))

                total += total_linea

            except:
                continue

        elementos.append(Spacer(1, 15))

        # 💰 TOTAL
        elementos.append(Paragraph(f"TOTAL: {round(total,2)}€", styles["Heading2"]))

        elementos.append(Spacer(1, 10))

        # 💳 PAGO
        if self.estado_pago == "pagado":
            elementos.append(Paragraph(f"Pagado ({self.metodo_pago})", styles["Normal"]))
        else:
            elementos.append(Paragraph("Pago pendiente", styles["Normal"]))

        # 🧱 construir PDF
        doc.build(elementos)

        print(f" PDF generado: {archivo}")


    def enviar_email(self, instance):

        import webbrowser

        nombre = self.nombre.text
        telefono = self.telefono.text

        resumen = ""
        total = 0

        for n, v1, v2, c, p in self.productos:
            try:
                cantidad = int(c.text)
                precio = float(p.text)
                total_linea = cantidad * precio

                linea = f"• {n.text} {v1.text} {v2.text} x{cantidad} = {total_linea:.2f}€\n"
                resumen += linea

                total += total_linea
            except:
                continue

        estado = "Pagado" if self.estado_pago == "pagado" else "Pendiente"

        cuerpo = f"""Hola {nombre} 😊,

    Aquí tienes el resumen de tu pedido:

    📦 PRODUCTOS:
    {resumen}

    💰 TOTAL: {total:.2f}€

    📅 Entrega: {self.fecha_entrega.text}
    💳 Estado: {estado}

    Gracias por confiar en Ruliña 💖✨
    """

        asunto = f"Pedido {nombre}"

        url = f"mailto:?subject={asunto}&body={cuerpo}"
        url = url.replace(" ", "%20").replace("\n", "%0A")

        webbrowser.open(url)

        print("Email completo preparado")

    def nuevo_pedido(self, instance):

        self.nombre.text = ""
        self.telefono.text = ""
        self.fecha_entrega.text = ""

        self.productos.clear()
        self.lista.clear_widgets()

        self.lbl_total.text = "TOTAL: 0€"

        self.estado_pago = "pendiente"
        self.metodo_pago = ""
        self.metodos_layout.opacity = 0

        print("Pedido limpio")

    