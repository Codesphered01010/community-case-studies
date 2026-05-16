<div align="center">
  <img src="https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1200&q=80" alt="Contributing Banner" width="100%" height="250" style="object-fit: cover; border-radius: 10px;">

  <h1>Contributing Guidelines</h1>

  <p><em>Terima kasih sudah mau berbagi karya dengan komunitas!<br>Ikuti langkah-langkah di bawah ini untuk menambahkan projectmu ke dalam repository ini.</em></p>
</div>

---

## Langkah-langkah Upload Project

### 1. Fork & Clone
1. Klik tombol **Fork** di pojok kanan atas repository ini.
2. Clone repository hasil fork ke komputer lokalmu:
   ```bash
   git clone https://github.com/<username-kamu>/community-case-studies.git
   cd community-case-studies
   ```

### 2. Buat Branch Baru
Buat branch baru dengan format `add/<username>-<project-name>`:
```bash
git checkout -b add/johndoe-discord-bot
```

### 3. Buat Folder & Tambahkan Project
1. Masuk ke folder `case-studies/`.
2. Pilih dan masuk ke **folder kategori** yang sesuai dengan projectmu (contoh: `bots/`).
3. Buat folder untuk projectmu dengan format `<nama-project>-<username>` (contoh: `discord-bot-johndoe/`).
4. Copy/pindahkan file projectmu ke dalam folder tersebut. **Sangat disarankan** membuat folder `assets/` di dalam projectmu untuk menyimpan gambar *screenshot* atau GIF demo.

### 4. Wajib: Tambahkan `README.md`
Setiap project **WAJIB** memiliki file `README.md` yang menjelaskan isi project tersebut.
Gunakan template yang sudah kami sediakan di [`templates/PROJECT_README.md`](../templates/PROJECT_README.md).

### 5. Commit & Push
Pastikan kamu tidak mengupload file rahasia (`.env`, `node_modules/`, `__pycache__/`).
```bash
git add .
git commit -m "feat: add discord bot project by johndoe"
git push origin add/johndoe-discord-bot
```

### 6. Buat Pull Request (PR)
1. Buka halaman GitHub repository aslimu.
2. Klik **Compare & pull request**.
3. Isi deskripsi PR menggunakan template yang sudah tersedia.
4. Tunggu review dari maintainer!

---
**Catatan Penting:**
- Pastikan project bisa dijalankan atau setidaknya bisa dipelajari strukturnya.
- Jika project berupa UI/UX, sertakan link Figma dan screenshot di README.
