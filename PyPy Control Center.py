import customtkinter as ctk
import psutil
import threading
import time

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PyPyControlCenter(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyPy Control Center")
        self.geometry("1000x700")
        self.minsize(950, 650)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.selected_pid = None
        self.process_widgets = {}

        self._create_sidebar()
        self._create_main_content()

        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()

        self._refresh_process_list()

    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🐍 PyPy Center", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 15))

        self.status_badge = ctk.CTkLabel(
            self.sidebar_frame,
            text="● SYSTEM MONITOR",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#2FA572"
        )
        self.status_badge.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.btn_kill = ctk.CTkButton(
            self.sidebar_frame, 
            text="End Selected Task", 
            fg_color="#D32F2F", 
            hover_color="#9A0007", 
            command=self._kill_selected_process
        )
        self.btn_kill.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance:", anchor="w")
        self.theme_label.grid(row=7, column=0, padx=20, pady=(10, 0))

        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Dark", "Light", "System"], 
            command=self.change_appearance_mode
        )
        self.theme_menu.grid(row=8, column=0, padx=20, pady=(5, 20))

    def _create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="PyPy Control Center - Advanced Metrics", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        self.card1 = ctk.CTkFrame(self.main_frame, corner_radius=12)
        self.card1.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.card1, text="CPU Load", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(12, 0))
        self.cpu_val = ctk.CTkLabel(self.card1, text="0%", font=ctk.CTkFont(size=24, weight="bold"))
        self.cpu_val.pack(anchor="w", padx=15, pady=2)
        self.cpu_bar = ctk.CTkProgressBar(self.card1, height=6, progress_color="#1F6AA5")
        self.cpu_bar.pack(fill="x", padx=15, pady=(0, 12))

        self.card2 = ctk.CTkFrame(self.main_frame, corner_radius=12)
        self.card2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.card2, text="RAM Usage", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(12, 0))
        self.ram_val = ctk.CTkLabel(self.card2, text="0.0 GB", font=ctk.CTkFont(size=24, weight="bold"))
        self.ram_val.pack(anchor="w", padx=15, pady=2)
        self.ram_bar = ctk.CTkProgressBar(self.card2, height=6, progress_color="#2FA572")
        self.ram_bar.pack(fill="x", padx=15, pady=(0, 12))

        self.card3 = ctk.CTkFrame(self.main_frame, corner_radius=12)
        self.card3.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.card3, text="Logical Threads", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(12, 0))
        self.proc_count_val = ctk.CTkLabel(self.card3, text=str(psutil.cpu_count()), font=ctk.CTkFont(size=24, weight="bold"))
        self.proc_count_val.pack(anchor="w", padx=15, pady=2)
        self.thread_bar = ctk.CTkProgressBar(self.card3, height=6, progress_color="#E59B24")
        self.thread_bar.pack(fill="x", padx=15, pady=(0, 12))
        self.thread_bar.set(0.6)

        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(15, 0))
        
        tab_proc = self.tabview.add("Active Processes")
        tab_credits = self.tabview.add("Credits")

        self.search_entry = ctk.CTkEntry(tab_proc, placeholder_text="Filter by process name or PID...")
        self.search_entry.pack(fill="x", padx=10, pady=(10, 5))
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_process_list())

        self.headers_frame = ctk.CTkFrame(tab_proc, height=30, fg_color=("gray85", "gray20"))
        self.headers_frame.pack(fill="x", padx=10, pady=5)
        self.headers_frame.grid_columnconfigure(0, weight=1)
        self.headers_frame.grid_columnconfigure(1, weight=3)
        self.headers_frame.grid_columnconfigure(2, weight=2)
        self.headers_frame.grid_columnconfigure(3, weight=2)

        ctk.CTkLabel(self.headers_frame, text="PID", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(self.headers_frame, text="NAME", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(self.headers_frame, text="MEM (MB)", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(self.headers_frame, text="STATUS", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=3, padx=10, sticky="w")

        self.scroll_frame = ctk.CTkScrollableFrame(tab_proc)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=3)
        self.scroll_frame.grid_columnconfigure(2, weight=2)
        self.scroll_frame.grid_columnconfigure(3, weight=2)

        self._create_credits_tab(tab_credits)

    def _create_credits_tab(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="PyPy Control Center", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(0, 10))
        ctk.CTkLabel(container, text="Version 1.0", font=ctk.CTkFont(size=14)).pack(pady=(0, 30))

        credits_box = ctk.CTkFrame(container, corner_radius=15)
        credits_box.pack(fill="x", padx=50, pady=10)

        ctk.CTkLabel(credits_box, text="Development Team", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(credits_box, text="Developer: TheMangler47").pack(pady=2)
        ctk.CTkLabel(credits_box, text="Logic & Backend: Python (Obviously)").pack(pady=2)
        ctk.CTkLabel(credits_box, text="Product Owner: You (Yes You! Lmfao)").pack(pady=(2, 15))

        tech_box = ctk.CTkFrame(container, corner_radius=15)
        tech_box.pack(fill="x", padx=50, pady=10)

        ctk.CTkLabel(tech_box, text="Core Technologies", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(tech_box, text="Framework: CustomTkinter (Modernized Tkinter)").pack(pady=2)
        ctk.CTkLabel(tech_box, text="Telemetry: psutil (Proc & System Utils)").pack(pady=2)
        ctk.CTkLabel(tech_box, text="Platform: Cross-Platform Python 3.x").pack(pady=(2, 15))

        ctk.CTkLabel(container, text="© 2026 PyPy Control Center Projects. All rights reserved.", font=ctk.CTkFont(size=10)).pack(side="bottom", pady=20)

    def _refresh_process_list(self):
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        self.process_widgets.clear()
        query = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""
        row = 0

        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'status']):
            try:
                info = proc.info
                pid, name, status = info['pid'], info['name'] or "N/A", info['status'] or "N/A"
                mem_mb = round(info['memory_info'].rss / (1024 * 1024), 1) if info['memory_info'] else 0.0

                if query and (query not in name.lower() and query not in str(pid)): continue
                if row > 100: break

                item_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent", height=28)
                item_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=1)
                item_frame.grid_columnconfigure(0, weight=1); item_frame.grid_columnconfigure(1, weight=3)
                item_frame.grid_columnconfigure(2, weight=2); item_frame.grid_columnconfigure(3, weight=2)

                lbl1 = ctk.CTkLabel(item_frame, text=str(pid), anchor="w")
                lbl1.grid(row=0, column=0, padx=10, sticky="w")
                lbl2 = ctk.CTkLabel(item_frame, text=name, anchor="w")
                lbl2.grid(row=0, column=1, padx=10, sticky="w")
                lbl3 = ctk.CTkLabel(item_frame, text=f"{mem_mb}", anchor="w")
                lbl3.grid(row=0, column=2, padx=10, sticky="w")
                lbl4 = ctk.CTkLabel(item_frame, text=status, anchor="w")
                lbl4.grid(row=0, column=3, padx=10, sticky="w")

                for w in (item_frame, lbl1, lbl2, lbl3, lbl4):
                    w.bind("<Button-1>", lambda e, p=pid, f=item_frame: self._select_process(p, f))

                self.process_widgets[pid] = item_frame
                row += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied): continue

    def _select_process(self, pid, frame):
        self.selected_pid = pid
        for f in self.process_widgets.values(): f.configure(fg_color="transparent")
        frame.configure(fg_color=("gray75", "gray30"))

    def _kill_selected_process(self):
        if self.selected_pid:
            try:
                p = psutil.Process(self.selected_pid)
                p.kill()
                self.selected_pid = None
                self.after(500, self._refresh_process_list)
            except: pass

    def _monitor_system(self):
        while True:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            self.after(0, self._update_metrics, cpu, ram)

    def _update_metrics(self, cpu, ram):
        self.cpu_val.configure(text=f"{cpu}%")
        self.cpu_bar.set(cpu / 100)
        self.ram_val.configure(text=f"{round(ram.used / (1024**3), 2)} GB")
        self.ram_bar.set(ram.percent / 100)

    def change_appearance_mode(self, new_mode: str):
        ctk.set_appearance_mode(new_mode)

if __name__ == "__main__":
    app = PyPyControlCenter()
    app.mainloop()
