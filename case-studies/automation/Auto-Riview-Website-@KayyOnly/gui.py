"""
gui.py — Website Review Bot GUI (Responsive)
Jalankan: python gui.py
Requires: pip install customtkinter
"""

import customtkinter as ctk
import subprocess
import threading
import sys
import os
import re
from datetime import datetime
from pathlib import Path

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

PURPLE      = "#534AB7"
PURPLE_DARK = "#3C3489"
PURPLE_LITE = "#EEEDFE"
PURPLE_LITE_DARK = "#2A2560"

MODE_CONFIG = {
    "Quick":    {"num": "1", "icon": "⚡", "desc": "10–30s · 1–3 hal · desktop"},
    "Standard": {"num": "2", "icon": "🎯", "desc": "30–90s · 5–15 hal · mobile+desktop"},
    "Deep":     {"num": "3", "icon": "🔬", "desc": "2–10m · 20–50 hal · full devices"},
}
PROVIDER = "groq"  # Fixed provider


# ── Reusable styled button ────────────────────────────────────────────────────

def make_selector_btn(parent, text, command, active=False, **kw):
    btn = ctk.CTkButton(
        parent, text=text, command=command,
        font=("", 11), corner_radius=8,
        fg_color=(PURPLE_LITE, PURPLE_DARK) if active else "transparent",
        border_width=2 if active else 1,
        border_color=PURPLE if active else ("gray80", "gray35"),
        text_color=(PURPLE_DARK, "white") if active else ("gray30", "gray70"),
        hover_color=(PURPLE_LITE, PURPLE_DARK),
        **kw
    )
    return btn


def set_btn_active(btn, active: bool):
    btn.configure(
        fg_color=(PURPLE_LITE, PURPLE_DARK) if active else "transparent",
        border_width=2 if active else 1,
        border_color=PURPLE if active else ("gray80", "gray35"),
        text_color=(PURPLE_DARK, "white") if active else ("gray30", "gray70"),
    )


# ── Scrollable sidebar frame ──────────────────────────────────────────────────

class ScrollableSidebar(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            width=250,
            corner_radius=0,
            fg_color=("gray95", "gray13"),
            scrollbar_button_color=("gray80", "gray30"),
            scrollbar_button_hover_color=("gray70", "gray40"),
            **kwargs
        )
        self.grid_columnconfigure(0, weight=1)


# ── Main App ──────────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Website Review Bot")
        self.geometry("1050x660")
        self.minsize(780, 520)

        self.selected_mode     = "Standard"
        self.is_running        = False
        self.process           = None
        self.last_report_path  = None
        self.mode_buttons      = {}

        self._build_layout()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        # Outer frame holds sidebar + run button (button stays pinned at bottom)
        outer = ctk.CTkFrame(self, width=268, corner_radius=0,
                             fg_color=("gray95", "gray13"))
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_propagate(False)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # Scrollable area
        sb = ScrollableSidebar(outer)
        sb.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        r = 0

        # ── Header ───────────────────────────────────────────────────────────
        header = ctk.CTkFrame(sb, fg_color="transparent")
        header.grid(row=r, column=0, sticky="ew", padx=14, pady=(16, 12)); r += 1
        ctk.CTkLabel(header, text="🤖", font=("", 24)).pack(side="left")
        meta = ctk.CTkFrame(header, fg_color="transparent")
        meta.pack(side="left", padx=10)
        ctk.CTkLabel(meta, text="Website Review Bot",
                     font=("", 13, "bold"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(meta, text="v2.0  ·  Groq AI",
                     font=("", 10), text_color=("gray55", "gray55"),
                     anchor="w").pack(anchor="w")

        self._divider(sb, r); r += 1

        # ── URL ───────────────────────────────────────────────────────────────
        self._label(sb, r, "🌐  TARGET URL"); r += 1
        self.url_entry = ctk.CTkEntry(
            sb, placeholder_text="https://example.com",
            height=36, corner_radius=8, font=("", 12))
        self.url_entry.grid(row=r, column=0, sticky="ew", padx=14, pady=(4, 0)); r += 1
        # Bind Enter key
        self.url_entry.bind("<Return>", lambda e: self._on_run())

        self._spacer(sb, r); r += 1

        # ── Mode ──────────────────────────────────────────────────────────────
        self._label(sb, r, "⚡  MODE ANALISIS"); r += 1
        mode_frame = ctk.CTkFrame(sb, fg_color="transparent")
        mode_frame.grid(row=r, column=0, sticky="ew", padx=14, pady=(4, 0)); r += 1
        mode_frame.grid_columnconfigure(0, weight=1)

        for i, (mode, cfg) in enumerate(MODE_CONFIG.items()):
            self._make_mode_card(mode_frame, i, mode, cfg)


        self._spacer(sb, r); r += 1
        self._divider(sb, r); r += 1

        # ── Mode detail info ──────────────────────────────────────────────────
        self._label(sb, r, "ℹ️  DETAIL MODE"); r += 1
        self.mode_info = ctk.CTkLabel(
            sb,
            text=self._get_mode_detail("Standard"),
            font=("", 11),
            text_color=("gray35", "gray65"),
            justify="left",
            anchor="w",
            wraplength=220,
        )
        self.mode_info.grid(row=r, column=0, sticky="w", padx=16, pady=(4, 12)); r += 1

        # ── Run button (pinned bottom) ────────────────────────────────────────
        self._divider(outer, 1, padx=0)
        self.run_btn = ctk.CTkButton(
            outer, text="▶   Run Analysis",
            font=("", 13, "bold"), height=44,
            corner_radius=0,
            fg_color=PURPLE_DARK, hover_color=PURPLE,
            command=self._on_run)
        self.run_btn.grid(row=2, column=0, sticky="ew")

    # ── Main Panel ────────────────────────────────────────────────────────────

    def _build_main(self):
        main = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # ── Tab view ──────────────────────────────────────────────────────────
        self.tabview = ctk.CTkTabview(
            main, corner_radius=10,
            segmented_button_selected_color=PURPLE,
            segmented_button_selected_hover_color=PURPLE_DARK,
            segmented_button_fg_color=("gray90", "gray18"))
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 0))

        # Tab: Live Log
        self.tabview.add("📋  Live Log")
        log_tab = self.tabview.tab("📋  Live Log")
        log_tab.grid_rowconfigure(0, weight=1)
        log_tab.grid_columnconfigure(0, weight=1)

        self.log_box = ctk.CTkTextbox(
            log_tab, font=("Consolas", 12),
            corner_radius=8, wrap="word", state="disabled")
        self.log_box.grid(row=0, column=0, sticky="nsew", pady=(6, 0))

        # Color tags
        for tag, color in [
            ("green", "#1D9E75"), ("yellow", "#BA7517"),
            ("red", "#C0392B"), ("purple", "#7C75E0"),
            ("dim", "gray55"), ("bold", None),
        ]:
            kw = {"foreground": color} if color else {}
            self.log_box._textbox.tag_config(tag, **kw)

        # Tab: AI Report
        self.tabview.add("🤖  AI Report")
        ai_tab = self.tabview.tab("🤖  AI Report")
        ai_tab.grid_rowconfigure(0, weight=1)
        ai_tab.grid_columnconfigure(0, weight=1)

        self.ai_box = ctk.CTkTextbox(
            ai_tab, font=("", 13),
            corner_radius=8, wrap="word", state="disabled")
        self.ai_box.grid(row=0, column=0, sticky="nsew", pady=(6, 0))

        # ── Status bar ────────────────────────────────────────────────────────
        status = ctk.CTkFrame(main, height=38, corner_radius=0,
                              fg_color=("gray92", "gray15"))
        status.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        status.grid_columnconfigure(0, weight=1)
        status.grid_propagate(False)

        self.status_lbl = ctk.CTkLabel(
            status, text="Ready — masukkan URL dan tekan Run",
            font=("", 11), text_color=("gray50", "gray60"), anchor="w")
        self.status_lbl.grid(row=0, column=0, padx=14, sticky="w")

        self.open_btn = ctk.CTkButton(
            status, text="📄 Buka Laporan", width=130, height=26,
            font=("", 11), corner_radius=6,
            fg_color="transparent", border_width=1,
            border_color=("gray70", "gray40"),
            text_color=("gray45", "gray65"),
            hover_color=("gray85", "gray25"),
            command=self._open_report, state="disabled")
        self.open_btn.grid(row=0, column=1, padx=(0, 10))

    # ── Helpers: sidebar widgets ──────────────────────────────────────────────

    def _label(self, parent, row, text):
        ctk.CTkLabel(parent, text=text, font=("", 10, "bold"),
                     text_color=("gray50", "gray55"), anchor="w").grid(
            row=row, column=0, sticky="w", padx=16, pady=(12, 2))

    def _divider(self, parent, row, padx=12):
        ctk.CTkFrame(parent, height=1,
                     fg_color=("gray83", "gray28")).grid(
            row=row, column=0, sticky="ew", padx=padx, pady=2)

    def _spacer(self, parent, row):
        ctk.CTkFrame(parent, height=4, fg_color="transparent").grid(
            row=row, column=0)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _make_mode_card(self, parent, row, mode, cfg):
        """Custom mode card: icon + name bold / desc smaller below."""
        is_active = (mode == self.selected_mode)

        card = ctk.CTkFrame(
            parent,
            corner_radius=8,
            border_width=2 if is_active else 1,
            border_color=PURPLE if is_active else ("gray80", "gray35"),
            fg_color=(PURPLE_LITE, PURPLE_DARK) if is_active else ("gray97", "gray18"),
            cursor="hand2",
        )
        card.grid(row=row, column=0, pady=3, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # Icon
        icon_lbl = ctk.CTkLabel(
            card, text=cfg["icon"], font=("", 18), width=36)
        icon_lbl.grid(row=0, column=0, rowspan=2, padx=(10, 4), pady=8)

        # Mode name
        name_lbl = ctk.CTkLabel(
            card, text=mode, font=("", 13, "bold"), anchor="w",
            text_color=(PURPLE_DARK, "white") if is_active else ("gray15", "gray90"))
        name_lbl.grid(row=0, column=1, sticky="w", padx=(4, 8), pady=(7, 0))

        # Description
        desc_lbl = ctk.CTkLabel(
            card, text=cfg["desc"], font=("", 10), anchor="w",
            text_color=(PURPLE, "gray70") if is_active else ("gray50", "gray55"))
        desc_lbl.grid(row=1, column=1, sticky="w", padx=(4, 8), pady=(0, 7))

        # Simpan referensi semua widget untuk update warna
        self.mode_buttons[mode] = {
            "card": card, "name": name_lbl, "desc": desc_lbl
        }

        # Bind klik di semua elemen
        for widget in (card, icon_lbl, name_lbl, desc_lbl):
            widget.bind("<Button-1>", lambda e, m=mode: self._on_mode(m))

    def _get_mode_detail(self, mode: str) -> str:
        details = {
            "Quick": (
                "✅ Homepage only\n"
                "✅ Basic performance & errors\n"
                "✅ Screenshot homepage\n"
                "❌ Tanpa crawling, video, auth\n"
                "📱 Desktop only · 1–3 halaman"
            ),
            "Standard": (
                "✅ Limited crawling\n"
                "✅ Responsive + mobile test\n"
                "✅ Accessibility & form testing\n"
                "✅ AI analysis aktif\n"
                "📱 Desktop + Mobile · 5–15 hal"
            ),
            "Deep": (
                "✅ Smart crawler + AI agent\n"
                "✅ Auth, visual & security testing\n"
                "✅ Video recording + replay\n"
                "✅ Deep AI analysis\n"
                "📱 Desktop + Tablet + Mobile · 20–50 hal"
            ),
        }
        return details.get(mode, "")

    def _on_mode(self, mode: str):
        self.selected_mode = mode
        for m, widgets in self.mode_buttons.items():
            active = (m == mode)
            widgets["card"].configure(
                border_width=2 if active else 1,
                border_color=PURPLE if active else ("gray80", "gray35"),
                fg_color=(PURPLE_LITE, PURPLE_DARK) if active else ("gray97", "gray18"),
            )
            widgets["name"].configure(
                text_color=(PURPLE_DARK, "white") if active else ("gray15", "gray90"))
            widgets["desc"].configure(
                text_color=(PURPLE, "gray70") if active else ("gray50", "gray55"))
        self.mode_info.configure(text=self._get_mode_detail(mode))

    def _on_run(self):
        if self.is_running:
            self._stop(); return

        url = self.url_entry.get().strip()
        if not url:
            self._log("⚠️  Masukkan URL terlebih dahulu!\n", "yellow"); return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, url)

        self._start(url)

    def _start(self, url: str):
        self.is_running = True
        self.run_btn.configure(text="⏹   Stop",
                               fg_color="#A32D2D", hover_color="#7A1F1F")
        self.status_lbl.configure(
            text=f"⏳  Berjalan · {self.selected_mode} mode · {url}")
        self.open_btn.configure(state="disabled")
        self._clear_log(); self._clear_ai()

        self._log(f"{'─'*52}\n", "dim")
        self._log("🤖  Website Review Bot\n", "purple")
        self._log(f"{'─'*52}\n", "dim")
        self._log(f"🌐  URL   : {url}\n")
        self._log(f"⚡  Mode  : {self.selected_mode}\n")
        self._log(f"🤖  AI    : Groq (llama-3.3-70b)\n")
        self._log(f"{'─'*52}\n\n", "dim")

        threading.Thread(
            target=self._run_process,
            args=(MODE_CONFIG[self.selected_mode]["num"], url),
            daemon=True
        ).start()

    def _run_process(self, mode_num: str, url: str):
        main_py = Path(__file__).parent.parent / "main.py"
        if not main_py.exists():
            # Coba lokasi sama dengan gui.py
            main_py = Path(__file__).parent / "main.py"

        try:
            self.process = subprocess.Popen(
                [sys.executable, str(main_py)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                cwd=str(main_py.parent),
                env={
                    **os.environ,
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONIOENCODING": "utf-8",   # ← fix emoji encoding
                    "PYTHONUTF8": "1",             # ← force UTF-8 di Windows
                },
            )

            # Kirim mode + URL + "q" agar main.py keluar setelah selesai
            self.process.stdin.write(f"{mode_num}\n{url}\nq\n")
            self.process.stdin.flush()
            self.process.stdin.close()

            ai_lines    = []
            capture_ai  = False

            for line in self.process.stdout:
                stripped = line.rstrip("\n")

                # Deteksi blok AI report
                if re.search(r"(AI Report|ANALISIS AI|Laporan AI)", stripped, re.I):
                    capture_ai = True
                if capture_ai:
                    ai_lines.append(stripped)

                tag = self._color_tag(stripped)
                self.after(0, self._log, stripped + "\n", tag)

                # Deteksi path laporan
                m = re.search(r"(report_\S+\.txt)", stripped)
                if m:
                    self.last_report_path = str(main_py.parent / m.group(1))

            self.process.wait()

            if ai_lines:
                self.after(0, self._set_ai, "\n".join(ai_lines))

            self.after(0, self._on_done, self.process.returncode == 0)

        except FileNotFoundError:
            self.after(0, self._log, "❌  main.py tidak ditemukan!\n", "red")
            self.after(0, self._on_done, False)
        except Exception as e:
            self.after(0, self._log, f"❌  Error: {e}\n", "red")
            self.after(0, self._on_done, False)

    def _stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self._log("\n⏹  Dihentikan.\n", "yellow")
        self._on_done(False)

    def _on_done(self, success: bool):
        self.is_running = False
        self.process    = None
        self.run_btn.configure(text="▶   Run Analysis",
                               fg_color=PURPLE_DARK, hover_color=PURPLE)
        if success:
            ts = datetime.now().strftime("%H:%M:%S")
            self.status_lbl.configure(
                text=f"✅  Selesai · {self.selected_mode} · {ts}")
            self._log("\n✅  Analisis selesai!\n", "green")
            if self.last_report_path:
                self.open_btn.configure(state="normal")
        else:
            self.status_lbl.configure(text="❌  Gagal atau dihentikan")

    # ── Log helpers ───────────────────────────────────────────────────────────

    def _color_tag(self, line: str) -> str:
        lo = line.lower()
        if any(k in lo for k in ["✅", "selesai", "berhasil", "success"]):
            return "green"
        if any(k in lo for k in ["❌", "error", "gagal", "failed", "critical"]):
            return "red"
        if any(k in lo for k in ["⚠️", "warning", "high", "medium"]):
            return "yellow"
        if any(k in lo for k in ["🤖", "skor", "claude", "openai", "gemini", "groq"]):
            return "purple"
        if not line.strip() or line.startswith(("─", "═", "=")):
            return "dim"
        return ""

    def _log(self, text: str, tag: str = ""):
        self.log_box.configure(state="normal")
        if tag:
            self.log_box._textbox.insert("end", text, tag)
        else:
            self.log_box.insert("end", text)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _set_ai(self, text: str):
        self.ai_box.configure(state="normal")
        self.ai_box.delete("1.0", "end")
        self.ai_box.insert("1.0", text)
        self.ai_box.configure(state="disabled")
        self.tabview.set("🤖  AI Report")

    def _clear_ai(self):
        self.ai_box.configure(state="normal")
        self.ai_box.delete("1.0", "end")
        self.ai_box.configure(state="disabled")

    def _open_report(self):
        if self.last_report_path and os.path.exists(self.last_report_path):
            os.startfile(self.last_report_path)
        else:
            self._log("⚠️  File laporan tidak ditemukan.\n", "yellow")


if __name__ == "__main__":
    App().mainloop()