import ctypes
import customtkinter as ctk
import tkinter as tk
import sqlite3
from pathlib import Path
from datetime import datetime  

ASSETS_PATH = Path(__file__).parent / "assets" / "frame-b1"
PATIENTS_DATA_FOLDER = Path(__file__).parent / "Data_Pasien"
DATABASE = Path(__file__).parent / "pasien.db"

PATIENTS_DATA_FOLDER.mkdir(parents=True, exist_ok=True)  # Membuat folder data pasien jika belum ada

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / path

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception as e:
    print(f"Error setting DPI awareness: {e}")

class PatientDataScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#FFFFFF")

        # Koneksi ke SQLite
        self.conn = sqlite3.connect(DATABASE)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS pasien
                          (id INTEGER PRIMARY KEY, nama TEXT, tanggal_pemeriksaan TEXT)''')

        # Frame untuk menempatkan elemen
        container = tk.Frame(self, bg="#FFFFFF")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Menambahkan logo (lebih kecil dari yang ada di welcome screen)
        logo_path = relative_to_assets("b1-image.png")
        if logo_path.exists():
            logo_image = tk.PhotoImage(file=logo_path)
            logo_label = tk.Label(container, image=logo_image, bg="#FFFFFF")
            logo_label.place(x=859, y=92)
        else:
            print(f"Error: File tidak ditemukan - {logo_path}")

        # Label untuk entry nama pasien
        self.name_entry_label = ctk.CTkLabel(container,
                    text="Nama Pasien",
                    font=("Poppins Bold", 30),
                    fg_color="#FFFFFF",
                    text_color="#000000")
        self.name_entry_label.place(x=115, y=294)

        # Entry nama pasien
        self.name_entry = ctk.CTkEntry(container,
                                fg_color="#DDDDDD",
                                text_color="#000000",
                                font=("Poppins Medium", 14),
                                corner_radius=15,
                                width=1750,
                                height=100)
        self.name_entry.place(x=0, y=0)

        # Label untuk entry tanggal pemeriksaan
        self.date_entry_label = ctk.CTkLabel(container,
                     text="Tanggal Pemeriksaan",
                     font=("Poppins Bold", 30),
                     fg_color="#FFFFFF",
                     text_color="#000000")
        self.date_entry_label.place(x=115, y=470)

        # Entry tanggal pemeriksaan
        self.date_entry = ctk.CTkEntry(container,
                                fg_color="#DDDDDD",
                                text_color="#000716",
                                font=("Poppins Medium", 14),
                                corner_radius=15)
        self.date_entry.place(x=86, y=535)

        # Container untuk tombol "Selanjutnya"
        button_container = tk.Canvas(container, bg="#FFFFFF")
        button_container.place(relx=0.5, rely=0.8, anchor="center")

        # Tombol simpan dan navigasi ke LiveCameraScreen
        save_button = ctk.CTkButton(
            button_container,
            text="Selanjutnya",
            font=("Poppins Medium", 20),
            fg_color="#A8DEE6",
            text_color="#16228E",
            corner_radius=15,
            command=self.save_and_navigate  # Memanggil fungsi save_and_navigate sebelum pindah halaman
        )
        save_button.pack(side="left", padx=(50, 0))

    def save_and_navigate(self):
        """
        Menyimpan data pasien dan membuat folder pasien, lalu berpindah ke LiveCameraScreen.
        """
        nama, tanggal_pemeriksaan = self.get_data_pasien()

        if not nama.strip():  # Memeriksa apakah nama pasien kosong
            print("Nama pasien tidak boleh kosong!")
            return

        # Format tanggal pemeriksaan ke YYYY-MM-DD
        try:
            tanggal_pemeriksaan = datetime.strptime(tanggal_pemeriksaan, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print("Format tanggal tidak valid! Harus dalam format YYYY-MM-DD.")
            return

        # Menyimpan data ke database
        self.save_pasien(nama, tanggal_pemeriksaan)

        # Ambil nomor pasien terakhir
        pasien_number = self.get_last_patient_number() + 1

        # Membuat folder untuk setiap pasien
        folder_name = PATIENTS_DATA_FOLDER / f"{tanggal_pemeriksaan}_Pasien-{pasien_number}"
        folder_name.mkdir(parents=True, exist_ok=True)
        print(f"Folder created: {folder_name}")

        # Pindah ke LiveCameraScreen setelah menyimpan data
        self.controller.show_frame("LiveCameraScreen")

    def get_last_patient_number(self):
        """ Mengambil jumlah pasien dari database. """
        self.c.execute("SELECT COUNT(*) FROM pasien")
        return self.c.fetchone()[0]

    def save_pasien(self, nama, tanggal_pemeriksaan):
        """ Menyimpan data pasien ke database. """
        self.c.execute("INSERT INTO pasien (nama, tanggal_pemeriksaan) VALUES (?, ?)", (nama, tanggal_pemeriksaan))
        self.conn.commit()

    def get_data_pasien(self):
        """ Mengambil data pasien dari entry. """
        return self.name_entry.get(), self.date_entry.get()

    def __del__(self):
        """ Menutup koneksi ke database ketika objek dihapus. """
        self.conn.close()