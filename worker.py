import socket
import threading
import time
from config import CONFIG_PARAMS

# Configuration Parameters
SERVER_IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
SERVER_PORT = CONFIG_PARAMS['SERVER_PORT']
EXIT_MESSAGE = CONFIG_PARAMS['EXIT_MESSAGE']

lock = threading.Lock()  # Para proteger el acceso a las variables globales

# Utilidad para verificar límite de tiempo
def check_time_limit(start_time: float, t: int, sorted_flag: list) -> bool:  # **# Cambio**
    """Verifica si el tiempo límite ha sido excedido."""
    if time.time() - start_time > t:
        sorted_flag[0] = 0
        return True
    return False


def controller(data: str):
    global lock

    with lock:
        try:
            # Inicializar variables locales
            start_time = time.time()  # **# Cambio** (Eliminado uso de variable global)
            is_sorted = [1]  # Usar lista para referencia mutable

            # Parsear y validar entrada
            data = data.split(",")
            if len(data) < 2:
                return "0,Error: Insufficient data"

            try:
                op = int(data.pop(0))
                t = int(data.pop(0))
                if t <= 0:
                    return "0,Error: Invalid time limit"
                array = list(map(int, data))
            except ValueError:
                return "0,Error: Non-numeric data"

            # Seleccionar algoritmo
            if op == 1:
                result = mergeSort(array, t, start_time, is_sorted)  # **# Cambio**
            elif op == 2:
                result = heapSort(array, t, start_time, is_sorted)  # **# Cambio**
            elif op == 3:
                result = quickSort(array, t, start_time, is_sorted)  # **# Cambio**
            else:
                return "0,Error: Invalid operation"

            # Construir respuesta
            return f"{is_sorted[0]}," + ",".join(map(str, result))

        except Exception as e:
            return f"0,Error: {str(e)}"


def mergeSort(data: list, t: int, start_time: float, sorted_flag: list) -> list:  # **# Cambio**
    if len(data) <= 1:
        return data

    if check_time_limit(start_time, t, sorted_flag):  # **# Cambio**
        return data

    mid = len(data) // 2
    leftHalf = mergeSort(data[:mid], t, start_time, sorted_flag)  # **# Cambio**
    rightHalf = mergeSort(data[mid:], t, start_time, sorted_flag)  # **# Cambio**

    return merge(leftHalf, rightHalf)


def merge(left, right) -> list:
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result


def heapSort(data: list, t: int, start_time: float, sorted_flag: list) -> list:  # **# Cambio**

    def heapify(arr, n, i):
        if check_time_limit(start_time, t, sorted_flag):  # **# Cambio**
            return

        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and arr[left] > arr[largest]:
            largest = left
        if right < n and arr[right] > arr[largest]:
            largest = right

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    n = len(data)

    # Construir max-heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(data, n, i)
        if sorted_flag[0] == 0:
            return data

    # Extraer elementos del heap
    for i in range(n - 1, 0, -1):
        data[i], data[0] = data[0], data[i]
        heapify(data, i, 0)
        if sorted_flag[0] == 0:
            return data

    return data


def quickSort(data: list, t: int, start_time: float, sorted_flag: list) -> list:  # **# Cambio**
    if len(data) <= 1:
        return data

    if check_time_limit(start_time, t, sorted_flag):  # **# Cambio**
        return data

    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]

    # Aplicar quickSort recursivamente
    sortedLeft = quickSort(left, t, start_time, sorted_flag)  # **# Cambio**
    sortedRight = quickSort(right, t, start_time, sorted_flag)  # **# Cambio**

    return sortedLeft + middle + sortedRight


# Receive Message Method (Secondary Thread)
def receive_messages(client_socket: "socket.socket") -> None:
    try:
        while True:
            message = client_socket.recv(2048)
            if not message:
                break

            data = message.decode('utf-8')
            response = controller(data)
            print(f"Server response: {response}")  # **# Cambio**

    except Exception as ex:
        print(f'Error receiving messages: {ex}')
    finally:
        client_socket.close()


# Start Client Method (Main Thread)
def start_client() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP_ADDRESS, SERVER_PORT))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        while True:
            message = input('<You> ')
            if message.lower() == EXIT_MESSAGE:
                print('Closing Connection...')
                client_socket.close()
                break

            client_socket.sendall(bytes(message, 'utf-8'))
    except Exception as ex:
        print(f'Error sending messages: {ex}')
    finally:
        if not client_socket._closed:  # **# Cambio**
            client_socket.close()


if __name__ == '__main__':
    start_client()
