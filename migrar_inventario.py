import sqlite3
import pymysql

# SQLite
sqlite_conn = sqlite3.connect(r"D:\IMAGENES\Titanium Events\Pedidos\inventario.db")
sqlite_cursor = sqlite_conn.cursor()

# MySQL con pymysql 💥
mysql_conn = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="rulina",
    port=3306
)

mysql_cursor = mysql_conn.cursor()

sqlite_cursor.execute("""
SELECT referencia, nombre, variante1, variante2, precio, cantidad, imagen, tipo, activo
FROM inventario
WHERE activo=1
""")

for row in sqlite_cursor.fetchall():
    mysql_cursor.execute("""
        INSERT INTO productos 
        (referencia, nombre, variante1, variante2, precio, cantidad, imagen, tipo, activo)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, row)

mysql_conn.commit()

sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(sqlite_cursor.fetchall())

print("💥 Inventario migrado correctamente")