import numpy as np
import struct
import socket
import cv2
import pickle
import time
import pyaudio
import threading
from threading import Thread

def server(HOST1,HOST2,PORT_v_send,PORT_a_send, PORT_v_recv, PORT_a_recv):
    b=1  
#HOST1 = '192.168.0.107'
#PORT_v_send = 8089
#PORT_a_send = 8000

    #videosocket
    videosocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')
    videosocket.bind((HOST1, PORT_v_send))
    print('Socket bind complete')
    videosocket.listen(10)
    print('Socket now listening')
    cVideo, addr = videosocket.accept()
    print(addr)
    #audiosocket
    audiosocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audiosocket.bind((HOST1,PORT_a_send))
    print('audio binded')
    audiosocket.listen(5)
    print('audio listening')
    cAudio, addr = audiosocket.accept()
    print(addr)
    #Video
    cap = cv2.VideoCapture(0)
    cap.set(3,320)
    cap.set(4,240)
    #Audio
    chunk = 1024
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = 44100,
                    input = True,
                    frames_per_buffer = chunk)


    def recordVideo():
        while True:
            ret,frame=cap.read() # Serialize frame
            data = pickle.dumps(frame)# Send message length first
            message_size = struct.pack("L", len(data)) ### CHANGED
            #print("sending data")# Then data
            cVideo.sendall(message_size + data)

    def recordAudio():
        time.sleep(5)
        while True:
            data = stream.read(chunk)
            if data:
                cAudio.sendall(data)

    print ('Connection accepted from ', addr)

    Thread(target = recordAudio).start()
    Thread(target = recordVideo).start()
    i=0
    while(i<1):
        try:
            if(b==1):
                #HOST2 = '172.16.37.141'
                #PORT_a_recv = 8006
                #PORT_v_recv = 8085
                #videosocket
                sock = None
                clientvideosocket_recv=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                clientvideosocket_recv.connect((HOST2,PORT_v_recv))
                #audiosocket
                clientaudiosocket_recv = socket.socket()
                clientaudiosocket_recv.connect((HOST2,PORT_a_recv))
                i=1
                #Audio
                chunk = 1024
                p_recv = pyaudio.PyAudio()
                stream_recv = p_recv.open(format = pyaudio.paInt16,
                                channels = 1,
                                rate = 44100,
                                output = True,
                                frames_per_buffer = chunk)
                #video
                cap_recv = cv2.VideoCapture(0)
                cap_recv.set(3,320)
                cap_recv.set(4,240)

                def receiveVideo_recv():
                    conn_recv = clientvideosocket_recv
                    #conn, addr = clientvideosocket.recvfrom(230400)

                    data = b'' ### CHANGED
                    payload_size = struct.calcsize("L") ### CHANGED

                    while True:
                        # Retrieve message size
                        while len(data) < payload_size:
                            data += conn_recv.recv(4096)
                        packed_msg_size = data[:payload_size]
                        data = data[payload_size:]
                        msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED
                        # Retrieve all data based on message size
                        while len(data) < msg_size:
                            data += conn_recv.recv(4096)
                        frame_data = data[:msg_size]
                        data = data[msg_size:]
                        # Extract frame
                        frame = pickle.loads(frame_data)
                        #print("akshatt", frame)
                        # Display
                        cv2.imshow('frame', frame)
                        cv2.waitKey(1)

                def receiveAudio_recv():
                    while True:
                          audioData_recv = clientaudiosocket_recv.recv(1024)
                          stream_recv.write(audioData_recv)
                          
                Thread(target = receiveVideo_recv).start()
                Thread(target = receiveAudio_recv).start()
        except:
            pass
 #server('172.16.37.198','172.16.37.141',8089,8000,8085,8006)       
