import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import os
import sys

# Import the logic module
from afis_console.core import sorter as logic

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AFIS Console - Tri de Rapports FAED")
        self.geometry("800x700")
        
        # Configure layout priority
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # Main Form
        self.grid_rowconfigure(2, weight=1) # Logs

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Assistant de Tri FAED", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Analysez, triez et générez un rapport pour vos fichiers PDF de signalisation.", text_color="gray")
        self.subtitle_label.pack(anchor="w")

        # --- Main Form Area ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # STEP 1: Source
        self.step1_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.step1_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        ctk.CTkLabel(self.step1_frame, text="1. Dossier Source", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(self.step1_frame, text="Sélectionnez le dossier contenant les rapports PDF à analyser.", font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", pady=(0, 5))

        self.src_input_frame = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        self.src_input_frame.pack(fill="x")
        
        self.folder_path = tk.StringVar()
        self.folder_entry = ctk.CTkEntry(self.src_input_frame, textvariable=self.folder_path, placeholder_text="Chemin du dossier source...", state="readonly", height=35)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_button = ctk.CTkButton(self.src_input_frame, text="Parcourir...", command=self.select_folder, height=35, width=120)
        self.browse_button.pack(side="right")

        # Separator
        ctk.CTkFrame(self.main_frame, height=2, fg_color=("gray80", "gray30")).grid(row=1, column=0, sticky="ew", padx=15)

        # STEP 2: Destination
        self.step2_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.step2_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        
        ctk.CTkLabel(self.step2_frame, text="2. Dossier Destination (Optionnel)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(self.step2_frame, text="Si vide, les dossiers triés seront créés directement dans la source.", font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", pady=(0, 5))

        self.dest_input_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        self.dest_input_frame.pack(fill="x")
        
        self.dest_path = tk.StringVar()
        self.dest_entry = ctk.CTkEntry(self.dest_input_frame, textvariable=self.dest_path, placeholder_text="Chemin du dossier de destination...", state="readonly", height=35)
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.dest_button = ctk.CTkButton(self.dest_input_frame, text="Parcourir...", command=self.select_dest, height=35, width=120, fg_color="gray")
        self.dest_button.pack(side="right")

        # STEP 3: Action
        self.step3_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.step3_frame.grid(row=3, column=0, padx=15, pady=20, sticky="ew")
        
        self.action_button = ctk.CTkButton(self.step3_frame, text="LANCER L'ANALYSE ET LE TRI", command=self.start_process, state="disabled", fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(size=16, weight="bold"), height=50)
        self.action_button.pack(fill="x")

        # --- Logs Section ---
        self.logs_frame = ctk.CTkFrame(self)
        self.logs_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.logs_frame.grid_columnconfigure(0, weight=1)
        self.logs_frame.grid_rowconfigure(1, weight=1)
        
        # Header Log + Open Button Container
        self.log_header_frame = ctk.CTkFrame(self.logs_frame, fg_color="transparent")
        self.log_header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5,0))
        
        ctk.CTkLabel(self.log_header_frame, text="Journal d'exécution", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        
        self.open_result_button = ctk.CTkButton(self.log_header_frame, text="Ouvrir le dossier de résultat", command=self.open_result_folder, height=24, font=ctk.CTkFont(size=11), fg_color="#3498db", state="disabled")
        self.open_result_button.pack(side="right")

        self.log_textbox = ctk.CTkTextbox(self.logs_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.log_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.log_message("Bienvenue. Veuillez sélectionner un dossier source pour commencer.")
        self.final_dest_dir = None

    def select_folder(self):
        folder_selected = filedialog.askdirectory(title="Sélectionner le dossier contenant les rapports")
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.action_button.configure(state="normal")
            self.log_message(f"✅ Source sélectionnée : {folder_selected}")

    def select_dest(self):
        folder_selected = filedialog.askdirectory(title="Sélectionner le dossier de destination (Optionnel)")
        if folder_selected:
            self.dest_path.set(folder_selected)
            self.log_message(f"➡️ Destination définie : {folder_selected}")
    
    def open_result_folder(self):
        if self.final_dest_dir and os.path.isdir(self.final_dest_dir):
            try:
                if sys.platform == "win32":
                    os.startfile(self.final_dest_dir)
                elif sys.platform == "darwin": # macOS
                    os.system(f"open '{self.final_dest_dir}'")
                else: # linux
                    os.system(f"xdg-open '{self.final_dest_dir}'")
                self.log_message(f"📂 Ouverture du dossier : {self.final_dest_dir}")
            except Exception as e:
                self.log_message(f"❌ Impossible d'ouvrir le dossier : {e}")

    def log_message(self, message):
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")

    def start_process(self):
        source_dir = self.folder_path.get()
        dest_dir = self.dest_path.get()
        if not source_dir or not os.path.exists(source_dir):
            self.log_message("❌ Erreur : Le dossier source est invalide.")
            return

        self.action_button.configure(state="disabled", text="TRAITEMENT EN COURS...")
        self.browse_button.configure(state="disabled")
        self.dest_button.configure(state="disabled")
        self.open_result_button.configure(state="disabled") # Reset state
        
        self.log_message(f"\n🚀 Démarrage du traitement...")
        self.log_message(f"   Source : {source_dir}")
        if dest_dir:
            self.log_message(f"   Dest.  : {dest_dir}")
            self.final_dest_dir = dest_dir
        else:
            self.final_dest_dir = source_dir
        
        # Run in thread to not freeze UI
        thread = threading.Thread(target=self.run_logic, args=(source_dir, dest_dir))
        thread.start()

    def run_logic(self, source_dir, dest_dir):
        try:
            if logic:
                def safe_log(msg):
                    self.after(0, lambda: self.log_message(msg))

                stats = logic.process_folder(source_dir, log_callback=safe_log, destination_dir=dest_dir)
                
                self.after(0, lambda: self.finish_process(stats))
            else:
                self.after(0, lambda: self.log_message("❌ Erreur critique : Module de logique introuvable."))
                self.after(0, lambda: self.finish_process(None))

        except Exception as e:
            self.after(0, lambda: self.log_message(f"❌ Erreur inattendue : {e}"))
            self.after(0, lambda: self.finish_process(None))

    def finish_process(self, stats):
        self.action_button.configure(state="normal", text="LANCER L'ANALYSE ET LE TRI")
        self.browse_button.configure(state="normal")
        self.dest_button.configure(state="normal")
        
        if stats:
             self.log_message(f"\n✨ Traitement terminé avec succès!")
             self.open_result_button.configure(state="normal") # Enable opening folder
        else:
             self.log_message(f"\n⚠️ Le traitement s'est terminé avec des erreurs.")
