import sqlite3
import os
from kivy.app import App
from datetime import datetime

# 📁 ruta dinámica (PC + móvil)
def get_db_path(nombre_db):
    from kivy.app import App
    import os

    app = App.get_running_app()

    if app:
        return os.path.join(app.user_data_dir, nombre_db)
    else:
        # 🔥 FORZAR ruta real en PC
        return os.path.join(os.path.dirname(__file__), nombre_db)

    print("USANDO DB:", get_db_path("inventario.db"))

# 📷 imágenes
BASE_DIR = "imagenes"

# ---------------- PRODUCTOS ----------------

def obtener_productos():
    conn = sqlite3.connect(get_db_path("inventario.db"))
    cur = conn.cursor()

    cur.execute("""
        SELECT MIN(referencia), nombre, MIN(precio), SUM(cantidad), MIN(imagen)
        FROM inventario
        WHERE activo=1 AND tipo='terminado'
        GROUP BY nombre
    """)

    datos = []

    for ref, nombre, precio, cantidad, imagen in cur.fetchall():

        if imagen:
            ruta_imagen = os.path.join(BASE_DIR, imagen)
        else:
            ruta_imagen = "imagenes/default.png"

        datos.append((ref, nombre, precio, cantidad, ruta_imagen))

    conn.close()
    return datos


def obtener_variantes(nombre):
    conn = sqlite3.connect(get_db_path("inventario.db"))
    cur = conn.cursor()

    cur.execute("""
        SELECT referencia, nombre, variante1, variante2, precio, cantidad
        FROM inventario
        WHERE nombre=? AND activo=1
    """, (nombre,))

    datos = cur.fetchall()
    conn.close()
    return datos


# ---------------- VENTAS ----------------

def guardar_venta(carrito):
    conn = sqlite3.connect(get_db_path("tienda.db"))
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in carrito:
        cursor.execute("""
            INSERT INTO ventas (ref, nombre, precio, cantidad, fecha)
            VALUES (?, ?, ?, ?, ?)
        """, (
            item["ref"],
            item["nombre"],
            item["precio"],
            item["cantidad"],
            fecha
        ))

    conn.commit()
    conn.close()


def obtener_ventas_mes_actual():
    conn = sqlite3.connect(get_db_path("tienda.db"))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, precio, cantidad, fecha
        FROM ventas
        WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
    """)

    datos = cursor.fetchall()
    conn.close()

    ventas_formateadas = []

    for id_, nombre, precio, cantidad, fecha in datos:

        partes = nombre.split(" ")

        nombre_base = partes[0]
        variante1 = partes[1] if len(partes) > 1 else ""
        variante2 = partes[2] if len(partes) > 2 else ""

        ventas_formateadas.append({
            "id": id_,
            "nombre": nombre_base,
            "variante1": variante1,
            "variante2": variante2,
            "precio": precio,
            "cantidad": cantidad,
            "fecha": fecha
        })

    return ventas_formateadas


# ---------------- PDF ----------------

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def exportar_pdf(ventas):
    fecha = datetime.now().strftime("%Y-%m")
    nombre_archivo = f"caja_{fecha}.pdf"

    doc = SimpleDocTemplate(nombre_archivo)
    estilos = getSampleStyleSheet()

    elementos = []

    elementos.append(Paragraph(f"Reporte de Caja - {fecha}", estilos["Title"]))
    elementos.append(Spacer(1, 10))

    total = 0

    for nombre, precio, cantidad, fecha in ventas:
        linea = f"{nombre} x{cantidad} - {precio * cantidad:.2f}€"
        elementos.append(Paragraph(linea, estilos["Normal"]))
        total += precio * cantidad

    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph(f"TOTAL: {total:.2f}€", estilos["Heading2"]))

    doc.build(elementos)

    print("PDF generado:", nombre_archivo)


# ---------------- TABLA ----------------

def crear_tabla_ventas():
    conn = sqlite3.connect(get_db_path("tienda.db"))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT,
            nombre TEXT,
            precio REAL,
            cantidad INTEGER,
            fecha TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- BORRADO ----------------

def borrar_todo_local():
    conn = sqlite3.connect(get_db_path("tienda.db"))
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ventas")

    conn.commit()
    conn.close()


def borrar_venta_local(id):
    conn = sqlite3.connect(get_db_path("tienda.db"))
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ventas WHERE id=?", (id,))

    conn.commit()
    conn.close()