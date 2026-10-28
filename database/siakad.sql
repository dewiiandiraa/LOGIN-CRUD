-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 28, 2026 at 03:10 AM
-- Server version: 8.4.3
-- PHP Version: 8.3.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `siakad`
--

-- --------------------------------------------------------

--
-- Table structure for table `dosen`
--

CREATE TABLE `dosen` (
  `nip` varchar(10) NOT NULL,
  `nama_dosen` varchar(100) NOT NULL,
  `jenis_kelamin` enum('Laki-laki','Perempuan') DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `no_telepon` varchar(15) DEFAULT NULL,
  `pendidikan_terakhir` varchar(10) DEFAULT NULL,
  `bidang_keahlian` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `dosen`
--

INSERT INTO `dosen` (`nip`, `nama_dosen`, `jenis_kelamin`, `email`, `no_telepon`, `pendidikan_terakhir`, `bidang_keahlian`) VALUES
('D001', 'Dr. Hendra Wijaya, M.Kom', 'Laki-laki', 'hendra@kampus.ac.id', '081298765432', 'S3', 'Kecerdasan Buatan'),
('D002', 'Prof. Sri Mulyani, M.T', 'Perempuan', 'sri@kampus.ac.id', '081298765433', 'S3', 'Rekayasa Perangkat Lunak'),
('D003', 'Ir. Bambang Sutrisno, M.Kom', 'Laki-laki', 'bambang@kampus.ac.id', '081298765434', 'S2', 'Jaringan Komputer'),
('D004', 'Dr. Rina Marlina, M.Si', 'Perempuan', 'rina@kampus.ac.id', '081298765435', 'S3', 'Basis Data'),
('D005', 'Yusuf Hamdani, M.Kom', 'Laki-laki', 'yusuf@kampus.ac.id', '081298765436', 'S2', 'Pemrograman Web');

-- --------------------------------------------------------

--
-- Table structure for table `jadwal_kuliah`
--

CREATE TABLE `jadwal_kuliah` (
  `id_jadwal` int NOT NULL,
  `kode_mk` varchar(10) DEFAULT NULL,
  `hari` enum('Senin','Selasa','Rabu','Kamis','Jumat','Sabtu') DEFAULT NULL,
  `jam_mulai` time DEFAULT NULL,
  `jam_selesai` time DEFAULT NULL,
  `ruangan` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `jadwal_kuliah`
--

INSERT INTO `jadwal_kuliah` (`id_jadwal`, `kode_mk`, `hari`, `jam_mulai`, `jam_selesai`, `ruangan`) VALUES
(1, 'MK001', 'Senin', '08:00:00', '10:30:00', 'Ruang A101'),
(2, 'MK002', 'Selasa', '10:30:00', '13:00:00', 'Ruang B202'),
(3, 'MK003', 'Rabu', '13:00:00', '15:30:00', 'Lab Komputer 1'),
(4, 'MK004', 'Kamis', '08:00:00', '10:30:00', 'Lab Jaringan'),
(5, 'MK005', 'Jumat', '08:00:00', '10:30:00', 'Ruang C303'),
(6, 'MK006', 'Sabtu', '09:00:00', '11:30:00', 'Ruang A102');

-- --------------------------------------------------------

--
-- Table structure for table `krs`
--

CREATE TABLE `krs` (
  `id_krs` int NOT NULL,
  `nim` varchar(10) DEFAULT NULL,
  `kode_mk` varchar(10) DEFAULT NULL,
  `semester_ambil` int DEFAULT NULL,
  `tahun_ajaran` varchar(10) DEFAULT NULL,
  `nilai_huruf` char(2) DEFAULT NULL,
  `nilai_angka` decimal(4,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `krs`
--

INSERT INTO `krs` (`id_krs`, `nim`, `kode_mk`, `semester_ambil`, `tahun_ajaran`, `nilai_huruf`, `nilai_angka`) VALUES
(1, '2021001', 'MK001', 1, '2021/2022', 'A', 4.00),
(2, '2021001', 'MK002', 3, '2022/2023', 'A-', 3.75),
(3, '2021002', 'MK001', 1, '2021/2022', 'B+', 3.30),
(4, '2022003', 'MK003', 4, '2023/2024', 'A', 4.00),
(5, '2022004', 'MK002', 3, '2023/2024', 'B', 3.00),
(6, '2023005', 'MK001', 1, '2023/2024', 'A-', 3.75);

-- --------------------------------------------------------

--
-- Table structure for table `mahasiswa`
--

CREATE TABLE `mahasiswa` (
  `nim` varchar(10) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `jenis_kelamin` enum('Laki-laki','Perempuan') NOT NULL,
  `tanggal_lahir` date NOT NULL,
  `tempat_lahir` varchar(50) DEFAULT NULL,
  `alamat` text,
  `no_telepon` varchar(15) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `jurusan` varchar(50) DEFAULT NULL,
  `angkatan` year DEFAULT NULL,
  `status` enum('Aktif','Cuti','Lulus','Drop Out') DEFAULT 'Aktif'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `mahasiswa`
--

INSERT INTO `mahasiswa` (`nim`, `nama_lengkap`, `jenis_kelamin`, `tanggal_lahir`, `tempat_lahir`, `alamat`, `no_telepon`, `email`, `jurusan`, `angkatan`, `status`) VALUES
('2021001', 'Budi Santoso', 'Laki-laki', '2003-05-12', 'Jakarta', 'Jl. Merdeka No. 10', '081234567890', 'budi@email.com', 'Teknik Informatika', '2021', 'Aktif'),
('2021002', 'Siti Nurhaliza', 'Perempuan', '2003-08-20', 'Bandung', 'Jl. Asia Afrika No. 5', '081234567891', 'siti@email.com', 'Sistem Informasi', '2021', 'Aktif'),
('2022003', 'Ahmad Fauzi', 'Laki-laki', '2004-01-15', 'Surabaya', 'Jl. Diponegoro No. 22', '081234567892', 'ahmad@email.com', 'Teknik Informatika', '2022', 'Aktif'),
('2022004', 'Dewi Lestari', 'Perempuan', '2004-03-10', 'Yogyakarta', 'Jl. Malioboro No. 8', '081234567893', 'dewi@email.com', 'Manajemen Informatika', '2022', 'Aktif'),
('2023005', 'Rizky Pratama', 'Laki-laki', '2005-07-25', 'Medan', 'Jl. Gatot Subroto No. 17', '081234567894', 'rizky@email.com', 'Sistem Informasi', '2023', 'Aktif'),
('2023006', 'Putri Ayu', 'Perempuan', '2005-11-30', 'Semarang', 'Jl. Pandanaran No. 3', '081234567895', 'putri@email.com', 'Teknik Informatika', '2023', 'Cuti'),
('202512007', 'Nurul Aisyah Zhafirah', 'Perempuan', '2006-06-16', 'Bontang', 'Jl. Arif Rahman Hakim', '0812345678', 'zzz@email.com', 'Teknik Informatika', '2025', 'Cuti'),
('202512055', 'Dewi Andira', 'Perempuan', '2006-12-04', 'Bontang', 'Jl. Brigjen Katamso No. 22', '0895327992415', 'dira@email.com', 'Teknik Informatika', '2025', 'Aktif');

-- --------------------------------------------------------

--
-- Table structure for table `mata_kuliah`
--

CREATE TABLE `mata_kuliah` (
  `kode_mk` varchar(10) NOT NULL,
  `nama_mk` varchar(100) NOT NULL,
  `sks` int NOT NULL,
  `semester` int DEFAULT NULL,
  `nip_dosen` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `mata_kuliah`
--

INSERT INTO `mata_kuliah` (`kode_mk`, `nama_mk`, `sks`, `semester`, `nip_dosen`) VALUES
('MK001', 'Algoritma dan Pemrograman', 3, 1, 'D001'),
('MK002', 'Basis Data', 3, 3, 'D004'),
('MK003', 'Pemrograman Web', 3, 4, 'D005'),
('MK004', 'Jaringan Komputer', 3, 5, 'D003'),
('MK005', 'Rekayasa Perangkat Lunak', 3, 5, 'D002'),
('MK006', 'Kecerdasan Buatan', 3, 6, 'D001');

-- --------------------------------------------------------

--
-- Table structure for table `pembayaran_ukt`
--

CREATE TABLE `pembayaran_ukt` (
  `id_pembayaran` int NOT NULL,
  `nim` varchar(10) DEFAULT NULL,
  `semester` int DEFAULT NULL,
  `tahun_ajaran` varchar(10) DEFAULT NULL,
  `jumlah_bayar` decimal(10,2) DEFAULT NULL,
  `tanggal_bayar` date DEFAULT NULL,
  `metode_pembayaran` enum('Transfer Bank','Virtual Account','Tunai') DEFAULT NULL,
  `status` enum('Lunas','Belum Lunas') DEFAULT 'Belum Lunas'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `pembayaran_ukt`
--

INSERT INTO `pembayaran_ukt` (`id_pembayaran`, `nim`, `semester`, `tahun_ajaran`, `jumlah_bayar`, `tanggal_bayar`, `metode_pembayaran`, `status`) VALUES
(1, '2021001', 1, '2021/2022', 3500000.00, '2021-08-15', 'Transfer Bank', 'Lunas'),
(2, '2021001', 3, '2022/2023', 3500000.00, '2022-08-10', 'Virtual Account', 'Lunas'),
(3, '2021002', 1, '2021/2022', 3500000.00, '2021-08-20', 'Transfer Bank', 'Lunas'),
(4, '2022003', 4, '2023/2024', 4000000.00, '2023-08-12', 'Virtual Account', 'Lunas'),
(5, '2022004', 3, '2023/2024', 3800000.00, NULL, NULL, 'Belum Lunas'),
(6, '2023005', 1, '2023/2024', 4000000.00, '2023-08-25', 'Tunai', 'Lunas');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dosen`
--
ALTER TABLE `dosen`
  ADD PRIMARY KEY (`nip`);

--
-- Indexes for table `jadwal_kuliah`
--
ALTER TABLE `jadwal_kuliah`
  ADD PRIMARY KEY (`id_jadwal`),
  ADD KEY `kode_mk` (`kode_mk`);

--
-- Indexes for table `krs`
--
ALTER TABLE `krs`
  ADD PRIMARY KEY (`id_krs`),
  ADD KEY `nim` (`nim`),
  ADD KEY `kode_mk` (`kode_mk`);

--
-- Indexes for table `mahasiswa`
--
ALTER TABLE `mahasiswa`
  ADD PRIMARY KEY (`nim`);

--
-- Indexes for table `mata_kuliah`
--
ALTER TABLE `mata_kuliah`
  ADD PRIMARY KEY (`kode_mk`),
  ADD KEY `nip_dosen` (`nip_dosen`);

--
-- Indexes for table `pembayaran_ukt`
--
ALTER TABLE `pembayaran_ukt`
  ADD PRIMARY KEY (`id_pembayaran`),
  ADD KEY `nim` (`nim`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `jadwal_kuliah`
--
ALTER TABLE `jadwal_kuliah`
  MODIFY `id_jadwal` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `krs`
--
ALTER TABLE `krs`
  MODIFY `id_krs` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `pembayaran_ukt`
--
ALTER TABLE `pembayaran_ukt`
  MODIFY `id_pembayaran` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `jadwal_kuliah`
--
ALTER TABLE `jadwal_kuliah`
  ADD CONSTRAINT `jadwal_kuliah_ibfk_1` FOREIGN KEY (`kode_mk`) REFERENCES `mata_kuliah` (`kode_mk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `krs`
--
ALTER TABLE `krs`
  ADD CONSTRAINT `krs_ibfk_1` FOREIGN KEY (`nim`) REFERENCES `mahasiswa` (`nim`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `krs_ibfk_2` FOREIGN KEY (`kode_mk`) REFERENCES `mata_kuliah` (`kode_mk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `mata_kuliah`
--
ALTER TABLE `mata_kuliah`
  ADD CONSTRAINT `mata_kuliah_ibfk_1` FOREIGN KEY (`nip_dosen`) REFERENCES `dosen` (`nip`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `pembayaran_ukt`
--
ALTER TABLE `pembayaran_ukt`
  ADD CONSTRAINT `pembayaran_ukt_ibfk_1` FOREIGN KEY (`nim`) REFERENCES `mahasiswa` (`nim`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
