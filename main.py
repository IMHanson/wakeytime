# This is your main script.
import time
import socket
import select
from machine import Pin
import eyes
import nattlys

button = Pin(19, Pin.IN, Pin.PULL_UP)
wakey_time = nattlys.get_wakeytime()
sleepy_time = nattlys.get_sleepytime()

#####   Web Page    #####

# HTTP server response
def http_response(status_code, content):
    return f"HTTP/1.0 {status_code}\r\n\n{content}\r\n".encode('utf-8')

# Handle client connections
def handle_requests():
    client, address = server_socket.accept()
    request = client.recv(1024)
    method = request.decode().split(' ')[0]
    path = request.decode().split(' ')[1]

    if path == '/':
        with open('index.html', 'r') as index:
            content = index.read()
        response = http_response('200 OK', content)
    
    elif path == '/wakey-time':
        if method == 'GET':
            response = http_response('200 OK', wakey_time)
        elif method == 'POST':
            request_content = request.decode().split('\r\n')[-1]
            nattlys.change_wakey_time(request_content)
            response = http_response('200 OK', 'Wakey-Time updated')

server_socket = socket.socket()
server_socket.bind(('', 80))
server_socket.listen(5)

select_obj = select.poll()
select_obj.register(server_socket, select.POLLIN)

#####   Main Loop   #####

while True:

    if not button.value():
        nattlys.dance_party()
        time.sleep_ms(100)
    
    handle_requests()
    nattlys.update_lights()
    time.sleep(10)