import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from decimal import Decimal, InvalidOperation

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
    # Menghapus tampilan lama sebelum memuat data terbaru
    for item in tree.get_children():
        tree.delete(item)
    try:
        db = connect_db()
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id_krs, nim, kode_mk, semester_ambil, tahun_ajaran, nilai_huruf, nilai_angka FROM krs ORDER BY id_krs")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            cursor.close()
        finally:
            db.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")


def ambil_form():
    nim = entry_nim.get().strip()
    kode_mk = entry_kode_mk.get().strip()
    semester = combo_semester.get().strip()
    tahun = entry_tahun.get().strip()
    huruf = combo_nilai_huruf.get().strip()
    angka = entry_nilai_angka.get().strip()

    if not all((nim, kode_mk, semester, tahun, huruf, angka)):
        messagebox.showwarning("Validasi", "Semua kolom wajib diisi!")
        return None
    try:
        semester_int = int(semester)
        angka_decimal = Decimal(angka)
        if not (1 <= semester_int <= 14):
            raise ValueError("Semester harus antara 1 dan 14")
        if not (Decimal("0") <= angka_decimal <= Decimal("4")):
            raise ValueError("Nilai angka harus antara 0 dan 4")
    except (ValueError, InvalidOperation) as e:
        messagebox.showwarning("Validasi", f"Semester atau nilai angka tidak valid: {e}")
        return None
    return (nim, kode_mk, semester_int, tahun, huruf, angka_decimal)


def jalankan_query(sql, params, pesan):
    db = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(sql, params)
        db.commit()
        berubah = cursor.rowcount
        cursor.close()
        if berubah == 0:
            messagebox.showwarning("Informasi", "Tidak ada data yang berubah.")
        else:
            messagebox.showinfo("Sukses", pesan)
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        if db:
            db.rollback()
        messagebox.showerror("Database Error", f"Operasi gagal: {e}")
    finally:
        if db:
            db.close()


def tambah_data():
    data = ambil_form()
    if data is None:
        return
    sql = """INSERT INTO krs (nim, kode_mk, semester_ambil, tahun_ajaran, nilai_huruf, nilai_angka)
             VALUES (%s, %s, %s, %s, %s, %s)"""
    jalankan_query(sql, data, "Data KRS berhasil ditambahkan!")


def edit_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Pilih data KRS yang ingin diubah!")
        return
    id_krs = tree.item(selected[0], "values")[0]
    data = ambil_form()
    if data is None:
        return
    sql = """UPDATE krs SET nim=%s, kode_mk=%s, semester_ambil=%s,
             tahun_ajaran=%s, nilai_huruf=%s, nilai_angka=%s WHERE id_krs=%s"""
    jalankan_query(sql, data + (id_krs,), "Data KRS berhasil diperbarui!")


def hapus_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Pilih data KRS yang ingin dihapus!")
        return
    id_krs = tree.item(selected[0], "values")[0]
    if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus KRS ID {id_krs}?"):
        jalankan_query("DELETE FROM krs WHERE id_krs=%s", (id_krs,), "Data KRS berhasil dihapus!")


def select_item(event):
    selected = tree.selection()
    if not selected:
        return
    values = tree.item(selected[0], "values")
    clear_fields(batalkan_pilihan=False)
    entry_id.insert(0, values[0])
    entry_nim.insert(0, values[1])
    entry_kode_mk.insert(0, values[2])
    combo_semester.set(values[3])
    entry_tahun.insert(0, values[4])
    combo_nilai_huruf.set(values[5])
    entry_nilai_angka.insert(0, values[6])


def clear_fields(batalkan_pilihan=True):
    for entry in (entry_id, entry_nim, entry_kode_mk, entry_tahun, entry_nilai_angka):
        entry.configure(state="normal")
        entry.delete(0, tk.END)
    entry_id.configure(state="readonly")
    combo_semester.set("")
    combo_nilai_huruf.set("")
    if batalkan_pilihan:
        for item in tree.selection():
            tree.selection_remove(item)


# --- GUI MAIN WINDOW ---
root = tk.Tk()
root.title("Aplikasi Data KRS - SIAKAD")
root.geometry("1050x550")

frame_form = tk.LabelFrame(root, text=" Form Data KRS ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

labels = ["ID KRS", "NIM", "Kode MK", "Semester Ambil", "Tahun Ajaran", "Nilai Huruf", "Nilai Angka"]
for i, label_text in enumerate(labels):
    tk.Label(frame_form, text=label_text).grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=5, pady=5)

entry_id = tk.Entry(frame_form, state="readonly")
entry_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
entry_nim = tk.Entry(frame_form)
entry_nim.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
entry_kode_mk = tk.Entry(frame_form)
entry_kode_mk.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
combo_semester = ttk.Combobox(frame_form, values=[str(i) for i in range(1, 15)], state="readonly")
combo_semester.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
entry_tahun = tk.Entry(frame_form)
entry_tahun.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
combo_nilai_huruf = ttk.Combobox(frame_form, values=["A", "A-", "B+", "B", "B-", "C+", "C", "D", "E"], state="readonly")
combo_nilai_huruf.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
entry_nilai_angka = tk.Entry(frame_form)
entry_nilai_angka.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

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
columns = ("id_krs", "nim", "kode_mk", "semester_ambil", "tahun_ajaran", "nilai_huruf", "nilai_angka")
tree = ttk.Treeview(frame_table, columns=columns, show="headings")
headers = ["ID KRS", "NIM", "Kode MK", "Semester Ambil", "Tahun Ajaran", "Nilai Huruf", "Nilai Angka"]
widths = [65, 110, 100, 120, 130, 100, 100]
for col, header, width in zip(columns, headers, widths):
    tree.heading(col, text=header)
    tree.column(col, width=width, anchor="center")
tree.bind("<<TreeviewSelect>>", select_item)
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

load_data()
root.mainloop()
