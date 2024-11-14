import os
import json
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import asyncio

# Archivo JSON para almacenar las cuentas vinculadas
ARCHIVO_CUENTAS = 'cuentas_vinculadas.json'

# Cargar cuentas desde el archivo JSON
def cargar_cuentas():
    if os.path.exists(ARCHIVO_CUENTAS):
        with open(ARCHIVO_CUENTAS, 'r') as archivo:
            return json.load(archivo)
    return {}

# Guardar cuentas en el archivo JSON
def guardar_cuentas(cuentas):
    with open(ARCHIVO_CUENTAS, 'w') as archivo:
        json.dump(cuentas, archivo)

# Función para agregar una nueva cuenta
async def agregar_cuenta():
    api_id = input("Ingrese el API ID: ")
    api_hash = input("Ingrese el API HASH: ")
    numero_telefono = input("Ingrese el número de teléfono (incluya el código de país): ")

    # Crear un nuevo cliente de Telethon
    client = TelegramClient(f'sesion_{numero_telefono}', api_id, api_hash)

    await client.connect()
    
    # Verificar si se requiere contraseña de dos factores
    if not await client.is_user_authorized():
        await client.send_code_request(numero_telefono)
        try:
            codigo = input("Ingrese el código recibido: ")
            await client.sign_in(numero_telefono, codigo)
        except SessionPasswordNeededError:
            contrasena = input("La cuenta tiene 2FA, ingrese la contraseña: ")
            await client.sign_in(password=contrasena)

    # Guardar la nueva cuenta en el archivo JSON
    cuentas = cargar_cuentas()
    cuentas[numero_telefono] = {"api_id": api_id, "api_hash": api_hash}
    guardar_cuentas(cuentas)

    print(f"La cuenta con el número {numero_telefono} ha sido agregada exitosamente.")
    await client.disconnect()

# Función para eliminar una cuenta existente
def eliminar_cuenta():
    cuentas = cargar_cuentas()
    if not cuentas:
        print("No hay cuentas vinculadas.")
        return

    # Mostrar las cuentas vinculadas con índice
    print("Cuentas vinculadas:")
    for i, numero in enumerate(cuentas.keys(), start=1):
        print(f"{i}: {numero}")

    # Seleccionar la cuenta a eliminar
    indice = int(input("Ingrese el número de la cuenta que desea eliminar: ")) - 1
    if indice < 0 or indice >= len(cuentas):
        print("Índice no válido.")
        return

    numero_a_eliminar = list(cuentas.keys())[indice]
    del cuentas[numero_a_eliminar]
    guardar_cuentas(cuentas)
    
    # Eliminar la sesión de la cuenta eliminada
    archivo_sesion = f'sesion_{numero_a_eliminar}.session'
    if os.path.exists(archivo_sesion):
        os.remove(archivo_sesion)

    print(f"La cuenta con el número {numero_a_eliminar} ha sido eliminada.")

# Menú principal
def menu():
    while True:
        print("\nSeleccione una opción:")
        print("1: Agregar cuenta")
        print("2: Eliminar cuenta")
        print("3: Salir")

        opcion = input("Opción: ")

        if opcion == '1':
            asyncio.run(agregar_cuenta())
        elif opcion == '2':
            eliminar_cuenta()
        elif opcion == '3':
            break
        else:
            print("Opción no válida.")

if __name__ == '__main__':
    menu()
