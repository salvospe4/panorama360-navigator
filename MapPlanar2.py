# VERSIONE ALTERNATIVA PIU' COMPATTA E LEGGIBILE CHE FA USO DI TENSORI

import cv2
import numpy as np

def create_planar(img, outputsize, alpha, phi, theta):
    # Dimensioni dell'immagine planare di output
    W, H = outputsize

    # Dimensioni dell'immagine equirettangolare
    He, We, _ = img.shape

    # Calcolo della matrice di rotazione
    R = rotate_matrix(theta, phi)

    # Generazione di una griglia di coordinate (u, v) sul piano tangente con np.meshgrid:
    # np.linspace genera un array 1D con valori equidistanti:
    # - Per u, da -1 a 1 con W punti (lungo l'asse orizzontale)
    # - Per v, da 1 a -1 con H punti, invertendo il segno per allineare l'asse v con l'asse z
    u, v = np.meshgrid(np.linspace(-1, 1, W), np.linspace(1, -1, H))
    
    # Proiezione dei punti della sfera nel piano tangente:
    # moltiplicando tan(alpha/2) * u (e per v) proietto tutti i punti della porzione di sfera con
    # field of view alpha, nella porzione di piano che rappresenta l'immagine di output
    # considerando che la sfera abbia raggio 1 e la relazione: H/2 = tan(alpha/2)
    y = np.tan(np.radians(alpha / 2)) * u
    z = np.tan(np.radians(alpha / 2)) * v
    x = 1 # il piano è tangente alla sfera nel punto (1,0,0)

    # Normalizzazione:
    # Vogliamo che i punti del piano "tocchino" la sfera, normalizzando, stiamo effettivamente 
    # ridimensionando questi punti in modo che "tocchino" la sfera. Ogni punto normalizzato 
    # avrà una distanza dall'origine (il centro della sfera) pari a 1
    norm = np.sqrt(x**2 + y**2 + z**2)
    x /= norm
    y /= norm
    z /= norm

    # Raggruppo le 3 coordinate di ogni punto in un tensore di dimensione (H, W, 3)
    # axis=2 indica che stiamo raggruppando rispetto alla 3° dimensione del tensore
    tangent_points = np.stack([x, y, z], axis=2)

    # Rotazione dei punti nelle posizioni finali specificati dagli angoli theta e phi:
    # R = R_z * R_y, che viene applicata a ogni vettore di tangent_points
    # axes=([2],[1]) specifica di moltiplicare lungo l'asse 2 di tangent_points (cioè [x,y,z])
    # per l'asse 1 di R che sarebbero le righe (prodotto riga per colonna).
    sphere_points = np.tensordot(tangent_points, R, axes=([2],[1]))
    
    # Conversione da coordinate cartesiane a sferiche:
    # longitudine = arctan(y/x), latitudine = arccos(z/modulo=1)
    lon = np.arctan2(sphere_points[:, :, 1], sphere_points[:, :, 0])
    lat = np.arccos(sphere_points[:, :, 2])

    # Mappatura delle coordinate sferiche nell'immagine equirettangolare
    map_x = (lon + np.pi) / (2 * np.pi) * We # sommando pi ottengo valori da 0 a 360 
    # spostando l'origine dell'asse lon al centro dell'immagine equirettangolare, in questo modo
    # non uso angoli negativi che sarebbero come risultato coordinate negative
    map_y = lat / np.pi * He

    # Controllo gli indici fuori dai limiti
    map_x = np.clip(map_x, 0, We - 1).astype(np.float32)
    map_y = np.clip(map_y, 0, He - 1).astype(np.float32)

    # Utilizzo di remap per creare l'immagine planare di output e applicare l'interpolazione bilineare
    output_img = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR)

    # Ritorno l'immagine di output con lo spazio dei colori RGB
    return cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB)

def rotate_matrix(theta, phi):
    theta_rad = np.radians(theta)
    phi_rad = np.radians(phi)

    # Con il piano canonico in (1,0,0) devo ruotare di (pi-theta) attorno all'asse y (angolo polare)
    new_theta = np.pi/2 - theta_rad

    R_y = np.array([[np.cos(new_theta), 0, -np.sin(new_theta)],
                    [0, 1, 0],
                    [np.sin(new_theta), 0, np.cos(new_theta)]])
    
    # Poi ruoto di phi attorno all'asse z (angolo azimut)
    R_z = np.array([[np.cos(phi_rad), -np.sin(phi_rad), 0],
                    [np.sin(phi_rad), np.cos(phi_rad), 0],
                    [0, 0, 1]])
    
    # La matrice di rotazione R è il prodotto delle due matrici
    # Moltiplicate in questo ordine ruoto prima rispetto a y e poi rispetto a z
    return np.matmul(R_z, R_y)

def video_capture(video_path):
    return cv2.VideoCapture(video_path)

def image_capture(video_path):
    return cv2.imread(video_path)

def progress_percent(video):
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)
    return (current_frame / total_frames) * 100

def get_frame_rate(video):
    frame_rate = round(video.get(cv2.CAP_PROP_FPS))
    if frame_rate == 0:
            frame_rate = 30
    return frame_rate