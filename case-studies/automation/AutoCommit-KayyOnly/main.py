import os
import random
import subprocess
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

AUTHOR = "KayyOnly"

class GraphGreenerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"🌱 Graph-Greener by {AUTHOR}")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1117")

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#0d1117")
        style.configure("TLabel", background="#0d1117", foreground="#c9d1d9", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#0d1117", foreground="#39d353", font=("Segoe UI", 16, "bold"))
        style.configure("Author.TLabel", background="#0d1117", foreground="#8b949e", font=("Segoe UI", 9, "italic"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#238636")
        style.map("TButton", background=[("active", "#2ea043")])
        style.configure("Green.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#39d353")
        style.map("Green.TButton", background=[("active", "#56d364")])
        style.configure("TEntry", fieldbackground="#161b22", foreground="#c9d1d9", insertcolor="#c9d1d9")
        style.configure("TSpinbox", fieldbackground="#161b22", foreground="#c9d1d9")

        # Header
        header_frame = ttk.Frame(root, padding="20 20 20 10")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="🌱 Graph-Greener", style="Header.TLabel").pack()
        ttk.Label(header_frame, text=f"GitHub Contribution Graph Commit Generator  •  by {AUTHOR}", style="Author.TLabel").pack(pady=(2, 0))
        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=5)

        # Form
        form_frame = ttk.Frame(root, padding="20 10 20 10")
        form_frame.pack(fill="x")

        # Commits count
        ttk.Label(form_frame, text="Number of Commits:").grid(row=0, column=0, sticky="w", pady=8)
        self.commits_var = tk.IntVar(value=20)
        commits_spin = ttk.Spinbox(form_frame, from_=1, to=10000, textvariable=self.commits_var, width=12, font=("Segoe UI", 10))
        commits_spin.grid(row=0, column=1, sticky="w", padx=10)

        # Repo path
        ttk.Label(form_frame, text="Repository Path:").grid(row=1, column=0, sticky="w", pady=8)
        path_frame = ttk.Frame(form_frame)
        path_frame.grid(row=1, column=1, sticky="w", padx=10)
        self.path_var = tk.StringVar(value=os.getcwd())
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=35, font=("Segoe UI", 10))
        path_entry.pack(side="left")
        ttk.Button(path_frame, text="Browse", command=self.browse_repo, width=8).pack(side="left", padx=(5, 0))

        # Filename
        ttk.Label(form_frame, text="Target Filename:").grid(row=2, column=0, sticky="w", pady=8)
        self.filename_var = tk.StringVar(value="data.txt")
        ttk.Entry(form_frame, textvariable=self.filename_var, width=35, font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", padx=10)

        # Commit message
        ttk.Label(form_frame, text="Commit Message:").grid(row=3, column=0, sticky="w", pady=8)
        self.message_var = tk.StringVar(value="graph-greener!")
        ttk.Entry(form_frame, textvariable=self.message_var, width=35, font=("Segoe UI", 10)).grid(row=3, column=1, sticky="w", padx=10)

        # Push checkbox
        self.push_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Push to remote after committing", variable=self.push_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=8)

        # Buttons
        btn_frame = ttk.Frame(root, padding="20 5 20 10")
        btn_frame.pack(fill="x")
        self.run_btn = ttk.Button(btn_frame, text="🚀 Generate Commits", command=self.start_generation, style="Green.TButton")
        self.run_btn.pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="🧹 Clear Log", command=self.clear_log).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Exit", command=root.quit).pack(side="right")

        # Progress
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=610)
        self.progress.pack(padx=20, pady=(5, 0))
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(root, textvariable=self.status_var, foreground="#8b949e", font=("Segoe UI", 9)).pack(pady=(2, 0))

        # Log
        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=10)
        ttk.Label(root, text="Activity Log:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)
        self.log_box = scrolledtext.ScrolledText(root, width=75, height=12, bg="#161b22", fg="#c9d1d9", insertbackground="#c9d1d9", font=("Consolas", 9), state="disabled")
        self.log_box.pack(padx=20, pady=5)

        # Footer
        ttk.Label(root, text=f"Made with 💚 by {AUTHOR}", foreground="#39d353", font=("Segoe UI", 9, "bold")).pack(pady=(0, 10))

    def browse_repo(self):
        path = filedialog.askdirectory(title="Select Git Repository")
        if path:
            self.path_var.set(path)

    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.status_var.set("Ready")
        self.progress["value"] = 0

    def random_date_in_last_year(self):
        today = datetime.now()
        start_date = today - timedelta(days=365)
        random_days = random.randint(0, 364)
        random_seconds = random.randint(0, 23*3600 + 3599)
        return start_date + timedelta(days=random_days, seconds=random_seconds)

    def make_commit(self, date, repo_path, filename, message):
        filepath = os.path.join(repo_path, filename)
        with open(filepath, "a") as f:
            f.write(f"Commit at {date.isoformat()}\n")
        subprocess.run(["git", "add", filename], cwd=repo_path, capture_output=True)
        env = os.environ.copy()
        date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str
        result = subprocess.run(["git", "commit", "-m", message], cwd=repo_path, env=env, capture_output=True, text=True)
        return result.returncode == 0

    def run_generation(self):
        num_commits = self.commits_var.get()
        repo_path = self.path_var.get()
        filename = self.filename_var.get()
        message = self.message_var.get()
        do_push = self.push_var.get()

        if not os.path.isdir(repo_path):
            messagebox.showerror("Error", "Repository path does not exist!")
            self.run_btn.configure(state="normal")
            return

        git_dir = os.path.join(repo_path, ".git")
        if not os.path.isdir(git_dir):
            messagebox.showerror("Error", "Selected directory is not a git repository!")
            self.run_btn.configure(state="normal")
            return

        self.progress["maximum"] = num_commits
        self.progress["value"] = 0
        self.log(f"Starting generation of {num_commits} commits...")
        self.log(f"Repo: {repo_path}")
        self.log(f"File: {filename}")
        self.log("-" * 50)

        success_count = 0
        for i in range(num_commits):
            commit_date = self.random_date_in_last_year()
            self.status_var.set(f"Processing commit {i+1}/{num_commits}...")
            ok = self.make_commit(commit_date, repo_path, filename, message)
            if ok:
                success_count += 1
                self.log(f"[{i+1}/{num_commits}] ✅ {commit_date.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                self.log(f"[{i+1}/{num_commits}] ❌ Failed at {commit_date.strftime('%Y-%m-%d %H:%M:%S')}")
            self.progress["value"] = i + 1
            self.root.update_idletasks()

        self.log("-" * 50)
        self.log(f"Commits created: {success_count}/{num_commits}")

        if do_push:
            self.status_var.set("Pushing to remote...")
            self.log("Pushing to remote repository...")
            result = subprocess.run(["git", "push"], cwd=repo_path, capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Push successful!")
            else:
                self.log(f"⚠️ Push output: {result.stderr or result.stdout}")

        self.status_var.set("Done!")
        self.run_btn.configure(state="normal")
        messagebox.showinfo("Complete", f"Finished! {success_count} commits generated.\nCheck your GitHub graph in a few minutes.")

    def start_generation(self):
        self.run_btn.configure(state="disabled")
        thread = threading.Thread(target=self.run_generation, daemon=True)
        thread.start()


def main():
    root = tk.Tk()
    app = GraphGreenerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
