import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Koneksi ke database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="siakad"
    )

# Nama kolom sesuai tabel mahasiswa di database
COLUMNS = (
    "nim", "nama_lengkap", "jenis_kelamin", "tanggal_lahir",
    "tempat_lahir", "alamat", "no_telepon", "email",
    "jurusan", "angkatan", "status"
)

def get_form_data():
    return (
        entry_nim.get().strip(),
        entry_nama.get().strip(),
        combo_jk.get().strip(),
        entry_tgl_lahir.get().strip(),
        entry_tempat_lahir.get().strip(),
        entry_alamat.get().strip(),
        entry_tlp.get().strip(),
        entry_email.get().strip(),
        entry_jurusan.get().strip(),
        entry_angkatan.get().strip(),
        combo_status.get().strip()
    )

def clear_fields():
    for widget in (
        entry_nim, entry_nama, entry_tgl_lahir, entry_tempat_lahir,
        entry_alamat, entry_tlp, entry_email, entry_jurusan, entry_angkatan
    ):
        widget.delete(0, tk.END)
    combo_jk.set("")
    combo_status.set("")
    tree.selection_remove(tree.selection())

def load_data():
    for item in tree.get_children():
        tree.delete(item)

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT nim, nama_lengkap, jenis_kelamin, tanggal_lahir,
                   tempat_lahir, alamat, no_telepon, email,
                   jurusan, angkatan, status
            FROM mahasiswa
            ORDER BY nim
        """)
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data:\n{e}")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def tambah_data():
    data = get_form_data()
    if not data[0] or not data[1]:
        messagebox.showwarning("Peringatan", "NIM dan nama lengkap wajib diisi!")
        return

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = """
            INSERT INTO mahasiswa
            (nim, nama_lengkap, jenis_kelamin, tanggal_lahir, tempat_lahir,
             alamat, no_telepon, email, jurusan, angkatan, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, data)
        db.commit()
        messagebox.showinfo("Sukses", "Data mahasiswa berhasil ditambahkan.")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal menambahkan data:\n{e}")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def edit_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Peringatan", "Pilih data mahasiswa yang ingin diubah.")
        return

    data = get_form_data()
    if not data[0] or not data[1]:
        messagebox.showwarning("Peringatan", "NIM dan nama lengkap wajib diisi!")
        return

    # NIM lama dipakai sebagai kunci untuk menemukan baris yang dipilih.
    old_values = tree.item(selected[0], "values")
    old_nim = old_values[0]

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = """
            UPDATE mahasiswa
            SET nim=%s, nama_lengkap=%s, jenis_kelamin=%s, tanggal_lahir=%s,
                tempat_lahir=%s, alamat=%s, no_telepon=%s, email=%s,
                jurusan=%s, angkatan=%s, status=%s
            WHERE nim=%s
        """
        cursor.execute(sql, data + (old_nim,))
        db.commit()
        if cursor.rowcount == 0:
            messagebox.showwarning("Info", "Tidak ada perubahan data atau NIM tidak ditemukan.")
        else:
            messagebox.showinfo("Sukses", "Data mahasiswa berhasil diperbarui.")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal memperbarui data:\n{e}")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def hapus_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Peringatan", "Pilih data mahasiswa yang ingin dihapus.")
        return

    values = tree.item(selected[0], "values")
    nim = values[0]
    nama = values[1]

    if not messagebox.askyesno(
        "Konfirmasi Hapus",
        f"Yakin ingin menghapus data {nama} (NIM {nim})?"
    ):
        return

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM mahasiswa WHERE nim = %s", (nim,))
        db.commit()
        messagebox.showinfo("Sukses", "Data mahasiswa berhasil dihapus.")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal menghapus data:\n{e}")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def select_item(event=None):
    selected = tree.selection()
    if not selected:
        return

    values = tree.item(selected[0], "values")
    clear_form_only()

    entry_nim.insert(0, values[0])
    entry_nama.insert(0, values[1])
    combo_jk.set(values[2])
    entry_tgl_lahir.insert(0, values[3])
    entry_tempat_lahir.insert(0, values[4])
    entry_alamat.insert(0, values[5])
    entry_tlp.insert(0, values[6])
    entry_email.insert(0, values[7])
    entry_jurusan.insert(0, values[8])
    entry_angkatan.insert(0, values[9])
    combo_status.set(values[10])

def clear_form_only():
    # Mengosongkan isian tanpa menghilangkan pilihan baris tabel.
    for widget in (
        entry_nim, entry_nama, entry_tgl_lahir, entry_tempat_lahir,
        entry_alamat, entry_tlp, entry_email, entry_jurusan, entry_angkatan
    ):
        widget.delete(0, tk.END)
    combo_jk.set("")
    combo_status.set("")

# Tampilan aplikasi
root = tk.Tk()
root.title("Aplikasi Data Mahasiswa - SIAKAD")
root.geometry("1250x700")
root.minsize(1000, 600)

frame_form = tk.LabelFrame(root, text="Form Data Mahasiswa", padx=10, pady=10)
frame_form.pack(fill="x", padx=12, pady=10)

fields = [
    ("NIM", 0, 0), ("Nama Lengkap", 0, 2),
    ("Jenis Kelamin", 1, 0), ("Tanggal Lahir (YYYY-MM-DD)", 1, 2),
    ("Tempat Lahir", 2, 0), ("Alamat", 2, 2),
    ("No. Telepon", 3, 0), ("Email", 3, 2),
    ("Jurusan", 4, 0), ("Angkatan", 4, 2),
    ("Status", 5, 0)
]
for label, row, col in fields:
    tk.Label(frame_form, text=label).grid(
        row=row, column=col, sticky="w", padx=5, pady=4
    )

entry_nim = tk.Entry(frame_form)
entry_nama = tk.Entry(frame_form)
combo_jk = ttk.Combobox(
    frame_form, values=["Laki-laki", "Perempuan"], state="readonly"
)
entry_tgl_lahir = tk.Entry(frame_form)
entry_tempat_lahir = tk.Entry(frame_form)
entry_alamat = tk.Entry(frame_form)
entry_tlp = tk.Entry(frame_form)
entry_email = tk.Entry(frame_form)
entry_jurusan = tk.Entry(frame_form)
entry_angkatan = tk.Entry(frame_form)
combo_status = ttk.Combobox(
    frame_form, values=["Aktif", "Cuti", "Lulus", "Nonaktif"], state="readonly"
)

widgets = [
    (entry_nim, 0, 1), (entry_nama, 0, 3),
    (combo_jk, 1, 1), (entry_tgl_lahir, 1, 3),
    (entry_tempat_lahir, 2, 1), (entry_alamat, 2, 3),
    (entry_tlp, 3, 1), (entry_email, 3, 3),
    (entry_jurusan, 4, 1), (entry_angkatan, 4, 3),
    (combo_status, 5, 1)
]
for widget, row, col in widgets:
    widget.grid(row=row, column=col, sticky="ew", padx=5, pady=4)

for col in (1, 3):
    frame_form.grid_columnconfigure(col, weight=1)

frame_btn = tk.Frame(root)
frame_btn.pack(fill="x", padx=12, pady=5)

tk.Button(frame_btn, text="Tambah", command=tambah_data, width=12,
          bg="#4CAF50", fg="white").pack(side="left", padx=4)
tk.Button(frame_btn, text="Edit", command=edit_data, width=12,
          bg="#2196F3", fg="white").pack(side="left", padx=4)
tk.Button(frame_btn, text="Hapus", command=hapus_data, width=12,
          bg="#f44336", fg="white").pack(side="left", padx=4)
tk.Button(frame_btn, text="Clear", command=clear_fields, width=12,
          bg="#777777", fg="white").pack(side="left", padx=4)
tk.Button(frame_btn, text="Refresh", command=load_data, width=12).pack(
    side="left", padx=4
)

frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=12, pady=10)

tree = ttk.Treeview(frame_table, columns=COLUMNS, show="headings")
headers = {
    "nim": "NIM",
    "nama_lengkap": "Nama Lengkap",
    "jenis_kelamin": "Jenis Kelamin",
    "tanggal_lahir": "Tanggal Lahir",
    "tempat_lahir": "Tempat Lahir",
    "alamat": "Alamat",
    "no_telepon": "No. Telepon",
    "email": "Email",
    "jurusan": "Jurusan",
    "angkatan": "Angkatan",
    "status": "Status"
}
widths = {
    "nim": 95, "nama_lengkap": 150, "jenis_kelamin": 105,
    "tanggal_lahir": 105, "tempat_lahir": 105, "alamat": 180,
    "no_telepon": 125, "email": 170, "jurusan": 140,
    "angkatan": 75, "status": 80
}
for col in COLUMNS:
    tree.heading(col, text=headers[col])
    tree.column(col, width=widths[col], minwidth=70, anchor="w")

scroll_y = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_table, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")
frame_table.grid_rowconfigure(0, weight=1)
frame_table.grid_columnconfigure(0, weight=1)

tree.bind("<<TreeviewSelect>>", select_item)

load_data()
root.mainloop()
