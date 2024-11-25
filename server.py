import socket
import threading
from config import CONFIG_PARAMS
from typing import List
import pickle
import queue
import time

# Configuration Parameters
IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
PORT = CONFIG_PARAMS['SERVER_PORT']
MAX_CLIENTS = CONFIG_PARAMS['SERVER_MAX_CLIENTS']
LIST_OF_CLIENTS: List["socket.socket"] = []
LIST_OF_WORKERS: List["socket.socket"] = []
worker_activo = -1
resultados = queue.Queue()
tiempoInicial = 0

# Remove Client from List of Clients
def remove_client(client_socket: "socket.socket") -> None:
    if client_socket in LIST_OF_CLIENTS:
        LIST_OF_CLIENTS.remove(client_socket)
    if client_socket in LIST_OF_WORKERS:
        LIST_OF_CLIENTS.remove(client_socket)

def broadcastWorker(message: bytes) -> None:
    global worker_activo
    worker_activo += 1
    if worker_activo >= len(LIST_OF_WORKERS):
        worker_activo = 0
    try:
        LIST_OF_WORKERS[worker_activo].sendall(message)
    except Exception as ex:
        LIST_OF_WORKERS[worker_activo].close()
        remove_client(LIST_OF_WORKERS[worker_activo])

# no usado
def broadcastClient(message: bytes, client_socket: "socket.socket") -> None:
    for client in LIST_OF_CLIENTS:
        if client != client_socket:
            try:
                print("Enviando a cliente")
                client.sendall(message)
            except Exception as ex:
                client.close()
                remove_client(client)

# Handle Client Method (Clients Secondary Threads)
def handle_client(client_socket: "socket.socket", client_address: "socket._RetAddress") -> None:
    try:
        client_socket.sendall(b'Seleccione un metodo de ordenamiento\n1) Mergesort\n2) Heapsort\n3) Quicksort')
        while True:
            op = int(client_socket.recv(2048).decode('utf-8'))
            if not op:
                remove_client(client_socket)
                break

            client_socket.sendall(b'Ingrese el tiempo de ejecucion en segundos')
            t = float(client_socket.recv(2048).decode('utf-8'))
            if not t:
                remove_client(client_socket)
                break
            
            client_socket.sendall(b'Escriba "si" para enviar los datos')
            data = client_socket.recv(30000000) 

            if not data:
                remove_client(client_socket)
                break

            data = pickle.loads(data)
            client_socket.sendall(b'Por favor espere, estamos ordenando el vector')

            global tiempoInicial
            tiempoInicial = time.time()
            message_to_send = pickle.dumps([op,t, [data,t, None]])
            broadcastWorker(message_to_send)
            message_to_send_user = resultados.get()

            client_socket.sendall(message_to_send_user)
            client_socket.sendall(b'\nSeleccione un metodo de ordenamiento\n1) Mergesort\n2) Heapsort\n3) Quicksort')

    except Exception as ex:
        print(f'Error on client {client_address[0]}: {ex}')
        remove_client(client_socket)
    finally:
        client_socket.close()

def handle_worker(client_socket: "socket.socket", client_address: "socket._RetAddress") -> None:
    try:
        while True:
            message = client_socket.recv(30000000) # 12288000
            if not message:
                remove_client(client_socket)
                break
            message = pickle.loads(message)
            
            if message[2][1] == True:
                # print(f"Lista ordenada {message[2][0]}")
                global tiempoInicial
                message_to_send = bytes(("Vector ordenado: "+str(message[2][0])+"\nTiempo que tomo resolverlo: "+(time.time()-tiempoInicial)+" segundos"),"utf-8")
                resultados.put(message_to_send) 
            else:
                print(f"El worker {LIST_OF_WORKERS[worker_activo]} no termino el ordenamiento. Enviando a worker {LIST_OF_WORKERS[worker_activo+1] if worker_activo+1 < len(LIST_OF_WORKERS) else LIST_OF_WORKERS[0]}")
                message_to_send = pickle.dumps(message)
                broadcastWorker(message_to_send)
    except Exception as ex:
        print(f'Error on worker {client_address[0]}: {ex}')
        remove_client(client_socket)
    finally:
        client_socket.close()

# Start Server Method (Main Thread)
def start_server() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP_ADDRESS, PORT))
    server_socket.listen(MAX_CLIENTS)

    print(f'Server started at {IP_ADDRESS}:{PORT} and listening...')

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            
            
            if not len(LIST_OF_CLIENTS): # definir la conexion como cliente si no hay ninguno
                print(client_address[0], 'connected as client')
                LIST_OF_CLIENTS.append(client_socket)
                client_thread = threading.Thread(target = handle_client, args = (client_socket, client_address))
            else:   # si ya hay cliente se definen los demas como worker
                print(client_address[0], 'connected as worker')
                LIST_OF_WORKERS.append(client_socket)
                client_thread = threading.Thread(target = handle_worker, args = (client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
    except Exception as ex:
        print(f'Error accepting clients: {ex}')
        print('Closing the server...')
    finally:
        for client in LIST_OF_CLIENTS:
            client.close()
        for client in LIST_OF_WORKERS:
            client.close()
        server_socket.close()


if __name__ == '__main__':
    start_server()