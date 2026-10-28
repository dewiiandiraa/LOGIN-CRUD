import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

DB_CONFIG = dict(host='localhost', user='root', password='', database='siakad')
COLUMNS = ('kode_mk', 'nama_mk', 'sks', 'semester', 'nip_dosen')


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


class SiakadApp:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.entries = []
        self.show_login()

    def reset_window(self):
        self.root.unbind('<Return>')
        for child in self.root.winfo_children():
            child.destroy()

    def show_login(self):
        self.reset_window()
        self.root.title('Login - SIAKAD')
        self.root.geometry('380x250')
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        main = tk.Frame(self.root, bg='#f0f0f0')
        main.pack(expand=True, fill='both', padx=20, pady=20)
        tk.Label(main, text='SIAKAD LOGIN', font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=(0, 20))
        form = tk.Frame(main, bg='#f0f0f0')
        form.pack()
        tk.Label(form, text='Username:', bg='#f0f0f0', width=10, anchor='e').grid(row=0, column=0, padx=5, pady=6)
        self.login_nip = tk.Entry(form, width=22)
        self.login_nip.grid(row=0, column=1, padx=5, pady=6)
        tk.Label(form, text='Password:', bg='#f0f0f0', width=10, anchor='e').grid(row=1, column=0, padx=5, pady=6)
        self.login_email = tk.Entry(form, width=22, show='*')
        self.login_email.grid(row=1, column=1, padx=5, pady=6)
        tk.Button(main, text='Login', bg='#4CAF50', fg='white', width=15, command=self.proses_login).pack(pady=(20, 0))
        self.root.bind('<Return>', lambda event: self.proses_login())
        self.login_nip.focus_set()

    def proses_login(self):
        nip = self.login_nip.get().strip()
        email = self.login_email.get().strip()
        if not nip or not email:
            messagebox.showwarning('Peringatan', 'Username (NIP) dan Password (Email) wajib diisi!')
            return
        db = None
        cursor = None
        try:
            db = connect_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute('SELECT nip, nama_dosen, email FROM dosen WHERE nip=%s AND email=%s', (nip, email))
            user = cursor.fetchone()
            if not user:
                messagebox.showerror('Gagal', 'Login gagal! Username atau Password salah.')
                return
            self.user = user
            messagebox.showinfo('Berhasil', f"Login berhasil!\nSelamat datang, {user['nama_dosen']}.")
            self.show_crud()
        except mysql.connector.Error as err:
            messagebox.showerror('Database Error', f'Koneksi database bermasalah:\n{err}')
        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()

    def show_crud(self):
        self.reset_window()
        self.root.title('Aplikasi Data Mata Kuliah - SIAKAD')
        self.root.geometry('900x520')
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        header = tk.Frame(self.root, bg='#f0f0f0')
        header.pack(fill='x', padx=15, pady=(10, 0))
        tk.Label(header, text=f"Login: {self.user['nama_dosen']}", bg='#f0f0f0').pack(side='left')
        tk.Button(header, text='Logout', command=self.logout).pack(side='right')
        form = tk.LabelFrame(self.root, text=' Form Data Mata Kuliah ', padx=10, pady=10)
        form.pack(fill='x', padx=15, pady=10)
        self.entries = []
        for i, label in enumerate(['Kode MK', 'Nama Mata Kuliah', 'SKS', 'Semester', 'NIP Dosen']):
            row, col = divmod(i, 2)
            tk.Label(form, text=label).grid(row=row, column=col*2, sticky='w', padx=5, pady=5)
            entry = tk.Entry(form)
            entry.grid(row=row, column=col*2+1, sticky='ew', padx=5, pady=5)
            self.entries.append(entry)
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)
        buttons = tk.Frame(self.root)
        buttons.pack(fill='x', padx=15, pady=5)
        for label, color, callback in [
            ('Tambah', '#4CAF50', self.tambah_data),
            ('Edit', '#2196F3', self.edit_data),
            ('Hapus', '#f44336', self.hapus_data),
            ('Clear', '#9E9E9E', self.clear_fields),
            ('Refresh', '#607D8B', self.load_data),
        ]:
            tk.Button(buttons, text=label, bg=color, fg='white', width=12, command=callback).pack(side='left', padx=5)
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill='both', expand=True, padx=15, pady=10)
        self.tree = ttk.Treeview(table_frame, columns=COLUMNS, show='headings')
        for col, title, width in [
            ('kode_mk', 'Kode MK', 100), ('nama_mk', 'Nama Mata Kuliah', 270),
            ('sks', 'SKS', 70), ('semester', 'Semester', 90), ('nip_dosen', 'NIP Dosen', 110)
        ]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width)
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.load_data()

    def logout(self):
        self.user = None
        self.show_login()

    def load_data(self):
        try:
            with connect_db() as db:
                cursor = db.cursor()
                try:
                    cursor.execute('SELECT kode_mk, nama_mk, sks, semester, nip_dosen FROM mata_kuliah ORDER BY kode_mk')
                    rows = cursor.fetchall()
                finally:
                    cursor.close()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror('Database Error', f'Gagal mengambil data: {err}')

    def ambil_form(self):
        data = tuple(entry.get().strip() for entry in self.entries)
        if not all(data):
            messagebox.showwarning('Validasi', 'Semua kolom wajib diisi!')
            return None
        try:
            sks, semester = int(data[2]), int(data[3])
            if sks <= 0 or semester <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning('Validasi', 'SKS dan Semester harus berupa bilangan bulat positif!')
            return None
        return (data[0], data[1], sks, semester, data[4])

    def run_query(self, sql, params, success):
        db = None
        cursor = None
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute(sql, params)
            affected = cursor.rowcount
            db.commit()
            if affected:
                messagebox.showinfo('Sukses', success)
            else:
                messagebox.showwarning('Informasi', 'Tidak ada data yang berubah.')
            self.clear_fields()
            self.load_data()
        except mysql.connector.Error as err:
            if db:
                db.rollback()
            messagebox.showerror('Database Error', f'Operasi gagal: {err}')
        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()

    def tambah_data(self):
        data = self.ambil_form()
        if data is not None:
            self.run_query('INSERT INTO mata_kuliah (kode_mk, nama_mk, sks, semester, nip_dosen) VALUES (%s,%s,%s,%s,%s)', data, 'Data mata kuliah berhasil ditambahkan!')

    def edit_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Warning', 'Pilih mata kuliah yang ingin diubah!')
            return
        data = self.ambil_form()
        if data is not None:
            kode_lama = self.tree.item(selected[0], 'values')[0]
            self.run_query('UPDATE mata_kuliah SET kode_mk=%s, nama_mk=%s, sks=%s, semester=%s, nip_dosen=%s WHERE kode_mk=%s', data + (kode_lama,), 'Data mata kuliah berhasil diperbarui!')

    def hapus_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Warning', 'Pilih mata kuliah yang ingin dihapus!')
            return
        kode = self.tree.item(selected[0], 'values')[0]
        if messagebox.askyesno('Konfirmasi', f'Yakin ingin menghapus mata kuliah {kode}?'):
            self.run_query('DELETE FROM mata_kuliah WHERE kode_mk=%s', (kode,), 'Data mata kuliah berhasil dihapus!')

    def select_item(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], 'values')
        for entry, value in zip(self.entries, values):
            entry.delete(0, tk.END)
            entry.insert(0, value)

    def clear_fields(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)


if __name__ == '__main__':
    root = tk.Tk()
    SiakadApp(root)
    root.mainloop()
