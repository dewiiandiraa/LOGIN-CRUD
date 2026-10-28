import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# --- KONEKSI DATABASE ---
def connect_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="siakad"
    )

# --- FUNGSI CRUD ---
def load_data():
    for item in tree.get_children():
        tree.delete(item)
    try:
        db = connect_db()
        try:
            cursor = db.cursor()
            cursor.execute("SELECT kode_mk, nama_mk, sks, semester, nip_dosen FROM mata_kuliah ORDER BY kode_mk")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
        finally:
            db.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")

def ambil_form():
    kode = entry_kode.get().strip()
    nama = entry_nama.get().strip()
    sks = entry_sks.get().strip()
    semester = entry_semester.get().strip()
    nip = entry_nip.get().strip()
    if not all((kode, nama, sks, semester, nip)):
        messagebox.showwarning("Validasi", "Semua kolom wajib diisi!")
        return None
    try:
        sks = int(sks)
        semester = int(semester)
        if sks <= 0 or semester <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Validasi", "SKS dan Semester harus berupa bilangan bulat positif!")
        return None
    return kode, nama, sks, semester, nip

def tambah_data():
    data = ambil_form()
    if data is None:
        return
    try:
        db = connect_db()
        try:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO mata_kuliah (kode_mk, nama_mk, sks, semester, nip_dosen) VALUES (%s, %s, %s, %s, %s)", data
            )
            db.commit()
        finally:
            db.close()
        messagebox.showinfo("Sukses", "Data mata kuliah berhasil ditambahkan!")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Gagal menambah data: {e}")

def edit_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Pilih mata kuliah yang ingin diubah!")
        return
    data = ambil_form()
    if data is None:
        return
    kode_lama = tree.item(selected[0], "values")[0]
    try:
        db = connect_db()
        try:
            cursor = db.cursor()
            cursor.execute(
                "UPDATE mata_kuliah SET kode_mk=%s, nama_mk=%s, sks=%s, semester=%s, nip_dosen=%s WHERE kode_mk=%s",
                (*data, kode_lama)
            )
            db.commit()
        finally:
            db.close()
        messagebox.showinfo("Sukses", "Data mata kuliah berhasil diperbarui!")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

def hapus_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Pilih mata kuliah yang ingin dihapus!")
        return
    kode = tree.item(selected[0], "values")[0]
    if not messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus mata kuliah {kode}?"):
        return
    try:
        db = connect_db()
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM mata_kuliah WHERE kode_mk=%s", (kode,))
            db.commit()
        finally:
            db.close()
        messagebox.showinfo("Sukses", "Data mata kuliah berhasil dihapus!")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Gagal menghapus data: {e}")

def select_item(event):
    selected = tree.selection()
    if not selected:
        return
    values = tree.item(selected[0], "values")
    for entry, value in zip(entries, values):
        entry.delete(0, tk.END)
        entry.insert(0, value)

def clear_fields():
    for entry in entries:
        entry.delete(0, tk.END)
    for item in tree.selection():
        tree.selection_remove(item)

# --- GUI MAIN WINDOW ---
root = tk.Tk()
root.title("Aplikasi Data Mata Kuliah - SIAKAD")
root.geometry("900x520")

frame_form = tk.LabelFrame(root, text=" Form Data Mata Kuliah ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

labels = ["Kode MK", "Nama Mata Kuliah", "SKS", "Semester", "NIP Dosen"]
entries = []
for i, label_text in enumerate(labels):
    row, col = divmod(i, 2)
    tk.Label(frame_form, text=label_text).grid(row=row, column=col*2, sticky="w", padx=5, pady=5)
    entry = tk.Entry(frame_form)
    entry.grid(row=row, column=col*2+1, padx=5, pady=5, sticky="ew")
    entries.append(entry)

entry_kode, entry_nama, entry_sks, entry_semester, entry_nip = entries
frame_form.grid_columnconfigure(1, weight=1)
frame_form.grid_columnconfigure(3, weight=1)

frame_btn = tk.Frame(root)
frame_btn.pack(fill="x", padx=15, pady=5)
for text, color, command in [
    ("Tambah", "#4CAF50", tambah_data),
    ("Edit", "#2196F3", edit_data),
    ("Hapus", "#f44336", hapus_data),
    ("Clear", "#9E9E9E", clear_fields),
]:
    tk.Button(frame_btn, text=text, bg=color, fg="white", command=command, width=12).pack(side="left", padx=5)

frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=15, pady=10)
columns = ("kode_mk", "nama_mk", "sks", "semester", "nip_dosen")
tree = ttk.Treeview(frame_table, columns=columns, show="headings")
for col, heading, width in [
    ("kode_mk", "Kode MK", 100),
    ("nama_mk", "Nama Mata Kuliah", 270),
    ("sks", "SKS", 70),
    ("semester", "Semester", 90),
    ("nip_dosen", "NIP Dosen", 110),
]:
    tree.heading(col, text=heading)
    tree.column(col, width=width)

tree.bind("<<TreeviewSelect>>", select_item)
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

load_data()
root.mainloop()
