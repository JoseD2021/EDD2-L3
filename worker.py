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
sorted = 1
dataQueue = queue.Queue()

# Utilidad para verificar límite de tiempo
def check_time_limit(start_time: float, t: int, sorted_flag: list) -> bool:  # **# Cambio**
    """Verifica si el tiempo límite ha sido excedido."""
    if time.time() - start_time > t:
        sorted_flag[0] = 0
        return True
    return False


def controller (data: list):
    global initialTime
    initialTime = time.time()
    op = int(data[0])
    t = int(data[1])
    if op == 1:
        newData = mergeSort(data[2], t)
    elif op == 2:
        newData = heapSort(data[2], t)
    elif op == 3:
        newData = quickSort(data[2], t)

    newData = [op, t, sorted, newData]
    dataQueue.put(data)


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
            message = client_socket.recv(12288000)
            if not message:
                break
            data = pickle.loads(message)
            controller(data)
            #print(data)

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
            data = dataQueue.get()
            client_socket.sendall(pickle.dumps(data))
    except Exception as ex:
        print(f'Error sending messages: {ex}')
        client_socket.close()


if __name__ == '__main__':
    start_client()