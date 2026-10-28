import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation
import mysql.connector

# Konfigurasi database SIAKAD
DB_CONFIG = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'siakad'}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

class SIAKAD:
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
        self.root.title('Login - SIAKAD')
        self.root.geometry('380x250')
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        frame = tk.Frame(self.root, bg='#f0f0f0')
        frame.pack(expand=True, padx=20, pady=20)
        tk.Label(frame, text='SIAKAD LOGIN', font=('Arial', 14, 'bold'), bg='#f0f0f0').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        tk.Label(frame, text='Username:', bg='#f0f0f0').grid(row=1, column=0, padx=5, pady=6, sticky='e')
        self.login_nip = tk.Entry(frame, width=24)
        self.login_nip.grid(row=1, column=1, padx=5, pady=6)
        tk.Label(frame, text='Password:', bg='#f0f0f0').grid(row=2, column=0, padx=5, pady=6, sticky='e')
        self.login_email = tk.Entry(frame, width=24, show='*')
        self.login_email.grid(row=2, column=1, padx=5, pady=6)
        tk.Button(frame, text='Login', width=15, bg='#4CAF50', fg='white', command=self.proses_login).grid(row=3, column=0, columnspan=2, pady=20)
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
        except mysql.connector.Error as e:
            messagebox.showerror('Database Error', str(e))
            return
        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()
        if user:
            self.user = user
            messagebox.showinfo('Berhasil', f"Login berhasil!\nSelamat datang, {user['nama_dosen']}.")
            self.show_crud()
        else:
            messagebox.showerror('Gagal', 'Login gagal! Username atau Password salah.')

    def show_crud(self):
        self.reset_window()
        self.root.title('Aplikasi Data KRS - SIAKAD')
        self.root.geometry('1050x550')
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        top = tk.Frame(self.root, bg='#f0f0f0')
        top.pack(fill='x', padx=15, pady=(10, 0))
        tk.Label(top, text=f"Data KRS | Login: {self.user['nama_dosen']}", bg='#f0f0f0', font=('Arial', 11, 'bold')).pack(side='left')
        tk.Button(top, text='Logout', command=self.logout, bg='#607D8B', fg='white', width=12).pack(side='right')

        form = tk.LabelFrame(self.root, text=' Form Data KRS ', padx=10, pady=10)
        form.pack(fill='x', padx=15, pady=10)
        labels = ['ID KRS', 'NIM', 'Kode MK', 'Semester Ambil', 'Tahun Ajaran', 'Nilai Huruf', 'Nilai Angka']
        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i // 2, column=(i % 2) * 2, sticky='w', padx=5, pady=5)
        self.fields = {}
        self.fields['id_krs'] = tk.Entry(form, state='readonly')
        self.fields['nim'] = tk.Entry(form)
        self.fields['kode_mk'] = tk.Entry(form)
        self.fields['semester_ambil'] = ttk.Combobox(form, values=[str(i) for i in range(1, 15)], state='readonly')
        self.fields['tahun_ajaran'] = tk.Entry(form)
        self.fields['nilai_huruf'] = ttk.Combobox(form, values=['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'D', 'E'], state='readonly')
        self.fields['nilai_angka'] = tk.Entry(form)
        self.columns = tuple(self.fields.keys())
        for i, key in enumerate(self.columns):
            self.fields[key].grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=5, sticky='ew')
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)

        buttons = tk.Frame(self.root)
        buttons.pack(fill='x', padx=15, pady=5)
        for label, color, callback in [('Tambah', '#4CAF50', self.tambah_data), ('Edit', '#2196F3', self.edit_data), ('Hapus', '#f44336', self.hapus_data), ('Clear', '#9E9E9E', self.clear_fields), ('Refresh', '#607D8B', self.load_data)]:
            tk.Button(buttons, text=label, bg=color, fg='white', command=callback, width=12).pack(side='left', padx=5)

        table_frame = tk.Frame(self.root)
        table_frame.pack(fill='both', expand=True, padx=15, pady=10)
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show='headings')
        widths = [65, 110, 100, 120, 130, 100, 100]
        for key, label, width in zip(self.columns, labels, widths):
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor='center')
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        self.load_data()

    def logout(self):
        self.user = None
        self.show_login()

    def clear_fields(self, batalkan_pilihan=True):
        for key, entry in self.fields.items():
            if key == 'id_krs':
                entry.configure(state='normal')
            if isinstance(entry, ttk.Combobox):
                entry.set('')
            else:
                entry.delete(0, tk.END)
            if key == 'id_krs':
                entry.configure(state='readonly')
        if batalkan_pilihan:
            for item in self.tree.selection():
                self.tree.selection_remove(item)

    def select_item(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], 'values')
        self.clear_fields(batalkan_pilihan=False)
        for key, value in zip(self.columns, values):
            field = self.fields[key]
            if key == 'id_krs':
                field.configure(state='normal')
            if isinstance(field, ttk.Combobox):
                field.set(value)
            else:
                field.insert(0, value)
            if key == 'id_krs':
                field.configure(state='readonly')

    def ambil_form(self):
        nim = self.fields['nim'].get().strip()
        kode = self.fields['kode_mk'].get().strip()
        semester = self.fields['semester_ambil'].get().strip()
        tahun = self.fields['tahun_ajaran'].get().strip()
        huruf = self.fields['nilai_huruf'].get().strip()
        angka = self.fields['nilai_angka'].get().strip()
        if not all((nim, kode, semester, tahun, huruf, angka)):
            messagebox.showwarning('Validasi', 'Semua kolom wajib diisi!')
            return None
        try:
            semester_int = int(semester)
            angka_decimal = Decimal(angka)
            if not 1 <= semester_int <= 14:
                raise ValueError('Semester harus antara 1 dan 14')
            if not angka_decimal.is_finite() or not Decimal('0') <= angka_decimal <= Decimal('4'):
                raise ValueError('Nilai angka harus antara 0 dan 4')
        except (ValueError, InvalidOperation) as e:
            messagebox.showwarning('Validasi', f'Semester atau nilai angka tidak valid: {e}')
            return None
        return (nim, kode, semester_int, tahun, huruf, angka_decimal)

    def load_data(self):
        db = None
        cursor = None
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute('SELECT id_krs, nim, kode_mk, semester_ambil, tahun_ajaran, nilai_huruf, nilai_angka FROM krs ORDER BY id_krs')
            rows = cursor.fetchall()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert('', 'end', values=row)
        except mysql.connector.Error as e:
            messagebox.showerror('Database Error', f'Gagal mengambil data: {e}')
        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()

    def jalankan_query(self, sql, params, pesan):
        db = None
        cursor = None
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute(sql, params)
            db.commit()
            if cursor.rowcount == 0:
                messagebox.showwarning('Informasi', 'Tidak ada data yang berubah.')
            else:
                messagebox.showinfo('Sukses', pesan)
            self.clear_fields()
            self.load_data()
        except mysql.connector.Error as e:
            if db:
                db.rollback()
            messagebox.showerror('Database Error', f'Operasi gagal: {e}')
        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()

    def tambah_data(self):
        data = self.ambil_form()
        if data is not None:
            self.jalankan_query('INSERT INTO krs (nim, kode_mk, semester_ambil, tahun_ajaran, nilai_huruf, nilai_angka) VALUES (%s, %s, %s, %s, %s, %s)', data, 'Data KRS berhasil ditambahkan!')

    def edit_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Warning', 'Pilih data KRS yang ingin diubah!')
            return
        data = self.ambil_form()
        if data is not None:
            id_krs = self.tree.item(selected[0], 'values')[0]
            self.jalankan_query('UPDATE krs SET nim=%s, kode_mk=%s, semester_ambil=%s, tahun_ajaran=%s, nilai_huruf=%s, nilai_angka=%s WHERE id_krs=%s', data + (id_krs,), 'Data KRS berhasil diperbarui!')

    def hapus_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Warning', 'Pilih data KRS yang ingin dihapus!')
            return
        id_krs = self.tree.item(selected[0], 'values')[0]
        if messagebox.askyesno('Konfirmasi', f'Yakin ingin menghapus KRS ID {id_krs}?'):
            self.jalankan_query('DELETE FROM krs WHERE id_krs=%s', (id_krs,), 'Data KRS berhasil dihapus!')

if __name__ == '__main__':
    root = tk.Tk()
    app = SIAKAD(root)
    root.mainloop()

