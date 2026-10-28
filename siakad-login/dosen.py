import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Konfigurasi database untuk login dan CRUD.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "siakad"
}

COLUMNS = (
    "nip", "nama_dosen", "jenis_kelamin", "email", "no_telepon",
    "pendidikan_terakhir", "bidang_keahlian"
)
HEADINGS = (
    "NIP", "Nama Dosen", "Jenis Kelamin", "Email", "No Telepon",
    "Pendidikan", "Bidang Keahlian"
)


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


class SiakadApp:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.selected_nip = None
        self.show_login()

    def clear_window(self):
        self.root.unbind("<Return>")
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        self.root.title("Login - SIAKAD")
        self.root.geometry("380x250")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        tk.Label(main_frame, text="SIAKAD LOGIN", font=("Arial", 14, "bold"),
                 bg="#f0f0f0").pack(pady=(0, 20))

        form = tk.Frame(main_frame, bg="#f0f0f0")
        form.pack()
        tk.Label(form, text="Username:", width=10, anchor="e", bg="#f0f0f0").grid(
            row=0, column=0, padx=5, pady=6)
        self.login_nip = tk.Entry(form, width=22, relief=tk.SOLID, bd=1)
        self.login_nip.grid(row=0, column=1, padx=5, pady=6)

        tk.Label(form, text="Password:", width=10, anchor="e", bg="#f0f0f0").grid(
            row=1, column=0, padx=5, pady=6)
        self.login_email = tk.Entry(form, width=22, show="*", relief=tk.SOLID, bd=1)
        self.login_email.grid(row=1, column=1, padx=5, pady=6)

        tk.Button(main_frame, text="Login", bg="#4CAF50", fg="white", width=15,
                  font=("Arial", 10, "bold"), command=self.proses_login).pack(pady=(20, 0))
        self.root.bind("<Return>", lambda event: self.proses_login())
        self.login_nip.focus_set()

    def proses_login(self):
        nip = self.login_nip.get().strip()
        email = self.login_email.get().strip()
        if not nip or not email:
            messagebox.showwarning("Peringatan", "Username (NIP) dan Password (Email) wajib diisi!")
            return
        try:
            with connect_db() as conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(
                        "SELECT nip, nama_dosen, email FROM dosen WHERE nip=%s AND email=%s",
                        (nip, email)
                    )
                    user = cursor.fetchone()
                finally:
                    cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Koneksi atau query bermasalah:\n{err}")
            return

        if user is None:
            messagebox.showerror("Gagal", "Login gagal! Username atau Password salah.")
            return
        self.user = user
        messagebox.showinfo("Berhasil", f"Login berhasil!\nSelamat datang, {user['nama_dosen']}.")
        self.show_crud()

    def show_crud(self):
        self.clear_window()
        self.selected_nip = None
        self.root.title("Aplikasi Data Dosen - SIAKAD")
        self.root.geometry("1050x570")
        self.root.minsize(900, 500)
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        header = tk.Frame(self.root, bg="#f0f0f0")
        header.pack(fill="x", padx=15, pady=(10, 0))
        tk.Label(header, text=f"Selamat datang, {self.user['nama_dosen']}",
                 font=("Arial", 11, "bold"), bg="#f0f0f0").pack(side="left")
        tk.Button(header, text="Logout", command=self.logout,
                  bg="#757575", fg="white", width=10).pack(side="right")

        frame_form = tk.LabelFrame(self.root, text=" Form Data Dosen ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=10)
        self.entries = {}
        for i, (column, heading) in enumerate(zip(COLUMNS, HEADINGS)):
            r, c = divmod(i, 2)
            tk.Label(frame_form, text=heading).grid(row=r, column=c * 2, sticky="w", padx=5, pady=3)
            if column == "jenis_kelamin":
                entry = ttk.Combobox(frame_form, values=["Laki-laki", "Perempuan"], state="readonly")
            else:
                entry = tk.Entry(frame_form)
            entry.grid(row=r, column=c * 2 + 1, sticky="ew", padx=5, pady=3)
            self.entries[column] = entry
        frame_form.columnconfigure(1, weight=1)
        frame_form.columnconfigure(3, weight=1)

        buttons = tk.Frame(self.root, bg="#f0f0f0")
        buttons.pack(fill="x", padx=15, pady=5)
        for label, color, action in [
            ("Tambah", "#4CAF50", self.tambah_data),
            ("Edit", "#2196F3", self.edit_data),
            ("Hapus", "#f44336", self.hapus_data),
            ("Clear", "#9E9E9E", self.clear_fields),
            ("Refresh", "#607D8B", self.load_data),
        ]:
            tk.Button(buttons, text=label, bg=color, fg="white", width=12,
                      command=action).pack(side="left", padx=5)

        frame_table = tk.Frame(self.root)
        frame_table.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree = ttk.Treeview(frame_table, columns=COLUMNS, show="headings")
        for col, heading in zip(COLUMNS, HEADINGS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=140 if col != "nip" else 105, minwidth=80)
        self.tree.bind("<<TreeviewSelect>>", self.select_item)
        vertical = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        horizontal = ttk.Scrollbar(frame_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        frame_table.columnconfigure(0, weight=1)
        frame_table.rowconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.load_data()

    def load_data(self):
        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT " + ", ".join(COLUMNS) + " FROM dosen")
                    rows = cursor.fetchall()
                finally:
                    cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Gagal mengambil data:\n{err}")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=["" if v is None else v for v in row])

    def form_values(self):
        return tuple(self.entries[col].get().strip() for col in COLUMNS)

    def clear_fields(self):
        self.selected_nip = None
        for col, entry in self.entries.items():
            if col == "jenis_kelamin":
                entry.set("")
            else:
                entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def select_item(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_nip = str(values[0])
        for col, value in zip(COLUMNS, values):
            entry = self.entries[col]
            if col == "jenis_kelamin":
                entry.set(value)
            else:
                entry.delete(0, tk.END)
                entry.insert(0, value)

    def execute_change(self, sql, params, success_message):
        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql, params)
                    affected = cursor.rowcount
                    conn.commit()
                finally:
                    cursor.close()
            if affected == 0:
                messagebox.showwarning("Tidak ditemukan", "Tidak ada data yang berubah.")
                return
            messagebox.showinfo("Sukses", success_message)
            self.clear_fields()
            self.load_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Operasi gagal:\n{err}")

    def tambah_data(self):
        values = self.form_values()
        if not values[0] or not values[1]:
            messagebox.showwarning("Peringatan", "NIP dan Nama Dosen wajib diisi!")
            return
        placeholders = ", ".join(["%s"] * len(COLUMNS))
        sql = f"INSERT INTO dosen ({', '.join(COLUMNS)}) VALUES ({placeholders})"
        self.execute_change(sql, values, "Data dosen berhasil ditambahkan!")

    def edit_data(self):
        if not self.selected_nip:
            messagebox.showwarning("Peringatan", "Pilih baris dosen yang ingin diedit!")
            return
        values = self.form_values()
        if not values[0] or not values[1]:
            messagebox.showwarning("Peringatan", "NIP dan Nama Dosen wajib diisi!")
            return
        # WHERE memakai NIP lama sehingga NIP juga bisa diperbarui.
        assignments = ", ".join(f"{col}=%s" for col in COLUMNS)
        self.execute_change(f"UPDATE dosen SET {assignments} WHERE nip=%s",
                            values + (self.selected_nip,), "Data dosen berhasil diperbarui!")

    def hapus_data(self):
        if not self.selected_nip:
            messagebox.showwarning("Peringatan", "Pilih baris dosen yang ingin dihapus!")
            return
        nip = self.selected_nip
        if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus dosen dengan NIP {nip}?"):
            self.execute_change("DELETE FROM dosen WHERE nip=%s", (nip,),
                                "Data dosen berhasil dihapus!")

    def logout(self):
        self.user = None
        self.show_login()


if __name__ == "__main__":
    root = tk.Tk()
    app = SiakadApp(root)
    root.mainloop()
