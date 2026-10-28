import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from decimal import Decimal, InvalidOperation
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
    try:
        db = connect_db()
        try:
            cursor = db.cursor()
            cursor.execute("""SELECT id_pembayaran, nim, semester, tahun_ajaran,
                              jumlah_bayar, tanggal_bayar, metode_pembayaran, status
                              FROM pembayaran_ukt ORDER BY id_pembayaran""")
            rows = cursor.fetchall()
        finally:
            db.close()
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            values = ["" if v is None else str(v) for v in row]
            tree.insert("", "end", values=values)
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")


def ambil_input():
    nim = entry_nim.get().strip()
    semester = combo_semester.get().strip()
    tahun = entry_tahun.get().strip()
    jumlah = entry_jumlah.get().strip()
    tanggal = entry_tanggal.get().strip()
    metode = combo_metode.get().strip()
    status = combo_status.get().strip()

    if not all([nim, semester, tahun, jumlah, status]):
        raise ValueError("NIM, Semester, Tahun Ajaran, Jumlah Bayar, dan Status wajib diisi!")
    if not semester.isdigit() or int(semester) < 1:
        raise ValueError("Semester harus berupa angka positif.")
    try:
        nominal = Decimal(jumlah)
        if not nominal.is_finite() or nominal < 0 or nominal.as_tuple().exponent < -2:
            raise ValueError
    except (InvalidOperation, ValueError):
        raise ValueError("Jumlah Bayar harus berupa angka positif dengan maksimal 2 desimal.")
    if tanggal:
        try:
            datetime.strptime(tanggal, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Tanggal harus valid dan berformat YYYY-MM-DD.")
    if status == "Lunas" and (not tanggal or not metode):
        raise ValueError("Pembayaran Lunas harus memiliki tanggal dan metode pembayaran.")
    return (nim, int(semester), tahun, nominal, tanggal or None, metode or None, status)


def tambah_data():
    try:
        nilai = ambil_input()
    except ValueError as e:
        messagebox.showwarning("Validasi", str(e))
        return
    db = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""INSERT INTO pembayaran_ukt
            (nim, semester, tahun_ajaran, jumlah_bayar, tanggal_bayar, metode_pembayaran, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", nilai)
        db.commit()
        messagebox.showinfo("Sukses", "Data pembayaran berhasil ditambahkan!")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        if db:
            db.rollback()
        messagebox.showerror("Error", f"Gagal menambah data: {e}")
    finally:
        if db:
            db.close()


def edit_data():
    if not selected_id.get():
        messagebox.showwarning("Warning", "Pilih data yang ingin diedit terlebih dahulu!")
        return
    try:
        nilai = ambil_input()
    except ValueError as e:
        messagebox.showwarning("Validasi", str(e))
        return
    db = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""UPDATE pembayaran_ukt SET nim=%s, semester=%s, tahun_ajaran=%s,
            jumlah_bayar=%s, tanggal_bayar=%s, metode_pembayaran=%s, status=%s
            WHERE id_pembayaran=%s""", nilai + (int(selected_id.get()),))
        db.commit()
        messagebox.showinfo("Sukses", "Data pembayaran berhasil diperbarui!" if cursor.rowcount else "Tidak ada perubahan data.")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        if db:
            db.rollback()
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")
    finally:
        if db:
            db.close()


def hapus_data():
    if not selected_id.get():
        messagebox.showwarning("Warning", "Pilih data yang ingin dihapus terlebih dahulu!")
        return
    kode = selected_id.get()
    if not messagebox.askyesno("Konfirmasi", f"Yakin menghapus pembayaran ID {kode}?"):
        return
    db = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM pembayaran_ukt WHERE id_pembayaran=%s", (int(kode),))
        db.commit()
        messagebox.showinfo("Sukses", "Data pembayaran berhasil dihapus!" if cursor.rowcount else "Data sudah tidak ditemukan.")
        clear_fields()
        load_data()
    except mysql.connector.Error as e:
        if db:
            db.rollback()
        messagebox.showerror("Error", f"Gagal menghapus data: {e}")
    finally:
        if db:
            db.close()


def select_item(event):
    pilihan = tree.selection()
    if not pilihan:
        return
    values = tree.item(pilihan[0], "values")
    selected_id.set(values[0])
    entry_id.config(state="normal")
    entry_id.delete(0, tk.END)
    entry_id.insert(0, values[0])
    entry_id.config(state="readonly")
    for widget, value in [(entry_nim, values[1]), (entry_tahun, values[3]),
                          (entry_jumlah, values[4]), (entry_tanggal, values[5])]:
        widget.delete(0, tk.END)
        widget.insert(0, value)
    combo_semester.set(values[2])
    combo_metode.set(values[6])
    combo_status.set(values[7])


def clear_fields():
    selected_id.set("")
    entry_id.config(state="normal")
    entry_id.delete(0, tk.END)
    entry_id.config(state="readonly")
    for widget in (entry_nim, entry_tahun, entry_jumlah, entry_tanggal):
        widget.delete(0, tk.END)
    for combo in (combo_semester, combo_metode, combo_status):
        combo.set("")
    for item in tree.selection():
        tree.selection_remove(item)


# --- GUI MAIN WINDOW ---
root = tk.Tk()
root.title("Aplikasi Data Pembayaran UKT")
root.geometry("1120x570")
selected_id = tk.StringVar()

frame_form = tk.LabelFrame(root, text=" Form Data Pembayaran UKT ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

labels = ["ID Pembayaran", "NIM", "Semester", "Tahun Ajaran", "Jumlah Bayar",
          "Tanggal Bayar (YYYY-MM-DD)", "Metode Pembayaran", "Status"]
for i, label in enumerate(labels):
    tk.Label(frame_form, text=label).grid(row=i // 2, column=(i % 2) * 2,
                                         sticky="w", padx=5, pady=5)

def letak(widget, row, column):
    widget.grid(row=row, column=column, sticky="ew", padx=5, pady=5)

entry_id = tk.Entry(frame_form, state="readonly")
letak(entry_id, 0, 1)
entry_nim = tk.Entry(frame_form)
letak(entry_nim, 0, 3)
combo_semester = ttk.Combobox(frame_form, values=[str(i) for i in range(1, 15)], state="readonly")
letak(combo_semester, 1, 1)
entry_tahun = tk.Entry(frame_form)
letak(entry_tahun, 1, 3)
entry_jumlah = tk.Entry(frame_form)
letak(entry_jumlah, 2, 1)
entry_tanggal = tk.Entry(frame_form)
letak(entry_tanggal, 2, 3)
combo_metode = ttk.Combobox(frame_form, values=["Transfer Bank", "Virtual Account", "Tunai"], state="readonly")
letak(combo_metode, 3, 1)
combo_status = ttk.Combobox(frame_form, values=["Lunas", "Belum Lunas"], state="readonly")
letak(combo_status, 3, 3)
frame_form.grid_columnconfigure(1, weight=1)
frame_form.grid_columnconfigure(3, weight=1)

frame_btn = tk.Frame(root)
frame_btn.pack(fill="x", padx=15, pady=5)
for label, color, func in [("Tambah", "#4CAF50", tambah_data),
                           ("Edit", "#2196F3", edit_data),
                           ("Hapus", "#f44336", hapus_data),
                           ("Clear", "#9E9E9E", clear_fields)]:
    tk.Button(frame_btn, text=label, bg=color, fg="white", width=12,
              command=func).pack(side="left", padx=5)

frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=15, pady=10)
columns = ("id_pembayaran", "nim", "semester", "tahun_ajaran", "jumlah_bayar",
           "tanggal_bayar", "metode_pembayaran", "status")
tree = ttk.Treeview(frame_table, columns=columns, show="headings")
headings = ["ID Pembayaran", "NIM", "Semester", "Tahun Ajaran", "Jumlah Bayar",
            "Tanggal Bayar", "Metode Pembayaran", "Status"]
widths = [110, 100, 75, 110, 120, 115, 150, 110]
for col, title, width in zip(columns, headings, widths):
    tree.heading(col, text=title)
    tree.column(col, width=width, minwidth=70)
tree.bind("<<TreeviewSelect>>", select_item)
scroll_y = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_table, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")
frame_table.grid_rowconfigure(0, weight=1)
frame_table.grid_columnconfigure(0, weight=1)

load_data()
root.mainloop()
