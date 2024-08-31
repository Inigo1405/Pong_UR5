import cv2
import mediapipe as mp
import numpy as np
import pyrealsense2 as rs
import rtde_control
import rtde_receive
import threading
from time import sleep

control = rtde_control.RTDEControlInterface("192.168.1.1")
receive = rtde_receive.RTDEReceiveInterface("192.168.1.1")

# Inicializar mediapipe para el seguimiento de manos
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.55,
    static_image_mode=False,
    max_num_hands=1,
)

player = {'x': 0, 'y': 0, 'z': 0}

def start_camera_and_show():
    global player

    # Configuración del pipeline y el stream de la cámara RealSense
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)
    print("Cámara encendida")

    while True:
        # Obtener frames del pipeline
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        # Convertir los frames a arrays de numpy
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())
        
        # Procesar el frame de color para la detección de manos
        color_image = cv2.flip(color_image, 1)
        frame_rgb = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # mp_drawing.draw_landmarks(
                #     color_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                point = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                cv2.circle(color_image, (int(point.x * color_image.shape[1]), int(point.y * color_image.shape[0])), 7, (0, 255, 0), -1)

                try:
                    player['x'] = int(point.x * color_image.shape[1])
                    player['y'] = int(point.y * color_image.shape[0])
                    player['z'] = depth_image[player['y'], player['x']]
                except:
                    pass


                    

        # Mostrar el frame de color
        cv2.imshow('Color Frame', color_image)

        # Salir del loop si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



def saludar_continuo():
    # Posicion 1B
    Angles_list_1b = [18.61, -60.30, -155.26, -55.70, 89.51, 102.20]
    Angles_list_2b = [-63.34, -68.71, -152.37, -48.53, 88.70, 20.24]
    Angles_list_3b = [-99.54, -112.04, -108.85, -48, 89.10, -16]
    Angles_list_4b = [-72.51, -137.10, -65.57, -66.74, 88.68, 10.98]
    Angles_list_5b = [-47.34, -113.87, -105.65, -50.49, 88.57, 36.19]
    Angles_list_6b = [-12.36, -112.87, -106.94, -50.98, 88.83, 71.19]
    #Convertir a radianes la lista de angulos
    Angles_list_1b=[np.radians(i) for i in Angles_list_1b]
    Angles_list_2b=[np.radians(i) for i in Angles_list_2b]
    Angles_list_3b=[np.radians(i) for i in Angles_list_3b]
    Angles_list_4b=[np.radians(i) for i in Angles_list_4b]
    Angles_list_5b=[np.radians(i) for i in Angles_list_5b]
    Angles_list_6b=[np.radians(i) for i in Angles_list_6b]
    
    while True:
        for i in range(1, 7):
            variable_name = f"Angles_list_{i}b"
            angles = eval(variable_name)  # Obtener la lista usando eval
            # print(f"{variable_name} en radianes: {angles}")
            control.moveJ(angles, 1.4, 1.05) # Rango [0, 3.14]
            print(f"{variable_name} en radianes: {angles}")
            print(receive.getActualTCPPose())



# Start 
#Comunicacion en tiempo real
home_position=[np.radians(i) for i in [-51.9, -71.85, -112.7, -85.96, 90, 38]]
control.moveJ(home_position, 1, 1)


start_position=[np.radians(i) for i in [50, -95, -112.7, 0, 90, 38]]
control.moveJ(start_position, 1, 1)


threading.Thread(target=start_camera_and_show).start() # Start the camera thread
# saludar_continuo()
while True:
    # print(player)
    if player['z'] >= 1200 and player['y'] <= 180:
        print("Moviendo")
        for i in range(2):
            start_position=[np.radians(i) for i in [-51.9, -90, -105, -20, 90, 38]]
            control.moveJ(start_position, 1.7, 1.4)
            start_position2=[np.radians(i) for i in [-51.9, -90, -95, 0, 90, 38]]
            control.moveJ(start_position2, 1.7, 1.4)
    # sleep(1)