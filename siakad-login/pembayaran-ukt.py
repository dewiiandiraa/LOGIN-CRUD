import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from decimal import Decimal, InvalidOperation
import mysql.connector

DB_CONFIG = dict(host='localhost', user='root', password='', database='siakad')


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


class Aplikasi:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.selected_id = None
        self.login_view()

    def bersihkan_jendela(self):
        self.root.unbind('<Return>')
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_view(self):
        self.bersihkan_jendela()
        self.root.title('Login - SIAKAD')
        self.root.geometry('380x250')
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        panel = tk.Frame(self.root, bg='#f0f0f0')
        panel.pack(expand=True, padx=20, pady=20)
        tk.Label(panel, text='SIAKAD LOGIN', font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=(0, 20))
        form = tk.Frame(panel, bg='#f0f0f0')
        form.pack()
        tk.Label(form, text='Username:', bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=6)
        self.login_nip = tk.Entry(form, width=24)
        self.login_nip.grid(row=0, column=1, padx=5, pady=6)
        tk.Label(form, text='Password:', bg='#f0f0f0').grid(row=1, column=0, padx=5, pady=6)
        self.login_email = tk.Entry(form, width=24, show='*')
        self.login_email.grid(row=1, column=1, padx=5, pady=6)
        tk.Button(panel, text='Login', bg='#4CAF50', fg='white', width=15, command=self.proses_login).pack(pady=18)
        self.root.bind('<Return>', lambda event: self.proses_login())
        self.login_nip.focus_set()

    def proses_login(self):
        nip = self.login_nip.get().strip()
        email = self.login_email.get().strip()
        if not nip or not email:
            messagebox.showwarning('Validasi', 'Username (NIP) dan Password (Email) wajib diisi!')
            return
        db = None
        cursor = None
        try:
            db = connect_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute('SELECT nip, nama_dosen FROM dosen WHERE nip=%s AND email=%s', (nip, email))
            user = cursor.fetchone()
            if user is None:
                messagebox.showerror('Gagal', 'Username atau Password salah.')
                return
            self.user = user
            messagebox.showinfo('Berhasil', f"Login berhasil!\nSelamat datang, {user['nama_dosen']}.")
            self.crud_view()
        except mysql.connector.Error as e:
            messagebox.showerror('Database Error', str(e))
        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()

    def crud_view(self):
        self.bersihkan_jendela()
        self.root.title('Aplikasi Data Pembayaran UKT - SIAKAD')
        self.root.geometry('1120x570')
        self.root.resizable(True, True)
        self.selected_id = None
        header = tk.Frame(self.root)
        header.pack(fill='x', padx=15, pady=(10, 0))
        tk.Label(header, text=f"Pembayaran UKT | {self.user['nama_dosen']}", font=('Arial', 12, 'bold')).pack(side='left')
        tk.Button(header, text='Logout', command=self.login_view, bg='#d9534f', fg='white').pack(side='right')
        form = tk.LabelFrame(self.root, text=' Form Data Pembayaran UKT ', padx=10, pady=10)
        form.pack(fill='x', padx=15, pady=10)
        fields = ['ID Pembayaran', 'NIM', 'Semester', 'Tahun Ajaran', 'Jumlah Bayar',
                  'Tanggal Bayar (YYYY-MM-DD)', 'Metode Pembayaran', 'Status']
        for i, title in enumerate(fields):
            tk.Label(form, text=title).grid(row=i // 2, column=(i % 2) * 2, sticky='w', padx=5, pady=5)
        self.entries = {}
        widgets = [
            tk.Entry(form, state='readonly'),
            tk.Entry(form),
            ttk.Combobox(form, values=[str(i) for i in range(1, 15)], state='readonly'),
            tk.Entry(form), tk.Entry(form), tk.Entry(form),
            ttk.Combobox(form, values=['Transfer Bank', 'Virtual Account', 'Tunai'], state='readonly'),
            ttk.Combobox(form, values=['Lunas', 'Belum Lunas'], state='readonly')
        ]
        for i, widget in enumerate(widgets):
            widget.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky='ew', padx=5, pady=5)
            self.entries[fields[i]] = widget
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)
        buttons = tk.Frame(self.root)
        buttons.pack(fill='x', padx=15, pady=5)
        for label, color, action in [
            ('Tambah', '#4CAF50', self.tambah_data), ('Edit', '#2196F3', self.edit_data),
            ('Hapus', '#f44336', self.hapus_data), ('Clear', '#9E9E9E', self.clear_fields),
            ('Refresh', '#607D8B', self.load_data)
        ]:
            tk.Button(buttons, text=label, bg=color, fg='white', width=12, command=action).pack(side='left', padx=5)
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill='both', expand=True, padx=15, pady=10)
        self.columns = ('id_pembayaran', 'nim', 'semester', 'tahun_ajaran', 'jumlah_bayar',
                        'tanggal_bayar', 'metode_pembayaran', 'status')
        headings = ['ID Pembayaran', 'NIM', 'Semester', 'Tahun Ajaran', 'Jumlah Bayar',
                    'Tanggal Bayar', 'Metode Pembayaran', 'Status']
        widths = [110, 100, 75, 110, 120, 115, 150, 110]
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show='headings')
        for col, title, width in zip(self.columns, headings, widths):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, minwidth=70)
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        sy = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        sx = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        sy.grid(row=0, column=1, sticky='ns')
        sx.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        self.load_data()

    def load_data(self):
        db = cursor = None
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute('''SELECT id_pembayaran, nim, semester, tahun_ajaran,
                              jumlah_bayar, tanggal_bayar, metode_pembayaran, status
                              FROM pembayaran_ukt ORDER BY id_pembayaran''')
            rows = cursor.fetchall()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert('', 'end', values=['' if v is None else str(v) for v in row])
        except mysql.connector.Error as e:
            messagebox.showerror('Database Error', f'Gagal mengambil data: {e}')
        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()

    def ambil_input(self):
        get = lambda name: self.entries[name].get().strip()
        nim, semester, tahun = get('NIM'), get('Semester'), get('Tahun Ajaran')
        jumlah, tanggal = get('Jumlah Bayar'), get('Tanggal Bayar (YYYY-MM-DD)')
        metode, status = get('Metode Pembayaran'), get('Status')
        if not all([nim, semester, tahun, jumlah, status]):
            raise ValueError('NIM, Semester, Tahun Ajaran, Jumlah Bayar, dan Status wajib diisi!')
        if not semester.isdigit() or not 1 <= int(semester) <= 14:
            raise ValueError('Semester harus antara 1 sampai 14.')
        try:
            nominal = Decimal(jumlah)
            if not nominal.is_finite() or nominal < 0 or nominal.as_tuple().exponent < -2:
                raise ValueError
        except (InvalidOperation, ValueError):
            raise ValueError('Jumlah Bayar harus angka tidak negatif dengan maksimal 2 desimal.')
        if tanggal:
            try:
                datetime.strptime(tanggal, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Tanggal harus valid dengan format YYYY-MM-DD.')
        if status == 'Lunas' and (not tanggal or not metode):
            raise ValueError('Pembayaran Lunas harus memiliki tanggal dan metode pembayaran.')
        return (nim, int(semester), tahun, nominal, tanggal or None, metode or None, status)

    def jalankan_query(self, sql, params, success):
        db = cursor = None
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute(sql, params)
            count = cursor.rowcount
            db.commit()
            if count:
                messagebox.showinfo('Sukses', success)
            else:
                messagebox.showinfo('Informasi', 'Tidak ada data yang berubah atau ditemukan.')
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
        try:
            data = self.ambil_input()
        except ValueError as e:
            messagebox.showwarning('Validasi', str(e))
            return
        self.jalankan_query('''INSERT INTO pembayaran_ukt
            (nim, semester, tahun_ajaran, jumlah_bayar, tanggal_bayar, metode_pembayaran, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)''', data, 'Data pembayaran berhasil ditambahkan!')

    def edit_data(self):
        if self.selected_id is None:
            messagebox.showwarning('Peringatan', 'Pilih data yang ingin diedit!')
            return
        try:
            data = self.ambil_input()
        except ValueError as e:
            messagebox.showwarning('Validasi', str(e))
            return
        self.jalankan_query('''UPDATE pembayaran_ukt SET nim=%s, semester=%s, tahun_ajaran=%s,
            jumlah_bayar=%s, tanggal_bayar=%s, metode_pembayaran=%s, status=%s
            WHERE id_pembayaran=%s''', data + (self.selected_id,), 'Data pembayaran berhasil diperbarui!')

    def hapus_data(self):
        if self.selected_id is None:
            messagebox.showwarning('Peringatan', 'Pilih data yang ingin dihapus!')
            return
        if messagebox.askyesno('Konfirmasi', f'Yakin menghapus pembayaran ID {self.selected_id}?'):
            self.jalankan_query('DELETE FROM pembayaran_ukt WHERE id_pembayaran=%s',
                                (self.selected_id,), 'Data pembayaran berhasil dihapus!')

    def select_item(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], 'values')
        self.selected_id = int(values[0])
        fields = ['ID Pembayaran', 'NIM', 'Semester', 'Tahun Ajaran', 'Jumlah Bayar',
                  'Tanggal Bayar (YYYY-MM-DD)', 'Metode Pembayaran', 'Status']
        for name, value in zip(fields, values):
            widget = self.entries[name]
            if name == 'ID Pembayaran':
                widget.config(state='normal')
            if isinstance(widget, ttk.Combobox):
                widget.set(value)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, value)
            if name == 'ID Pembayaran':
                widget.config(state='readonly')

    def clear_fields(self):
        self.selected_id = None
        for name, widget in self.entries.items():
            if name == 'ID Pembayaran':
                widget.config(state='normal')
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            else:
                widget.delete(0, tk.END)
            if name == 'ID Pembayaran':
                widget.config(state='readonly')
        for item in self.tree.selection():
            self.tree.selection_remove(item)


if __name__ == '__main__':
    root = tk.Tk()
    Aplikasi(root)
    root.mainloop()
