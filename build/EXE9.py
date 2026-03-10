import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk
import subprocess
import os
import sys
import platform
import threading
import tempfile

# -----------------------------
# DPI FIX (Windows only)
# -----------------------------
if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass


# -----------------------------
# OPTIONAL PIL FOR LOGO
# -----------------------------
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False


# =========================================================
# ===================== RESOURCE PATH =====================
# =========================================================

def resource_path(relative):
    """Resolve path to a bundled resource, works both frozen and in dev."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


# =========================================================
# ====================== CONFIG ===========================
# =========================================================

APP_TITLE = "EXE9 Universal Compiler"
WINDOW_GEOMETRY = "900x840"

LOGO_IMAGE_PATH = resource_path("exe9transparent.png")
LOGO_MAX_HEIGHT = 130

DND_IMAGE_PATH = resource_path("draganddrop.png")
DND_IMAGE_MAX_HEIGHT = 100

DND_ZONE_HEIGHT = 160

ICON_PATH = resource_path("appicon.ico")  # Window + taskbar icon

BG_COLOR = "#001130"
FG_COLOR = "#39C49F"

BUTTON_COLOR = "#39C49F"
BUTTON_HOVER_COLOR = "#57e8c0"
BUTTON_TEXT_COLOR = "#000000"

CLEAR_BUTTON_COLOR = "#c0392b"
CLEAR_BUTTON_HOVER_COLOR = "#e74c3c"
CLEAR_BUTTON_TEXT_COLOR = "#ffffff"

INPUT_BG_COLOR = "#0c1a3a"
INPUT_TEXT_COLOR = "#ffffff"
INPUT_BORDER_COLOR = "#39C49F"

LABEL_COLOR = "#39C49F"

LOG_BG_COLOR = "#191919"
LOG_FG_COLOR = "#39C49F"

PROGRESS_COLOR = "#39C49F"
PROGRESS_TROUGH_COLOR = "#0c1a3a"

FONT_SIZE_LABEL = 10
FONT_SIZE_ENTRY = 10
FONT_SIZE_BUTTON = 11
FONT_SIZE_LOG = 10

FONT_LABEL = ("Segoe UI", FONT_SIZE_LABEL)
FONT_ENTRY = ("Segoe UI", FONT_SIZE_ENTRY)
FONT_BUTTON = ("Segoe UI", FONT_SIZE_BUTTON, "bold")
FONT_LOG = ("Consolas", FONT_SIZE_LOG)

LOG_HEIGHT = 12

PLACEHOLDER_SCRIPT_TEXT = "Drag & drop a Python file here or click Browse"
PLACEHOLDER_ICON_TEXT = "Optional: Select an icon file (.ico / .icns / .png)"
PLACEHOLDER_DATA_TEXT = "No data files selected"

INITIAL_LOG_MESSAGE = "--- Ready to Compile ---"

PLACEHOLDER_EXE_TEXT  = "Drag & drop an .exe here or click Browse"
PLACEHOLDER_CERT_TEXT = "Select a certificate file (.pfx)"
PLACEHOLDER_PASS_TEXT = "Certificate password"
PLACEHOLDER_PUBL_TEXT = "Publisher / company name"
SEAL_LOG_INITIAL      = "--- SEALit9 Ready ---"
FOOTER_MESSAGE = "Output will be in the script's 'dist' folder."
SIGNATURE = "Build and Design by Milo Pesqueira - DO NOT DISTRIBUTE - More info on exe9.org"


# =========================================================
# ===================== PLACEHOLDER ENTRY =================
# =========================================================

class PlaceholderEntry(tk.Entry):

    def __init__(self, master=None, placeholder="", color="grey", **kwargs):
        super().__init__(master, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = INPUT_TEXT_COLOR

        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e=None):
        if self.get() == self.placeholder:
            self.delete(0, "end")
            self.config(fg=self.default_fg_color)

    def _add_placeholder(self, e=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

    def get_real_value(self):
        val = self.get()
        if val == self.placeholder:
            return ""
        return val

    def reset(self):
        self.delete(0, "end")
        self._add_placeholder()


# =========================================================
# ===================== APPLICATION =======================
# =========================================================

class CompilerApp:

    def __init__(self, master):

        self.master = master
        master.title(APP_TITLE)
        master.geometry(WINDOW_GEOMETRY)
        master.configure(bg=BG_COLOR)

        # ── Window / taskbar icon ──────────────────────────
        _sys = platform.system()
        if _sys == "Windows" and os.path.exists(ICON_PATH):
            try:
                master.iconbitmap(ICON_PATH)
            except Exception:
                pass
        elif _sys in ("Darwin", "Linux"):
            _png_icon = resource_path("appicon.png")
            if os.path.exists(_png_icon):
                try:
                    _icon_img = tk.PhotoImage(file=_png_icon)
                    master.iconphoto(True, _icon_img)
                except Exception:
                    pass

        self.script_path = tk.StringVar(value=PLACEHOLDER_SCRIPT_TEXT)
        self.icon_path = tk.StringVar(value=PLACEHOLDER_ICON_TEXT)
        self.data_folder = tk.StringVar(value=PLACEHOLDER_DATA_TEXT)

        self._current_script_path = ""

        self.create_widgets()

    # -----------------------------------------------------

    def _make_clear_btn(self, parent, command):
        """Return a styled red Clear button."""
        btn = tk.Button(
            parent,
            text="Clear",
            command=command,
            bg=CLEAR_BUTTON_COLOR,
            fg=CLEAR_BUTTON_TEXT_COLOR,
            font=FONT_BUTTON,
            bd=0,
            padx=6
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=CLEAR_BUTTON_HOVER_COLOR))
        btn.bind("<Leave>", lambda e: btn.config(bg=CLEAR_BUTTON_COLOR))
        return btn

    # -----------------------------------------------------

    def create_widgets(self):

        # ── Logo ──────────────────────────────────────────
        if PIL_AVAILABLE and os.path.exists(LOGO_IMAGE_PATH):
            try:
                img = Image.open(LOGO_IMAGE_PATH)
                w, h = img.size
                ratio = LOGO_MAX_HEIGHT / h
                img = img.resize((int(w * ratio), LOGO_MAX_HEIGHT), Image.Resampling.LANCZOS)
                self.logo = ImageTk.PhotoImage(img)
                tk.Label(self.master, image=self.logo, bg=BG_COLOR).pack(pady=(15, 10))
            except:
                pass

        tk.Label(
            self.master,
            text=SIGNATURE,
            bg=BG_COLOR,
            fg="#02bf4e",
            font=("Segoe UI Bold", 11)
        ).pack(pady=(0, 6))

        # ── Notebook tabs ─────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("EXE9.TNotebook",
            background=BG_COLOR, borderwidth=0)
        style.configure("EXE9.TNotebook.Tab",
            background="#0c1a3a",
            foreground=LABEL_COLOR,
            font=FONT_BUTTON,
            padding=[18, 6],
            borderwidth=0)
        style.map("EXE9.TNotebook.Tab",
            background=[("selected", BG_COLOR)],
            foreground=[("selected", "#ffffff")])

        self.notebook = ttk.Notebook(self.master, style="EXE9.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 0))

        # ── Tab 1: EXE9 compiler ──────────────────────────
        self.tab_compiler = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_compiler, text="  EXE9  ")

        frame = tk.Frame(self.tab_compiler, bg=BG_COLOR)
        frame.pack(padx=60, fill="x", pady=10)

        self.create_script_row(frame)
        self.create_icon_row(frame)
        self.create_data_row(frame)

        compile_btn = tk.Button(
            self.tab_compiler,
            text="Generate EXE9" if platform.system() == "Windows" else ("Generate .app" if platform.system() == "Darwin" else "Generate Binary"),
            command=self.compile_thread,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            font=FONT_BUTTON,
            bd=0,
            padx=20,
            pady=8,
            activebackground=BUTTON_HOVER_COLOR
        )

        compile_btn.pack(pady=18)

        compile_btn.bind("<Enter>", lambda e: compile_btn.config(bg=BUTTON_HOVER_COLOR))
        compile_btn.bind("<Leave>", lambda e: compile_btn.config(bg=BUTTON_COLOR))

        # ── Progress bar ──────────────────────────────────
        progress_frame = tk.Frame(self.tab_compiler, bg=BG_COLOR)
        progress_frame.pack(fill="x", padx=50, pady=(0, 4))

        self.progress_label = tk.Label(
            progress_frame,
            text="",
            bg=BG_COLOR,
            fg=LABEL_COLOR,
            font=("Segoe UI", 9)
        )
        self.progress_label.pack(anchor="w")

        style.configure(
            "EXE9.Horizontal.TProgressbar",
            troughcolor=PROGRESS_TROUGH_COLOR,
            background=PROGRESS_COLOR,
            darkcolor=PROGRESS_COLOR,
            lightcolor=PROGRESS_COLOR,
            bordercolor=INPUT_BORDER_COLOR,
            thickness=14
        )

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style="EXE9.Horizontal.TProgressbar",
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.pack(fill="x")

        # ── Log terminal ──────────────────────────────────
        self.log = tk.Text(
            self.tab_compiler,
            height=LOG_HEIGHT,
            bg=LOG_BG_COLOR,
            fg=LOG_FG_COLOR,
            font=FONT_LOG,
            borderwidth=0
        )

        self.log.pack(fill="both", expand=True, padx=50, pady=(4, 6))
        self.log.insert(tk.END, INITIAL_LOG_MESSAGE + "\n")

        tk.Label(
            self.tab_compiler,
            text=FOOTER_MESSAGE,
            bg=BG_COLOR,
            fg="#7f8c8d",
            font=("Segoe UI", 9)
        ).pack(pady=(0, 6))

        # ── Tab 2: SEALit9 signer ─────────────────────────
        self.tab_seal = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_seal, text="  SEALit9  ")
        self.create_seal_tab()

    # -----------------------------------------------------

    def create_script_row(self, frame):

        tk.Label(frame, text="Python Script", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT_LABEL)\
            .grid(row=0, column=0, sticky="nw", pady=(8, 0))

        # ── Tall drag-and-drop zone ──────────────────────
        dnd_frame = tk.Frame(
            frame,
            bg=INPUT_BG_COLOR,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER_COLOR,
            height=DND_ZONE_HEIGHT
        )
        dnd_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        dnd_frame.grid_propagate(False)

        dnd_frame.columnconfigure(0, weight=1)
        dnd_frame.rowconfigure(0, weight=1)

        inner = tk.Frame(dnd_frame, bg=INPUT_BG_COLOR)
        inner.grid(row=0, column=0)

        # Drag-and-drop image
        self.dnd_image_ref = None
        if PIL_AVAILABLE and os.path.exists(DND_IMAGE_PATH):
            try:
                img = Image.open(DND_IMAGE_PATH)
                w, h = img.size
                ratio = DND_IMAGE_MAX_HEIGHT / h
                img = img.resize((int(w * ratio), DND_IMAGE_MAX_HEIGHT), Image.Resampling.LANCZOS)
                self.dnd_image_ref = ImageTk.PhotoImage(img)
                tk.Label(
                    inner,
                    image=self.dnd_image_ref,
                    bg=INPUT_BG_COLOR
                ).pack(pady=(6, 4))
            except:
                pass

        # Path label — updates when a file is dropped / browsed
        self.script_path_label = tk.Label(
            inner,
            text=PLACEHOLDER_SCRIPT_TEXT, #Sc-ript designed, written, and dev-eloped by Milo Lennon Pesq-ueira
            bg=INPUT_BG_COLOR,
            fg="grey",
            font=FONT_ENTRY,
            wraplength=500,
            justify="center"
        )
        self.script_path_label.pack(pady=(0, 6))

        for widget in (dnd_frame, inner, self.script_path_label):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self.handle_drop)

        # ── Button column: Browse on top, Clear below ────
        btn_col = tk.Frame(frame, bg=BG_COLOR)
        btn_col.grid(row=0, column=2, sticky="n", pady=(8, 0))

        tk.Button(
            btn_col,
            text="Browse",
            command=self.select_script,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            font=FONT_BUTTON,
            bd=0
        ).pack(fill="x")

        self._make_clear_btn(btn_col, self.clear_script).pack(fill="x", pady=(4, 0))

        frame.grid_columnconfigure(1, weight=1)

    # -----------------------------------------------------

    def _set_script_path(self, path):
        self._current_script_path = path
        self.script_path_label.config(text=path, fg=INPUT_TEXT_COLOR)

    def clear_script(self):
        self._current_script_path = ""
        self.script_path_label.config(text=PLACEHOLDER_SCRIPT_TEXT, fg="grey")

    # -----------------------------------------------------

    def create_icon_row(self, frame):

        tk.Label(frame, text="Icon File", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT_LABEL)\
            .grid(row=1, column=0, sticky="w")

        self.icon_box = PlaceholderEntry(
            frame,
            placeholder=PLACEHOLDER_ICON_TEXT,
            bg=INPUT_BG_COLOR,
            fg=INPUT_TEXT_COLOR,
            font=FONT_ENTRY,
            bd=0,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER_COLOR
        )
        self.icon_box.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        btn_col = tk.Frame(frame, bg=BG_COLOR)
        btn_col.grid(row=1, column=2)

        tk.Button(
            btn_col,
            text="Browse",
            command=self.select_icon,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            font=FONT_BUTTON,
            bd=0
        ).pack(side="left")

        self._make_clear_btn(btn_col, self.icon_box.reset).pack(side="left", padx=(4, 0))

    # -----------------------------------------------------

    def create_data_row(self, frame):

        tk.Label(frame, text="Extra Data Files", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT_LABEL)\
            .grid(row=2, column=0, sticky="nw", pady=(8, 0))

        # Listbox container
        list_frame = tk.Frame(
            frame,
            bg=INPUT_BG_COLOR,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER_COLOR
        )
        list_frame.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.data_listbox = tk.Listbox(
            list_frame,
            bg=INPUT_BG_COLOR,
            fg=INPUT_TEXT_COLOR,
            font=FONT_ENTRY,
            selectbackground="#1a3a6a",
            selectforeground=INPUT_TEXT_COLOR, #Script designed, written, and developed by Milo Lennon Pesqueira
            borderwidth=0,
            highlightthickness=0,
            height=4,
            activestyle="none"
        )
        self.data_listbox.pack(fill="both", expand=True, padx=4, pady=4)

        # Placeholder text item
        self.data_listbox.insert(tk.END, PLACEHOLDER_DATA_TEXT)
        self.data_listbox.config(fg="grey")

        btn_col = tk.Frame(frame, bg=BG_COLOR)
        btn_col.grid(row=2, column=2, sticky="n", pady=(8, 0))

        tk.Button(
            btn_col,
            text="Add",
            command=self.select_data,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            font=FONT_BUTTON,
            bd=0
        ).pack(fill="x")

        self._make_clear_btn(btn_col, self.clear_data_files).pack(fill="x", pady=(4, 0))

    # -----------------------------------------------------

    def handle_drop(self, event):
        path = event.data.strip("{}")
        if path.lower().endswith(".py"):
            self._set_script_path(path)
            self.update_log(f"Script dropped: {path}")

    # -----------------------------------------------------

    def update_log(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.master.update_idletasks()

    # -----------------------------------------------------

    def _set_progress(self, value, label=""):
        """Thread-safe progress + label update."""
        self.master.after(0, lambda: self.progress_var.set(value))
        if label:
            self.master.after(0, lambda: self.progress_label.config(text=label))

    def _reset_progress(self):
        self.master.after(0, lambda: self.progress_var.set(0))
        self.master.after(0, lambda: self.progress_label.config(text=""))

    # -----------------------------------------------------

    def select_script(self):
        path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if path:
            self._set_script_path(path)

    def select_icon(self):
        _sys = platform.system()
        if _sys == "Darwin":
            filetypes = [("Icon Files", "*.icns"), ("PNG Images", "*.png"), ("All Files", "*.*")]
        elif _sys == "Linux":
            filetypes = [("PNG Images", "*.png"), ("Icon Files", "*.ico"), ("All Files", "*.*")]
        else:
            filetypes = [("Icon Files", "*.ico"), ("All Files", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.icon_box.delete(0, tk.END)
            self.icon_box.insert(0, path)

    def select_data(self):
        paths = filedialog.askopenfilenames(title="Select data files to bundle")
        if paths:
            # Remove placeholder if still showing
            if self.data_listbox.size() == 1 and self.data_listbox.get(0) == PLACEHOLDER_DATA_TEXT:
                self.data_listbox.delete(0)
                self.data_listbox.config(fg=INPUT_TEXT_COLOR)
            for p in paths:
                # Avoid duplicates
                existing = list(self.data_listbox.get(0, tk.END))
                if p not in existing:
                    self.data_listbox.insert(tk.END, p)

    def clear_data_files(self):
        self.data_listbox.delete(0, tk.END)
        self.data_listbox.insert(tk.END, PLACEHOLDER_DATA_TEXT)
        self.data_listbox.config(fg="grey")

    # -----------------------------------------------------

    def compile_thread(self):
        threading.Thread(target=self.compile_script, daemon=True).start()

    # -----------------------------------------------------

    # PyInstaller output keywords mapped to progress milestones
    PROGRESS_MILESTONES = [
        ("Building PKG",        15, "Building package..."),
        ("checking PKG",        20, "Checking package..."),
        ("Building EXE",        30, "Building EXE..."),
        ("Appending PKG",       45, "Appending package to EXE..."),
        ("Building COLLECT",    55, "Collecting files..."),
        ("Analyzing",           65, "Analyzing dependencies..."),
        ("Processing",          75, "Processing..."),
        ("Copying",             82, "Copying files..."),
        ("Writing",             90, "Writing output..."),
        ("successfully built",  98, "Finishing up..."),
    ]

    def compile_script(self):

        script = self._current_script_path

        if not os.path.exists(script):
            self.update_log("ERROR: Invalid Python script.")
            return

        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--clean",
            "--noconfirm",
            "--windowed"
        ]

        icon = self.icon_box.get_real_value()
        _sys = platform.system()
        valid_icon_exts = {
            "Windows": (".ico",),
            "Darwin":  (".icns", ".png"),
            "Linux":   (".png", ".ico"),
        }.get(_sys, (".ico",))
        if os.path.exists(icon) and icon.lower().endswith(valid_icon_exts):
            command.extend(["--icon", icon])

        data_files = list(self.data_listbox.get(0, tk.END))
        if data_files and data_files[0] != PLACEHOLDER_DATA_TEXT:
            for data in data_files:
                if os.path.exists(data):
                    if os.path.isdir(data):
                        data_arg = f"{data}{os.pathsep}{os.path.basename(data)}"
                    else:
                        data_arg = f"{data}{os.pathsep}."
                    command.extend(["--add-data", data_arg])

        command.append(script)

        self.update_log("\n--- Starting Compilation ---")
        self.update_log("Running PyInstaller...")
        self._set_progress(5, "Starting compilation...")

        try:
            creation_flags = 0
            if platform.system() == "Windows":
                creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creation_flags,
                cwd=os.path.dirname(script)
            )

            for line in process.stdout:
                line = line.rstrip()
                self.update_log(line)

                # Advance bar on recognized milestone lines
                for keyword, value, label in self.PROGRESS_MILESTONES:
                    if keyword.lower() in line.lower():
                        self._set_progress(value, label)
                        break

            process.wait()

            if process.returncode == 0:
                self._set_progress(100, "Complete!")
                _sys = platform.system()
                dist_path = os.path.join(os.path.dirname(script), "dist")
                if _sys == "Darwin":
                    self.update_log("\nSUCCESS: .app bundle created!")
                elif _sys == "Linux":
                    self.update_log("\nSUCCESS: Binary created!")
                else:
                    exe_name = os.path.splitext(os.path.basename(script))[0] + ".exe"
                    compiled_exe = os.path.join(dist_path, exe_name)
                    self._last_compiled_exe = compiled_exe
                    self.master.after(0, self._autofill_seal_exe)
                    self.update_log("\nSUCCESS: EXE Created")
                self.update_log(f"Check: {dist_path}")
            else:
                self._set_progress(0, "Compilation failed.")
                self.update_log("\nCompilation failed.")

        except Exception as e:
            self._reset_progress()
            self.update_log(f"FATAL ERROR: {e}")


    # =========================================================
    # ====================== SEALit9 TAB ======================
    # =========================================================

    def create_seal_tab(self):
        """Build the SEALit9 signing tab."""

        self._last_compiled_exe = ""
        pad = dict(padx=60)

        # ── Signing mode dropdown ─────────────────────────
        mode_frame = tk.Frame(self.tab_seal, bg=BG_COLOR)
        mode_frame.pack(fill="x", pady=(18, 4), **pad)

        tk.Label(
            mode_frame,
            text="Signing Mode",
            bg=BG_COLOR,
            fg=LABEL_COLOR,
            font=FONT_LABEL
        ).pack(side="left", padx=(0, 14))

        self.seal_mode = tk.StringVar(value="Certificate")
        mode_menu = ttk.Combobox(
            mode_frame,
            textvariable=self.seal_mode,
            values=["Certificate", "Self-Signed Certificate"],
            state="readonly",
            font=FONT_ENTRY,
            width=28
        )
        mode_menu.pack(side="left")
        mode_menu.bind("<<ComboboxSelected>>", lambda e: self._seal_mode_changed())

        # Style the combobox to match the theme
        style = ttk.Style()
        style.configure("TCombobox",
            fieldbackground=INPUT_BG_COLOR,
            background=INPUT_BG_COLOR,
            foreground=INPUT_TEXT_COLOR,
            selectbackground=INPUT_BG_COLOR,
            selectforeground=INPUT_TEXT_COLOR,
            bordercolor=INPUT_BORDER_COLOR,
            arrowcolor=LABEL_COLOR
        )

        # ── EXE drag-and-drop zone ────────────────────────
        exe_label_frame = tk.Frame(self.tab_seal, bg=BG_COLOR)
        exe_label_frame.pack(fill="x", pady=(12, 0), **pad)
        tk.Label(
            exe_label_frame,
            text="Executable File",
            bg=BG_COLOR,
            fg=LABEL_COLOR,
            font=FONT_LABEL
        ).pack(side="left")

        exe_row = tk.Frame(self.tab_seal, bg=BG_COLOR)
        exe_row.pack(fill="x", pady=(4, 0), **pad)
        exe_row.columnconfigure(0, weight=1)

        dnd_frame = tk.Frame(
            exe_row,
            bg=INPUT_BG_COLOR,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER_COLOR,
            height=DND_ZONE_HEIGHT
        )
        dnd_frame.pack(side="left", fill="x", expand=True)
        dnd_frame.pack_propagate(False)
        dnd_frame.columnconfigure(0, weight=1)
        dnd_frame.rowconfigure(0, weight=1)

        inner = tk.Frame(dnd_frame, bg=INPUT_BG_COLOR)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        self.seal_dnd_image_ref = None
        if PIL_AVAILABLE and os.path.exists(DND_IMAGE_PATH):
            try:
                img = Image.open(DND_IMAGE_PATH)
                w, h = img.size
                ratio = DND_IMAGE_MAX_HEIGHT / h
                img = img.resize((int(w * ratio), DND_IMAGE_MAX_HEIGHT), Image.Resampling.LANCZOS)
                self.seal_dnd_image_ref = ImageTk.PhotoImage(img)
                tk.Label(inner, image=self.seal_dnd_image_ref, bg=INPUT_BG_COLOR).pack(pady=(0, 4))
            except:
                pass

        self.seal_exe_label = tk.Label(
            inner,
            text=PLACEHOLDER_EXE_TEXT,
            bg=INPUT_BG_COLOR,
            fg="grey",
            font=FONT_ENTRY,
            wraplength=480,
            justify="center"
        )
        self.seal_exe_label.pack()

        for widget in (dnd_frame, inner, self.seal_exe_label):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._seal_exe_drop)

        exe_btn_col = tk.Frame(exe_row, bg=BG_COLOR)
        exe_btn_col.pack(side="left", padx=(10, 0), anchor="n")

        tk.Button(
            exe_btn_col,
            text="Browse",
            command=self._seal_browse_exe,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            font=FONT_BUTTON,
            bd=0
        ).pack(fill="x")
        self._make_clear_btn(exe_btn_col, self._seal_clear_exe).pack(fill="x", pady=(4, 0))

        # ── Certificate fields (hidden in self-sign mode) ─
        self.seal_cert_frame = tk.Frame(self.tab_seal, bg=BG_COLOR)
        self.seal_cert_frame.pack(fill="x", pady=(10, 0), **pad)

        cert_grid = tk.Frame(self.seal_cert_frame, bg=BG_COLOR)
        cert_grid.pack(fill="x")
        cert_grid.columnconfigure(1, weight=1)

        tk.Label(cert_grid, text="Certificate (.pfx)", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT_LABEL)            .grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.seal_cert_box = PlaceholderEntry(
            cert_grid,
            placeholder=PLACEHOLDER_CERT_TEXT,
            bg=INPUT_BG_COLOR,
            fg=INPUT_TEXT_COLOR,
            font=FONT_ENTRY,
            bd=0,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER_COLOR
        )
        self.seal_cert_box.grid(row=0, column=1, padx=10, sticky="ew")

        cert_btn_col = tk.Frame(cert_grid, bg=BG_COLOR)
        cert_btn_col.grid(row=0, column=2)
        tk.Button(
            cert_btn_col,
            text="Browse",
            command=self._seal_browse_cert,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            font=FONT_BUTTON,
            bd=0
        ).pack(side="left")
        self._make_clear_btn(cert_btn_col, self.seal_cert_box.reset).pack(side="left", padx=(4, 0))

        tk.Label(cert_grid, text="Password", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT_LABEL)            .grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.seal_pass_box = PlaceholderEntry(
            cert_grid,
            placeholder=PLACEHOLDER_PASS_TEXT,
            bg=INPUT_BG_COLOR,
            fg=INPUT_TEXT_COLOR,
            font=FONT_ENTRY,
            bd=0,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER_COLOR,
            show=""
        )
        self.seal_pass_box.grid(row=1, column=1, padx=10, pady=(6, 0), sticky="ew")
        # Show actual password characters once focused
        self.seal_pass_box.bind("<FocusIn>", lambda e: (
            self.seal_pass_box._clear_placeholder(e),
            self.seal_pass_box.config(show="●")
        ))
        self.seal_pass_box.bind("<FocusOut>", lambda e: (
            self.seal_pass_box._add_placeholder(e),
            self.seal_pass_box.config(show="" if self.seal_pass_box.get() == PLACEHOLDER_PASS_TEXT else "●")
        ))

        self._make_clear_btn(
            cert_grid,
            lambda: (self.seal_pass_box.reset(), self.seal_pass_box.config(show=""))
        ).grid(row=1, column=2, pady=(6, 0), sticky="w", padx=(4, 0))

        # ── Publisher name field (shown in self-sign mode) ─
        self.seal_pub_frame = tk.Frame(self.tab_seal, bg=BG_COLOR)
        # not packed yet — shown only in self-sign mode

        pub_grid = tk.Frame(self.seal_pub_frame, bg=BG_COLOR)
        pub_grid.pack(fill="x")
        pub_grid.columnconfigure(1, weight=1)

        tk.Label(pub_grid, text="Publisher Name", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT_LABEL)            .grid(row=0, column=0, sticky="w")

        self.seal_pub_box = PlaceholderEntry(
            pub_grid,
            placeholder=PLACEHOLDER_PUBL_TEXT,
            bg=INPUT_BG_COLOR,
            fg=INPUT_TEXT_COLOR,
            font=FONT_ENTRY,
            bd=0,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER_COLOR
        )
        self.seal_pub_box.grid(row=0, column=1, padx=10, sticky="ew")
        self._make_clear_btn(pub_grid, self.seal_pub_box.reset).grid(row=0, column=2)

        # ── Sign button ───────────────────────────────────
        self._seal_sign_btn = tk.Button(
            self.tab_seal,
            text="SEALit9",
            command=self._seal_thread,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            font=FONT_BUTTON,
            bd=0,
            padx=20,
            pady=8,
            activebackground=BUTTON_HOVER_COLOR
        )
        self._seal_sign_btn.pack(pady=16)
        self._seal_sign_btn.bind("<Enter>", lambda e: self._seal_sign_btn.config(bg=BUTTON_HOVER_COLOR))
        self._seal_sign_btn.bind("<Leave>", lambda e: self._seal_sign_btn.config(bg=BUTTON_COLOR))

        # ── SEALit9 log ───────────────────────────────────
        self.seal_log = tk.Text(
            self.tab_seal,
            height=LOG_HEIGHT,
            bg=LOG_BG_COLOR,
            fg=LOG_FG_COLOR,
            font=FONT_LOG,
            borderwidth=0
        )
        self.seal_log.pack(fill="both", expand=True, padx=50, pady=(0, 6))
        self.seal_log.insert(tk.END, SEAL_LOG_INITIAL + "\n")

        tk.Label(
            self.tab_seal,
            text="Signed files are saved alongside the original executable.",
            bg=BG_COLOR,
            fg="#7f8c8d",
            font=("Segoe UI", 9)
        ).pack(pady=(0, 6))

        # Apply initial mode state
        self._seal_mode_changed()

    # ---------------------------------------------------------

    def _seal_mode_changed(self):
        mode = self.seal_mode.get()
        if mode == "Self-Signed Certificate":
            self.seal_cert_frame.pack_forget()
            self.seal_pub_frame.pack(fill="x", pady=(10, 0), padx=60, before=self._seal_sign_btn)
        else:
            self.seal_pub_frame.pack_forget()
            self.seal_cert_frame.pack(fill="x", pady=(10, 0), padx=60, before=self._seal_sign_btn)

    def _seal_exe_drop(self, event):
        path = event.data.strip("{}")
        if path.lower().endswith(".exe"):
            self._seal_set_exe(path)

    def _seal_set_exe(self, path):
        self._seal_exe_path = path
        self.seal_exe_label.config(text=path, fg=INPUT_TEXT_COLOR)

    def _seal_clear_exe(self):
        self._seal_exe_path = ""
        self.seal_exe_label.config(text=PLACEHOLDER_EXE_TEXT, fg="grey")

    def _seal_browse_exe(self):
        path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
        if path:
            self._seal_set_exe(path)

    def _seal_browse_cert(self):
        path = filedialog.askopenfilename(filetypes=[("PFX Certificate", "*.pfx"), ("All Files", "*.*")])
        if path:
            self.seal_cert_box.delete(0, tk.END)
            self.seal_cert_box.insert(0, path)
            self.seal_cert_box.config(fg=INPUT_TEXT_COLOR)

    def _autofill_seal_exe(self):
        if self._last_compiled_exe and os.path.exists(self._last_compiled_exe):
            self._seal_set_exe(self._last_compiled_exe)
            self.notebook.select(self.tab_seal)

    def _seal_log(self, text):
        self.seal_log.insert(tk.END, text + "\n")
        self.seal_log.see(tk.END)
        self.master.update_idletasks()

    def _seal_thread(self):
        threading.Thread(target=self._seal_sign, daemon=True).start()

    # ---------------------------------------------------------

    def _find_signtool(self):
        """Locate signtool.exe from Windows SDK, preferring correct architecture."""
        import shutil
        import struct
        arch = "x64" if struct.calcsize("P") == 8 else "x86"

        common = [
            r"C:\Program Files (x86)\Windows Kits\10\bin",
            r"C:\Program Files\Windows Kits\10\bin",
        ]

        # Collect all candidates, score arch-matched ones higher
        candidates = []
        for base in common:
            if os.path.isdir(base):
                for root, dirs, files in os.walk(base):
                    if "signtool.exe" in files:
                        path = os.path.join(root, "signtool.exe")
                        score = 1 if arch in root.lower() else 0
                        candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]

        # Fall back to PATH
        return shutil.which("signtool") or ""

    def _seal_sign(self):

        exe = getattr(self, "_seal_exe_path", "")
        if not exe or not os.path.exists(exe):
            self._seal_log("ERROR: No valid .exe file selected.")
            return

        if platform.system() != "Windows":
            self._seal_log("ERROR: Signing with signtool is only supported on Windows.")
            return

        signtool = self._find_signtool()
        if not signtool:
            self._seal_log(
                "ERROR: signtool.exe not found.\n"
                "Install the Windows 10/11 SDK from:\n"
                "https://developer.microsoft.com/windows/downloads/windows-sdk/"
            )
            return

        mode = self.seal_mode.get()
        self._seal_log(f"\n--- Starting SEALit9 [{mode}] ---")
        self._seal_log(f"Target: {exe}")

        if mode == "Self-Signed Certificate":
            self._seal_sign_self(exe, signtool)
        else:
            self._seal_sign_cert(exe, signtool)

    def _seal_sign_cert(self, exe, signtool):
        cert = self.seal_cert_box.get_real_value()
        password = self.seal_pass_box.get_real_value()

        if not cert or not os.path.exists(cert):
            self._seal_log("ERROR: No valid certificate file selected.")
            return

        cmd = [signtool, "sign", "/fd", "SHA256", "/f", cert]
        if password:
            cmd += ["/p", password]
        cmd += ["/tr", "http://timestamp.digicert.com", "/td", "SHA256", exe]

        self._seal_log("Running signtool...")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.stdout:
                self._seal_log(result.stdout.strip())
            if result.stderr:
                self._seal_log(result.stderr.strip())
            if result.returncode == 0:
                self._seal_log("\nSUCCESS: File signed successfully.")
            else:
                self._seal_log(f"\nFAILED: signtool exited with code {result.returncode}.")
        except Exception as e:
            self._seal_log(f"FATAL ERROR: {e}")

    def _seal_sign_self(self, exe, signtool):
        publisher = self.seal_pub_box.get_real_value()
        if not publisher:
            self._seal_log("ERROR: Please enter a publisher name.")
            return

        self._seal_log(f"Generating self-signed certificate for: {publisher}")

        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives.serialization import pkcs12
            import datetime

            # Generate key
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

            # Build self-signed cert
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, publisher),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, publisher),
            ])
            now = datetime.datetime.utcnow()
            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(now)
                .not_valid_after(now + datetime.timedelta(days=3650))
                .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
                .sign(key, hashes.SHA256())
            )

            # Export as .pfx to a temp file
            pfx_data = pkcs12.serialize_key_and_certificates(
                name=publisher.encode(),
                key=key,
                cert=cert,
                cas=None,
                encryption_algorithm=serialization.BestAvailableEncryption(b"selfsigned_temp")
            )

            with tempfile.NamedTemporaryFile(suffix=".pfx", delete=False) as f:
                f.write(pfx_data)
                pfx_path = f.name

            self._seal_log("Certificate generated. Signing...")

            cmd = [
                signtool, "sign",
                "/fd", "SHA256",
                "/f", pfx_path,
                "/p", "selfsigned_temp",
                "/tr", "http://timestamp.digicert.com",
                "/td", "SHA256",
                exe
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.stdout:
                self._seal_log(result.stdout.strip())
            if result.stderr:
                self._seal_log(result.stderr.strip())

            os.unlink(pfx_path)

            if result.returncode == 0:
                self._seal_log(f"\nSUCCESS: File self-signed as '{publisher}'.")
                self._seal_log("Note: This signature proves ownership but will still")
                self._seal_log("show 'Unknown Publisher' warnings on other machines.")
            else:
                self._seal_log(f"\nFAILED: signtool exited with code {result.returncode}.")

        except ImportError:
            self._seal_log(
                "ERROR: The \'cryptography\' library is required for self-signing.\n"
                "Run:  pip install cryptography"
            )
        except Exception as e:
            self._seal_log(f"FATAL ERROR: {e}")


# =========================================================
# ===================== START APP =========================
# =========================================================

if __name__ == "__main__":

    root = TkinterDnD.Tk()
    root.tk.call('tk', 'scaling', 1.4)

    app = CompilerApp(root)

    root.mainloop()