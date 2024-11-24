import socket
import threading
from config import CONFIG_PARAMS
import pickle

# Configuration Parameters
SERVER_IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
SERVER_PORT = CONFIG_PARAMS['SERVER_PORT']
EXIT_MESSAGE = CONFIG_PARAMS['EXIT_MESSAGE']

def read_txt(ruta):
    try:
        with open(ruta, 'r') as archivo:
            lineas = archivo.readlines()
            vector = [int(linea.strip()) for linea in lineas if linea.strip().isdigit()]
        return vector
    except Exception as ex:
        print(f"Error al leer el archivo: {ex}")
        return []

# Receive Message Method (Secondary Thread)
def receive_messages(client_socket: "socket.socket") -> None:
    try:
        while True:
            message = client_socket.recv(2048)
            if not message:
                break
            print('\r', end = '')
            print(message.decode('utf-8'))
            print('<You> ', end = '', flush = True)
    except Exception as ex:
        print(f'Error receiving messages: {ex}')
    finally:
        client_socket.close()

# Start Client Method (Main Thread)
def start_client() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP_ADDRESS, SERVER_PORT))

    receive_thread = threading.Thread(target = receive_messages, args = (client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        while True:
            message = input('<You> ')
            if message.lower() == EXIT_MESSAGE:
                print('Closing Connection...')
                client_socket.close()
                break
            elif message.lower() == "si":
                ruta_archivo = 'test.txt'
                vector = read_txt(ruta_archivo)
                if vector:
                    client_socket.sendall(pickle.dumps(vector))
                else:
                    print("No se pudo leer el archivo o está vacío.")
                continue
            client_socket.sendall(bytes(message, 'utf-8'))
    except Exception as ex:
        print(f'Error sending messages: {ex}')
        client_socket.close()


if __name__ == '__main__':
    start_client()


""" copia por si acaso
import socket
import threading
from config import CONFIG_PARAMS
import pickle
# Configuration Parameters
SERVER_IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
SERVER_PORT = CONFIG_PARAMS['SERVER_PORT']
EXIT_MESSAGE = CONFIG_PARAMS['EXIT_MESSAGE']

# Receive Message Method (Secondary Thread)
def receive_messages(client_socket: "socket.socket") -> None:
    try:
        while True:
            message = client_socket.recv(2048)
            if not message:
                break
            print('\r', end = '')
            print(message.decode('utf-8'))
            print('<You> ', end = '', flush = True)
    except Exception as ex:
        print(f'Error receiving messages: {ex}')
    finally:
        client_socket.close()



datos = [1,2,3]
# Start Client Method (Main Thread)
def start_client() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP_ADDRESS, SERVER_PORT))

    receive_thread = threading.Thread(target = receive_messages, args = (client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        while True:
            message = input('<You> ')
            if message.lower() == EXIT_MESSAGE:
                print('Closing Connection...')
                client_socket.close()
                break
            elif message.lower() == "si":
                client_socket.sendall(pickle.dumps(datos))
                continue
            client_socket.sendall(bytes(message, 'utf-8'))
    except Exception as ex:
        print(f'Error sending messages: {ex}')
        client_socket.close()


if __name__ == '__main__':
    start_client()
"""