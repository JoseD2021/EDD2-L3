import socket
import threading
from config import CONFIG_PARAMS
import time

# Configuration Parameters
SERVER_IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
SERVER_PORT = CONFIG_PARAMS['SERVER_PORT']
EXIT_MESSAGE = CONFIG_PARAMS['EXIT_MESSAGE']

initialTime = 0
sorted = 1

def controller (data: str):
    global initialTime
    initialTime = time.time()
    data = data.split(",")
    op = data.pop(0)
    t = data.pop(0)
    if op == 1:
        newData = mergeSort(data, t)
    elif op == 2:
        newData = heapSort(data, t)
    elif op == 3:
        newData = quickSort(data, t)

    newData = f"{sorted},"

def mergeSort(data: str, t:int) -> list:
    global initialTime

    if len(data) <= 1:
        return data

    if time.time() - initialTime > t: 
        global sorted 
        sorted = 0
        return data
    
    mid = len(data) // 2
    leftHalf = data[:mid]
    rightHalf = data[mid:]


    sortedLeft = mergeSort(leftHalf)
    sortedRight = mergeSort(rightHalf)

    return merge(sortedLeft, sortedRight)

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

def heapSort(data, t:int):
    pass

def quickSort(data, t:int):
    pass

# Receive Message Method (Secondary Thread)
def receive_messages(client_socket: "socket.socket") -> None:
    try:
        while True:
            message = client_socket.recv(2048)
            if not message:
                break
            print('\r', end = '')
            data = message.decode('utf-8')
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
            message = input('<You> ')
            if message.lower() == EXIT_MESSAGE:
                print('Closing Connection...')
                client_socket.close()
                break
            
            client_socket.sendall(bytes(message, 'utf-8'))
    except Exception as ex:
        print(f'Error sending messages: {ex}')
        client_socket.close()


if __name__ == '__main__':
    start_client()