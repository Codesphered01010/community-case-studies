# [AUTO RIVIEW WEBSITE]

> **Part of [CodeSphred Community](https://github.com/Codesphered01010)**  
> *Project ini adalah salah satu hasil karya member komunitas dalam repositori [Community Case Studies](https://github.com/Codesphered01010/community-case-studies).*

---

> *Auto riview web adalah tools automation testing berbasis AI yang dirancang untuk melakukan audit website secara otomatis mulai dari crawling halaman, pengecekan performa, responsive testing, accessibility audit, visual testing, hingga analisis bug dan error menggunakan AI.
Project ini dibuat untuk membantu developer dan QA engineer melakukan website testing lebih cepat, otomatis, dan lebih mendalam tanpa harus melakukan pengecekan manual satu per satu.*

## Author
*Sebutkan siapa saja yang berkontribusi dalam project ini.*
- **[Kayy]** - [QA Automation Developer] - [Github.com/KayyOnly]

## Tech Stack
*Sebutkan teknologi, framework, atau library utama yang digunakan.*
- Python 3.10
- Playwright
- Rich
- AsyncIO
- Groq API
- CustomTkinter (GUI)
- TailwindCSS
- dotenv
- JSON-based reporting

## Architecture / System Design
*Jelaskan alur kerja aplikasi atau arsitektur sistemnya. Kamu bisa menambahkan diagram (flowchart/C4 model) jika ada.*
- **Flow Sistem:**
Website Target
      ↓
Smart Website Crawler
      ↓
Responsive & Interaction Testing
      ↓
Accessibility + Visual Testing
      ↓
Network/API Inspection
      ↓
Local Rule Engine
      ↓
AI Summary Builder
      ↓
AI Analysis (Groq)
      ↓
Professional QA Report
- **Komponen Utama:**
- Crawler Engine: Mendeteksi halaman website dan route penting.
- Responsive Engine: Menguji tampilan desktop, tablet, dan mobile.
- Interaction Tester: Menjalankan automation interaction seperti klik, form, navigasi, dan auth flow.
- Local Rule Engine: Menganalisa issue secara lokal tanpa AI. (not finished yet)
- AI Summary Builder: Merangkum hasil testing agar payload AI tetap ringan.
- AI Analyzer: Membuat laporan QA profesional menggunakan AI.

## Features
*Sebutkan fitur-fitur unggulan dari project ini.*
- [x] Fitur unggulan pertama : Smart Website Crawling
- [x] Fitur unggulan kedua : Automation UI & Interaction Testing
- [x] Fitur unggulan ketiga : Responsive Testing (Desktop, Tablet, Mobile)
- [x] Fitur unggulan keempat : Accessibility Audit
- [x] Fitur unggulan kelima : Visual Testing & Screenshot Detection
- [x] Fitur unggulan keenam : Video Recording Testing Session
- [x] Fitur unggulan ketujuh : API & Network Inspection

## Challenges & Learnings
*Ceritakan tantangan terbesar saat membuat project ini dan apa yang kamu pelajari.*
- **Tantangan: Salah satu tantangan terbesar adalah menangani payload AI yang terlalu besar akibat hasil crawling, logs, screenshot metadata, dan interaction testing yang sangat banyak.** Kesulitan saat mengelola state management yang kompleks.
- **Solusi/Pelajaran: Dari project ini juga dipelajari bagaimana membangun arsitektur automation testing yang scalable dan efisien untuk modern web application seperti Next.js dan React.** Mempelajari Redux Toolkit membuat pengelolaan state jauh lebih mudah dan rapi.

## Impact / Results
*Apa hasil nyata setelah project ini selesai/dideploy? (Opsional)*
- Mengurangi proses pengecekan manual yang repetitif.
- Membantu mempercepat proses QA testing website secara otomatis.

## Screenshot
*Tambahkan screenshot atau GIF dari projectmu agar member lain bisa melihat hasilnya!*

![Screenshot](https://files.catbox.moe/qhi7zj.png)

## Demo / Repository Link
- **Live Demo:** [Link ke Vercel/Netlify/dll] (Opsional)
- **Original Repo:** [Link ke repository utama projectmu jika ada] (Opsional)
- **Figma:** [Link desain UI/UX] (Opsional)

## License
*Project ini berada di bawah lisensi [MIT/Apache/dll].*
