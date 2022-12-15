import tkinter as tk
import socket
import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import threading
# from vidstream import AudioSender, AudioReceiver, ScreenShareClient, CameraClient, StreamingServer


# PARAM

# CMD / ipconfig / IPv4 Address 
# or  with socket:
LOCAL_IP_ADDRESS =      socket.gethostbyname( socket.gethostname() )
print(LOCAL_IP_ADDRESS)

# disable_warnings(InsecureRequestWarning)
# PUBLIC_IP_ADDRESS =     requests.get('https://www.ipify.org', verify=False).text
# print(PUBLIC_IP_ADDRESS)


# # Create a server
# server = StreamingServer(LOCAL_IP_ADDRESS, 9999)


def App():
    # GUI
    window = tk.Tk()
    window.title("Laurent's Zoom v0.0.1 Alpha")
    window.geometry('350x200')
    
    label_target_ip = tk.Label( window, text = "Target IP:" )
    label_target_ip.pack()
    
    text_target_ip = tk.Text( window, height = 1 )
    text_target_ip.pack()
    
    # BUTTON
    btn_listen = tk.Button( window, text = "Start Listening" , width = 50)
    btn_listen.pack( anchor = tk.CENTER, expand = True )
    
    btn_camera = tk.Button( window, text = "Start Camera Stream" , width = 50)
    btn_camera.pack( anchor = tk.CENTER, expand = True )
    
    btn_screen = tk.Button( window, text = "Start Screen Sharing" , width = 50)
    btn_screen.pack( anchor = tk.CENTER, expand = True )
    
    btn_audio = tk.Button( window, text = "Start Audio Sharing" , width = 50)
    btn_audio.pack( anchor = tk.CENTER, expand = True )
    
    
    window.mainloop()


if __name__ == '__main__':
    App()

