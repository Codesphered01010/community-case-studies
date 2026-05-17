import json
import os
import time
from typing import Any

from groq import Groq

from ai.summary_builder import SummaryBuilder


ADVANCED_ANALYSIS_PROMPT_TEMPLATE = """Anda adalah Senior QA Engineer dan Senior Web Developer.

Analisa hasil testing website berikut dan buat laporan QA profesional dalam Bahasa Indonesia yang natural, jelas, dan mudah dipahami.

Fokus analisa:

* Performance
* Bug & error
* UI/UX
* Responsive issue
* Accessibility
* API/network issue
* Security basic issue
* Frontend rendering/hydration
* Form validation
* Asset/media issue
* SEO basic

Jangan membuat asumsi tanpa bukti.
Jika data kurang jelas, tulis:
⚠️ Perlu validasi manual lebih lanjut.

Gunakan severity:

* CRITICAL
* HIGH
* MEDIUM
* LOW

========================================
DATA TESTING
============

{testing_data_json}

========================================
FORMAT OUTPUT
=============

# 🏆 SKOR KESELURUHAN: X/100

Berikan ringkasan kondisi website secara profesional.

| Kategori        | Skor  |
| --------------- | ----- |
| Stability       | X/100 |
| Performance     | X/100 |
| Security        | X/100 |
| Accessibility   | X/100 |
| User Experience | X/100 |
| Maintainability | X/100 |

---

# ⚡ ANALISIS PERFORMA

Bahas:

* load time
* FCP/LCP
* render performance
* API latency
* asset loading
* bottleneck
* dampak UX & SEO
* rekomendasi optimasi

---

# 🐛 BUG & ERROR

Untuk setiap issue gunakan format:

## [SEVERITY] Nama Masalah

### Ringkasan

### Detail Teknis

### Dampak

### Kemungkinan Penyebab

### Cara Fix

### Prioritas

Jika tidak ada masalah:
✅ Tidak ada bug/error signifikan ditemukan.

---

# 📋 UI & RESPONSIVE

Evaluasi:

* form & validation
* responsive layout
* overflow
* hydration mismatch
* usability
* mobile issue
* layout shift

---

# ♿ AKSESIBILITAS

Evaluasi:

* alt text
* semantic HTML
* heading structure
* ARIA
* keyboard navigation

---

# 🔐 SECURITY DASAR

Cek indikasi:

* exposed secret
* insecure header
* XSS/CSRF indication
* auth issue
* dependency risk

Jangan membuat klaim berlebihan tanpa bukti.

---

# ⚙️ FRONTEND & BACKEND

Analisa:

* React/Next.js hydration
* rendering issue
* component/CSS issue
* failed request
* abnormal status code
* slow API
* timeout

---

# 🎯 5 PRIORITAS UTAMA

Urutkan 5 masalah paling penting berdasarkan dampak bisnis & UX.

---

# 📌 KESIMPULAN AKHIR

Jelaskan:

* kesiapan website
* risiko utama
* area yang perlu improvement
* apakah layak production


---"""


def _score(avg_load_time: float, errors: int, a11y: int) -> int:
    score = 100
    if avg_load_time > 3000:
        score -= 15
    if avg_load_time > 5000:
        score -= 15
    score -= min(errors * 3, 30)
    score -= min(a11y * 2, 25)
    return max(score, 0)


class AIAnalyzer:
    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.summary_builder = SummaryBuilder(max_payload_chars=20000)

    def _build_prompt(self, summary_data: dict[str, Any]) -> str:
        formatted_json = json.dumps(summary_data, indent=2, ensure_ascii=False)
        return ADVANCED_ANALYSIS_PROMPT_TEMPLATE.format(testing_data_json=formatted_json)

    def _fallback_markdown(self, report_payload: dict[str, Any], score: int) -> str:
        summary = report_payload["summary"]
        return (
            f"# 🏆 SKOR KESELURUHAN: [{score}/100]\n\n"
            "⚠️ Perlu validasi manual lebih lanjut. (AI tidak tersedia, fallback lokal aktif)\n\n"
            "# ⚡ ANALISIS PERFORMA\n"
            f"- Rata-rata load time: {summary['avg_load_time_ms']} ms.\n"
            "- Potensi bottleneck: asset besar, request lambat, atau render blocking.\n\n"
            "# 🐛 BUG & ERROR\n"
            f"- Console errors: {summary['total_console_errors']}.\n"
            f"- Failed requests: {summary['total_failed_requests']}.\n\n"
            "# ♿ AKSESIBILITAS\n"
            f"- Total isu aksesibilitas dasar: {summary['total_accessibility_issues']}.\n\n"
            "# 🎯 5 PRIORITAS UTAMA\n"
            "1. Perbaiki failed request dan error console yang memblokir fitur utama.\n"
            "2. Optimasi resource statis (gambar, CSS, JS) serta aktifkan caching.\n"
            "3. Perbaiki aksesibilitas penting: alt text, label form, struktur heading.\n"
            "4. Validasi form input di frontend + backend untuk menurunkan error submission.\n"
            "5. Lakukan audit manual keamanan dasar (header security, auth flow, input sanitization).\n\n"
            "# 📌 KESIMPULAN AKHIR\n"
            "Website dapat diaudit otomatis dengan baik, namun masih memerlukan perbaikan prioritas sebelum dinilai siap production penuh."
        )

    def _request_with_retry(self, client: Groq, prompt: str, retries: int = 2) -> str:
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Anda adalah QA engineer senior yang memberikan laporan profesional berbasis bukti."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    max_tokens=1800,
                )
                return (response.choices[0].message.content or "").strip()
            except Exception as exc:
                last_error = exc
                if attempt == retries:
                    break
                time.sleep(1.0)
        raise RuntimeError(f"Groq request failed after retry: {last_error}")

    def analyze(self, report_payload: dict[str, Any]) -> dict[str, Any]:
        ai_summary, summary_debug = self.summary_builder.build_summary(report_payload)
        perf = report_payload["summary"]["avg_load_time_ms"]
        err = report_payload["summary"]["total_console_errors"] + report_payload["summary"]["total_failed_requests"]
        a11y = report_payload["summary"]["total_accessibility_issues"]
        local_score = _score(perf, err, a11y)

        if not self.api_key:
            fallback = self._fallback_markdown(report_payload, local_score)
            return {
                "score": local_score,
                "analysis": "GROQ_API_KEY tidak tersedia. Menggunakan analisis lokal berbasis rule.",
                "ai_summary": ai_summary,
                "summary_debug": summary_debug,
                "recommendations": [
                    "Perbaiki console error dan failed request terlebih dahulu.",
                    "Optimalkan asset statis (gambar, CSS, JS).",
                    "Tambahkan label/alt text untuk aksesibilitas.",
                ],
                "markdown_report": fallback,
            }

        client = Groq(api_key=self.api_key)
        prompt = self._build_prompt(ai_summary)

        try:
            raw = self._request_with_retry(client, prompt, retries=2)
            markdown_report = raw if raw else self._fallback_markdown(report_payload, local_score)
            return {
                "score": local_score,
                "analysis": "Analisis Groq berhasil dibuat.",
                "ai_summary": ai_summary,
                "summary_debug": summary_debug,
                "recommendations": [],
                "markdown_report": markdown_report,
            }
        except Exception as exc:
            print(f"\n[DEBUG] Groq error: {exc}\n")
            fallback = self._fallback_markdown(report_payload, local_score)
            return {
                "score": local_score,
                "analysis": f"Groq gagal dipanggil, fallback lokal aktif: {exc}",
                "recommendations": ["Cek GROQ_API_KEY, model, dan koneksi jaringan."],
                "markdown_report": fallback,
            }