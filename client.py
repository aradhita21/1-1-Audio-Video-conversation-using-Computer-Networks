import cv2
import numpy as np
import socket
import sys
import pickle
import struct
import pyaudio
import threading
from threading import Thread
import time

#HOST1 = '172.16.37.198'
#PORTA = 8000
#PORTV = 8089

def client(HOST1,HOST2,PORT_v_recv,PORT_a_recv,PORT_v_send,PORT_a_send):
    b=1
    #videosocket
    sock = None
    clientvideosocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    clientvideosocket.connect((HOST1,PORT_v_recv))
    #audiosocket
    clientaudiosocket = socket.socket()
    clientaudiosocket.connect((HOST1,PORT_a_recv))
    #Audio
    chunk = 1024
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = 44100,
                    output = True,
                    frames_per_buffer = chunk)
    #video
    cap = cv2.VideoCapture(0)
    cap.set(3,320)
    cap.set(4,240)

    def receiveVideo():
        conn = clientvideosocket
        data = b'' ### CHANGED
        payload_size = struct.calcsize("L") ### CHANGED

        while True:
        # Retrieve message size
            while len(data) < payload_size:
                data += conn.recv(4096)
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED
            # Retrieve all data based on message size
            while len(data) < msg_size:
                data += conn.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]
            # Extract frame
            frame = pickle.loads(frame_data)
            # Display
            cv2.imshow('frame', frame)
            cv2.waitKey(1)

    def receiveAudio():
         while True:
              audioData = clientaudiosocket.recv(1024)
              stream.write(audioData)         
    Thread(target = receiveVideo).start()
    Thread(target = receiveAudio).start()

        
        #HOST_send = '192.168.0.100'
        #PORTV_send = 8085
        #PORTA_send = 8006
    if(b==1):
        cap = cv2.VideoCapture(0)
        #cap = cv2.VideoCapture('https://hosting1234567.000webhostapp.com/final_hackathon_video.mp4')
        cap.set(3,320)
        cap.set(4,240)

        #videosocket
        videosocket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')
        videosocket_send.bind((HOST2, PORT_v_send))
        print('Socket bind complete')
        videosocket_send.listen(10)
        print('Socket now listening')
        cVideo_send, addr_send = videosocket_send.accept()
        print(addr_send)
        #audiosocket
        audiosocket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        audiosocket_send.bind((HOST2,PORT_a_send))
        print('audio binded')
        audiosocket_send.listen(5)
        print('audio listening')
        cAudio_send, addr = audiosocket_send.accept()
        print(addr)
        cap_send = cv2.VideoCapture(0)
        cap_send.set(3,320)
        cap_send.set(4,240)
        #Audio
        chunk = 1024
        chunk = 1024
        p_send = pyaudio.PyAudio()
        stream_send = p_send.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = 44100,
                    input = True,
                    frames_per_buffer = chunk)


        def recordVideo_send():
            while True:
                ret,frame=cap.read() # Serialize frame
                data = pickle.dumps(frame)# Send message length first
                message_size = struct.pack("L", len(data)) ### CHANGED
                #print("sending data")# Then data
                cVideo_send.sendall(message_size + data)

        def recordAudio_send():
            time.sleep(5)
            while True:
                data = stream_send.read(chunk)
                if data:
                    cAudio_send.sendall(data)

        print ('Connection accepted from ', addr)

        Thread(target = recordAudio_send).start()
        Thread(target = recordVideo_send).start()
    
