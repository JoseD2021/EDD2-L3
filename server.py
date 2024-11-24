import socket
import threading
from config import CONFIG_PARAMS
from typing import List
import pickle
import queue

# Configuration Parameters
IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
PORT = CONFIG_PARAMS['SERVER_PORT']
MAX_CLIENTS = CONFIG_PARAMS['SERVER_MAX_CLIENTS']
LIST_OF_CLIENTS: List["socket.socket"] = []
LIST_OF_WORKERS: List["socket.socket"] = []
terminado = True
resultados = queue.Queue()

# Remove Client from List of Clients
def remove_client(client_socket: "socket.socket") -> None:
    if client_socket in LIST_OF_CLIENTS:
        LIST_OF_CLIENTS.remove(client_socket)


# Attemp to Broadcast a worker Message
def broadcastWorker(message: bytes, client_socket: "socket.socket") -> None:
    for client in LIST_OF_WORKERS:
        if client != client_socket:
            try:
                client.sendall(message)
            except Exception as ex:
                client.close()
                remove_client(client)

# Attemp to Broadcast a client Message
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
    # try:
        
        client_socket.sendall(b'Seleccione un metodo de ordenamiento\n1) Mergesort\n2) Heapsort\n3) Quicksort')
        
        while True:
            # global terminado
            # if terminado:
                op = client_socket.recv(2048).decode('utf-8')
                op = int(op)
                if not op:
                    remove_client(client_socket)
                    break
                # print(f'<{client_address[0]}>', message.decode('utf-8'))

                client_socket.sendall(b'Ingrese el tiempo de ejecucion en segundos')
                t = int(client_socket.recv(2048).decode('utf-8'))

                if not t:
                    remove_client(client_socket)
                    break
                
                client_socket.sendall(b'Escriba "si" para enviar los datos')
                data = client_socket.recv(12288000) # 12288000

                if not data:
                    remove_client(client_socket)
                    break
                data = pickle.loads(data)
                client_socket.sendall(b'Por favor espere, estamos ordenando el vector')


                # print(f"{op.decode('utf-8')} +  {t.decode('utf-8')} + {data}")
                # message_to_send = bytes(f"{op.decode('utf-8')},{t.decode('utf-8')},{data}", 'utf-8')
                message_to_send = pickle.dumps([op,t, [data,t, None]])
                broadcastWorker(message_to_send, client_socket)

                message_to_send_user = resultados.get()
                print("Resultados para enviar: ",message_to_send_user)
                client_socket.sendall(message_to_send_user)

    # except Exception as ex:
    #     print(f'Error on client {client_address[0]}: {ex}')
    #     remove_client(client_socket)
    # finally:
    #     client_socket.close()

def handle_worker(client_socket: "socket.socket", client_address: "socket._RetAddress") -> None:
    #try:
        while True:
            message = client_socket.recv(12288000) # 12288000
            if not message:
                remove_client(client_socket)
                break
            message = pickle.loads(message)
            
            if message[2][1] == True:
                print(f"Lista ordenada {message[2][0]}")
                message_to_send = bytes(("Tiempo que tomo resolverlo: 0, vector ordenado: "+str(message[2][0])),"utf-8")
                resultados.put(message_to_send)
                #broadcastClient(message_to_send, client_socket)
            else:
                print("No se resolvio")
                message_to_send = pickle.dumps(message)
                broadcastWorker(message_to_send, client_socket)
    #except Exception as ex:
    #    print(f'Error on client {client_address[0]}: {ex}')
    #    remove_client(client_socket)
    #finally:
    #    client_socket.close()

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
        server_socket.close()


if __name__ == '__main__':
    start_server()