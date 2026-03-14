"""
NovaPay Desktop Banking Application
Tkinter GUI - Professional Dark Theme
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import requests
import json
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api"

# ─── THEME PALETTE ───────────────────────────────────────────────────────────
COLORS = {
    "bg": "#F9FAFB",
    "sidebar_bg": "#FFFFFF",
    "sidebar_border": "#E5E7EB",
    "primary": "#0057FF",
    "primary_dark": "#0040CC",
    "primary_light": "#EEF3FF",
    "white": "#FFFFFF",
    "dark": "#0A0F1E",
    "gray900": "#1A1F36",
    "gray700": "#374151",
    "gray500": "#6B7280",
    "gray300": "#D1D5DB",
    "gray100": "#F3F4F6",
    "border": "#E5E7EB",
    "success": "#00C896",
    "danger": "#FF4757",
    "warning": "#FFB300",
    "success_bg": "#E6FBF5",
    "danger_bg": "#FFE8EC",
    "warning_bg": "#FFF8E6",
    "card_shadow": "#00000010",
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "subheading": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "logo": ("Segoe UI", 16, "bold"),
    "mono": ("Courier New", 10),
    "amount": ("Segoe UI", 22, "bold"),
}


# ─── API CLIENT ───────────────────────────────────────────────────────────────
class APIClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{API_BASE}{endpoint}"
        try:
            resp = self.session.request(
                method, url,
                headers=self._headers(),
                json=data,
                params=params,
                timeout=10
            )
            return resp
        except requests.ConnectionError:
            raise Exception("Cannot connect to server. Make sure the Django server is running.")
        except requests.Timeout:
            raise Exception("Request timed out.")

    def get(self, endpoint, params=None):
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data):
        return self._request("POST", endpoint, data=data)

    def patch(self, endpoint, data):
        return self._request("PATCH", endpoint, data=data)

    def login(self, username, password):
        resp = self.post("/auth/login/", {"username": username, "password": password})
        if resp.status_code == 200:
            data = resp.json()
            self.access_token = data["tokens"]["access"]
            self.refresh_token = data["tokens"]["refresh"]
            return data["user"]
        raise Exception(resp.json().get("error", "Login failed"))

    def register(self, form_data):
        resp = self.post("/auth/register/", form_data)
        if resp.status_code == 201:
            data = resp.json()
            self.access_token = data["tokens"]["access"]
            self.refresh_token = data["tokens"]["refresh"]
            return data["user"]
        errors = resp.json()
        msg = "; ".join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in errors.items()])
        raise Exception(msg)


api = APIClient()


# ─── HELPER WIDGETS ──────────────────────────────────────────────────────────

def card_frame(parent, padx=16, pady=16, **kwargs):
    """A white card with border"""
    f = tk.Frame(parent, bg=COLORS["white"], bd=1, relief="solid",
                 highlightbackground=COLORS["border"], highlightthickness=1, **kwargs)
    return f


def styled_button(parent, text, command, style="primary", width=None, icon=""):
    bg = {"primary": COLORS["primary"], "danger": COLORS["danger"],
          "success": COLORS["success"], "outline": COLORS["white"],
          "ghost": COLORS["bg"]}.get(style, COLORS["primary"])
    fg = {"outline": COLORS["primary"], "ghost": COLORS["gray700"]}.get(style, COLORS["white"])
    label = f"{icon} {text}".strip() if icon else text
    kwargs = dict(text=label, command=command, bg=bg, fg=fg,
                  font=FONTS["body_bold"], relief="flat", cursor="hand2",
                  padx=12, pady=6, bd=0)
    if width:
        kwargs["width"] = width
    btn = tk.Button(parent, **kwargs)
    btn.bind("<Enter>", lambda e: btn.config(bg=_hover(bg)))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def _hover(color):
    """Darken hex color slightly"""
    c = color.lstrip("#")
    if len(c) != 6:
        return color
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return f"#{max(0,r-20):02x}{max(0,g-20):02x}{max(0,b-20):02x}"


def section_label(parent, text):
    lbl = tk.Label(parent, text=text.upper(), font=("Segoe UI", 8, "bold"),
                   bg=COLORS["sidebar_bg"], fg=COLORS["gray500"])
    return lbl


# ─── LOGIN WINDOW ─────────────────────────────────────────────────────────────
class LoginWindow(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success
        self.title("NovaPay — Sign In")
        self.geometry("440x580")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])
        self.grab_set()
        self._center()
        self._build()

    def _center(self):
        self.update_idletasks()
        w, h = 440, 580
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        # Header
        header = tk.Frame(self, bg=COLORS["primary"], height=8)
        header.pack(fill="x")

        container = tk.Frame(self, bg=COLORS["white"], padx=40, pady=30)
        container.pack(fill="both", expand=True, padx=24, pady=20)

        # Logo
        logo_frame = tk.Frame(container, bg=COLORS["white"])
        logo_frame.pack(pady=(0, 24))
        tk.Label(logo_frame, text="🛡 NovaPay", font=FONTS["title"],
                 bg=COLORS["white"], fg=COLORS["dark"]).pack()
        tk.Label(logo_frame, text="Secure Digital Banking", font=FONTS["small"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack()

        # Title
        tk.Label(container, text="Welcome back", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="w")
        tk.Label(container, text="Sign in to your account", font=FONTS["body"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w", pady=(2, 16))

        # Username
        tk.Label(container, text="Username", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
        self.username_var = tk.StringVar()
        un_entry = ttk.Entry(container, textvariable=self.username_var, font=FONTS["body"], width=30)
        un_entry.pack(fill="x", ipady=6, pady=(4, 12))
        un_entry.focus()

        # Password
        tk.Label(container, text="Password", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
        self.pw_var = tk.StringVar()
        pw_entry = ttk.Entry(container, textvariable=self.pw_var, show="●",
                             font=FONTS["body"], width=30)
        pw_entry.pack(fill="x", ipady=6, pady=(4, 16))
        pw_entry.bind("<Return>", lambda e: self._login())

        # Error label
        self.error_var = tk.StringVar()
        self.error_lbl = tk.Label(container, textvariable=self.error_var,
                                  font=FONTS["small"], bg=COLORS["danger_bg"],
                                  fg=COLORS["danger"], wraplength=320, padx=8, pady=6)

        # Login button
        self.login_btn = styled_button(container, "Sign In", self._login, "primary", icon="→")
        self.login_btn.pack(fill="x", ipady=4, pady=(0, 12))

        # Register link
        reg_frame = tk.Frame(container, bg=COLORS["white"])
        reg_frame.pack()
        tk.Label(reg_frame, text="Don't have an account?", font=FONTS["small"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack(side="left")
        reg_link = tk.Label(reg_frame, text=" Create account", font=FONTS["small"],
                            bg=COLORS["white"], fg=COLORS["primary"], cursor="hand2")
        reg_link.pack(side="left")
        reg_link.bind("<Button-1>", lambda e: self._open_register())

        # SSL note
        tk.Label(container, text="🔒 256-bit SSL encrypted", font=("Segoe UI", 8),
                 bg=COLORS["white"], fg=COLORS["gray300"]).pack(pady=(16, 0))

    def _login(self):
        username = self.username_var.get().strip()
        password = self.pw_var.get()
        if not username or not password:
            self._show_error("Please enter username and password")
            return
        self.login_btn.config(state="disabled", text="Signing in…")
        self.update()

        def do_login():
            try:
                user = api.login(username, password)
                self.after(0, lambda: self._success(user))
            except Exception as ex:
                self.after(0, lambda: self._show_error(str(ex)))
                self.after(0, lambda: self.login_btn.config(state="normal", text="→ Sign In"))

        threading.Thread(target=do_login, daemon=True).start()

    def _success(self, user):
        self.destroy()
        self.on_success(user)

    def _show_error(self, msg):
        self.error_var.set(f"⚠  {msg}")
        self.error_lbl.pack(fill="x", pady=(0, 8))

    def _open_register(self):
        self.destroy()
        RegisterWindow(self.master, self.on_success)


# ─── REGISTER WINDOW ──────────────────────────────────────────────────────────
class RegisterWindow(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success
        self.title("NovaPay — Create Account")
        self.geometry("480x680")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])
        self.grab_set()
        self._center()
        self._build()

    def _center(self):
        self.update_idletasks()
        w, h = 480, 680
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        header = tk.Frame(self, bg=COLORS["primary"], height=8)
        header.pack(fill="x")
        container = tk.Frame(self, bg=COLORS["white"], padx=40, pady=24)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        tk.Label(container, text="Create Account", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="w")
        tk.Label(container, text="Join NovaPay — start banking securely", font=FONTS["body"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w", pady=(2, 16))

        self.vars = {}
        fields = [
            ("first_name", "First Name", ""),
            ("last_name", "Last Name", ""),
            ("username", "Username", ""),
            ("email", "Email Address", ""),
            ("phone", "Phone Number", ""),
            ("password", "Password", "●"),
            ("password2", "Confirm Password", "●"),
        ]

        for key, label, show in fields:
            tk.Label(container, text=label, font=FONTS["body_bold"],
                     bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
            self.vars[key] = tk.StringVar()
            entry = ttk.Entry(container, textvariable=self.vars[key],
                              font=FONTS["body"], show=show if show else "")
            entry.pack(fill="x", ipady=5, pady=(2, 10))

        self.error_var = tk.StringVar()
        self.error_lbl = tk.Label(container, textvariable=self.error_var,
                                  font=FONTS["small"], bg=COLORS["danger_bg"],
                                  fg=COLORS["danger"], wraplength=360, padx=8, pady=6)

        self.reg_btn = styled_button(container, "Create Account", self._register, "primary", icon="✓")
        self.reg_btn.pack(fill="x", ipady=4, pady=(4, 10))

        reg_frame = tk.Frame(container, bg=COLORS["white"])
        reg_frame.pack()
        tk.Label(reg_frame, text="Already have an account?", font=FONTS["small"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack(side="left")
        link = tk.Label(reg_frame, text=" Sign in", font=FONTS["small"],
                        bg=COLORS["white"], fg=COLORS["primary"], cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._go_login())

    def _register(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        if data["password"] != data["password2"]:
            self._show_error("Passwords don't match")
            return
        if not all([data["first_name"], data["username"], data["email"], data["password"]]):
            self._show_error("Please fill in all required fields")
            return
        self.reg_btn.config(state="disabled", text="Creating account…")
        self.update()

        def do_register():
            try:
                user = api.register(data)
                self.after(0, lambda: self._success(user))
            except Exception as ex:
                self.after(0, lambda: self._show_error(str(ex)))
                self.after(0, lambda: self.reg_btn.config(state="normal", text="✓ Create Account"))

        threading.Thread(target=do_register, daemon=True).start()

    def _success(self, user):
        self.destroy()
        self.on_success(user)

    def _show_error(self, msg):
        self.error_var.set(f"⚠  {msg}")
        self.error_lbl.pack(fill="x", pady=(0, 8))

    def _go_login(self):
        self.destroy()
        LoginWindow(self.master, self.on_success)


# ─── MAIN APPLICATION ─────────────────────────────────────────────────────────
class NovaPay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NovaPay Desktop Banking")
        self.geometry("1100x680")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg"])
        self.user = None
        self.current_page = None
        self._withdraw_root()
        self._setup_styles()
        self.after(100, self._show_login)

    def _withdraw_root(self):
        self.withdraw()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure("TEntry", padding=4)
        style.configure("Treeview",
                        background=COLORS["white"],
                        fieldbackground=COLORS["white"],
                        foreground=COLORS["gray900"],
                        rowheight=36,
                        font=FONTS["body"])
        style.configure("Treeview.Heading",
                        font=FONTS["body_bold"],
                        background=COLORS["gray100"],
                        foreground=COLORS["gray700"])
        style.map("Treeview", background=[("selected", COLORS["primary_light"])],
                  foreground=[("selected", COLORS["primary"])])
        style.configure("TScrollbar", background=COLORS["gray100"])

    def _show_login(self):
        LoginWindow(self, self._on_login)

    def _on_login(self, user):
        self.user = user
        self.deiconify()
        self._build_main()

    def _build_main(self):
        # Clear window
        for w in self.winfo_children():
            w.destroy()

        # Layout: sidebar + content
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=220,
                                bd=0, relief="flat",
                                highlightbackground=COLORS["border"],
                                highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._navigate("dashboard")

    def _build_sidebar(self):
        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"], pady=16)
        logo_frame.pack(fill="x", padx=16)
        tk.Label(logo_frame, text="🛡 NovaPay", font=FONTS["logo"],
                 bg=COLORS["sidebar_bg"], fg=COLORS["dark"]).pack(side="left")

        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x")

        # Nav items
        nav_scroll = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        nav_scroll.pack(fill="both", expand=True, pady=8)

        NAV = [
            ("Main Menu", None),
            ("  Dashboard", "dashboard", "⊞"),
            ("  Accounts", "accounts", "◈"),
            ("  Transactions", "transactions", "⇄"),
            ("  Transfer", "transfer", "➤"),
            ("Banking Services", None),
            ("  Cards", "cards", "▣"),
            ("  Loans", "loans", "⊕"),
            ("  Beneficiaries", "beneficiaries", "♥"),
            ("Account", None),
            ("  Profile", "profile", "◉"),
        ]

        self.nav_buttons = {}
        for item in NAV:
            if len(item) == 2 and item[1] is None:
                # Section label
                section_label(nav_scroll, item[0]).pack(anchor="w", padx=12, pady=(10, 2))
            else:
                label, page, icon = item
                btn = self._nav_btn(nav_scroll, f"{icon} {label.strip()}", page)
                self.nav_buttons[page] = btn

        # Bottom: user + logout
        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", side="bottom")
        bottom = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"], pady=10)
        bottom.pack(fill="x", side="bottom", padx=12)

        name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip() or self.user.get('username', 'User')
        tk.Label(bottom, text=f"◉ {name}", font=FONTS["body_bold"],
                 bg=COLORS["sidebar_bg"], fg=COLORS["gray900"]).pack(anchor="w")
        tk.Label(bottom, text=self.user.get('email', ''), font=FONTS["small"],
                 bg=COLORS["sidebar_bg"], fg=COLORS["gray500"]).pack(anchor="w")
        logout_btn = tk.Label(bottom, text="⇤ Sign Out", font=FONTS["small"],
                              bg=COLORS["sidebar_bg"], fg=COLORS["danger"], cursor="hand2")
        logout_btn.pack(anchor="w", pady=(6, 0))
        logout_btn.bind("<Button-1>", lambda e: self._logout())

    def _nav_btn(self, parent, text, page):
        btn = tk.Button(parent, text=text, font=FONTS["body"],
                        bg=COLORS["sidebar_bg"], fg=COLORS["gray700"],
                        relief="flat", anchor="w", cursor="hand2",
                        padx=12, pady=7,
                        command=lambda p=page: self._navigate(p))
        btn.pack(fill="x", padx=4, pady=1)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["gray100"]))
        btn.bind("<Leave>", lambda e, b=btn, p=page: b.config(
            bg=COLORS["primary_light"] if self.current_page == p else COLORS["sidebar_bg"]))
        return btn

    def _navigate(self, page):
        self.current_page = page
        # Update nav button colors
        for p, btn in self.nav_buttons.items():
            if p == page:
                btn.config(bg=COLORS["primary_light"], fg=COLORS["primary"],
                           font=FONTS["body_bold"])
            else:
                btn.config(bg=COLORS["sidebar_bg"], fg=COLORS["gray700"],
                           font=FONTS["body"])

        # Clear content
        for w in self.content.winfo_children():
            w.destroy()

        # Build page
        pages = {
            "dashboard": DashboardPage,
            "accounts": AccountsPage,
            "transactions": TransactionsPage,
            "transfer": TransferPage,
            "cards": CardsPage,
            "loans": LoansPage,
            "beneficiaries": BeneficiariesPage,
            "profile": ProfilePage,
        }
        cls = pages.get(page, DashboardPage)
        cls(self.content, self.user, self._navigate).pack(fill="both", expand=True)

    def _logout(self):
        if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
            api.access_token = None
            api.refresh_token = None
            self.withdraw()
            self._show_login()


# ─── PAGE BASE ────────────────────────────────────────────────────────────────
class BasePage(tk.Frame):
    def __init__(self, master, user, navigate):
        super().__init__(master, bg=COLORS["bg"])
        self.user = user
        self.navigate = navigate

    def topbar(self, title, subtitle=""):
        bar = tk.Frame(self, bg=COLORS["white"],
                       highlightbackground=COLORS["border"], highlightthickness=1)
        bar.pack(fill="x")
        inner = tk.Frame(bar, bg=COLORS["white"], pady=12)
        inner.pack(fill="x", padx=20)
        tk.Label(inner, text=title, font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["dark"]).pack(side="left")
        if subtitle:
            tk.Label(inner, text=f"  {subtitle}", font=FONTS["small"],
                     bg=COLORS["white"], fg=COLORS["gray500"]).pack(side="left")

    def scroll_area(self):
        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scroll.set)

        frame = tk.Frame(canvas, bg=COLORS["bg"])
        window = canvas.create_window((0, 0), window=frame, anchor="nw")

        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(e):
            canvas.itemconfig(window, width=e.width)

        frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        return frame

    def stat_card(self, parent, label, value, icon, color, change=""):
        card = tk.Frame(parent, bg=COLORS["white"], bd=1, relief="flat",
                        highlightbackground=COLORS["border"], highlightthickness=1)
        inner = tk.Frame(card, bg=COLORS["white"], padx=16, pady=14)
        inner.pack(fill="both")

        # Icon circle
        icon_lbl = tk.Label(inner, text=icon, font=("Segoe UI", 14),
                            bg=COLORS.get(f"{color}_bg", COLORS["primary_light"]),
                            fg=COLORS.get(color, COLORS["primary"]),
                            width=3, height=1)
        icon_lbl.pack(side="left", padx=(0, 12))

        info = tk.Frame(inner, bg=COLORS["white"])
        info.pack(side="left")
        tk.Label(info, text=label, font=FONTS["small"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w")
        tk.Label(info, text=str(value), font=FONTS["amount"],
                 bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="w")
        if change:
            tk.Label(info, text=change, font=FONTS["small"],
                     bg=COLORS["white"], fg=COLORS["success"]).pack(anchor="w")
        return card

    def loading_label(self, parent, text="Loading…"):
        lbl = tk.Label(parent, text=f"⟳  {text}", font=FONTS["body"],
                       bg=COLORS["bg"], fg=COLORS["gray500"])
        lbl.pack(pady=30)
        return lbl

    def empty_label(self, parent, text="No data found"):
        lbl = tk.Label(parent, text=f"⊘  {text}", font=FONTS["body"],
                       bg=COLORS["bg"], fg=COLORS["gray300"])
        lbl.pack(pady=40)

    def alert(self, parent, msg, kind="success"):
        colors = {"success": (COLORS["success_bg"], COLORS["success"]),
                  "error": (COLORS["danger_bg"], COLORS["danger"]),
                  "info": (COLORS["primary_light"], COLORS["primary"])}
        bg, fg = colors.get(kind, (COLORS["gray100"], COLORS["gray700"]))
        icons = {"success": "✓", "error": "✗", "info": "ℹ"}
        icon = icons.get(kind, "•")
        frm = tk.Frame(parent, bg=bg, padx=10, pady=8)
        frm.pack(fill="x", padx=20, pady=(8, 0))
        tk.Label(frm, text=f"{icon}  {msg}", font=FONTS["body"],
                 bg=bg, fg=fg, wraplength=700, justify="left").pack(anchor="w")
        self.after(5000, frm.destroy)

    def fetch_async(self, fn, callback):
        def worker():
            try:
                result = fn()
                self.after(0, lambda: callback(result, None))
            except Exception as e:
                self.after(0, lambda: callback(None, e))
        threading.Thread(target=worker, daemon=True).start()


# ─── DASHBOARD PAGE ───────────────────────────────────────────────────────────
class DashboardPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("Dashboard", f"Welcome back, {user.get('first_name', user.get('username', ''))}!")
        self.scroll_frame = self.scroll_area()
        self._load()

    def _load(self):
        lbl = self.loading_label(self.scroll_frame)
        self.fetch_async(
            lambda: api.get("/dashboard/").json(),
            lambda data, err: self._render(data, err, lbl)
        )

    def _render(self, data, err, lbl):
        lbl.destroy()
        if err:
            self.empty_label(self.scroll_frame, f"Error: {err}")
            return

        content = tk.Frame(self.scroll_frame, bg=COLORS["bg"], padx=20, pady=16)
        content.pack(fill="both", expand=True)

        # Stats row
        stats_row = tk.Frame(content, bg=COLORS["bg"])
        stats_row.pack(fill="x", pady=(0, 16))
        stats = [
            ("Total Balance", f"${float(data.get('total_balance', 0)):,.2f}", "💰", "success", "↑ 3.2% this month"),
            ("Active Cards", str(data.get("active_cards", 0)), "💳", "primary", "Debit & Credit"),
            ("Active Loans", str(data.get("active_loans", 0)), "🏦", "warning", "Outstanding"),
            ("Notifications", str(data.get("unread_notifications", 0)), "🔔", "danger", "Unread"),
        ]
        for label, value, icon, color, change in stats:
            card = self.stat_card(stats_row, label, value, icon, color, change)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Quick actions
        qa_frame = tk.LabelFrame(content, text=" Quick Actions ", font=FONTS["subheading"],
                                  bg=COLORS["white"], fg=COLORS["gray700"],
                                  bd=1, relief="flat",
                                  highlightbackground=COLORS["border"], highlightthickness=1)
        qa_frame.pack(fill="x", pady=(0, 16))
        inner = tk.Frame(qa_frame, bg=COLORS["white"], pady=12, padx=12)
        inner.pack()
        for label, page, icon in [
            ("Deposit", "accounts", "⬇"), ("Withdraw", "accounts", "⬆"),
            ("Transfer", "transfer", "➤"), ("Pay Bill", "transactions", "◉"),
            ("View Cards", "cards", "▣"), ("Apply Loan", "loans", "⊕"),
        ]:
            btn = tk.Frame(inner, bg=COLORS["white"], cursor="hand2")
            btn.pack(side="left", padx=8)
            icon_lbl = tk.Label(btn, text=icon, font=("Segoe UI", 18),
                                 bg=COLORS["primary_light"], fg=COLORS["primary"],
                                 width=3, height=1)
            icon_lbl.pack()
            tk.Label(btn, text=label, font=FONTS["small"],
                     bg=COLORS["white"], fg=COLORS["gray700"]).pack()
            for w in [btn, icon_lbl]:
                w.bind("<Button-1>", lambda e, p=page: self.navigate(p))
                w.bind("<Enter>", lambda e, b=icon_lbl: b.config(bg=COLORS["primary"], fg=COLORS["white"]))
                w.bind("<Leave>", lambda e, b=icon_lbl: b.config(bg=COLORS["primary_light"], fg=COLORS["primary"]))

        # Recent transactions
        txn_frame = tk.LabelFrame(content, text=" Recent Transactions ", font=FONTS["subheading"],
                                   bg=COLORS["white"], fg=COLORS["gray700"],
                                   bd=1, relief="flat",
                                   highlightbackground=COLORS["border"], highlightthickness=1)
        txn_frame.pack(fill="x")

        txns = data.get("recent_transactions", [])
        if not txns:
            tk.Label(txn_frame, text="No recent transactions", font=FONTS["body"],
                     bg=COLORS["white"], fg=COLORS["gray300"], pady=20).pack()
        else:
            for txn in txns[:8]:
                self._txn_row(txn_frame, txn)

    def _txn_row(self, parent, txn):
        row = tk.Frame(parent, bg=COLORS["white"],
                       highlightbackground=COLORS["gray100"], highlightthickness=1)
        row.pack(fill="x", padx=12, pady=2)
        inner = tk.Frame(row, bg=COLORS["white"], pady=8, padx=8)
        inner.pack(fill="x")

        type_colors = {"DEPOSIT": COLORS["success"], "WITHDRAWAL": COLORS["danger"],
                       "TRANSFER": COLORS["primary"]}
        icons = {"DEPOSIT": "⬇", "WITHDRAWAL": "⬆", "TRANSFER": "⇄", "PAYMENT": "◉"}
        t = txn.get("transaction_type", "")
        color = type_colors.get(t, COLORS["gray500"])
        icon = icons.get(t, "•")

        tk.Label(inner, text=icon, font=("Segoe UI", 12), bg=COLORS["white"],
                 fg=color).pack(side="left", padx=(0, 10))

        info = tk.Frame(inner, bg=COLORS["white"])
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=txn.get("description") or t, font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray900"]).pack(anchor="w")
        date_str = txn.get("created_at", "")[:16].replace("T", " ") if txn.get("created_at") else ""
        tk.Label(info, text=f"{date_str}  ·  Ref: {txn.get('reference', '')[:12]}…",
                 font=FONTS["small"], bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w")

        is_credit = t in ("DEPOSIT", "REFUND")
        amount_color = COLORS["success"] if is_credit else COLORS["danger"]
        prefix = "+" if is_credit else "-"
        tk.Label(inner, text=f"{prefix}${float(txn.get('amount', 0)):,.2f}",
                 font=FONTS["body_bold"], bg=COLORS["white"],
                 fg=amount_color).pack(side="right")


# ─── ACCOUNTS PAGE ────────────────────────────────────────────────────────────
class AccountsPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("My Accounts")
        self.scroll_frame = self.scroll_area()
        self._load()

    def _load(self):
        lbl = self.loading_label(self.scroll_frame)
        self.fetch_async(
            lambda: api.get("/accounts/").json(),
            lambda data, err: self._render(data, err, lbl)
        )

    def _render(self, data, err, lbl):
        lbl.destroy()
        if err:
            self.empty_label(self.scroll_frame, str(err))
            return

        content = tk.Frame(self.scroll_frame, bg=COLORS["bg"], padx=20, pady=16)
        content.pack(fill="both", expand=True)

        # Header with New Account button
        hdr = tk.Frame(content, bg=COLORS["bg"])
        hdr.pack(fill="x", pady=(0, 16))
        tk.Label(hdr, text=f"{len(data)} account(s)", font=FONTS["body"],
                 bg=COLORS["bg"], fg=COLORS["gray500"]).pack(side="left")
        styled_button(hdr, "New Account", lambda: self._create_account(content), "primary", icon="+").pack(side="right")

        if not data:
            self.empty_label(content, "No accounts yet. Open your first account!")
            return

        for acc in data:
            self._account_card(content, acc)

    def _account_card(self, parent, acc):
        card = tk.Frame(parent, bg=COLORS["white"],
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0, 12))
        inner = tk.Frame(card, bg=COLORS["white"], padx=16, pady=14)
        inner.pack(fill="x")

        # Left
        left = tk.Frame(inner, bg=COLORS["white"])
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text=f"{acc.get('account_type', '')} Account",
                 font=FONTS["subheading"], bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="w")
        tk.Label(left, text=acc.get("account_number", ""), font=FONTS["mono"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w")
        status = acc.get("status", "")
        status_color = {"ACTIVE": COLORS["success"], "FROZEN": COLORS["danger"]}.get(status, COLORS["gray500"])
        tk.Label(left, text=f"● {status}", font=FONTS["small"],
                 bg=COLORS["white"], fg=status_color).pack(anchor="w", pady=(4, 0))

        # Right
        right = tk.Frame(inner, bg=COLORS["white"])
        right.pack(side="right")
        tk.Label(right, text=f"{acc.get('currency', '')} {float(acc.get('balance', 0)):,.2f}",
                 font=FONTS["amount"], bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="e")
        tk.Label(right, text=f"Available: {float(acc.get('available_balance', 0)):,.2f}",
                 font=FONTS["small"], bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="e")

        btn_row = tk.Frame(inner, bg=COLORS["white"])
        btn_row.pack(fill="x", pady=(10, 0))
        styled_button(btn_row, "Deposit", lambda a=acc: self._deposit(a), "primary", icon="⬇").pack(side="left", padx=(0, 8))
        styled_button(btn_row, "Withdraw", lambda a=acc: self._withdraw(a), "outline", icon="⬆").pack(side="left")

    def _deposit(self, acc):
        amount = simpledialog.askfloat("Deposit", f"Enter amount to deposit to {acc['account_number']}:", minvalue=1)
        if not amount:
            return
        desc = simpledialog.askstring("Description", "Narration (optional):", initialvalue="Deposit")

        def do():
            try:
                resp = api.post("/transactions/deposit/", {"account_id": acc["id"], "amount": amount, "description": desc or "Deposit"})
                if resp.status_code == 201:
                    self.after(0, lambda: messagebox.showinfo("Success", f"${amount:,.2f} deposited successfully!"))
                    self.after(0, self._load)
                else:
                    msg = resp.json().get("error", "Deposit failed")
                    self.after(0, lambda: messagebox.showerror("Error", msg))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=do, daemon=True).start()

    def _withdraw(self, acc):
        amount = simpledialog.askfloat("Withdraw", f"Enter amount (Available: {acc['available_balance']}):", minvalue=1)
        if not amount:
            return
        desc = simpledialog.askstring("Description", "Narration (optional):", initialvalue="Withdrawal")

        def do():
            try:
                resp = api.post("/transactions/withdraw/", {"account_id": acc["id"], "amount": amount, "description": desc or "Withdrawal"})
                if resp.status_code == 201:
                    self.after(0, lambda: messagebox.showinfo("Success", f"${amount:,.2f} withdrawn successfully!"))
                    self.after(0, self._load)
                else:
                    msg = resp.json().get("error", "Withdrawal failed")
                    self.after(0, lambda: messagebox.showerror("Error", msg))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=do, daemon=True).start()

    def _create_account(self, parent):
        acc_type = simpledialog.askstring("New Account", "Account type (SAVINGS/CHECKING/BUSINESS/FIXED):", initialvalue="SAVINGS")
        if not acc_type:
            return
        currency = simpledialog.askstring("Currency", "Currency (USD/EUR/GBP/KES):", initialvalue="USD")
        if not currency:
            return

        def do():
            try:
                resp = api.post("/accounts/", {"account_type": acc_type.upper(), "currency": currency.upper()})
                if resp.status_code == 201:
                    self.after(0, lambda: messagebox.showinfo("Success", "New account created!"))
                    self.after(0, self._load)
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "Failed to create account"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=do, daemon=True).start()


# ─── TRANSACTIONS PAGE ────────────────────────────────────────────────────────
class TransactionsPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("Transaction History")
        self._build()

    def _build(self):
        content = tk.Frame(self, bg=COLORS["bg"], padx=20, pady=16)
        content.pack(fill="both", expand=True)

        # Treeview
        cols = ("Date", "Type", "Description", "Reference", "Amount", "Status")
        tree_frame = tk.Frame(content, bg=COLORS["white"],
                              highlightbackground=COLORS["border"], highlightthickness=1)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        widths = {"Date": 140, "Type": 100, "Description": 200, "Reference": 160, "Amount": 110, "Status": 90}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 120), anchor="center" if col in ("Type", "Amount", "Status") else "w")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Bottom controls
        bottom = tk.Frame(content, bg=COLORS["bg"], pady=8)
        bottom.pack(fill="x")
        styled_button(bottom, "Refresh", self._load, "primary", icon="⟳").pack(side="left")
        tk.Label(bottom, textvariable=(self.count_var := tk.StringVar(value="")),
                 font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["gray500"]).pack(side="right")

        self._load()

    def _load(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.count_var.set("Loading…")

        def do():
            try:
                resp = api.get("/transactions/")
                txns = resp.json() if resp.status_code == 200 else []
                self.after(0, lambda: self._populate(txns))
            except Exception as e:
                self.after(0, lambda: self.count_var.set(f"Error: {e}"))

        threading.Thread(target=do, daemon=True).start()

    def _populate(self, txns):
        self.count_var.set(f"{len(txns)} transaction(s)")
        TYPE_SIGNS = {"DEPOSIT": "+", "REFUND": "+"}
        for txn in txns:
            t = txn.get("transaction_type", "")
            amount = float(txn.get("amount", 0))
            sign = TYPE_SIGNS.get(t, "-")
            date = txn.get("created_at", "")[:16].replace("T", " ")
            self.tree.insert("", "end", values=(
                date, t, txn.get("description") or t,
                txn.get("reference", ""),
                f"{sign}${amount:,.2f}",
                txn.get("status", "")
            ))
            item = self.tree.get_children()[-1]
            if sign == "+":
                self.tree.item(item, tags=("credit",))
            else:
                self.tree.item(item, tags=("debit",))

        self.tree.tag_configure("credit", foreground=COLORS["success"])
        self.tree.tag_configure("debit", foreground=COLORS["danger"])


# ─── TRANSFER PAGE ────────────────────────────────────────────────────────────
class TransferPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("Transfer Money", "Send funds securely")
        self.accounts = []
        self._build()
        self._load_accounts()

    def _build(self):
        outer = tk.Frame(self, bg=COLORS["bg"], padx=60, pady=30)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=COLORS["white"],
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", pady=20, ipadx=20, ipady=16)

        tk.Label(card, text="➤  Send Money", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="w", padx=20, pady=(16, 4))
        tk.Label(card, text="Transfer funds to any NovaPay account", font=FONTS["body"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w", padx=20, pady=(0, 16))

        form = tk.Frame(card, bg=COLORS["white"], padx=20)
        form.pack(fill="x")

        # From Account
        tk.Label(form, text="From Account", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
        self.from_var = tk.StringVar()
        self.from_combo = ttk.Combobox(form, textvariable=self.from_var, state="readonly", font=FONTS["body"])
        self.from_combo.pack(fill="x", ipady=5, pady=(4, 12))

        # To Account
        tk.Label(form, text="Recipient Account Number", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
        self.to_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.to_var, font=FONTS["mono"]).pack(fill="x", ipady=5, pady=(4, 12))

        # Amount
        tk.Label(form, text="Amount", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
        self.amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.amount_var, font=FONTS["body"]).pack(fill="x", ipady=5, pady=(4, 12))

        # Description
        tk.Label(form, text="Narration (optional)", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
        self.desc_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.desc_var, font=FONTS["body"]).pack(fill="x", ipady=5, pady=(4, 12))

        self.alert_frame = tk.Frame(card, bg=COLORS["white"])
        self.alert_frame.pack(fill="x", padx=20)

        btn_row = tk.Frame(card, bg=COLORS["white"], padx=20, pady=(0, 16))
        btn_row.pack(fill="x")
        styled_button(btn_row, "Send Transfer", self._transfer, "primary", icon="➤").pack(side="left", ipady=4)

    def _load_accounts(self):
        def do():
            try:
                resp = api.get("/accounts/")
                accs = resp.json() if resp.status_code == 200 else []
                self.accounts = accs
                labels = [f"{a['account_type']} — {a['account_number']} (${float(a['balance']):,.2f})" for a in accs]
                self.after(0, lambda: self.from_combo.config(values=labels))
                if labels:
                    self.after(0, lambda: self.from_combo.current(0))
            except:
                pass
        threading.Thread(target=do, daemon=True).start()

    def _transfer(self):
        idx = self.from_combo.current()
        if idx < 0 or not self.accounts:
            messagebox.showwarning("Warning", "Please select a source account")
            return
        from_account = self.accounts[idx]
        to_number = self.to_var.get().strip()
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Enter a valid amount")
            return
        if not to_number:
            messagebox.showwarning("Warning", "Enter recipient account number")
            return

        fee = amount * 0.001
        total = amount + fee
        confirm = messagebox.askyesno(
            "Confirm Transfer",
            f"Transfer Details:\n\n"
            f"From: {from_account['account_number']}\n"
            f"To:   {to_number}\n"
            f"Amount: ${amount:,.2f}\n"
            f"Fee:    ${fee:.2f}\n"
            f"Total:  ${total:,.2f}\n\n"
            f"Proceed?"
        )
        if not confirm:
            return

        def do():
            try:
                resp = api.post("/transactions/transfer/", {
                    "from_account_id": from_account["id"],
                    "to_account_number": to_number,
                    "amount": amount,
                    "description": self.desc_var.get() or "Transfer"
                })
                if resp.status_code == 201:
                    self.after(0, lambda: messagebox.showinfo("Success", f"Transfer of ${amount:,.2f} completed!"))
                    self.after(0, lambda: [v.set("") for v in (self.to_var, self.amount_var, self.desc_var)])
                    self.after(0, self._load_accounts)
                else:
                    msg = resp.json().get("error", "Transfer failed")
                    self.after(0, lambda: messagebox.showerror("Error", msg))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=do, daemon=True).start()


# ─── CARDS PAGE ───────────────────────────────────────────────────────────────
class CardsPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("My Cards")
        self.scroll_frame = self.scroll_area()
        self._load()

    def _load(self):
        lbl = self.loading_label(self.scroll_frame)
        self.fetch_async(
            lambda: api.get("/cards/").json(),
            lambda data, err: self._render(data, err, lbl)
        )

    def _render(self, data, err, lbl):
        lbl.destroy()
        if err or not isinstance(data, list):
            self.empty_label(self.scroll_frame, "No cards found.")
            return

        content = tk.Frame(self.scroll_frame, bg=COLORS["bg"], padx=20, pady=16)
        content.pack(fill="both", expand=True)

        if not data:
            self.empty_label(content, "No cards linked to your accounts.")
            return

        for card in data:
            card_widget = tk.Frame(content, bg=COLORS["white"],
                                   highlightbackground=COLORS["border"], highlightthickness=1)
            card_widget.pack(fill="x", pady=(0, 12))

            # Card visual
            visual = tk.Frame(card_widget, bg=COLORS["gray900"], height=100)
            visual.pack(fill="x")

            vis_inner = tk.Frame(visual, bg=COLORS["gray900"], padx=16, pady=10)
            vis_inner.pack(fill="x")
            tk.Label(vis_inner, text="▣  " + card.get("network", ""), font=FONTS["subheading"],
                     bg=COLORS["gray900"], fg="white").pack(side="left")
            tk.Label(vis_inner, text=card.get("card_type", ""), font=FONTS["body"],
                     bg=COLORS["gray900"], fg=COLORS["gray300"]).pack(side="right")

            num_row = tk.Frame(visual, bg=COLORS["gray900"], padx=16)
            num_row.pack(fill="x")
            tk.Label(num_row, text=card.get("masked_number", "****  ****  ****  ****"),
                     font=FONTS["mono"], bg=COLORS["gray900"], fg="white").pack(anchor="w")

            # Details
            info = tk.Frame(card_widget, bg=COLORS["white"], padx=16, pady=12)
            info.pack(fill="x")
            tk.Label(info, text=card.get("card_holder_name", ""), font=FONTS["subheading"],
                     bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="w")
            tk.Label(info, text=f"Expires: {str(card.get('expiry_month', '')).zfill(2)}/{str(card.get('expiry_year', ''))[-2:]}  |  Limit: ${float(card.get('spending_limit', 0)):,.0f}",
                     font=FONTS["small"], bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w")

            status = card.get("status", "ACTIVE")
            status_color = COLORS["success"] if status == "ACTIVE" else COLORS["danger"]
            tk.Label(info, text=f"● {status}", font=FONTS["body_bold"],
                     bg=COLORS["white"], fg=status_color).pack(anchor="w", pady=(4, 8))

            label = "Block Card" if status == "ACTIVE" else "Activate Card"
            btn_style = "danger" if status == "ACTIVE" else "success"
            styled_button(info, label, lambda c=card: self._toggle(c), btn_style).pack(anchor="w")

    def _toggle(self, card):
        action = "block" if card.get("status") == "ACTIVE" else "activate"
        if not messagebox.askyesno("Confirm", f"Are you sure you want to {action} this card?"):
            return

        def do():
            try:
                resp = api.post(f"/cards/{card['id']}/toggle/", {})
                if resp.status_code == 200:
                    self.after(0, lambda: messagebox.showinfo("Success", f"Card {action}d successfully!"))
                    self.after(0, self._load)
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "Failed to update card"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=do, daemon=True).start()


# ─── LOANS PAGE ───────────────────────────────────────────────────────────────
class LoansPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("Loans")
        self.scroll_frame = self.scroll_area()
        self._load()

    def _load(self):
        lbl = self.loading_label(self.scroll_frame)
        self.fetch_async(
            lambda: api.get("/loans/").json(),
            lambda data, err: self._render(data, err, lbl)
        )

    def _render(self, data, err, lbl):
        lbl.destroy()
        if err:
            self.empty_label(self.scroll_frame, str(err))
            return

        content = tk.Frame(self.scroll_frame, bg=COLORS["bg"], padx=20, pady=16)
        content.pack(fill="both", expand=True)

        hdr = tk.Frame(content, bg=COLORS["bg"])
        hdr.pack(fill="x", pady=(0, 16))
        tk.Label(hdr, text=f"{len(data)} loan(s)", font=FONTS["body"],
                 bg=COLORS["bg"], fg=COLORS["gray500"]).pack(side="left")
        styled_button(hdr, "Apply for Loan", self._apply, "primary", icon="+").pack(side="right")

        if not data:
            self.empty_label(content, "No loan applications yet.")
            return

        STATUS_COLORS = {"PENDING": COLORS["warning"], "ACTIVE": COLORS["success"],
                         "APPROVED": COLORS["primary"], "REJECTED": COLORS["danger"], "PAID": COLORS["gray500"]}

        for loan in data:
            card = tk.Frame(content, bg=COLORS["white"],
                            highlightbackground=COLORS["border"], highlightthickness=1)
            card.pack(fill="x", pady=(0, 10))
            inner = tk.Frame(card, bg=COLORS["white"], padx=16, pady=12)
            inner.pack(fill="x")

            top = tk.Frame(inner, bg=COLORS["white"])
            top.pack(fill="x")
            tk.Label(top, text=f"{loan.get('loan_type', '')} Loan",
                     font=FONTS["subheading"], bg=COLORS["white"], fg=COLORS["dark"]).pack(side="left")
            status = loan.get("status", "")
            tk.Label(top, text=f"  {status}  ", font=FONTS["small"],
                     bg=STATUS_COLORS.get(status, COLORS["gray500"]), fg="white").pack(side="right")

            details = tk.Frame(inner, bg=COLORS["white"])
            details.pack(fill="x", pady=(8, 0))
            for label, value in [
                ("Principal", f"${float(loan.get('principal_amount', 0)):,.2f}"),
                ("Outstanding", f"${float(loan.get('outstanding_balance', 0)):,.2f}"),
                ("Monthly EMI", f"${float(loan.get('monthly_installment', 0)):,.2f}"),
                ("Rate", f"{loan.get('interest_rate', 0)}% p.a."),
                ("Tenure", f"{loan.get('tenure_months', 0)} months"),
            ]:
                col = tk.Frame(details, bg=COLORS["white"])
                col.pack(side="left", padx=(0, 24))
                tk.Label(col, text=label, font=FONTS["small"],
                         bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w")
                tk.Label(col, text=value, font=FONTS["body_bold"],
                         bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="w")

    def _apply(self):
        win = tk.Toplevel(self)
        win.title("Loan Application")
        win.geometry("440x480")
        win.configure(bg=COLORS["white"])
        win.grab_set()

        tk.Label(win, text="Apply for Loan", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["dark"]).pack(pady=(20, 4), padx=24, anchor="w")

        form = tk.Frame(win, bg=COLORS["white"], padx=24)
        form.pack(fill="x")

        fields = {}
        labels_and_defaults = [
            ("account_id", "Account ID (paste from accounts)", ""),
            ("loan_type", "Loan Type (PERSONAL/MORTGAGE/AUTO/BUSINESS/STUDENT)", "PERSONAL"),
            ("amount", "Loan Amount (USD)", ""),
            ("tenure_months", "Tenure in Months", "12"),
            ("purpose", "Purpose (optional)", ""),
        ]
        for key, lbl, default in labels_and_defaults:
            tk.Label(form, text=lbl, font=FONTS["body_bold"], bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w", pady=(8, 2))
            var = tk.StringVar(value=default)
            fields[key] = var
            ttk.Entry(form, textvariable=var, font=FONTS["body"]).pack(fill="x", ipady=4)

        def submit():
            try:
                resp = api.post("/loans/apply/", {
                    "account_id": fields["account_id"].get().strip(),
                    "loan_type": fields["loan_type"].get().strip().upper(),
                    "amount": float(fields["amount"].get()),
                    "tenure_months": int(fields["tenure_months"].get()),
                    "purpose": fields["purpose"].get(),
                })
                if resp.status_code == 201:
                    messagebox.showinfo("Success", "Loan application submitted!")
                    win.destroy()
                    self._load()
                else:
                    errors = resp.json()
                    messagebox.showerror("Error", str(errors))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        styled_button(form, "Submit Application", submit, "primary", icon="✓").pack(fill="x", pady=16, ipady=4)


# ─── BENEFICIARIES PAGE ───────────────────────────────────────────────────────
class BeneficiariesPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("Beneficiaries")
        self.scroll_frame = self.scroll_area()
        self._load()

    def _load(self):
        lbl = self.loading_label(self.scroll_frame)
        self.fetch_async(
            lambda: api.get("/beneficiaries/").json(),
            lambda data, err: self._render(data, err, lbl)
        )

    def _render(self, data, err, lbl):
        lbl.destroy()
        content = tk.Frame(self.scroll_frame, bg=COLORS["bg"], padx=20, pady=16)
        content.pack(fill="both", expand=True)

        hdr = tk.Frame(content, bg=COLORS["bg"])
        hdr.pack(fill="x", pady=(0, 16))
        styled_button(hdr, "Add Beneficiary", self._add, "primary", icon="+").pack(side="right")

        if not data:
            self.empty_label(content, "No saved beneficiaries.")
            return

        cols = ("Name", "Account Number", "Bank", "Nickname", "Favorite")
        self.tree = ttk.Treeview(content, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        for b in data:
            self.tree.insert("", "end", values=(
                b.get("name"), b.get("account_number"),
                b.get("bank_name", "—"), b.get("nickname", "—"),
                "★" if b.get("is_favorite") else ""
            ))
        self.tree.pack(fill="both", expand=True)

    def _add(self):
        name = simpledialog.askstring("Add Beneficiary", "Full Name:")
        if not name: return
        account_number = simpledialog.askstring("Add Beneficiary", "Account Number:")
        if not account_number: return
        bank = simpledialog.askstring("Add Beneficiary", "Bank Name (optional):", initialvalue="")
        nick = simpledialog.askstring("Add Beneficiary", "Nickname (optional):", initialvalue="")

        def do():
            try:
                resp = api.post("/beneficiaries/", {"name": name, "account_number": account_number, "bank_name": bank or "", "nickname": nick or ""})
                if resp.status_code == 201:
                    self.after(0, lambda: messagebox.showinfo("Success", "Beneficiary added!"))
                    self.after(0, self._load)
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "Failed to add beneficiary"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=do, daemon=True).start()


# ─── PROFILE PAGE ─────────────────────────────────────────────────────────────
class ProfilePage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("Profile Settings")
        self._build()

    def _build(self):
        outer = tk.Frame(self, bg=COLORS["bg"], padx=40, pady=20)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=COLORS["white"],
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", pady=20)
        inner = tk.Frame(card, bg=COLORS["white"], padx=24, pady=20)
        inner.pack(fill="x")

        # Avatar
        initials = (self.user.get("first_name", "")[:1] + self.user.get("last_name", "")[:1]).upper() or self.user.get("username", "U")[:1].upper()
        avatar = tk.Label(inner, text=initials, font=FONTS["title"],
                          bg=COLORS["primary"], fg="white", width=3, height=1)
        avatar.pack(side="left", padx=(0, 20))

        info = tk.Frame(inner, bg=COLORS["white"])
        info.pack(side="left")
        name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip() or self.user.get("username", "")
        tk.Label(info, text=name, font=FONTS["heading"], bg=COLORS["white"], fg=COLORS["dark"]).pack(anchor="w")
        tk.Label(info, text=f"@{self.user.get('username', '')}  ·  {self.user.get('email', '')}",
                 font=FONTS["body"], bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w")
        verified = "✓ Verified" if self.user.get("is_verified") else "⊘ Not Verified"
        v_color = COLORS["success"] if self.user.get("is_verified") else COLORS["warning"]
        tk.Label(info, text=verified, font=FONTS["body_bold"], bg=COLORS["white"], fg=v_color).pack(anchor="w", pady=(4, 0))

        # Change Password
        pw_frame = tk.LabelFrame(outer, text=" Change Password ", font=FONTS["subheading"],
                                  bg=COLORS["white"], fg=COLORS["gray700"],
                                  bd=1, relief="flat",
                                  highlightbackground=COLORS["border"], highlightthickness=1)
        pw_frame.pack(fill="x")
        form = tk.Frame(pw_frame, bg=COLORS["white"], padx=20, pady=16)
        form.pack(fill="x")

        self.old_pw = tk.StringVar()
        self.new_pw = tk.StringVar()
        for label, var in [("Current Password", self.old_pw), ("New Password", self.new_pw)]:
            tk.Label(form, text=label, font=FONTS["body_bold"], bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
            ttk.Entry(form, textvariable=var, show="●", font=FONTS["body"]).pack(fill="x", ipady=5, pady=(4, 10))

        styled_button(form, "Update Password", self._change_pw, "primary", icon="🔒").pack(anchor="w")

    def _change_pw(self):
        old = self.old_pw.get()
        new = self.new_pw.get()
        if not old or not new:
            messagebox.showwarning("Warning", "Please fill in both password fields")
            return

        def do():
            try:
                resp = api.post("/profile/change-password/", {"old_password": old, "new_password": new})
                if resp.status_code == 200:
                    self.after(0, lambda: messagebox.showinfo("Success", "Password changed successfully!"))
                    self.after(0, lambda: [self.old_pw.set(""), self.new_pw.set("")])
                else:
                    msg = resp.json().get("error", "Failed to change password")
                    self.after(0, lambda: messagebox.showerror("Error", msg))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=do, daemon=True).start()


# ─── ANALYTICS PAGE ──────────────────────────────────────────────────────────
class AnalyticsPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("Analytics", "Spending insights & account statements")
        self.scroll_frame = self.scroll_area()
        self.stmt_accounts = []
        self.stmt_acc_var = tk.StringVar()
        self.stmt_start = tk.StringVar()
        self.stmt_end = tk.StringVar()
        self.stmt_tree_frame = None
        self._load()

    def _load(self):
        lbl = self.loading_label(self.scroll_frame, "Loading analytics...")
        self.fetch_async(
            lambda: api.get("/analytics/spending/").json(),
            lambda data, err: self._render(data, err, lbl)
        )

    def _render(self, data, err, lbl):
        lbl.destroy()
        if err or not isinstance(data, dict):
            self.empty_label(self.scroll_frame, f"Analytics unavailable: {err}")
            return

        content = tk.Frame(self.scroll_frame, bg=COLORS["bg"], padx=20, pady=16)
        content.pack(fill="both", expand=True)

        monthly = data.get("monthly", [])
        breakdown = data.get("current_month_breakdown", [])
        current = monthly[-1] if monthly else {}
        prev = monthly[-2] if len(monthly) > 1 else {}

        def pct_change(now, prev_val):
            if prev_val and prev_val != 0:
                return f"{((now - prev_val) / abs(prev_val) * 100):+.1f}% vs last month"
            return "No prior data"

        stats_row = tk.Frame(content, bg=COLORS["bg"])
        stats_row.pack(fill="x", pady=(0, 16))

        for label, value, icon, color, change in [
            ("This Month Income",   f"${current.get(chr(105)+chr(110)+chr(99)+chr(111)+chr(109)+chr(101), 0):,.0f}",   "💰", "success", pct_change(current.get("income", 0), prev.get("income", 0))),
            ("This Month Expenses", f"${current.get('expenses', 0):,.0f}", "💸", "danger",  pct_change(current.get("expenses", 0), prev.get("expenses", 0))),
            ("Net Cash Flow",       f"${current.get('net', 0):,.0f}",      "📊", "primary", "Surplus" if current.get("net", 0) >= 0 else "Deficit"),
        ]:
            card = self.stat_card(stats_row, label, value, icon, color, change)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # 6-month table
        tbl_frame = tk.LabelFrame(content, text=" 6-Month Summary ", font=FONTS["subheading"],
                                   bg=COLORS["white"], fg=COLORS["gray700"],
                                   bd=1, relief="flat",
                                   highlightbackground=COLORS["border"], highlightthickness=1)
        tbl_frame.pack(fill="x", pady=(0, 16))

        cols = ("Month", "Income", "Expenses", "Net")
        tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=6)
        for col, w in zip(cols, [100, 130, 130, 130]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")

        for m in reversed(monthly):
            net = m.get("net", 0)
            tree.insert("", "end", values=(
                f"{m[chr(109)+chr(111)+chr(110)+chr(116)+chr(104)]} {m[chr(121)+chr(101)+chr(97)+chr(114)]}",
                f"${m.get(chr(105)+chr(110)+chr(99)+chr(111)+chr(109)+chr(101),0):,.2f}",
                f"${m.get(chr(101)+chr(120)+chr(112)+chr(101)+chr(110)+chr(115)+chr(101)+chr(115),0):,.2f}",
                f"${net:,.2f}",
            ), tags=("pos" if net >= 0 else "neg",))

        tree.tag_configure("pos", foreground=COLORS["success"])
        tree.tag_configure("neg", foreground=COLORS["danger"])
        tree.pack(fill="x", padx=12, pady=10)

        # Breakdown bars
        if breakdown:
            bk_frame = tk.LabelFrame(content, text=" Transaction Breakdown - This Month ",
                                      font=FONTS["subheading"],
                                      bg=COLORS["white"], fg=COLORS["gray700"],
                                      bd=1, relief="flat",
                                      highlightbackground=COLORS["border"], highlightthickness=1)
            bk_frame.pack(fill="x", pady=(0, 16))
            inner = tk.Frame(bk_frame, bg=COLORS["white"], padx=12, pady=10)
            inner.pack(fill="x")
            total_vol = sum(float(b.get("total", 0)) for b in breakdown) or 1
            for b in breakdown:
                row = tk.Frame(inner, bg=COLORS["white"])
                row.pack(fill="x", pady=3)
                lbl_text = f"{b.get('transaction_type','')} ({b.get('count',0)} txns)"
                tk.Label(row, text=lbl_text, font=FONTS["body"], bg=COLORS["white"],
                         fg=COLORS["gray700"], width=28, anchor="w").pack(side="left")
                bar_w = 220
                pct = float(b.get("total", 0)) / total_vol
                canvas = tk.Canvas(row, width=bar_w, height=12, bg=COLORS["gray100"], highlightthickness=0)
                canvas.pack(side="left", padx=6)
                canvas.create_rectangle(0, 0, int(bar_w * pct), 12, fill=COLORS["primary"], outline="")
                tk.Label(row, text=f"${float(b.get('total',0)):,.2f}",
                         font=FONTS["body_bold"], bg=COLORS["white"], fg=COLORS["dark"]).pack(side="left")

        # Statement generator
        stmt_frame = tk.LabelFrame(content, text=" Account Statement ",
                                    font=FONTS["subheading"],
                                    bg=COLORS["white"], fg=COLORS["gray700"],
                                    bd=1, relief="flat",
                                    highlightbackground=COLORS["border"], highlightthickness=1)
        stmt_frame.pack(fill="x")
        ctrl = tk.Frame(stmt_frame, bg=COLORS["white"], padx=12, pady=10)
        ctrl.pack(fill="x")

        acc_combo = ttk.Combobox(ctrl, textvariable=self.stmt_acc_var,
                                  state="readonly", font=FONTS["body"], width=30)

        def load_acc():
            try:
                resp = api.get("/accounts/")
                accs = resp.json() if resp.status_code == 200 else []
                self.stmt_accounts = accs
                labels = [f"{a[chr(97)+chr(99)+chr(99)+chr(111)+chr(117)+chr(110)+chr(116)+chr(95)+chr(116)+chr(121)+chr(112)+chr(101)]} - {a[chr(97)+chr(99)+chr(99)+chr(111)+chr(117)+chr(110)+chr(116)+chr(95)+chr(110)+chr(117)+chr(109)+chr(98)+chr(101)+chr(114)]}" for a in accs]
                self.after(0, lambda: acc_combo.config(values=labels))
                if labels:
                    self.after(0, lambda: acc_combo.current(0))
            except:
                pass

        threading.Thread(target=load_acc, daemon=True).start()

        tk.Label(ctrl, text="Account:", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(side="left")
        acc_combo.pack(side="left", padx=6)
        tk.Label(ctrl, text="From (YYYY-MM-DD):", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(side="left", padx=(8, 0))
        ttk.Entry(ctrl, textvariable=self.stmt_start, width=12, font=FONTS["body"]).pack(side="left", padx=4)
        tk.Label(ctrl, text="To:", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(side="left", padx=(4, 0))
        ttk.Entry(ctrl, textvariable=self.stmt_end, width=12, font=FONTS["body"]).pack(side="left", padx=4)

        self.stmt_tree_frame = tk.Frame(stmt_frame, bg=COLORS["white"])
        self.stmt_tree_frame.pack(fill="x", padx=12, pady=(0, 12))

        def generate():
            idx = acc_combo.current()
            if idx < 0 or not self.stmt_accounts:
                messagebox.showwarning("Warning", "Select an account")
                return
            acc = self.stmt_accounts[idx]
            params = {}
            if self.stmt_start.get(): params["start_date"] = self.stmt_start.get()
            if self.stmt_end.get():   params["end_date"]   = self.stmt_end.get()

            def do():
                try:
                    resp = api.get(f"/analytics/statement/{acc[chr(105)+chr(100)]}/", params=params)
                    if resp.status_code == 200:
                        self.after(0, lambda: self._show_statement(resp.json()))
                    else:
                        self.after(0, lambda: messagebox.showerror("Error", "Failed to load statement"))
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror("Error", str(e)))

            threading.Thread(target=do, daemon=True).start()

        styled_button(ctrl, "Generate Statement", generate, "primary", icon=">>").pack(side="left", padx=8)

    def _show_statement(self, data):
        if not self.stmt_tree_frame:
            return
        for w in self.stmt_tree_frame.winfo_children():
            w.destroy()

        summary = data.get("summary", {})
        summ_row = tk.Frame(self.stmt_tree_frame, bg=COLORS["white"])
        summ_row.pack(fill="x", pady=(4, 8))

        for label, val, color in [
            ("Credits",  f"${summary.get(chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(95)+chr(99)+chr(114)+chr(101)+chr(100)+chr(105)+chr(116)+chr(115), 0):,.2f}", COLORS["success"]),
            ("Debits",   f"${summary.get(chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(95)+chr(100)+chr(101)+chr(98)+chr(105)+chr(116)+chr(115),  0):,.2f}", COLORS["danger"]),
            ("Net",      f"${summary.get(chr(110)+chr(101)+chr(116), 0):,.2f}",  COLORS["primary"]),
            ("Txn Count",str(summary.get(chr(116)+chr(114)+chr(97)+chr(110)+chr(115)+chr(97)+chr(99)+chr(116)+chr(105)+chr(111)+chr(110)+chr(95)+chr(99)+chr(111)+chr(117)+chr(110)+chr(116), 0)), COLORS["gray700"]),
            ("Balance",  f"${data.get(chr(99)+chr(117)+chr(114)+chr(114)+chr(101)+chr(110)+chr(116)+chr(95)+chr(98)+chr(97)+chr(108)+chr(97)+chr(110)+chr(99)+chr(101), 0):,.2f}", COLORS["dark"]),
        ]:
            col = tk.Frame(summ_row, bg=COLORS["gray100"], padx=10, pady=6)
            col.pack(side="left", padx=4)
            tk.Label(col, text=label, font=FONTS["small"], bg=COLORS["gray100"], fg=COLORS["gray500"]).pack()
            tk.Label(col, text=val,   font=FONTS["body_bold"], bg=COLORS["gray100"], fg=color).pack()

        stmt = data.get("statement", [])
        if not stmt:
            tk.Label(self.stmt_tree_frame, text="No transactions in this period.",
                     font=FONTS["body"], bg=COLORS["white"], fg=COLORS["gray300"]).pack(pady=8)
            return

        cols = ("Date", "Description", "Type", "Credit", "Debit", "Balance")
        tree = ttk.Treeview(self.stmt_tree_frame, columns=cols, show="headings", height=8)
        widths = {"Date": 130, "Description": 200, "Type": 100, "Credit": 90, "Debit": 90, "Balance": 110}
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=widths[col],
                        anchor="e" if col in ("Credit", "Debit", "Balance") else "w")

        sv = ttk.Scrollbar(self.stmt_tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sv.set)
        sv.pack(side="right", fill="y")
        tree.pack(fill="x")

        for row in stmt:
            credit = f"${row[chr(99)+chr(114)+chr(101)+chr(100)+chr(105)+chr(116)]:,.2f}" if row.get("credit") else "-"
            debit  = f"${row[chr(100)+chr(101)+chr(98)+chr(105)+chr(116)]:,.2f}"          if row.get("debit")  else "-"
            tree.insert("", "end", values=(
                row["date"], row["description"], row.get("type",""),
                credit, debit, f"${row[chr(98)+chr(97)+chr(108)+chr(97)+chr(110)+chr(99)+chr(101)]:,.2f}"
            ))


# ─── SETTINGS PAGE ────────────────────────────────────────────────────────────
class SettingsPage(BasePage):
    def __init__(self, master, user, navigate):
        super().__init__(master, user, navigate)
        self.topbar("Settings", "Application preferences")
        self._build()

    def _build(self):
        outer = tk.Frame(self, bg=COLORS["bg"], padx=40, pady=20)
        outer.pack(fill="both", expand=True)

        for section_title, settings in [
            ("Notifications", [
                ("Email alerts for transactions", True),
                ("SMS alerts for large transactions", True),
                ("Login notifications", True),
                ("Promotional emails", False),
            ]),
            ("Security", [
                ("Require PIN for transfers", True),
                ("Auto-logout after 15 minutes", False),
                ("Two-factor authentication", False),
            ]),
            ("Display", [
                ("Show balance on dashboard", True),
                ("Compact transaction view", False),
                ("Show transaction fees", True),
            ]),
        ]:
            frame = tk.LabelFrame(outer, text=f"  {section_title}  ", font=FONTS["subheading"],
                                   bg=COLORS["white"], fg=COLORS["gray700"],
                                   bd=1, relief="flat",
                                   highlightbackground=COLORS["border"], highlightthickness=1)
            frame.pack(fill="x", pady=(0, 14))
            inner = tk.Frame(frame, bg=COLORS["white"], padx=16, pady=10)
            inner.pack(fill="x")
            for label, default in settings:
                row = tk.Frame(inner, bg=COLORS["white"])
                row.pack(fill="x", pady=4)
                tk.Label(row, text=label, font=FONTS["body"], bg=COLORS["white"],
                         fg=COLORS["gray700"]).pack(side="left")
                var = tk.BooleanVar(value=default)
                tk.Checkbutton(row, variable=var, bg=COLORS["white"],
                                activebackground=COLORS["white"],
                                fg=COLORS["primary"], selectcolor=COLORS["white"],
                                cursor="hand2").pack(side="right")

        # Server info
        srv_frame = tk.LabelFrame(outer, text="  Server Connection  ", font=FONTS["subheading"],
                                   bg=COLORS["white"], fg=COLORS["gray700"],
                                   bd=1, relief="flat",
                                   highlightbackground=COLORS["border"], highlightthickness=1)
        srv_frame.pack(fill="x")
        inner = tk.Frame(srv_frame, bg=COLORS["white"], padx=16, pady=12)
        inner.pack(fill="x")

        tk.Label(inner, text="API Base URL", font=FONTS["body_bold"],
                 bg=COLORS["white"], fg=COLORS["gray700"]).pack(anchor="w")
        self.api_var = tk.StringVar(value=API_BASE)
        ttk.Entry(inner, textvariable=self.api_var, font=FONTS["mono"], width=40).pack(
            fill="x", ipady=4, pady=(4, 10))

        self.conn_var = tk.StringVar(value="")
        tk.Label(inner, textvariable=self.conn_var, font=FONTS["body"],
                 bg=COLORS["white"], fg=COLORS["gray500"]).pack(anchor="w", pady=(0, 8))

        def test():
            self.conn_var.set("Testing...")
            def do():
                try:
                    r = requests.post(f"{self.api_var.get()}/auth/login/",
                                      json={"username": "x", "password": "x"}, timeout=5)
                    if r.status_code in (400, 401, 200):
                        self.after(0, lambda: self.conn_var.set("OK  Server is reachable and responding"))
                    else:
                        self.after(0, lambda: self.conn_var.set(f"Unexpected status {r.status_code}"))
                except Exception as e:
                    self.after(0, lambda: self.conn_var.set(f"Cannot connect: {e}"))
            threading.Thread(target=do, daemon=True).start()

        styled_button(inner, "Test Connection", test, "outline", icon="⚡").pack(anchor="w")


# ─── PATCH NovaPay WITH EXTENDED NAVIGATION ───────────────────────────────────
_EXTENDED_PAGES = {
    "dashboard":     DashboardPage,
    "accounts":      AccountsPage,
    "transactions":  TransactionsPage,
    "transfer":      TransferPage,
    "cards":         CardsPage,
    "loans":         LoansPage,
    "beneficiaries": BeneficiariesPage,
    "profile":       ProfilePage,
    "analytics":     AnalyticsPage,
    "settings":      SettingsPage,
}

_EXTENDED_NAV = [
    ("Main Menu", None),
    ("  Dashboard",    "dashboard",     "[ ]"),
    ("  Accounts",     "accounts",      "( )"),
    ("  Transactions", "transactions",  "<->"),
    ("  Transfer",     "transfer",      "-->"),
    ("  Analytics",    "analytics",     "///"),
    ("Banking Services", None),
    ("  Cards",        "cards",         "[#]"),
    ("  Loans",        "loans",         "[+]"),
    ("  Beneficiaries","beneficiaries", "[v]"),
    ("Account", None),
    ("  Profile",      "profile",       "[o]"),
    ("  Settings",     "settings",      "[s]"),
]


def _extended_navigate(self, page):
    self.current_page = page
    for p, btn in self.nav_buttons.items():
        if p == page:
            btn.config(bg=COLORS["primary_light"], fg=COLORS["primary"], font=FONTS["body_bold"])
        else:
            btn.config(bg=COLORS["sidebar_bg"], fg=COLORS["gray700"], font=FONTS["body"])
    for w in self.content.winfo_children():
        w.destroy()
    cls = _EXTENDED_PAGES.get(page, DashboardPage)
    cls(self.content, self.user, self._navigate).pack(fill="both", expand=True)


def _extended_build_sidebar(self):
    logo_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"], pady=16)
    logo_frame.pack(fill="x", padx=16)
    tk.Label(logo_frame, text="NovaPay", font=FONTS["logo"],
             bg=COLORS["sidebar_bg"], fg=COLORS["dark"]).pack(side="left")
    tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x")

    nav_scroll = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
    nav_scroll.pack(fill="both", expand=True, pady=8)

    self.nav_buttons = {}
    for item in _EXTENDED_NAV:
        if len(item) == 2 and item[1] is None:
            section_label(nav_scroll, item[0]).pack(anchor="w", padx=12, pady=(10, 2))
        else:
            label, page, icon = item
            btn = self._nav_btn(nav_scroll, f"{label.strip()}", page)
            self.nav_buttons[page] = btn

    tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", side="bottom")
    bottom = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"], pady=10)
    bottom.pack(fill="x", side="bottom", padx=12)

    name = f"{self.user.get('first_name','')} {self.user.get('last_name','')}".strip() or self.user.get("username","User")
    tk.Label(bottom, text=name, font=FONTS["body_bold"],
             bg=COLORS["sidebar_bg"], fg=COLORS["gray900"]).pack(anchor="w")
    tk.Label(bottom, text=self.user.get("email",""), font=FONTS["small"],
             bg=COLORS["sidebar_bg"], fg=COLORS["gray500"]).pack(anchor="w")
    logout_lbl = tk.Label(bottom, text="Sign Out", font=FONTS["small"],
                           bg=COLORS["sidebar_bg"], fg=COLORS["danger"], cursor="hand2")
    logout_lbl.pack(anchor="w", pady=(6, 0))
    logout_lbl.bind("<Button-1>", lambda e: self._logout())


NovaPay._navigate = _extended_navigate
NovaPay._build_sidebar = _extended_build_sidebar


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = NovaPay()
    app.mainloop()