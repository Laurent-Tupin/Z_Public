import tkinter as tk
import socket
import threading
# import requests
# from urllib3.exceptions import InsecureRequestWarning
# from urllib3 import disable_warnings

from vidstream import AudioSender, AudioReceiver, ScreenShareClient, CameraClient, StreamingServer


# PARAM

# CMD / ipconfig / IPv4 Address 
# or  with socket:
LOCAL_IP_ADDRESS =      socket.gethostbyname( socket.gethostname() )
print(LOCAL_IP_ADDRESS)

# disable_warnings(InsecureRequestWarning)
# PUBLIC_IP_ADDRESS =     requests.get('https://www.ipify.org', verify=False).text
# print(PUBLIC_IP_ADDRESS)



def App():
    # Define the Connection object here so we have only 1 instance and not a different one each time you click on a button
    server = StreamingServer(LOCAL_IP_ADDRESS, 9999)
    receiver = AudioReceiver(LOCAL_IP_ADDRESS, 8888)
    
    # Features
    def start_listening():
        t1 = threading.Thread( target = server.start_server )
        t2 = threading.Thread( target = receiver.start_server )
        t1.start()
        t2.start()
    def start_camera_stream():
        camera_client = CameraClient( text_target_ip.get(1.0, 'end-1c'), 7777 )
        t3 = threading.Thread( target = camera_client.start_stream )
        t3.start()
    def start_screen_sharing():
        screen_client = ScreenShareClient( text_target_ip.get(1.0, 'end-1c'), 7777 )
        t4 = threading.Thread( target = screen_client.start_stream )
        t4.start()
    def start_audio_stream():
        audio_sender = AudioSender( text_target_ip.get(1.0, 'end-1c'), 6666 )
        t5 = threading.Thread( target = audio_sender.start_stream )
        t5.start()
    
    # GUI - Window Interface
    window = tk.Tk()
    window.title("Zoomie v0.0.1 Alpha")
    window.geometry('350x200')
    
    # label_target_Team =     tk.Label( window, text = "Input X here to say that you are listening:" )
    # label_target_Team.pack()
    # text_target_Team =      tk.Text( window, height = 1 )
    # text_target_Team.pack()
        
    label_target_ip =       tk.Label( window, text = "Target IP:" )
    label_target_ip.pack()
    text_target_ip =        tk.Text( window, height = 1 )
    text_target_ip.pack()
    
    # BUTTON
    btn_listen = tk.Button( window, text = "Start Listening" , width = 50, 
                           command = start_listening )
    btn_listen.pack( anchor = tk.CENTER, expand = True )
    
    btn_camera = tk.Button( window, text = "Start Camera Stream" , width = 50, 
                           command = start_camera_stream )
    btn_camera.pack( anchor = tk.CENTER, expand = True )
    
    btn_screen = tk.Button( window, text = "Start Screen Sharing" , width = 50, 
                           command = start_screen_sharing )
    btn_screen.pack( anchor = tk.CENTER, expand = True )
    
    btn_audio = tk.Button( window, text = "Start Audio Stream" , width = 50, 
                          command = start_audio_stream )
    btn_audio.pack( anchor = tk.CENTER, expand = True )
    
    
    
    
    window.mainloop()


if __name__ == '__main__':
    App()




