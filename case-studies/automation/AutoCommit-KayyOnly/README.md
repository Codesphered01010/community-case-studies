# AutoCommit (CARA PENGGUNAAN CEK DI REPO ASLI)

> **Part of [CodeSphred Community](https://github.com/Codesphered01010)**  
> *Project ini adalah salah satu hasil karya member komunitas dalam repositori [Community Case Studies](https://github.com/Codesphered01010/community-case-studies).*

---

> **AutoCommit** adalah tools berbasis GUI (Tkinter) yang secara otomatis menghasilkan commit history pada repository Git lokal dengan timestamp yang didistribusikan secara acak dalam rentang 1 tahun terakhir. Tujuannya untuk membantu mengisi **GitHub Contribution Graph** dengan aktivitas commit yang terlihat natural. Cocok untuk personal testing, portfolio, atau eksperimen dengan Git history.

## Author
- **KayyOnly** - Solo Developer / Creator - [GitHub](https://github.com/KayyOnly)

## Tech Stack
*Tools ini dibangun dengan stack yang minimalis dan tidak memerlukan dependencies eksternal:*
- **Python 3.7+** — Bahasa utama
- **Tkinter** — GUI framework (built-in Python)
- **Git CLI** — Untuk operasi add, commit, dan push
- **Subprocess, OS, Random, Datetime** — Standard library Python

## Architecture / System Design
Aplikasi ini berjalan sebagai desktop GUI yang berinteraksi langsung dengan Git CLI melalui subprocess:

- **GUI Layer (Tkinter):** Menyediakan form input (jumlah commit, path repo, filename, message) dan menampilkan progress bar serta activity log.
- **Logic Layer:** Menghasilkan tanggal & waktu acak dalam 365 hari terakhir menggunakan `random` dan `datetime`.
- **Git Integration Layer:** Menulis ke file target, menjalankan `git add`, `git commit` dengan environment variable `GIT_AUTHOR_DATE` dan `GIT_COMMITTER_DATE` untuk memanipulasi timestamp, serta opsional `git push` ke remote.
- **Threading:** Proses pembuatan commit berjalan di background thread agar UI tetap responsif.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  User Input │ --> │  Random Date │ --> │  Git Add/Commit │
│   (GUI)     │     │   Generator  │     │   (Subprocess)  │
└─────────────┘     └──────────────┘     └─────────────────┘
                                                │
                                                v
                                         ┌──────────────┐
                                         │  Git Push    │
                                         │  (Optional)  │
                                         └──────────────┘
```

## Features
- [x] **GUI Modern Dark Theme** — Tampilan elegan dengan warna ala GitHub dark mode (`#0d1117` & hijau contribution)
- [x] **Random Date Distribution** — Commit tersebar acak dalam 365 hari terakhir agar terlihat natural
- [x] **Browse Folder** — Pilih repository dengan file picker (tidak perlu ketik path manual)
- [x] **Progress Bar Real-time** — Pantau proses pembuatan commit secara visual
- [x] **Activity Log** — Lihat status setiap commit (success/fail) dengan timestamp
- [x] **Auto Push** — Opsi push otomatis ke remote setelah semua commit selesai dibuat
- [x] **Non-blocking UI** — Proses berjalan di background thread, GUI tidak freeze
- [x] **Validasi Repository** — Cek otomatis apakah folder yang dipilih adalah repository Git yang valid
- [x] **Custom Commit Message** — Atur pesan commit sesuai keinginan
- [x] **No External Dependencies** — Hanya pakai standard library Python + Tkinter

## Challenges & Learnings
- **Tantangan:** Awalnya proses pembuatan commit membuat UI freeze karena berjalan di main thread. Pengguna tidak bisa melihat progress secara real-time dan mengira aplikasi crash.
- **Solusi/Pelajaran:** Menerapkan `threading.Thread` dengan `daemon=True` untuk menjalankan proses commit di background. Belajar cara update UI (progress bar & log) dari thread lain menggunakan `root.update_idletasks()` dan thread-safe approach di Tkinter.
- **Tantangan:** Manipulasi tanggal commit agar muncul di GitHub Contribution Graph memerlukan pemahaman tentang `GIT_AUTHOR_DATE` dan `GIT_COMMITTER_DATE` environment variables, bukan hanya `--date` flag.
- **Solusi/Pelajaran:** Mengetahui bahwa GitHub menggunakan author date untuk contribution graph, sehingga perlu set kedua environment variable tersebut sebelum menjalankan `git commit` via subprocess.

## Impact / Results
- Berhasil mengotomatisasi pembuatan 20–100+ commit dalam hitungan detik yang sebelumnya harus dilakukan manual satu per satu.
- Tools ini murni personal project untuk eksperimen dengan Git internals dan Tkinter GUI development.

## Screenshot
*Tambahkan screenshot atau GIF dari projectmu agar member lain bisa melihat hasilnya!*

```
┌─────────────────────────────────────────────┐
│  🌱 AutoCommit                              │
│  GitHub Contribution Graph Commit Generator  │
│  by KayyOnly                                │
├─────────────────────────────────────────────┤
│  Number of Commits: [20        ]            │
│  Repository Path:   [/path/to/repo] [Browse]│
│  Target Filename:   [data.txt   ]            │
│  Commit Message:    [graph-greener!]         │
│  [✓] Push to remote after committing        │
├─────────────────────────────────────────────┤
│  [🚀 Generate Commits] [🧹 Clear] [❌ Exit] │
│  [===================>    ] 15/20...         │
├─────────────────────────────────────────────┤
│  Activity Log:                              │
│  [1/20] ✅ 2025-08-14 09:23:17              │
│  [2/20] ✅ 2025-03-02 14:55:42              │
│  ...                                        │
├─────────────────────────────────────────────┤
│            Made with 💚 by KayyOnly         │
└─────────────────────────────────────────────┘
```

## Demo / Repository Link
- **Live Demo:** *Desktop app, tidak tersedia live demo* (Opsional)
- **Original Repo:** [https://github.com/Kayyonly/GraphGreener_Tools] (Opsional)
- **Figma:** *Tidak menggunakan desain Figma, UI native Tkinter* (Opsional)

## License
Project ini berada di bawah lisensi **MIT**.

> ⚠️ **Disclaimer:** Tools ini dibuat untuk educational purposes dan personal testing. Penggunaan untuk memanipulasi GitHub Contribution Graph secara massal dapat melanggar Terms of Service GitHub. Gunakan dengan bijak dan tanggung jawab sendiri.

---

<p align="center">
  <sub>Made with 💚 by KayyOnly</sub>
</p>
