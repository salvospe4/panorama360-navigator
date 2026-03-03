import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
import time

from MapPlanar import create_planar, video_capture, image_capture, get_frame_rate, progress_percent

# Versione alternativa (decommentare per utilizzarla)
# from MapPlanar2 import create_planar, video_capture, image_capture, get_frame_rate, progress_percent

class NavigationApp:
    def __init__(self, window_title):
        
        # Metodo per selezionare il file (immagine o video) dal file system
        self.file_path, self.is_video = self.select_file()
       
        # Creazione e configurazione della finestra principale
        self.window = tk.Tk()
        self.window.title(window_title)

        window_width = 400
        window_height = 560
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.window.focus_force()
        
        # Dichiarazione di variabili
        self.theta = 90
        self.phi = 0
        self.alpha = 60
        self.output_size = (400, 400)
        self.paused = False
        
        # Se il file è un video viene letto il video e viene calcolato il frame rate
        if self.is_video:
            self.vid = video_capture(self.file_path)
            if not self.vid.isOpened():
                raise RuntimeError("Errore nell'apertura del video")
            self.frame_rate = get_frame_rate(self.vid)
            self.update_interval = int(1000 / self.frame_rate)
        # Altrimenti se è un immagine viene letta l'immagine
        else:
            self.image = image_capture(self.file_path)  
        
        #Creazione di tutti gli elementi della GUI
        self.canvas = tk.Canvas(self.window, width=self.output_size[0], height=self.output_size[1])
        self.canvas.pack()

        player_frame = tk.Frame(self.window)
        if self.is_video:
            player_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.pause_button = ttk.Button(player_frame, text="⏸", command=self.toggle_video_pause, width=3)
        self.pause_button.pack(side=tk.LEFT, padx=10)

        self.progress_var = tk.DoubleVar() 
        self.progress_bar = ttk.Progressbar(player_frame, maximum=100, variable=self.progress_var, length=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        button_frame = tk.Frame(self.window)
        button_frame.pack(anchor=tk.CENTER)

        self.btn_left = ttk.Button(button_frame, text="←", command=lambda: self.update_angles(0, -10), width=3)
        self.btn_left.grid(row=1, column=0)

        self.btn_up = ttk.Button(button_frame, text="↑", command=lambda: self.update_angles(-10, 0), width=3)
        self.btn_up.grid(row=0, column=1)

        self.btn_right = ttk.Button(button_frame, text="→", command=lambda: self.update_angles(0, 10), width=3)
        self.btn_right.grid(row=1, column=2)

        self.btn_down = ttk.Button(button_frame, text="↓", command=lambda: self.update_angles(10, 0), width=3)
        self.btn_down.grid(row=2, column=1)

        spacer = tk.Frame(button_frame, width=30)  
        spacer.grid(row=1, column=3)

        self.btn_zoom_in = ttk.Button(button_frame, text="+", command=self.zoom_in, width=3)
        self.btn_zoom_in.grid(row=1, column=4)

        self.btn_zoom_out = ttk.Button(button_frame, text="-", command=self.zoom_out, width=3)
        self.btn_zoom_out.grid(row=1, column=5)

        self.coordinates_label = tk.Label(self.window, text=f"Coordinates: θ={self.theta}, φ={self.phi} - FOV: {self.alpha}°")
        self.coordinates_label.pack(anchor=tk.CENTER, expand=True)

        # Navigazione tramite le frecce della tastiera
        self.window.bind("<Left>", lambda e: self.update_angles(0, -10))
        self.window.bind("<Right>", lambda e: self.update_angles(0, 10))
        self.window.bind("<Up>", lambda e: self.update_angles(-10, 0))
        self.window.bind("<Down>", lambda e: self.update_angles(10, 0))
        
        # A seconda del tipo di media richiamo il corrispettivo metodo per mostrare l'immagine o il video
        if self.is_video:
            self.update_video_frame()
        else:
            self.update_image_frame()
        
        self.window.mainloop()

        
    # Metodi per la verifica del formato file
    def is_video_file(self,filepath):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        _, ext = os.path.splitext(filepath)
        return ext.lower() in video_extensions
    
    def is_image_file(self,filepath):
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        _, ext = os.path.splitext(filepath)
        return ext.lower() in image_extensions


    def select_file(self):
        root = tk.Tk()
        root.withdraw()  # Nascondo la finestra principale
        is_video = False 
        # Chiedo all'utente di selezionare un file
        file_path = filedialog.askopenfilename(title='Scegli un file', filetypes=[('All Files', '*.*')])
        root.destroy()  # Chiudo la finestra dopo la selezione
        
        if file_path:  # Controllo se l'utente ha selezionato un file
            if self.is_video_file(file_path):
               is_video=True
            elif self.is_image_file(file_path):
               is_video=False
            else:
                print("Formato non supportato. Seleziona un video o un'immagine nei formati supportati.")
        else:
            print("Nessun file selezionato. Riavvia l'applicazione.")

        return (file_path, is_video)

    # Metodo per aggiornare gli angoli con controllo di valori accettabili
    def update_angles(self, d_theta, d_phi):
        # Aggiorna theta (latitudine) mantenendolo tra 0 e 180 gradi
        # 90 gradi rappresenta l'equatore, 0 il polo nord e 180 il polo sud
        self.theta = max(0, min(180, self.theta + d_theta))

        # phi tra 0 e 359, poi lo trasliamo nell'intervallo [-180,180] per rendere piu intuitiva la navigazione
        self.phi = (self.phi + d_phi) % 360
        if self.phi in range(181,360,1) :
            self.phi = -360 + self.phi 

        self.coordinates_label.config(text=f"Coordinates: θ={self.theta}, φ={self.phi} - FOV: {self.alpha}°")
        # Se è un video in pausa o un'immagine statica chiamo il metodo per cambiare frame
        if self.paused and self.is_video:
            self.update_paused_frame()
        elif not self.is_video:
            self.update_image_frame()
    
    def zoom_in(self):
        self.alpha = max(20, self.alpha - 10)
        self.coordinates_label.config(text=f"Coordinates: θ={self.theta}, φ={self.phi} - FOV: {self.alpha}°")
        if self.paused and self.is_video:
            self.update_paused_frame()
        elif not self.is_video:
            self.update_image_frame()
    
    def zoom_out(self):
        self.alpha = min(120, self.alpha + 10)
        self.coordinates_label.config(text=f"Coordinates: θ={self.theta}, φ={self.phi} - FOV: {self.alpha}°")
        if self.paused and self.is_video:
            self.update_paused_frame()
        elif not self.is_video:
            self.update_image_frame()

    def toggle_video_pause(self):
        self.paused = not self.paused  # Alterna lo stato di pausa 
        if not self.paused:
            self.pause_button.config(text="⏸")
            self.update_video_frame()  # Riprendi l'aggiornamento del frame
        else:
            self.pause_button.config(text="▶")
    
    # Metodo che permette di cambiare frame nel tempo
    def update_video_frame(self):
        start_time = time.time()
        if not self.paused and self.vid.isOpened():
            ret, self.frame = self.vid.read()
            if ret:
                #Salva il frame corrente in self.current_frame per poterlo utilizzare in caso di pausa.
                self.current_frame = self.frame
                self.frame = create_planar(self.frame, self.output_size, self.alpha, self.phi, self.theta)
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.progress_var.set(progress_percent(self.vid))
                # In base al tempo di esecuzione della funzione create_planar calcolo l'intervallo tra i frame
                duration = int((time.time() - start_time) * 1000)
                self.new_update_interval = max(1, int(self.update_interval - duration))
                self.window.after(self.new_update_interval, self.update_video_frame)
            else:
                self.vid.release()
                self.window.destroy()

    # Metodo per aggiornare l'immagine con la nuova angolazione
    def update_image_frame(self):
        transformed_image = create_planar(self.image, self.output_size, self.alpha, self.phi, self.theta)
        photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_image))
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.photo = photo  #Mantieni una referenza alla foto per evitare il garbage collection

    # Metodo per aggiornare il frame del video in pausa con la nuova angolazione
    def update_paused_frame(self):
        transformed_image = create_planar(self.frame, self.output_size, self.alpha, self.phi, self.theta)
        photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_image))
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.photo = photo