"""Login SIAKAD dan CRUD Mahasiswa. Untuk demonstrasi lokal saja.
Login menggunakan NIP dan email dosen (bukan autentikasi aman untuk produksi).
"""
import tkinter as tk
from tkinter import messagebox
import mysql.connector

DB_CONFIG = dict(host="localhost", user="root", password="", database="siakad")

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.render()

    def render(self):
        self.root.unbind("<Return>")
        for child in self.root.winfo_children():
            child.destroy()
        self.root.title("Login - SIAKAD")
        self.root.geometry("380x250")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(expand=True, padx=20, pady=20)
        tk.Label(frame, text="SIAKAD LOGIN", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=(0, 18))
        form = tk.Frame(frame, bg="#f0f0f0")
        form.pack()
        tk.Label(form, text="Username:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=6)
        self.entry_nip = tk.Entry(form, width=25)
        self.entry_nip.grid(row=0, column=1, padx=5, pady=6)
        tk.Label(form, text="Password:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=6)
        self.entry_email = tk.Entry(form, width=25, show="*")
        self.entry_email.grid(row=1, column=1, padx=5, pady=6)
        tk.Button(frame, text="Login", width=15, bg="#4CAF50", fg="white", command=self.proses_login).pack(pady=16)
        self.root.bind("<Return>", lambda event: self.proses_login())
        self.entry_nip.focus_set()

    def proses_login(self):
        nip = self.entry_nip.get().strip()
        email = self.entry_email.get().strip()
        if not nip or not email:
            messagebox.showwarning("Peringatan", "NIP dan Email wajib diisi!")
            return
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT nip, nama_dosen FROM dosen WHERE nip=%s AND email=%s", (nip, email))
            user = cursor.fetchone()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
            return
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()
        if not user:
            messagebox.showerror("Gagal", "NIP atau Email tidak sesuai.")
            return
        messagebox.showinfo("Berhasil", f"Selamat datang, {user['nama_dosen']}!")
        self.root.unbind("<Return>")
        for child in self.root.winfo_children():
            child.destroy()
        buka_crud_mahasiswa(self.root, self)


def buka_crud_mahasiswa(parent, login):
    # Isolasi namespace fungsi CRUD asli supaya tetap bekerja dengan variabel globalnya.
    namespace = {"parent": parent, "__name__": "crud_mahasiswa_embedded"}
    exec(compile(CRUD_SOURCE, "crud_mahasiswa", "exec"), namespace)
    bar = tk.Frame(parent)
    bar.pack(fill="x", padx=12, pady=(0, 8))
    tk.Button(bar, text="Logout", bg="#d97706", fg="white", width=12,
              command=login.render).pack(side="right")

CRUD_SOURCE = 'import tkinter as tk\nfrom tkinter import ttk, messagebox\nimport mysql.connector\n\n# Koneksi ke database\ndef connect_db():\n    return mysql.connector.connect(\n        host="localhost",\n        user="root",\n        password="",\n        database="siakad"\n    )\n\n# Nama kolom sesuai tabel mahasiswa di database\nCOLUMNS = (\n    "nim", "nama_lengkap", "jenis_kelamin", "tanggal_lahir",\n    "tempat_lahir", "alamat", "no_telepon", "email",\n    "jurusan", "angkatan", "status"\n)\n\ndef get_form_data():\n    return (\n        entry_nim.get().strip(),\n        entry_nama.get().strip(),\n        combo_jk.get().strip(),\n        entry_tgl_lahir.get().strip(),\n        entry_tempat_lahir.get().strip(),\n        entry_alamat.get().strip(),\n        entry_tlp.get().strip(),\n        entry_email.get().strip(),\n        entry_jurusan.get().strip(),\n        entry_angkatan.get().strip(),\n        combo_status.get().strip()\n    )\n\ndef clear_fields():\n    for widget in (\n        entry_nim, entry_nama, entry_tgl_lahir, entry_tempat_lahir,\n        entry_alamat, entry_tlp, entry_email, entry_jurusan, entry_angkatan\n    ):\n        widget.delete(0, tk.END)\n    combo_jk.set("")\n    combo_status.set("")\n    tree.selection_remove(tree.selection())\n\ndef load_data():\n    for item in tree.get_children():\n        tree.delete(item)\n\n    db = None\n    cursor = None\n    try:\n        db = connect_db()\n        cursor = db.cursor()\n        cursor.execute("""\n            SELECT nim, nama_lengkap, jenis_kelamin, tanggal_lahir,\n                   tempat_lahir, alamat, no_telepon, email,\n                   jurusan, angkatan, status\n            FROM mahasiswa\n            ORDER BY nim\n        """)\n        for row in cursor.fetchall():\n            tree.insert("", "end", values=row)\n    except mysql.connector.Error as e:\n        messagebox.showerror("Database Error", f"Gagal mengambil data:\\n{e}")\n    finally:\n        if cursor:\n            cursor.close()\n        if db and db.is_connected():\n            db.close()\n\ndef tambah_data():\n    data = get_form_data()\n    if not data[0] or not data[1]:\n        messagebox.showwarning("Peringatan", "NIM dan nama lengkap wajib diisi!")\n        return\n\n    db = None\n    cursor = None\n    try:\n        db = connect_db()\n        cursor = db.cursor()\n        sql = """\n            INSERT INTO mahasiswa\n            (nim, nama_lengkap, jenis_kelamin, tanggal_lahir, tempat_lahir,\n             alamat, no_telepon, email, jurusan, angkatan, status)\n            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n        """\n        cursor.execute(sql, data)\n        db.commit()\n        messagebox.showinfo("Sukses", "Data mahasiswa berhasil ditambahkan.")\n        clear_fields()\n        load_data()\n    except mysql.connector.Error as e:\n        messagebox.showerror("Database Error", f"Gagal menambahkan data:\\n{e}")\n    finally:\n        if cursor:\n            cursor.close()\n        if db and db.is_connected():\n            db.close()\n\ndef edit_data():\n    selected = tree.selection()\n    if not selected:\n        messagebox.showwarning("Peringatan", "Pilih data mahasiswa yang ingin diubah.")\n        return\n\n    data = get_form_data()\n    if not data[0] or not data[1]:\n        messagebox.showwarning("Peringatan", "NIM dan nama lengkap wajib diisi!")\n        return\n\n    # NIM lama dipakai sebagai kunci untuk menemukan baris yang dipilih.\n    old_values = tree.item(selected[0], "values")\n    old_nim = old_values[0]\n\n    db = None\n    cursor = None\n    try:\n        db = connect_db()\n        cursor = db.cursor()\n        sql = """\n            UPDATE mahasiswa\n            SET nim=%s, nama_lengkap=%s, jenis_kelamin=%s, tanggal_lahir=%s,\n                tempat_lahir=%s, alamat=%s, no_telepon=%s, email=%s,\n                jurusan=%s, angkatan=%s, status=%s\n            WHERE nim=%s\n        """\n        cursor.execute(sql, data + (old_nim,))\n        db.commit()\n        if cursor.rowcount == 0:\n            messagebox.showwarning("Info", "Tidak ada perubahan data atau NIM tidak ditemukan.")\n        else:\n            messagebox.showinfo("Sukses", "Data mahasiswa berhasil diperbarui.")\n        clear_fields()\n        load_data()\n    except mysql.connector.Error as e:\n        messagebox.showerror("Database Error", f"Gagal memperbarui data:\\n{e}")\n    finally:\n        if cursor:\n            cursor.close()\n        if db and db.is_connected():\n            db.close()\n\ndef hapus_data():\n    selected = tree.selection()\n    if not selected:\n        messagebox.showwarning("Peringatan", "Pilih data mahasiswa yang ingin dihapus.")\n        return\n\n    values = tree.item(selected[0], "values")\n    nim = values[0]\n    nama = values[1]\n\n    if not messagebox.askyesno(\n        "Konfirmasi Hapus",\n        f"Yakin ingin menghapus data {nama} (NIM {nim})?"\n    ):\n        return\n\n    db = None\n    cursor = None\n    try:\n        db = connect_db()\n        cursor = db.cursor()\n        cursor.execute("DELETE FROM mahasiswa WHERE nim = %s", (nim,))\n        db.commit()\n        messagebox.showinfo("Sukses", "Data mahasiswa berhasil dihapus.")\n        clear_fields()\n        load_data()\n    except mysql.connector.Error as e:\n        messagebox.showerror("Database Error", f"Gagal menghapus data:\\n{e}")\n    finally:\n        if cursor:\n            cursor.close()\n        if db and db.is_connected():\n            db.close()\n\ndef select_item(event=None):\n    selected = tree.selection()\n    if not selected:\n        return\n\n    values = tree.item(selected[0], "values")\n    clear_form_only()\n\n    entry_nim.insert(0, values[0])\n    entry_nama.insert(0, values[1])\n    combo_jk.set(values[2])\n    entry_tgl_lahir.insert(0, values[3])\n    entry_tempat_lahir.insert(0, values[4])\n    entry_alamat.insert(0, values[5])\n    entry_tlp.insert(0, values[6])\n    entry_email.insert(0, values[7])\n    entry_jurusan.insert(0, values[8])\n    entry_angkatan.insert(0, values[9])\n    combo_status.set(values[10])\n\ndef clear_form_only():\n    # Mengosongkan isian tanpa menghilangkan pilihan baris tabel.\n    for widget in (\n        entry_nim, entry_nama, entry_tgl_lahir, entry_tempat_lahir,\n        entry_alamat, entry_tlp, entry_email, entry_jurusan, entry_angkatan\n    ):\n        widget.delete(0, tk.END)\n    combo_jk.set("")\n    combo_status.set("")\n\n# Tampilan aplikasi\nroot = parent\nroot.title("Aplikasi Data Mahasiswa - SIAKAD")\nroot.resizable(True, True)\nroot.geometry("1250x700")\nroot.minsize(1000, 600)\n\nframe_form = tk.LabelFrame(root, text="Form Data Mahasiswa", padx=10, pady=10)\nframe_form.pack(fill="x", padx=12, pady=10)\n\nfields = [\n    ("NIM", 0, 0), ("Nama Lengkap", 0, 2),\n    ("Jenis Kelamin", 1, 0), ("Tanggal Lahir (YYYY-MM-DD)", 1, 2),\n    ("Tempat Lahir", 2, 0), ("Alamat", 2, 2),\n    ("No. Telepon", 3, 0), ("Email", 3, 2),\n    ("Jurusan", 4, 0), ("Angkatan", 4, 2),\n    ("Status", 5, 0)\n]\nfor label, row, col in fields:\n    tk.Label(frame_form, text=label).grid(\n        row=row, column=col, sticky="w", padx=5, pady=4\n    )\n\nentry_nim = tk.Entry(frame_form)\nentry_nama = tk.Entry(frame_form)\ncombo_jk = ttk.Combobox(\n    frame_form, values=["Laki-laki", "Perempuan"], state="readonly"\n)\nentry_tgl_lahir = tk.Entry(frame_form)\nentry_tempat_lahir = tk.Entry(frame_form)\nentry_alamat = tk.Entry(frame_form)\nentry_tlp = tk.Entry(frame_form)\nentry_email = tk.Entry(frame_form)\nentry_jurusan = tk.Entry(frame_form)\nentry_angkatan = tk.Entry(frame_form)\ncombo_status = ttk.Combobox(\n    frame_form, values=["Aktif", "Cuti", "Lulus", "Nonaktif"], state="readonly"\n)\n\nwidgets = [\n    (entry_nim, 0, 1), (entry_nama, 0, 3),\n    (combo_jk, 1, 1), (entry_tgl_lahir, 1, 3),\n    (entry_tempat_lahir, 2, 1), (entry_alamat, 2, 3),\n    (entry_tlp, 3, 1), (entry_email, 3, 3),\n    (entry_jurusan, 4, 1), (entry_angkatan, 4, 3),\n    (combo_status, 5, 1)\n]\nfor widget, row, col in widgets:\n    widget.grid(row=row, column=col, sticky="ew", padx=5, pady=4)\n\nfor col in (1, 3):\n    frame_form.grid_columnconfigure(col, weight=1)\n\nframe_btn = tk.Frame(root)\nframe_btn.pack(fill="x", padx=12, pady=5)\n\ntk.Button(frame_btn, text="Tambah", command=tambah_data, width=12,\n          bg="#4CAF50", fg="white").pack(side="left", padx=4)\ntk.Button(frame_btn, text="Edit", command=edit_data, width=12,\n          bg="#2196F3", fg="white").pack(side="left", padx=4)\ntk.Button(frame_btn, text="Hapus", command=hapus_data, width=12,\n          bg="#f44336", fg="white").pack(side="left", padx=4)\ntk.Button(frame_btn, text="Clear", command=clear_fields, width=12,\n          bg="#777777", fg="white").pack(side="left", padx=4)\ntk.Button(frame_btn, text="Refresh", command=load_data, width=12).pack(\n    side="left", padx=4\n)\n\nframe_table = tk.Frame(root)\nframe_table.pack(fill="both", expand=True, padx=12, pady=10)\n\ntree = ttk.Treeview(frame_table, columns=COLUMNS, show="headings")\nheaders = {\n    "nim": "NIM",\n    "nama_lengkap": "Nama Lengkap",\n    "jenis_kelamin": "Jenis Kelamin",\n    "tanggal_lahir": "Tanggal Lahir",\n    "tempat_lahir": "Tempat Lahir",\n    "alamat": "Alamat",\n    "no_telepon": "No. Telepon",\n    "email": "Email",\n    "jurusan": "Jurusan",\n    "angkatan": "Angkatan",\n    "status": "Status"\n}\nwidths = {\n    "nim": 95, "nama_lengkap": 150, "jenis_kelamin": 105,\n    "tanggal_lahir": 105, "tempat_lahir": 105, "alamat": 180,\n    "no_telepon": 125, "email": 170, "jurusan": 140,\n    "angkatan": 75, "status": 80\n}\nfor col in COLUMNS:\n    tree.heading(col, text=headers[col])\n    tree.column(col, width=widths[col], minwidth=70, anchor="w")\n\nscroll_y = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)\nscroll_x = ttk.Scrollbar(frame_table, orient="horizontal", command=tree.xview)\ntree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)\n\ntree.grid(row=0, column=0, sticky="nsew")\nscroll_y.grid(row=0, column=1, sticky="ns")\nscroll_x.grid(row=1, column=0, sticky="ew")\nframe_table.grid_rowconfigure(0, weight=1)\nframe_table.grid_columnconfigure(0, weight=1)\n\ntree.bind("<<TreeviewSelect>>", select_item)\n\nload_data()\n\n'

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
