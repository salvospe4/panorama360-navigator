import cv2
import numpy as np

# Metodo che calcola l'immagine planare dall'immagine equirettangolare
def create_planar(equirectangular_img, output_size, fov_deg, long_deg, lat_deg):
    
    output_height, output_width = output_size
    H_e, W_e, _ = equirectangular_img.shape
    
    fov_rad = np.deg2rad(fov_deg)

    # Nel nostro sistema di riferimento la latitudine varia da -90 a 90 mentre per l'utente da 0 a 180
    lat_deg -= 90

    # Calcolo le matrici di rotazione
    R_z = rotation_matrix_around_z(long_deg)
    R_y = rotation_matrix_around_y(lat_deg)

    # Moltiplico le due matrici di rotazione (prima attorno a y, poi attorno a z)
    R = np.matmul(R_z, R_y)

    # La funzione np.meshgrid è usata per creare due matrici di coordinate px e py: una per le coordinate x (px) 
    # e una per le coordinate y (py). Queste matrici sono utilizzate per rappresentare le coordinate di ciascun punto
    # nell'immagine di output (planare) su cui verrà mappata l'immagine equirettangolare.
    px, py = np.meshgrid(np.arange(output_width), np.arange(output_height))
    
    # Calcolo le coordinate nel piano tangente per ogni punto dell'immagine di output planare
    # basandoci sul campo visivo (FOV) specificato
    y_tan = (px.flatten() / (output_width - 1) - 0.5) * np.tan(fov_rad / 2) * 2
    z_tan = (0.5 - py.flatten() / (output_height - 1)) * np.tan(fov_rad / 2) * 2
    x_tan = np.ones_like(y_tan)
    
    # Impilo gli array creando una nuova matrice dove ogni riga rappresenta una componente (x,y,z) nello spazio 3D
    # dunque ha 3 righe e tante colonne quanti sono i pixel dell'immagine planare
    xyz_tan = np.vstack((x_tan, y_tan, z_tan))
    
    # Calcolo la norma di ciascun vettore individuato sulle colonne della matrice
    norms = np.linalg.norm(xyz_tan, axis=0)

    # Normalizzo i vettori (per proiettare i punti sulla sfera)
    xyz_normalized = xyz_tan / norms

    # Applico la rotazione ai vettori normalizzati per ruotare i punti rispetto all'angolazione desiderata
    xyz_rotated = np.matmul(R, xyz_normalized)
    
    # Calcolo le coordinate sferiche dei punti
    phi = np.arctan2(xyz_rotated[1], xyz_rotated[0])
    theta = np.arccos(xyz_rotated[2])
    
    # Calcolo la posizione dei punti nell'immagine equirettangolare
    map_x = (phi + np.pi) / (2 * np.pi) * (W_e - 1)
    map_y = (theta / np.pi) * (H_e - 1)
    
    # Converto gli array in matrici di dimensione (H,W)
    map_x = map_x.reshape((output_height, output_width)).astype(np.float32)
    map_y = map_y.reshape((output_height, output_width)).astype(np.float32)
    
    # Uso remap di OpenCV per creare l'immagine planare di output dalla posizione dei punti
    # mappati nell'immagine equirettangolare e applico l'interpolazione bilineare 
    planar_img = cv2.remap(equirectangular_img, map_x, map_y, interpolation=cv2.INTER_LINEAR)
    
    # Ritorno l'immagine di output nello spazio dei colori RGB
    return cv2.cvtColor(planar_img, cv2.COLOR_BGR2RGB)

# Calcolo la matrice di rotazione intorno a y di un angolo theta (angolo polare)
def rotation_matrix_around_y(theta_degrees):

    theta_radians = np.radians(theta_degrees)
    
    # La rotazione è in senso orario
    R_y = np.array([[np.cos(theta_radians), 0, np.sin(theta_radians)],
                    [0, 1, 0],
                    [-np.sin(theta_radians), 0, np.cos(theta_radians)]])
    return R_y

# Calcolo la matrice di rotazione intorno a y di un angolo theta (angolo azimut)
def rotation_matrix_around_z(phi_degrees):

    phi_radians = np.radians(phi_degrees)
    
    # La rotazione è in senso antiorario
    R_z = np.array([[np.cos(phi_radians), -np.sin(phi_radians), 0],
                    [np.sin(phi_radians), np.cos(phi_radians), 0],
                    [0, 0, 1]])
    return R_z


def video_capture(video_path):
    return cv2.VideoCapture(video_path)

def image_capture(image_path):
    return cv2.imread(image_path)

def progress_percent(video):
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)
    return (current_frame / total_frames) * 100

def get_frame_rate(video):
    frame_rate = round(video.get(cv2.CAP_PROP_FPS))
    if frame_rate == 0:
            frame_rate = 30
    return frame_rate