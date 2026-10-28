import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector

# --- KONEKSI DATABASE ---
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="siakad"
    )

# --- FUNGSI CRUD ---
def load_data():
    for item in tree.get_children():
        tree.delete(item)
    db = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT id_jadwal, kode_mk, hari, jam_mulai, jam_selesai, ruangan FROM jadwal_kuliah ORDER BY id_jadwal")
        for row in cursor.fetchall():
            tree.insert("", "end", values=tuple(str(v) for v in row))
        cursor.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")
    finally:
        if db is not None and db.is_connected():
            db.close()

def get_form_data():
    kode = entry_kode.get().strip()
    hari = combo_hari.get().strip()
    mulai = entry_mulai.get().strip()
    selesai = entry_selesai.get().strip()
    ruangan = entry_ruangan.get().strip()
    if not all([kode, hari, mulai, selesai, ruangan]):
        messagebox.showwarning("Validasi", "Semua kolom wajib diisi!")
        return None
    try:
        waktu_mulai = datetime.strptime(mulai, "%H:%M:%S").time()
        waktu_selesai = datetime.strptime(selesai, "%H:%M:%S").time()
    except ValueError:
        messagebox.showwarning("Validasi", "Gunakan format jam HH:MM:SS, contoh 08:00:00")
        return None
    if waktu_mulai >= waktu_selesai:
        messagebox.showwarning("Validasi", "Jam selesai harus lebih besar dari jam mulai!")
        return None
    return kode, hari, mulai, selesai, ruangan

def tambah_data():
    data = get_form_data()
    if data is None:
        return
    db = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO jadwal_kuliah (kode_mk, hari, jam_mulai, jam_selesai, ruangan) VALUES (%s, %s, %s, %s, %s)",
            data
        )
        db.commit()
        cursor.close()
        messagebox.showinfo("Sukses", "Data jadwal berhasil ditambahkan!")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Gagal menambah data: {e}")
    finally:
        if db is not None and db.is_connected():
            db.close()

def edit_data():
    id_jadwal = entry_id.get().strip()
    if not id_jadwal:
        messagebox.showwarning("Warning", "Pilih jadwal yang ingin diubah!")
        return
    data = get_form_data()
    if data is None:
        return
    db = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE jadwal_kuliah SET kode_mk=%s, hari=%s, jam_mulai=%s, jam_selesai=%s, ruangan=%s WHERE id_jadwal=%s",
            data + (id_jadwal,)
        )
        db.commit()
        cursor.close()
        messagebox.showinfo("Sukses", "Data jadwal berhasil diperbarui!")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")
    finally:
        if db is not None and db.is_connected():
            db.close()

def hapus_data():
    id_jadwal = entry_id.get().strip()
    if not id_jadwal:
        messagebox.showwarning("Warning", "Pilih jadwal yang ingin dihapus!")
        return
    if not messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus jadwal ID {id_jadwal}?"):
        return
    db = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM jadwal_kuliah WHERE id_jadwal=%s", (id_jadwal,))
        db.commit()
        cursor.close()
        messagebox.showinfo("Sukses", "Data jadwal berhasil dihapus!")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Gagal menghapus data: {e}")
    finally:
        if db is not None and db.is_connected():
            db.close()

def select_item(event):
    selected = tree.selection()
    if not selected:
        return
    values = tree.item(selected[0], "values")
    clear_fields()
    entry_id.config(state="normal")
    entry_id.insert(0, values[0])
    entry_id.config(state="readonly")
    entry_kode.insert(0, values[1])
    combo_hari.set(values[2])
    entry_mulai.insert(0, values[3])
    entry_selesai.insert(0, values[4])
    entry_ruangan.insert(0, values[5])

def clear_fields():
    entry_id.config(state="normal")
    entry_id.delete(0, tk.END)
    entry_id.config(state="readonly")
    entry_kode.delete(0, tk.END)
    combo_hari.set("")
    entry_mulai.delete(0, tk.END)
    entry_selesai.delete(0, tk.END)
    entry_ruangan.delete(0, tk.END)
    for selected in tree.selection():
        tree.selection_remove(selected)

# --- GUI MAIN WINDOW ---
root = tk.Tk()
root.title("Aplikasi Data Jadwal - SIAKAD")
root.geometry("900x520")

frame_form = tk.LabelFrame(root, text=" Form Data Jadwal ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

labels = ["ID Jadwal", "Kode MK", "Hari", "Jam Mulai", "Jam Selesai", "Ruangan"]
for i, label_text in enumerate(labels):
    tk.Label(frame_form, text=label_text).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=6)

entry_id = tk.Entry(frame_form, state="readonly")
entry_id.grid(row=0, column=1, padx=5, pady=6, sticky="ew")
entry_kode = tk.Entry(frame_form)
entry_kode.grid(row=0, column=3, padx=5, pady=6, sticky="ew")
combo_hari = ttk.Combobox(frame_form, values=["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"], state="readonly")
combo_hari.grid(row=1, column=1, padx=5, pady=6, sticky="ew")
entry_mulai = tk.Entry(frame_form)
entry_mulai.grid(row=1, column=3, padx=5, pady=6, sticky="ew")
entry_selesai = tk.Entry(frame_form)
entry_selesai.grid(row=2, column=1, padx=5, pady=6, sticky="ew")
entry_ruangan = tk.Entry(frame_form)
entry_ruangan.grid(row=2, column=3, padx=5, pady=6, sticky="ew")
frame_form.grid_columnconfigure(1, weight=1)
frame_form.grid_columnconfigure(3, weight=1)

frame_btn = tk.Frame(root)
frame_btn.pack(fill="x", padx=15, pady=5)
tk.Button(frame_btn, text="Tambah", bg="#4CAF50", fg="white", command=tambah_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Edit", bg="#2196F3", fg="white", command=edit_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Hapus", bg="#f44336", fg="white", command=hapus_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Clear", bg="#9E9E9E", fg="white", command=clear_fields, width=12).pack(side="left", padx=5)

frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=15, pady=10)
columns = ("id_jadwal", "kode_mk", "hari", "jam_mulai", "jam_selesai", "ruangan")
tree = ttk.Treeview(frame_table, columns=columns, show="headings")
headings = ["ID Jadwal", "Kode MK", "Hari", "Jam Mulai", "Jam Selesai", "Ruangan"]
widths = [80, 110, 100, 120, 120, 160]
for col, heading, width in zip(columns, headings, widths):
    tree.heading(col, text=heading)
    tree.column(col, width=width)
tree.bind("<<TreeviewSelect>>", select_item)
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

load_data()
root.mainloop()
