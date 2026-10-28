import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'siakad'
}


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


class SiakadApp:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.show_login()

    def reset_window(self):
        self.root.unbind('<Return>')
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.reset_window()
        self.user = None
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
        self.login_nip = tk.Entry(form, width=24)
        self.login_nip.grid(row=0, column=1, padx=5, pady=6)
        tk.Label(form, text='Password:', bg='#f0f0f0', width=10, anchor='e').grid(row=1, column=0, padx=5, pady=6)
        self.login_email = tk.Entry(form, width=24, show='*')
        self.login_email.grid(row=1, column=1, padx=5, pady=6)
        tk.Button(main, text='Login', bg='#4CAF50', fg='white', width=15,
                  command=self.proses_login).pack(pady=(20, 0))
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
        except mysql.connector.Error as err:
            messagebox.showerror('Database Error', f'Koneksi atau query bermasalah:\n{err}')
            return
        finally:
            if cursor is not None:
                cursor.close()
            if db is not None and db.is_connected():
                db.close()
        if user is None:
            messagebox.showerror('Gagal', 'Login gagal! NIP atau Email salah.')
            return
        self.user = user
        messagebox.showinfo('Berhasil', f"Login berhasil!\nSelamat datang, {user['nama_dosen']}.")
        self.show_jadwal()

    def show_jadwal(self):
        self.reset_window()
        self.root.title('Aplikasi Data Jadwal Kuliah - SIAKAD')
        self.root.geometry('950x560')
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')

        top = tk.Frame(self.root, bg='#f0f0f0')
        top.pack(fill='x', padx=15, pady=(10, 0))
        tk.Label(top, text=f"Login sebagai: {self.user['nama_dosen']}", bg='#f0f0f0',
                 font=('Arial', 10, 'bold')).pack(side='left')
        tk.Button(top, text='Logout', command=self.show_login, bg='#777777',
                  fg='white', width=12).pack(side='right')

        frame_form = tk.LabelFrame(self.root, text=' Form Data Jadwal ', padx=10, pady=10)
        frame_form.pack(fill='x', padx=15, pady=10)
        labels = ['ID Jadwal', 'Kode MK', 'Hari', 'Jam Mulai', 'Jam Selesai', 'Ruangan']
        for i, label in enumerate(labels):
            tk.Label(frame_form, text=label).grid(row=i//2, column=(i%2)*2,
                                                   sticky='w', padx=5, pady=6)
        self.entry_id = tk.Entry(frame_form, state='readonly')
        self.entry_kode = tk.Entry(frame_form)
        self.combo_hari = ttk.Combobox(frame_form,
                                      values=['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'],
                                      state='readonly')
        self.entry_mulai = tk.Entry(frame_form)
        self.entry_selesai = tk.Entry(frame_form)
        self.entry_ruangan = tk.Entry(frame_form)
        for i, widget in enumerate([self.entry_id, self.entry_kode, self.combo_hari,
                                    self.entry_mulai, self.entry_selesai, self.entry_ruangan]):
            widget.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=6, sticky='ew')
        frame_form.grid_columnconfigure(1, weight=1)
        frame_form.grid_columnconfigure(3, weight=1)

        buttons = tk.Frame(self.root)
        buttons.pack(fill='x', padx=15, pady=5)
        for title, color, callback in [
            ('Tambah', '#4CAF50', self.tambah_data),
            ('Edit', '#2196F3', self.edit_data),
            ('Hapus', '#f44336', self.hapus_data),
            ('Clear', '#9E9E9E', self.clear_fields),
            ('Refresh', '#607D8B', self.load_data),
        ]:
            tk.Button(buttons, text=title, bg=color, fg='white', command=callback,
                      width=12).pack(side='left', padx=5)

        frame_table = tk.Frame(self.root)
        frame_table.pack(fill='both', expand=True, padx=15, pady=10)
        columns = ('id_jadwal', 'kode_mk', 'hari', 'jam_mulai', 'jam_selesai', 'ruangan')
        headings = ['ID Jadwal', 'Kode MK', 'Hari', 'Jam Mulai', 'Jam Selesai', 'Ruangan']
        widths = [80, 110, 100, 120, 120, 160]
        self.tree = ttk.Treeview(frame_table, columns=columns, show='headings')
        for col, heading, width in zip(columns, headings, widths):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        scrollbar = ttk.Scrollbar(frame_table, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.load_data()

    def load_data(self):
        db = None
        cursor = None
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute('SELECT id_jadwal, kode_mk, hari, jam_mulai, jam_selesai, ruangan '
                           'FROM jadwal_kuliah ORDER BY id_jadwal')
            rows = cursor.fetchall()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert('', 'end', values=tuple('' if v is None else str(v) for v in row))
        except mysql.connector.Error as err:
            messagebox.showerror('Database Error', f'Gagal mengambil data: {err}')
        finally:
            if cursor is not None:
                cursor.close()
            if db is not None and db.is_connected():
                db.close()

    def get_form_data(self):
        data = (self.entry_kode.get().strip(), self.combo_hari.get().strip(),
                self.entry_mulai.get().strip(), self.entry_selesai.get().strip(),
                self.entry_ruangan.get().strip())
        if not all(data):
            messagebox.showwarning('Validasi', 'Semua kolom selain ID Jadwal wajib diisi!')
            return None
        try:
            mulai = datetime.strptime(data[2], '%H:%M:%S').time()
            selesai = datetime.strptime(data[3], '%H:%M:%S').time()
        except ValueError:
            messagebox.showwarning('Validasi', 'Gunakan format jam HH:MM:SS, contoh 08:00:00')
            return None
        if mulai >= selesai:
            messagebox.showwarning('Validasi', 'Jam selesai harus lebih besar dari jam mulai!')
            return None
        return data

    def execute_change(self, sql, params, success_message):
        db = None
        cursor = None
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute(sql, params)
            if cursor.rowcount == 0:
                db.rollback()
                messagebox.showwarning('Tidak ditemukan', 'Tidak ada data yang berubah. Periksa ID jadwal.')
                return
            db.commit()
            messagebox.showinfo('Sukses', success_message)
            self.clear_fields()
            self.load_data()
        except mysql.connector.Error as err:
            if db is not None:
                db.rollback()
            messagebox.showerror('Database Error', str(err))
        finally:
            if cursor is not None:
                cursor.close()
            if db is not None and db.is_connected():
                db.close()

    def tambah_data(self):
        data = self.get_form_data()
        if data is not None:
            self.execute_change(
                'INSERT INTO jadwal_kuliah (kode_mk, hari, jam_mulai, jam_selesai, ruangan) '
                'VALUES (%s, %s, %s, %s, %s)', data, 'Data jadwal berhasil ditambahkan!')

    def edit_data(self):
        id_jadwal = self.entry_id.get().strip()
        if not id_jadwal:
            messagebox.showwarning('Warning', 'Pilih jadwal yang ingin diubah!')
            return
        data = self.get_form_data()
        if data is not None:
            self.execute_change(
                'UPDATE jadwal_kuliah SET kode_mk=%s, hari=%s, jam_mulai=%s, '
                'jam_selesai=%s, ruangan=%s WHERE id_jadwal=%s',
                data + (id_jadwal,), 'Data jadwal berhasil diperbarui!')

    def hapus_data(self):
        id_jadwal = self.entry_id.get().strip()
        if not id_jadwal:
            messagebox.showwarning('Warning', 'Pilih jadwal yang ingin dihapus!')
            return
        if messagebox.askyesno('Konfirmasi', f'Yakin ingin menghapus jadwal ID {id_jadwal}?'):
            self.execute_change('DELETE FROM jadwal_kuliah WHERE id_jadwal=%s',
                                (id_jadwal,), 'Data jadwal berhasil dihapus!')

    def select_item(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], 'values')
        self.clear_fields()
        self.entry_id.config(state='normal')
        self.entry_id.insert(0, values[0])
        self.entry_id.config(state='readonly')
        self.entry_kode.insert(0, values[1])
        self.combo_hari.set(values[2])
        self.entry_mulai.insert(0, values[3])
        self.entry_selesai.insert(0, values[4])
        self.entry_ruangan.insert(0, values[5])
        self.tree.selection_set(selected[0])

    def clear_fields(self):
        self.entry_id.config(state='normal')
        self.entry_id.delete(0, tk.END)
        self.entry_id.config(state='readonly')
        self.entry_kode.delete(0, tk.END)
        self.combo_hari.set('')
        self.entry_mulai.delete(0, tk.END)
        self.entry_selesai.delete(0, tk.END)
        self.entry_ruangan.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)


if __name__ == '__main__':
    root = tk.Tk()
    app = SiakadApp(root)
    root.mainloop()
