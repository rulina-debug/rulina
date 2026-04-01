import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


from db import obtener_ventas_mes_actual, borrar_todo_local

# 📄 PDF
def generar_pdf(ventas):

    from datetime import datetime

    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"caja_{fecha}.pdf"

    doc = SimpleDocTemplate(nombre_archivo)
    styles = getSampleStyleSheet()

    contenido = []

    contenido.append(Paragraph("Resumen de ventas mensual", styles["Title"]))

    total = 0

    for v in ventas:
        total_linea = float(v["precio"]) * int(v["cantidad"])

        linea = f"{v['fecha']} - {v['nombre']} x{v['cantidad']} = {total_linea:.2f}€"
        contenido.append(Paragraph(linea, styles["Normal"]))

        total += total_linea

    contenido.append(Paragraph(f"TOTAL: {round(total,2)}€", styles["Heading2"]))

    doc.build(contenido)

    print(f"PDF generado: {nombre_archivo}")


# 🧾 Pantalla Caja
from kivy.uix.screenmanager import Screen

class CajaScreen(Screen):

    def volver_menu(self, instance):
        self.manager.current = "menu"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # 🔙 botón volver
        btn_back = Button(
            text="VOLVER",
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.3, 0.3, 1)
        )
        btn_back.bind(on_press=self.volver_menu)

        layout.add_widget(btn_back)

        # 📊 botón caja
        btn = Button(text="Ver caja mensual", size_hint_y=None, height=60)
        btn.bind(on_press=self.abrir_caja)

        layout.add_widget(btn)

        self.add_widget(layout)

    def cerrar_caja(self):
        self.popup_caja.dismiss()
        self.manager.current = "menu"


    def abrir_caja(self, instance):

        ventas = obtener_ventas_mes_actual()

        layout = BoxLayout(orientation="vertical", spacing=10)

        # 🔙 BOTÓN VOLVER
        btn_volver = Button(
            text="Menú",
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.3, 0.3, 1)
        )

        btn_volver.bind(on_press=lambda x: self.cerrar_caja())

        layout.add_widget(btn_volver)

        scroll = ScrollView()
        lista = BoxLayout(orientation="vertical", size_hint_y=None)
        lista.bind(minimum_height=lista.setter("height"))

        self.venta_seleccionada = None

        total_mes = 0

        for v in ventas:

            texto = f"{v['fecha']} - {v['nombre']} {v['variante1']} {v['variante2']} x{v['cantidad']} = {v['precio'] * v['cantidad']:.2f}€"

            btn = Button(
                text=texto,
                size_hint_y=None,
                height=40
            )

            # 👉 seleccionar venta
            btn.bind(on_press=lambda x, v=v, b=btn: self.seleccionar_venta(v, b))

            lista.add_widget(btn)

            total_mes += float(v["precio"]) * int(v["cantidad"])

        scroll.add_widget(lista)
        layout.add_widget(scroll)

        layout.add_widget(Label(
            text=f"TOTAL MES: {round(total_mes,2)}€",
            size_hint_y=None,
            height=40
        ))

        # 🗑️ borrar una
        btn_borrar = Button(text="Borrar seleccionada", size_hint_y=None, height=50)
        btn_borrar.bind(on_press=lambda x: self.eliminar_seleccion())

        # 🧨 borrar todo
        btn_borrar_todo = Button(text="Borrar TODO", size_hint_y=None, height=50)
        btn_borrar_todo.bind(on_press=lambda x: self.eliminar_todo())

        # 📄 PDF
        btn_pdf = Button(text="Generar PDF", size_hint_y=None, height=50)
        btn_pdf.bind(on_press=lambda x: generar_pdf(ventas))

        layout.add_widget(btn_borrar)
        layout.add_widget(btn_borrar_todo)
        layout.add_widget(btn_pdf)

        self.popup_caja = Popup(
            title="Caja mensual",
            content=layout,
            size_hint=(0.95, 0.95)
        )

        self.popup_caja.open()


    def borrar_todo(self):
        borrar_todo_local()


    from db import borrar_venta_local

    def borrar_venta(self, id):
        borrar_venta_local(id)


    def seleccionar_venta(self, venta, boton):

        # 🔄 quitar color al anterior
        if hasattr(self, "boton_seleccionado") and self.boton_seleccionado:
            self.boton_seleccionado.background_color = (1, 1, 1, 1)

        # ✅ guardar nueva selección
        self.venta_seleccionada = venta
        self.boton_seleccionado = boton

        # 🎨 pintar seleccionado
        boton.background_color = (0.2, 0.8, 0.2, 1)  # verde bonito

        print("Seleccionada:", venta)


    def eliminar_seleccion(self):

        if not self.venta_seleccionada:
            print("❌ No hay selección")
            return

        from db import borrar_venta_local

        borrar_venta_local(self.venta_seleccionada["id"])

        print("🗑️ Venta eliminada")

        # 🔥 reset selección
        self.venta_seleccionada = None

        # 🔥 refrescar sin romper
        self.popup_caja.dismiss()
        self.abrir_caja(None)

    def eliminar_todo(self):
        self.borrar_todo()

        print("TODO BORRADO")

        self.popup_caja.dismiss()
        self.abrir_caja(None)