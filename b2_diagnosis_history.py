import os
import sqlite3
import ctypes
from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Canvas, Button, PhotoImage, ttk, Frame
from datetime import datetime

# Menentukan path utama proyek (relatif, tidak hardcoded)
BASE_PATH = Path(__file__).resolve().parent.parent  # Naik 1 level ke folder proyek utama

# Path ke assets dan data pasien menggunakan relative path
ASSETS_PATH = Path(__file__).parent / "assets" / "frame-b2"
DATA_IMPOR_PATH = BASE_PATH / "Data_Pasien"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Mengaktifkan DPI Awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception as e:
    print(f"Error setting DPI awareness: {e}")

# Kelas untuk frame daftar riwayat pemeriksaan
class DiagnosisHistoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#FFFFFF")

        # Membuat frame untuk header dan konten
        header_frame = Frame(self, bg="#A8DFE6")
        header_frame.pack(fill="x", pady=10)

        content_frame = Frame(self, bg="#FFFFFF")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Bagian header
        tk.Label(header_frame, text="Daftar Riwayat Pemeriksaan", font=("Poppins Bold", 30), bg="#A8DFE6", fg="#15218E").grid(row=0, column=0, padx=20, pady=10)

        # Tombol kembali
        button_image_1_path = relative_to_assets("b2-button.png")
        if button_image_1_path.exists():
            button_image_1 = PhotoImage(file=button_image_1_path)
            button_1 = Button(
                header_frame,
                image=button_image_1,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: controller.show_frame("TransAIDScreen"),  # Navigasi kembali ke layar utama
                relief="flat"
            )
            button_1.grid(row=0, column=1, padx=20, pady=10, sticky="e")
            self.button_image_1 = button_image_1
        else:
            print(f"Error: File not found - {button_image_1_path}")

        # Treeview untuk menampilkan data pasien
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Poppins Bold", 18), background="#A8DFE6", foreground="#15218E")
        style.configure("Treeview", font=("Poppins", 16), rowheight=50)  # Ubah rowheight untuk entri lebih tinggi
        style.map("Treeview", background=[('selected', '#16228E')], foreground=[('selected', 'white')])

        # Atur tag untuk pewarnaan
        style.configure("Treeview", fieldbackground="white")
        self.tree = ttk.Treeview(content_frame, columns=("No.", "Nama Pasien", "Tanggal Pemeriksaan", "Hasil Pemeriksaan"), show='headings', selectmode='browse')
        self.tree.grid(row=1, column=0, sticky="nsew")

        # Konfigurasi headings
        self.tree.heading("No.", text="No.")
        self.tree.heading("Nama Pasien", text="Nama Pasien")
        self.tree.heading("Tanggal Pemeriksaan", text="Tanggal Pemeriksaan")
        self.tree.heading("Hasil Pemeriksaan", text="Hasil Pemeriksaan")

        # Konfigurasi kolom
        self.tree.column("No.", width=50, anchor='center')
        self.tree.column("Nama Pasien", width=500, anchor='w')
        self.tree.column("Tanggal Pemeriksaan", width=300, anchor='center')
        self.tree.column("Hasil Pemeriksaan", width=200, anchor='center')

        # Scrollbar untuk Treeview
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure row/column weights for content_frame
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Tampilkan data pasien dari folder data_impor di tabel
        self.display_folders()

        # Event binding untuk pewarnaan row dan aksi double-click
        self.tree.bind('<<TreeviewSelect>>', self.change_row_color)
        self.tree.bind("<Double-1>", self.on_double_click)

    def display_folders(self):
        # Membersihkan treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Pastikan folder DATA_IMPOR_PATH ada
        if not DATA_IMPOR_PATH.exists():
            print(f"Folder data pasien tidak ditemukan: {DATA_IMPOR_PATH}")
            return

        # Mendapatkan daftar folder dalam data_impor
        folder_list = [folder for folder in DATA_IMPOR_PATH.iterdir() if folder.is_dir()]

        # Fungsi untuk mengurutkan berdasarkan tanggal dan nomor pasien
        def sort_key(folder_name):
            folder_parts = folder_name.name.split('_')
            tanggal = folder_parts[0]
            pasien = folder_parts[1]  

            pasien_num = int(pasien.split('-')[1])  

            return (datetime.strptime(tanggal, '%Y-%m-%d'), pasien_num)

        # Urutkan folder berdasarkan tanggal (descending) dan nomor pasien (descending jika tanggal sama)
        folder_list.sort(key=sort_key, reverse=True)

        # Menampilkan data folder ke dalam treeview
        for idx, folder in enumerate(folder_list, start=1):
            folder_parts = folder.name.split('_')
            tanggal_pemeriksaan = folder_parts[0]  
            nama_pasien = folder_parts[1]  
            self.tree.insert('', 'end', values=(idx, nama_pasien, tanggal_pemeriksaan, ""))

    def change_row_color(self, event):
        for row in self.tree.get_children():
            self.tree.item(row, tags="normal")
        
        for selected_row in self.tree.selection():
            self.tree.item(selected_row, tags="selected")

        self.tree.tag_configure("normal", background="white")
        self.tree.tag_configure("selected", background="#16228E")

    def on_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            nama_pasien = self.tree.item(selected_item)["values"][1]
            tanggal_pemeriksaan = self.tree.item(selected_item)["values"][2]

            pasien_num = int(nama_pasien.split('-')[1])

            image_path_1 = DATA_IMPOR_PATH / f"{tanggal_pemeriksaan}_{nama_pasien}" / f"{pasien_num}.1.png"
            image_path_2 = DATA_IMPOR_PATH / f"{tanggal_pemeriksaan}_{nama_pasien}" / f"{pasien_num}.2.png"

            print("Path Gambar 1:", image_path_1)
            print("Path Gambar 2:", image_path_2)

            if not image_path_1.exists():
                print(f"Error: Gambar {image_path_1} tidak ditemukan.")
                return
            if not image_path_2.exists():
                print(f"Error: Gambar {image_path_2} tidak ditemukan.")
                return

            self.controller.frames["DiagnosisResultScreen"].load_images(str(image_path_1), str(image_path_2), nama_pasien)
            self.controller.show_frame("DiagnosisResultScreen")
