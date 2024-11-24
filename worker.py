import socket
import threading
from config import CONFIG_PARAMS
import time
import pickle
import queue

# Configuration Parameters
SERVER_IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
SERVER_PORT = CONFIG_PARAMS['SERVER_PORT']
EXIT_MESSAGE = CONFIG_PARAMS['EXIT_MESSAGE']

initialTime = 0
dataQueue = queue.Queue()

def controller (data: list):
    op = int(data[0])
    t = int(data[1])
    if op == 1:
        newData = mergeSort(data[2], t)
    elif op == 2:
        newData = heap_sort_with_state(data[2][0], t, data[2][2])
    elif op == 3:
        newData = quickSort(data[2][0], t, data[2][2]) # quicksort devuelve lista bool stack, requiere array t y stack
    #print(f"New data: {newData}")
    newData = [op, t, newData]
    
    dataQueue.put(newData)

def mergeSort(arr, t):
    pass

def heapify_with_stack(arr, n, i, heapify_stack):
    while heapify_stack:
        node, state = heapify_stack.pop()

        if state == 0:  # Comparar y determinar el mayor
            largest = node
            left = 2 * node + 1
            right = 2 * node + 2

            if left < n and arr[left] > arr[largest]:
                largest = left
            if right < n and arr[right] > arr[largest]:
                largest = right

            if largest != node:
                arr[node], arr[largest] = arr[largest], arr[node]
                heapify_stack.append((largest, 0))  # Continuar con el subárbol
        else:
            break

        # Pausar brevemente para observar el proceso
        time.sleep(.001)

    return heapify_stack

def heap_sort_with_state(arr, max_time, execution_state=None):
    start_time = time.time()
    n = len(arr)

    # Inicializar estado si no se proporciona
    if execution_state is None:
        execution_state = {
            "phase": "build_heap",
            "build_index": n // 2 - 1,
            "sort_index": n - 1,
            "heapify_stack": [],
        }

    phase = execution_state["phase"]
    build_index = execution_state["build_index"]
    sort_index = execution_state["sort_index"]
    heapify_stack = execution_state["heapify_stack"]

    # Fase 1: Construcción del heap
    if phase == "build_heap":
        while build_index >= 0:
            if time.time() - start_time > max_time:
                return [arr, False, {
                    "phase": "build_heap",
                    "build_index": build_index,
                    "sort_index": sort_index,
                    "heapify_stack": heapify_stack,
                }]

            if not heapify_stack:
                heapify_stack = [(build_index, 0)]

            heapify_stack = heapify_with_stack(arr, n, build_index, heapify_stack)
            if not heapify_stack:
                build_index -= 1

        # Cambiar a la fase de ordenamiento
        execution_state["phase"] = "sort_heap"
        execution_state["sort_index"] = n - 1

    # Fase 2: Ordenamiento por extracción
    if phase == "sort_heap":
        while sort_index > 0:
            if time.time() - start_time > max_time:
                return [arr, False, {
                    "phase": "sort_heap",
                    "build_index": build_index,
                    "sort_index": sort_index,
                    "heapify_stack": heapify_stack,
                }]

            # Intercambiar la raíz del heap con el último elemento
            arr[0], arr[sort_index] = arr[sort_index], arr[0]
            sort_index -= 1  # Reducir el tamaño del heap

            # Restablecer heapify_stack para reordenar el heap restante
            heapify_stack = [(0, 0)]
            heapify_stack = heapify_with_stack(arr, sort_index + 1, 0, heapify_stack)

            # Pausa para simular procesamiento
            time.sleep(.001)

    # Verificar si el arreglo está completamente ordenado
    is_sorted = all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))
    return [arr, is_sorted, None if is_sorted else execution_state]


def quickSort(arr, t, stack=None):
    print(f"Stack: {stack}")
    start_time = time.time()
    if stack is None:
        stack = [(0, len(arr) - 1)]
    is_sorted = True

    while stack:
        start, end = stack.pop()
        if start >= end:
            continue

        pivot = arr[end]
        low = start

        for i in range(start, end):
            if arr[i] < pivot:
                arr[i], arr[low] = arr[low], arr[i]
                low += 1

        arr[low], arr[end] = arr[end], arr[low]

        if time.time() - start_time > t:
            stack.append((start, low - 1))
            stack.append((low + 1, end))
            is_sorted = False
            break

        stack.append((start, low - 1))
        stack.append((low + 1, end))
        time.sleep(.001)
    return [arr, is_sorted, stack]

# Receive Message Method (Secondary Thread)
def receive_messages(client_socket: "socket.socket") -> None:
    try:
        while True:
            message = client_socket.recv(30000000)
            if not message:
                break
            data = pickle.loads(message)
            #print(f"Data: {data}")
            controller(data)
            # print("informacion recibida", data)
            
            #print('<You> ', end = '', flush = True)
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
            print("\n\nEsperando cola")
            data = dataQueue.get()
            print("Cola recibida")
            client_socket.sendall(pickle.dumps(data))
            print("Enviado a server")
    except Exception as ex:
        print(f'Error sending messages: {ex}')
        client_socket.close()


if __name__ == '__main__':
    start_client()