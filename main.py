"""
IT-Инвентарь — учёт программ, лицензий и компьютеров.
Только стандартная библиотека Python (tkinter + sqlite3).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime, date, timedelta
import random

# ===================== ПАЛИТРА =====================
C = {
    "bg":           "#F5F6F8",
    "sidebar":      "#1B2438",
    "sidebar_act":  "#2B3A5C",
    "sidebar_hov":  "#232E48",
    "card":         "#FFFFFF",
    "card_border":  "#E4E7EC",
    "text":         "#101828",
    "text_dim":     "#667085",
    "accent":       "#2563EB",
    "accent_h":     "#1D4ED8",
    "accent_soft":  "#EFF4FF",
    "green":        "#12B76A",
    "green_bg":     "#E6F7EF",
    "orange":       "#F79009",
    "orange_bg":    "#FEF3DC",
    "red":          "#F04438",
    "red_bg":       "#FEECEB",
    "purple":       "#7A5AF8",
    "purple_bg":    "#F3F0FF",
    "border":       "#EAECF0",
    "input_bg":     "#FFFFFF",
    "input_border": "#D0D5DD",
    "row_hover":    "#F9FAFB",
    "menu_text":    "#C6CFE0",
    "menu_muted":   "#8B98B8",
    "divider":      "#2A3654",
}

FONT = "Segoe UI"
DB_FILE = "it_inventory.db"
CATEGORIES = ["Офисные", "Графические", "Антивирусы", "Системные",
              "Разработка", "Бухгалтерия", "Браузеры", "Прочие"]


# ===================== БД =====================
class DB:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create()
        self._seed()

    def _create(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS computers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT NOT NULL UNIQUE,
            department TEXT,
            user TEXT
        );
        CREATE TABLE IF NOT EXISTS software (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            version TEXT,
            has_license INTEGER DEFAULT 0,
            license_key TEXT,
            install_date TEXT,
            end_date TEXT,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS software_computers (
            software_id INTEGER NOT NULL,
            computer_id INTEGER NOT NULL,
            PRIMARY KEY (software_id, computer_id),
            FOREIGN KEY(software_id) REFERENCES software(id) ON DELETE CASCADE,
            FOREIGN KEY(computer_id) REFERENCES computers(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK (id=1),
            full_name TEXT,
            email TEXT,
            role TEXT,
            department TEXT,
            phone TEXT
        );
        """)
        self.conn.execute("""INSERT OR IGNORE INTO user_profile
            (id, full_name, email, role, department, phone)
            VALUES(1, 'Александр Смирнов', 'a.smirnov@company.ru',
                   'Администратор', 'Отдел IT', '+7 (900) 123-45-67')""")
        self.conn.commit()

    def _seed(self):
        if self.conn.execute("SELECT COUNT(*) FROM computers").fetchone()[0] > 0:
            return
        comps = [
            ("PC-01", "Отдел бухгалтерии", "Иванов И.И."),
            ("PC-02", "Отдел бухгалтерии", "Петрова А.С."),
            ("PC-03", "Отдел продаж",      "Сидоров П.П."),
            ("PC-04", "Отдел продаж",      "Козлов Д.А."),
            ("PC-05", "Отдел IT",          "Смирнов В.В."),
            ("PC-06", "Отдел IT",          "Морозов Е.А."),
            ("PC-07", "Отдел кадров",      "Николаева О.В."),
            ("PC-08", "Дирекция",          "Директор"),
            ("PC-09", "Отдел продаж",      "Волков А.А."),
            ("PC-10", "Отдел бухгалтерии", "Федорова М.И."),
            ("PC-11", "Отдел IT",          "Лебедев К.С."),
            ("PC-12", "Отдел кадров",      "Орлова Т.Н."),
        ]
        self.conn.executemany(
            "INSERT INTO computers(hostname,department,user) VALUES(?,?,?)", comps)

        today = date.today()
        def d(days): return (today + timedelta(days=days)).isoformat()
        software = [
            ("Microsoft Office", "Офисные", "2019", 1,
             "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX", d(-400), d(5),
             "Пакет офисных приложений (Word, Excel, PowerPoint и др.)"),
            ("Adobe Photoshop", "Графические", "2022", 1,
             "PHT22-XXXX-XXXX-XXXX", d(-300), d(12), "Растровый графический редактор"),
            ("Kaspersky Endpoint Security", "Антивирусы", "11", 1,
             "KES11-XXXX-XXXX", d(-350), d(25), "Антивирусная защита"),
            ("Windows 10 Pro", "Системные", "22H2", 1,
             "W10P-XXXXX-XXXXX", d(-500), d(61), "Операционная система"),
            ("1С:Предприятие", "Бухгалтерия", "8.3", 1,
             "1C83-XXXX-XXXX", d(-200), d(76), "Платформа для бухучёта"),
            ("Google Chrome", "Браузеры", "118", 0, "", d(-100), d(89), "Веб-браузер"),
            ("Visual Studio Code", "Разработка", "1.80", 0, "", d(-150), d(127), "Редактор кода"),
            ("Adobe Acrobat Reader", "Офисные", "2024", 0, "", d(-90), d(143), "Просмотр PDF"),
            ("Microsoft Excel", "Офисные", "2019", 1,
             "XXXXX-XXXXX-XXXXX", d(-400), d(30), "Электронные таблицы"),
            ("Adobe Illustrator", "Графические", "2022", 1,
             "IL22-XXXX-XXXX", d(-300), d(45), "Векторный редактор"),
            ("Avast Business", "Антивирусы", "23", 1,
             "AVST-XXXX-XXXX", d(-350), d(180), "Антивирус"),
            ("Windows 11 Pro", "Системные", "23H2", 1,
             "W11P-XXXXX-XXXXX", d(-120), d(240), "Операционная система"),
            ("Microsoft Word", "Офисные", "2019", 1,
             "XXXXX-XXXXX-XXXXX", d(-400), d(-10), "Текстовый редактор"),
            ("Photoshop Elements", "Графические", "2021", 1,
             "PE21-XXXX-XXXX", d(-800), d(-30), "Упрощённый редактор"),
            ("Firefox", "Браузеры", "120", 0, "", d(-50), d(200), "Веб-браузер"),
            ("PyCharm", "Разработка", "2023.2", 0, "", d(-100), d(300), "IDE для Python"),
            ("SAP", "Бухгалтерия", "S/4HANA", 1,
             "SAP-XXXX-XXXX", d(-600), d(400), "ERP-система"),
            ("7-Zip", "Прочие", "23.01", 0, "", d(-200), None, "Архиватор"),
            ("Notepad++", "Прочие", "8.5", 0, "", d(-300), None, "Текстовый редактор"),
            ("Figma", "Графические", "Web", 0, "", d(-50), d(150), "Онлайн-дизайн"),
            ("Telegram", "Прочие", "10.2", 0, "", d(-30), None, "Мессенджер"),
            ("Zoom", "Прочие", "5.17", 0, "", d(-60), None, "Видеоконференции"),
            ("Slack", "Прочие", "4.35", 0, "", d(-90), None, "Корпоративный чат"),
            ("Docker", "Разработка", "24.0", 0, "", d(-200), None, "Контейнеризация"),
            ("Postman", "Разработка", "11", 0, "", d(-40), None, "Тестирование API"),
        ]
        self.conn.executemany("""INSERT INTO software
            (name,category,version,has_license,license_key,install_date,end_date,description)
            VALUES(?,?,?,?,?,?,?,?)""", software)

        sw_ids = [r[0] for r in self.conn.execute("SELECT id FROM software").fetchall()]
        pc_ids = [r[0] for r in self.conn.execute("SELECT id FROM computers").fetchall()]
        links = set()
        for sid in sw_ids:
            for cid in random.sample(pc_ids, random.randint(1, 5)):
                links.add((sid, cid))
        self.conn.executemany(
            "INSERT OR IGNORE INTO software_computers(software_id,computer_id) VALUES(?,?)",
            list(links))
        self.conn.commit()

    def q(self, sql, p=()):
        return self.conn.execute(sql, p).fetchall()

    def x(self, sql, p=()):
        cur = self.conn.execute(sql, p)
        self.conn.commit()
        return cur.lastrowid

    def close(self):
        self.conn.close()


# ===================== ХЕЛПЕРЫ =====================
def days_left(end_date):
    if not end_date:
        return None
    try:
        d = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (d - date.today()).days


def status_of(sw):
    if not sw["has_license"]:
        return ("Нет лицензии", C["text_dim"], "#F2F4F7")
    dl = days_left(sw["end_date"])
    if dl is None:
        return ("Активна", C["green"], C["green_bg"])
    if dl < 0:
        return ("Истекла", C["red"], C["red_bg"])
    return ("Активна", C["green"], C["green_bg"])


def make_button(parent, text, command, kind="normal", width=None):
    styles = {
        "normal":  (C["card"], C["text"], C["border"], C["row_hover"]),
        "primary": (C["accent"], "white", C["accent"], C["accent_h"]),
        "ghost":   (C["card"], C["text_dim"], C["border"], C["row_hover"]),
        "danger":  (C["red"], "white", C["red"], "#D92D20"),
    }
    bg, fg, border, hover = styles[kind]
    btn = tk.Button(parent, text=text, command=command,
                    bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
                    relief="flat", bd=0, highlightthickness=1,
                    highlightbackground=border, highlightcolor=border,
                    font=(FONT, 10), cursor="hand2", padx=14, pady=6)
    if width:
        btn.configure(width=width)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    return btn


def make_entry(parent, textvariable=None, width=None, placeholder=None):
    wrap = tk.Frame(parent, bg=C["input_bg"],
                    highlightthickness=1, highlightbackground=C["input_border"],
                    highlightcolor=C["accent"])
    e = tk.Entry(wrap, textvariable=textvariable, bg=C["input_bg"],
                 fg=C["text"], insertbackground=C["text"],
                 relief="flat", bd=0, font=(FONT, 11))
    e.pack(fill="both", expand=True, padx=10, pady=6)
    if width:
        wrap.configure(width=width)
    if placeholder:
        e.insert(0, placeholder)
        e.configure(fg=C["text_dim"])

        def on_focus_in(_):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.configure(fg=C["text"])

        def on_focus_out(_):
            if not e.get():
                e.insert(0, placeholder)
                e.configure(fg=C["text_dim"])

        e.bind("<FocusIn>", on_focus_in)
        e.bind("<FocusOut>", on_focus_out)
    wrap.entry = e
    return wrap


def card_frame(parent, **kw):
    return tk.Frame(parent, bg=C["card"],
                    highlightthickness=1, highlightbackground=C["card_border"], **kw)


# ===================== SIDEBAR =====================
class Sidebar(tk.Frame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent, bg=C["sidebar"], width=230)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.buttons = {}
        self.active = None

        logo = tk.Frame(self, bg=C["sidebar"])
        logo.pack(fill="x", padx=20, pady=(22, 6))
        badge = tk.Label(logo, text="IT", bg=C["accent"], fg="white",
                         font=(FONT, 12, "bold"), width=3, height=1)
        badge.pack(side="left", ipady=4)
        titles = tk.Frame(logo, bg=C["sidebar"])
        titles.pack(side="left", padx=(10, 0))
        tk.Label(titles, text="IT-Инвентарь", font=(FONT, 13, "bold"),
                 fg="white", bg=C["sidebar"]).pack(anchor="w")
        tk.Label(titles, text="Программы • Лицензии • ПК",
                 font=(FONT, 9), fg=C["menu_muted"], bg=C["sidebar"]).pack(anchor="w")

        tk.Frame(self, bg=C["divider"], height=1).pack(fill="x", padx=16, pady=(16, 10))

        menu = [
            ("home",      "🏠", "Главная"),
            ("software",  "▦",  "Программы"),
            ("computers", "🖥", "Компьютеры"),
            ("licenses",  "🔑", "Лицензии"),
            ("deadlines", "⏱", "Сроки"),
            ("filter",    "▼",  "Фильтр"),
        ]
        for key, icon, label in menu:
            btn = tk.Button(self, text=f"  {icon}   {label}", anchor="w",
                            bg=C["sidebar"], fg=C["menu_text"],
                            activebackground=C["sidebar_hov"],
                            activeforeground="white",
                            relief="flat", bd=0, font=(FONT, 11),
                            cursor="hand2", padx=14, pady=10,
                            command=lambda k=key: self._click(k))
            btn.pack(fill="x", padx=10, pady=1)
            btn.bind("<Enter>", lambda e, b=btn, k=key: self._hover(b, k))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._unhover(b, k))
            self.buttons[key] = btn

        tk.Frame(self, bg=C["sidebar"]).pack(fill="both", expand=True)
        settings = tk.Button(self, text="  ⚙   Настройки", anchor="w",
                             bg=C["sidebar"], fg=C["menu_muted"],
                             activebackground=C["sidebar_hov"],
                             activeforeground="white",
                             relief="flat", bd=0, font=(FONT, 11),
                             cursor="hand2", padx=14, pady=10,
                             command=lambda: messagebox.showinfo(
                                 "Настройки",
                                 "Тема: светлая\nБаза данных: it_inventory.db"))
        settings.pack(fill="x", padx=10, pady=(1, 16))

        self.set_active("home")

    def _hover(self, btn, key):
        if key != self.active:
            btn.configure(bg=C["sidebar_hov"])

    def _unhover(self, btn, key):
        if key != self.active:
            btn.configure(bg=C["sidebar"])

    def _click(self, key):
        self.set_active(key)
        self.on_navigate(key)

    def set_active(self, key):
        self.active = key
        for k, btn in self.buttons.items():
            if k == key:
                btn.configure(bg=C["sidebar_act"], fg="white")
            else:
                btn.configure(bg=C["sidebar"], fg=C["menu_text"])


# ===================== TOPBAR =====================
class TopBar(tk.Frame):
    def __init__(self, parent, title, subtitle=None, app=None):
        super().__init__(parent, bg=C["card"], height=64)
        self.pack_propagate(False)
        self.app = app
        self.menu_popup = None

        left = tk.Frame(self, bg=C["card"])
        left.pack(side="left", padx=24, fill="y")
        tk.Label(left, text=title, font=(FONT, 15, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(12, 0))
        if subtitle:
            tk.Label(left, text=subtitle, font=(FONT, 9),
                     fg=C["text_dim"], bg=C["card"]).pack(anchor="w")

        right = tk.Frame(self, bg=C["card"])
        right.pack(side="right", padx=24)

        # Уведомления
        notif = tk.Label(right, text="🔔", font=(FONT, 14),
                         fg=C["text_dim"], bg=C["card"], cursor="hand2")
        notif.pack(side="left", padx=8)
        notif.bind("<Button-1>", lambda e: self._show_notifications())

        # Аккаунт
        profile = self.app.db.q("SELECT * FROM user_profile WHERE id=1")[0]
        initials = "".join([w[0].upper() for w in profile["full_name"].split()[:2]])

        self.account_btn = tk.Frame(right, bg=C["card"], cursor="hand2")
        self.account_btn.pack(side="left", padx=(8, 0))

        self.avatar = tk.Label(self.account_btn, text=initials,
                               bg=C["accent"], fg="white",
                               font=(FONT, 10, "bold"), width=3, height=1)
        self.avatar.pack(side="left", ipady=4)

        name_wrap = tk.Frame(self.account_btn, bg=C["card"])
        name_wrap.pack(side="left", padx=(8, 4))
        self.name_lbl = tk.Label(name_wrap, text=profile["full_name"],
                                 font=(FONT, 11, "bold"),
                                 fg=C["text"], bg=C["card"])
        self.name_lbl.pack(anchor="w")
        self.role_lbl = tk.Label(name_wrap, text=profile["role"],
                                 font=(FONT, 9),
                                 fg=C["text_dim"], bg=C["card"])
        self.role_lbl.pack(anchor="w")

        self.caret = tk.Label(self.account_btn, text="▾", font=(FONT, 9),
                              fg=C["text_dim"], bg=C["card"])
        self.caret.pack(side="left")

        for w in (self.account_btn, self.avatar, self.name_lbl,
                  self.role_lbl, self.caret, name_wrap):
            w.bind("<Button-1>", lambda e: self._toggle_account_menu())

    # ---------- Меню аккаунта ----------
    def _toggle_account_menu(self):
        if self.menu_popup and self.menu_popup.winfo_exists():
            self._close_menu()
            return
        self._open_menu()

    def _open_menu(self):
        profile = self.app.db.q("SELECT * FROM user_profile WHERE id=1")[0]

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg=C["card_border"])
        popup.attributes("-topmost", True)
        self.menu_popup = popup

        self.update_idletasks()
        btn_x = self.account_btn.winfo_rootx()
        btn_y = self.account_btn.winfo_rooty()
        btn_w = self.account_btn.winfo_width()
        btn_h = self.account_btn.winfo_height()
        menu_w = 320
        menu_h = 520
        x = btn_x + btn_w - menu_w
        y = btn_y + btn_h + 6
        popup.geometry(f"{menu_w}x{menu_h}+{x}+{y}")

        outer = tk.Frame(popup, bg=C["card_border"])
        outer.pack(fill="both", expand=True)
        box = tk.Frame(outer, bg=C["card"])
        box.pack(fill="both", expand=True, padx=1, pady=1)

        # Шапка
        header = tk.Frame(box, bg=C["card"])
        header.pack(fill="x", padx=16, pady=(16, 12))

        initials = "".join([w[0].upper() for w in profile["full_name"].split()[:2]])
        av = tk.Label(header, text=initials, bg=C["accent"], fg="white",
                      font=(FONT, 13, "bold"), width=4, height=2)
        av.pack(side="left")

        info = tk.Frame(header, bg=C["card"])
        info.pack(side="left", padx=(12, 0), fill="x", expand=True)
        tk.Label(info, text=profile["full_name"], font=(FONT, 12, "bold"),
                 fg=C["text"], bg=C["card"], anchor="w").pack(fill="x")
        tk.Label(info, text=profile["email"], font=(FONT, 9),
                 fg=C["text_dim"], bg=C["card"], anchor="w").pack(fill="x")
        tk.Label(info, text=f" {profile['role']} ",
                 font=(FONT, 8, "bold"),
                 fg=C["accent"], bg=C["accent_soft"]).pack(anchor="w", pady=(4, 0))

        tk.Frame(box, bg=C["border"], height=1).pack(fill="x", padx=12)

        # Пункты
        def item(icon, label, cmd, danger=False, hint=None):
            row = tk.Frame(box, bg=C["card"], cursor="hand2")
            row.pack(fill="x", padx=8, pady=1)

            fg = C["red"] if danger else C["text"]
            ic_lbl = tk.Label(row, text=icon, font=(FONT, 12),
                              fg=fg, bg=C["card"], width=3, anchor="w")
            ic_lbl.pack(side="left", padx=(8, 4), pady=8)

            txt = tk.Frame(row, bg=C["card"])
            txt.pack(side="left", fill="x", expand=True)
            tk.Label(txt, text=label,
                     font=(FONT, 10, "bold" if not danger else "normal"),
                     fg=fg, bg=C["card"], anchor="w").pack(fill="x")
            if hint:
                tk.Label(txt, text=hint, font=(FONT, 8),
                         fg=C["text_dim"], bg=C["card"], anchor="w").pack(fill="x")

            hover_widgets = [row, ic_lbl, txt] + list(txt.winfo_children())

            def on_enter(_):
                for w in hover_widgets:
                    try: w.configure(bg=C["row_hover"])
                    except Exception: pass

            def on_leave(_):
                for w in hover_widgets:
                    try: w.configure(bg=C["card"])
                    except Exception: pass

            def on_click(_):
                self._close_menu()
                cmd()

            for w in hover_widgets:
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)

        item("👤", "Мой профиль", self._open_profile,
             hint="Просмотр данных пользователя")
        item("✏", "Редактировать профиль", self._edit_profile,
             hint="Имя, email, телефон, отдел")
        item("🔑", "Сменить пароль", self._change_password,
             hint="Обновить пароль учётной записи")

        tk.Frame(box, bg=C["border"], height=1).pack(fill="x", padx=12, pady=4)

        item("⚙", "Настройки приложения", self._open_settings,
             hint="Тема, база данных, уведомления")
        item("📥", "Экспорт данных", self._export_data,
             hint="CSV всех программ и лицензий")
        item("📊", "Отчёты", self._show_reports,
             hint="Сводка по лицензиям и срокам")

        tk.Frame(box, bg=C["border"], height=1).pack(fill="x", padx=12, pady=4)

        item("❓", "Справка", self._show_help,
             hint="Горячие клавиши и советы")
        item("🚪", "Выйти", self._logout, danger=True,
             hint="Завершить сеанс")

        popup.bind("<FocusOut>", lambda e: self._close_menu())
        popup.focus_set()

    def _close_menu(self):
        if self.menu_popup and self.menu_popup.winfo_exists():
            self.menu_popup.destroy()
        self.menu_popup = None

    # ---------- Действия ----------
    def _open_profile(self):
        profile = self.app.db.q("SELECT * FROM user_profile WHERE id=1")[0]
        UserProfileDialog(self.app, self.app.db, profile, self.app, readonly=True)

    def _edit_profile(self):
        profile = self.app.db.q("SELECT * FROM user_profile WHERE id=1")[0]
        UserProfileDialog(self.app, self.app.db, profile, self.app)

    def _change_password(self):
        ChangePasswordDialog(self.app, self.app.db)

    def _open_settings(self):
        SettingsDialog(self.app, self.app.db)

    def _export_data(self):
        path = filedialog.asksaveasfilename(
            parent=self.app, defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="it_inventory_export.csv")
        if not path:
            return
        rows = self.app.db.q("""SELECT s.name, s.category, s.version,
                                       s.has_license, s.license_key,
                                       s.install_date, s.end_date,
                                       s.description,
                                       COUNT(sc.computer_id) AS cnt
                                FROM software s
                                LEFT JOIN software_computers sc ON sc.software_id=s.id
                                GROUP BY s.id
                                ORDER BY s.name""")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Название", "Категория", "Версия", "Лицензия",
                        "Ключ", "Дата установки", "Дата окончания",
                        "Описание", "Компьютеров"])
            for r in rows:
                w.writerow([
                    r["name"], r["category"] or "", r["version"] or "",
                    "Да" if r["has_license"] else "Нет",
                    r["license_key"] or "", r["install_date"] or "",
                    r["end_date"] or "", r["description"] or "", r["cnt"]
                ])
        messagebox.showinfo("Экспорт", f"Данные сохранены:\n{path}",
                            parent=self.app)

    def _show_reports(self):
        ReportsDialog(self.app, self.app.db)

    def _show_help(self):
        messagebox.showinfo(
            "Справка",
            "IT-Инвентарь — учёт ПО и лицензий.\n\n"
            "Разделы:\n"
            "• Программы — список ПО и лицензий\n"
            "• Компьютеры — рабочие станции\n"
            "• Лицензии — ключи и сроки\n"
            "• Сроки — контроль дедлайнов\n"
            "• Фильтр — расширенный поиск\n\n"
            "Клик по названию программы открывает карточку.\n"
            "Данные хранятся в файле it_inventory.db.",
            parent=self.app)

    def _show_notifications(self):
        NotificationsDialog(self.app, self.app.db)

    def _logout(self):
        if messagebox.askyesno("Выход",
                               "Завершить сеанс и закрыть приложение?",
                               parent=self.app):
            self._close_menu()
            self.app._on_close()


# ===================== ДИАЛОГ ПРОФИЛЯ =====================
class UserProfileDialog(tk.Toplevel):
    def __init__(self, parent, db, profile, app, readonly=False):
        super().__init__(parent)
        self.db = db
        self.app = app
        self.readonly = readonly
        self.title("Профиль пользователя")
        self.configure(bg=C["card"])
        self.geometry("480x520")
        self.transient(parent)
        self.grab_set()

        wrap = tk.Frame(self, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        initials = "".join([w[0].upper() for w in profile["full_name"].split()[:2]])
        header = tk.Frame(wrap, bg=C["card"])
        header.pack(fill="x", pady=(0, 12))
        av = tk.Label(header, text=initials, bg=C["accent"], fg="white",
                      font=(FONT, 16, "bold"), width=4, height=2)
        av.pack(side="left")
        info = tk.Frame(header, bg=C["card"])
        info.pack(side="left", padx=(14, 0))
        tk.Label(info, text=profile["full_name"], font=(FONT, 14, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w")
        tk.Label(info, text=profile["role"], font=(FONT, 10),
                 fg=C["accent"], bg=C["card"]).pack(anchor="w")

        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x", pady=8)

        title = "Данные профиля" if readonly else "Редактирование профиля"
        tk.Label(wrap, text=title, font=(FONT, 11, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(4, 8))

        self.vars = {}
        fields = [
            ("full_name", "ФИО"),
            ("email", "Email"),
            ("phone", "Телефон"),
            ("role", "Роль"),
            ("department", "Отдел"),
        ]
        for key, label in fields:
            row = tk.Frame(wrap, bg=C["card"])
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, font=(FONT, 10),
                     fg=C["text_dim"], bg=C["card"], width=14,
                     anchor="w").pack(side="left")
            var = tk.StringVar(value=profile[key] or "")
            self.vars[key] = var
            w = make_entry(row, var)
            w.pack(side="left", fill="x", expand=True)
            if readonly:
                w.entry.configure(state="disabled")

        btns = tk.Frame(wrap, bg=C["card"])
        btns.pack(fill="x", pady=(16, 0))
        if readonly:
            make_button(btns, "Редактировать", self._switch_to_edit,
                        "primary").pack(side="right")
            make_button(btns, "Закрыть", self.destroy,
                        "ghost").pack(side="right", padx=(0, 8))
        else:
            make_button(btns, "Сохранить", self.save,
                        "primary").pack(side="right")
            make_button(btns, "Отмена", self.destroy,
                        "ghost").pack(side="right", padx=(0, 8))

    def _switch_to_edit(self):
        self.destroy()
        profile = self.db.q("SELECT * FROM user_profile WHERE id=1")[0]
        UserProfileDialog(self.app, self.db, profile, self.app, readonly=False)

    def save(self):
        full_name = self.vars["full_name"].get().strip()
        if not full_name:
            messagebox.showwarning("Ошибка", "ФИО не может быть пустым",
                                   parent=self)
            return
        self.db.x("""UPDATE user_profile SET
            full_name=?, email=?, phone=?, role=?, department=?
            WHERE id=1""",
            (full_name,
             self.vars["email"].get().strip(),
             self.vars["phone"].get().strip(),
             self.vars["role"].get().strip(),
             self.vars["department"].get().strip()))
        messagebox.showinfo("Профиль", "Данные сохранены", parent=self)
        self.destroy()
        # Обновим шапку
        self.app.refresh_all_topbars()


# ===================== СМЕНА ПАРОЛЯ =====================
class ChangePasswordDialog(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Смена пароля")
        self.configure(bg=C["card"])
        self.geometry("440x340")
        self.transient(parent)
        self.grab_set()

        wrap = tk.Frame(self, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(wrap, text="🔑 Смена пароля", font=(FONT, 14, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w")
        tk.Label(wrap, text="Введите текущий пароль и новый дважды.",
                 font=(FONT, 9), fg=C["text_dim"],
                 bg=C["card"]).pack(anchor="w", pady=(2, 12))

        self.vars = {}
        for key, label in [("old", "Текущий пароль"),
                           ("new1", "Новый пароль"),
                           ("new2", "Повтор пароля")]:
            row = tk.Frame(wrap, bg=C["card"])
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, font=(FONT, 10),
                     fg=C["text_dim"], bg=C["card"], width=16,
                     anchor="w").pack(side="left")
            var = tk.StringVar()
            self.vars[key] = var
            w = make_entry(row, var)
            w.pack(side="left", fill="x", expand=True)
            w.entry.configure(show="•")

        btns = tk.Frame(wrap, bg=C["card"])
        btns.pack(fill="x", pady=(20, 0))
        make_button(btns, "Сохранить", self.save, "primary").pack(side="right")
        make_button(btns, "Отмена", self.destroy,
                    "ghost").pack(side="right", padx=(0, 8))

    def save(self):
        old = self.vars["old"].get()
        n1 = self.vars["new1"].get()
        n2 = self.vars["new2"].get()
        if not old:
            messagebox.showwarning("Ошибка", "Введите текущий пароль", parent=self)
            return
        if len(n1) < 4:
            messagebox.showwarning("Ошибка",
                                   "Новый пароль должен содержать минимум 4 символа",
                                   parent=self)
            return
        if n1 != n2:
            messagebox.showwarning("Ошибка", "Пароли не совпадают", parent=self)
            return
        # Здесь можно было бы проверить old по хешу из БД — для демо просто ок
        messagebox.showinfo("Пароль", "Пароль успешно изменён", parent=self)
        self.destroy()


# ===================== НАСТРОЙКИ =====================
class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Настройки приложения")
        self.configure(bg=C["card"])
        self.geometry("480x420")
        self.transient(parent)
        self.grab_set()

        wrap = tk.Frame(self, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(wrap, text="⚙ Настройки", font=(FONT, 14, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w")
        tk.Label(wrap, text="Основные параметры приложения",
                 font=(FONT, 9), fg=C["text_dim"],
                 bg=C["card"]).pack(anchor="w", pady=(2, 12))

        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x", pady=6)

        # Тема
        row = tk.Frame(wrap, bg=C["card"])
        row.pack(fill="x", pady=8)
        tk.Label(row, text="Тема оформления", font=(FONT, 10),
                 fg=C["text_dim"], bg=C["card"], width=20,
                 anchor="w").pack(side="left")
        self.theme = tk.StringVar(value="Светлая")
        ttk.Combobox(row, textvariable=self.theme, state="readonly",
                     values=["Светлая", "Тёмная (скоро)"],
                     font=(FONT, 10)).pack(side="left", fill="x", expand=True)

        # Уведомления о сроках
        row = tk.Frame(wrap, bg=C["card"])
        row.pack(fill="x", pady=8)
        tk.Label(row, text="Уведомления о сроках", font=(FONT, 10),
                 fg=C["text_dim"], bg=C["card"], width=20,
                 anchor="w").pack(side="left")
        self.notify = tk.BooleanVar(value=True)
        tk.Checkbutton(row, text="Напоминать о лицензиях",
                       variable=self.notify, bg=C["card"], fg=C["text"],
                       selectcolor=C["card"], activebackground=C["card"],
                       font=(FONT, 10)).pack(side="left")

        # Порог напоминания
        row = tk.Frame(wrap, bg=C["card"])
        row.pack(fill="x", pady=8)
        tk.Label(row, text="Порог напоминания (дней)", font=(FONT, 10),
                 fg=C["text_dim"], bg=C["card"], width=20,
                 anchor="w").pack(side="left")
        self.threshold = tk.StringVar(value="30")
        make_entry(row, self.threshold, width=10).pack(side="left")

        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x", pady=10)

        tk.Label(wrap, text=f"База данных: {DB_FILE}",
                 font=(FONT, 9), fg=C["text_dim"],
                 bg=C["card"]).pack(anchor="w")

        btns = tk.Frame(wrap, bg=C["card"])
        btns.pack(fill="x", pady=(20, 0))
        make_button(btns, "Сохранить", self.save, "primary").pack(side="right")
        make_button(btns, "Отмена", self.destroy,
                    "ghost").pack(side="right", padx=(0, 8))

    def save(self):
        messagebox.showinfo("Настройки", "Параметры сохранены", parent=self)
        self.destroy()


# ===================== ОТЧЁТЫ =====================
class ReportsDialog(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Отчёты")
        self.configure(bg=C["card"])
        self.geometry("620x520")
        self.transient(parent)
        self.grab_set()

        wrap = tk.Frame(self, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(wrap, text="📊 Сводные отчёты", font=(FONT, 14, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(0, 12))

        total = db.q("SELECT COUNT(*) c FROM software")[0]["c"]
        licensed = db.q("SELECT COUNT(*) c FROM software WHERE has_license=1")[0]["c"]
        today = date.today()
        expired = db.q("""SELECT COUNT(*) c FROM software
            WHERE has_license=1 AND end_date IS NOT NULL AND end_date != ''
            AND date(end_date) < date(?)""", (today.isoformat(),))[0]["c"]
        soon = db.q("""SELECT COUNT(*) c FROM software
            WHERE has_license=1 AND end_date IS NOT NULL AND end_date != ''
            AND date(end_date) BETWEEN date(?) AND date(?, '+30 day')""",
            (today.isoformat(), today.isoformat()))[0]["c"]
        comps = db.q("SELECT COUNT(*) c FROM computers")[0]["c"]

        stats = [
            ("Всего программ в базе", total, C["accent"]),
            ("С лицензией",           licensed, C["green"]),
            ("Просрочено",            expired, C["red"]),
            ("Истекает в 30 дней",    soon, C["orange"]),
            ("Компьютеров",           comps, C["purple"]),
        ]
        for label, val, color in stats:
            row = tk.Frame(wrap, bg=C["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=(FONT, 11),
                     fg=C["text"], bg=C["card"], anchor="w").pack(side="left")
            tk.Label(row, text=str(val), font=(FONT, 12, "bold"),
                     fg=color, bg=C["card"]).pack(side="right")

        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x", pady=10)

        tk.Label(wrap, text="Категории", font=(FONT, 11, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(0, 6))
        cats = db.q("""SELECT category, COUNT(*) c FROM software
                       GROUP BY category ORDER BY c DESC""")
        for cat in cats:
            row = tk.Frame(wrap, bg=C["card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=cat["category"] or "—", font=(FONT, 10),
                     fg=C["text"], bg=C["card"], anchor="w").pack(side="left")
            tk.Label(row, text=str(cat["c"]), font=(FONT, 10, "bold"),
                     fg=C["text_dim"], bg=C["card"]).pack(side="right")

        make_button(wrap, "Закрыть", self.destroy,
                    "primary").pack(side="right", pady=(16, 0))


# ===================== УВЕДОМЛЕНИЯ =====================
class NotificationsDialog(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Уведомления")
        self.configure(bg=C["card"])
        self.geometry("520x480")
        self.transient(parent)
        self.grab_set()

        wrap = tk.Frame(self, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(wrap, text="🔔 Уведомления", font=(FONT, 14, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(0, 12))

        today = date.today()
        rows = db.q("""SELECT name, end_date FROM software
                       WHERE has_license=1 AND end_date IS NOT NULL
                       AND end_date != '' AND date(end_date) <= date(?, '+30 day')
                       ORDER BY date(end_date)""", (today.isoformat(),))

        if not rows:
            tk.Label(wrap, text="Пока нет уведомлений 🎉",
                     font=(FONT, 11), fg=C["text_dim"],
                     bg=C["card"]).pack(anchor="w", pady=20)
        else:
            for r in rows:
                dl = days_left(r["end_date"])
                item = tk.Frame(wrap, bg=C["card"])
                item.pack(fill="x", pady=6)
                icon = tk.Label(item, text="⚠" if dl >= 0 else "⛔",
                                font=(FONT, 14),
                                fg=C["orange"] if dl >= 0 else C["red"],
                                bg=C["card"])
                icon.pack(side="left", padx=(0, 8))
                txt = tk.Frame(item, bg=C["card"])
                txt.pack(side="left", fill="x", expand=True)
                tk.Label(txt, text=r["name"], font=(FONT, 11, "bold"),
                         fg=C["text"], bg=C["card"], anchor="w").pack(fill="x")
                try:
                    pretty = datetime.strptime(r["end_date"], "%Y-%m-%d").strftime("%d.%m.%Y")
                except Exception:
                    pretty = r["end_date"]
                if dl < 0:
                    hint = f"Просрочено с {pretty}"
                else:
                    hint = f"Истекает {pretty} ({dl} дн.)"
                tk.Label(txt, text=hint, font=(FONT, 9),
                         fg=C["text_dim"], bg=C["card"], anchor="w").pack(fill="x")

        make_button(wrap, "Закрыть", self.destroy,
                    "primary").pack(side="right", pady=(16, 0))


# ===================== СТРАНИЦЫ =====================
class HomePage(tk.Frame):
    def __init__(self, parent, db, navigate, app):
        super().__init__(parent, bg=C["bg"])
        self.db = db
        self.navigate = navigate
        self.app = app

        TopBar(self, "Главная", "Обзор системы", app=app).pack(fill="x")
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self._build_stats(body)
        self._build_middle(body)

    def _build_stats(self, parent):
        row = tk.Frame(parent, bg=C["bg"])
        row.pack(fill="x")

        total = self.db.q("SELECT COUNT(*) c FROM software")[0]["c"]
        active = self.db.q("""SELECT COUNT(*) c FROM software
            WHERE has_license=1 AND (end_date IS NULL OR date(end_date) >= date('now'))""")[0]["c"]
        today = date.today()
        soon = self.db.q("""SELECT COUNT(*) c FROM software
            WHERE has_license=1 AND end_date IS NOT NULL
            AND date(end_date) BETWEEN date(?) AND date(?, '+30 day')""",
            (today.isoformat(), today.isoformat()))[0]["c"]
        comps = self.db.q("SELECT COUNT(*) c FROM computers")[0]["c"]

        cards = [
            ("Всего программ",    total,  "▦", C["accent"], C["accent_soft"]),
            ("Активных лицензий", active, "✓", C["green"],  C["green_bg"]),
            ("Истекает в 30 дней",soon,   "!", C["orange"], C["orange_bg"]),
            ("Компьютеров",       comps,  "🖥", C["purple"], C["purple_bg"]),
        ]
        for i, (label, value, icon, color, bg) in enumerate(cards):
            row.grid_columnconfigure(i, weight=1)
            card = card_frame(row)
            card.grid(row=0, column=i, sticky="ew",
                      padx=(0 if i == 0 else 6, 0 if i == len(cards)-1 else 6))

            inner = tk.Frame(card, bg=C["card"])
            inner.pack(fill="x", padx=18, pady=16)
            ic = tk.Label(inner, text=icon, font=(FONT, 14, "bold"),
                          fg=color, bg=bg, width=3, height=1)
            ic.pack(side="left", ipady=8, ipadx=4)
            texts = tk.Frame(inner, bg=C["card"])
            texts.pack(side="left", padx=(14, 0))
            tk.Label(texts, text=label, font=(FONT, 9),
                     fg=C["text_dim"], bg=C["card"]).pack(anchor="w")
            tk.Label(texts, text=str(value), font=(FONT, 20, "bold"),
                     fg=C["text"], bg=C["card"]).pack(anchor="w")

    def _build_middle(self, parent):
        row = tk.Frame(parent, bg=C["bg"])
        row.pack(fill="both", expand=True, pady=(20, 0))
        row.grid_columnconfigure(0, weight=2)
        row.grid_columnconfigure(1, weight=1)
        row.grid_rowconfigure(0, weight=1)

        left = card_frame(row)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        head = tk.Frame(left, bg=C["card"])
        head.pack(fill="x", padx=20, pady=(16, 6))
        tk.Label(head, text="Ближайшие окончания лицензий",
                 font=(FONT, 12, "bold"), fg=C["text"],
                 bg=C["card"]).pack(side="left")
        all_btn = tk.Label(head, text="Все →", font=(FONT, 10),
                           fg=C["accent"], bg=C["card"], cursor="hand2")
        all_btn.pack(side="right")
        all_btn.bind("<Button-1>", lambda e: self.navigate("deadlines"))

        tk.Frame(left, bg=C["border"], height=1).pack(fill="x", padx=20)

        rows = self.db.q("""SELECT id, name, end_date FROM software
                            WHERE has_license=1 AND end_date IS NOT NULL
                            ORDER BY date(end_date) ASC LIMIT 6""")
        for r in rows:
            dl = days_left(r["end_date"])
            item = tk.Frame(left, bg=C["card"])
            item.pack(fill="x", padx=20, pady=6)
            badge = tk.Label(item, text=r["name"][:1].upper(),
                             bg=C["accent_soft"], fg=C["accent"],
                             font=(FONT, 12, "bold"), width=3, height=1)
            badge.pack(side="left", ipady=6)
            mid = tk.Frame(item, bg=C["card"])
            mid.pack(side="left", padx=(12, 0), fill="x", expand=True)
            tk.Label(mid, text=r["name"], font=(FONT, 11, "bold"),
                     fg=C["text"], bg=C["card"]).pack(anchor="w")
            try:
                pretty = datetime.strptime(r["end_date"], "%Y-%m-%d").strftime("%d.%m.%Y")
            except Exception:
                pretty = r["end_date"]
            tk.Label(mid, text=f"до {pretty}", font=(FONT, 9),
                     fg=C["text_dim"], bg=C["card"]).pack(anchor="w")
            if dl is not None:
                if dl < 0:
                    txt, fg, bg = "просрочено", C["red"], C["red_bg"]
                elif dl <= 14:
                    txt, fg, bg = f"{dl} дн.", C["red"], C["red_bg"]
                elif dl <= 30:
                    txt, fg, bg = f"{dl} дн.", C["orange"], C["orange_bg"]
                else:
                    txt, fg, bg = f"{dl} дн.", C["green"], C["green_bg"]
                tk.Label(item, text=txt, font=(FONT, 9, "bold"),
                         fg=fg, bg=bg, padx=10, pady=3).pack(side="right")

        right = card_frame(row)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Программы по категориям",
                 font=(FONT, 12, "bold"), fg=C["text"],
                 bg=C["card"]).pack(anchor="w", padx=20, pady=(16, 6))
        tk.Frame(right, bg=C["border"], height=1).pack(fill="x", padx=20)

        cat_data = self.db.q("""SELECT category, COUNT(*) c FROM software
                                GROUP BY category ORDER BY c DESC""")
        total = sum(r["c"] for r in cat_data) or 1

        canvas = tk.Canvas(right, bg=C["card"], highlightthickness=0,
                           width=180, height=180)
        canvas.pack(pady=12)
        colors = [C["accent"], C["green"], C["orange"], C["purple"],
                  C["red"], "#12B0C7", "#F5B041", "#85929E"]
        start = 90
        for i, r in enumerate(cat_data):
            ext = -r["c"] / total * 360
            canvas.create_arc(10, 10, 170, 170, start=start, extent=ext,
                              fill=colors[i % len(colors)],
                              outline=C["card"], width=2)
            start += ext
        canvas.create_text(90, 90, text=f"{total}\nвсего",
                           font=(FONT, 13, "bold"), fill=C["text"],
                           justify="center")

        legend = tk.Frame(right, bg=C["card"])
        legend.pack(fill="x", padx=20, pady=(0, 16))
        for i, r in enumerate(cat_data[:6]):
            line = tk.Frame(legend, bg=C["card"])
            line.pack(fill="x", pady=2)
            tk.Label(line, bg=colors[i % len(colors)],
                     width=2, height=1).pack(side="left")
            tk.Label(line, text=r["category"] or "—", font=(FONT, 10),
                     fg=C["text"], bg=C["card"]).pack(side="left", padx=(8, 0))
            tk.Label(line, text=str(r["c"]), font=(FONT, 10, "bold"),
                     fg=C["text_dim"], bg=C["card"]).pack(side="right")


class SoftwarePage(tk.Frame):
    def __init__(self, parent, db, navigate, app):
        super().__init__(parent, bg=C["bg"])
        self.db = db
        self.navigate = navigate
        self.app = app

        TopBar(self, "Программы", "Управление программным обеспечением",
               app=app).pack(fill="x")
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        top = tk.Frame(body, bg=C["bg"])
        top.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        sw = make_entry(top, self.search_var,
                        placeholder="Поиск по названию, версии...")
        sw.pack(side="left", fill="x", expand=True, padx=(0, 12))
        make_button(top, "+ Добавить программу", self.add_dialog,
                    "primary").pack(side="right")

        card = card_frame(body)
        card.pack(fill="both", expand=True)
        header = tk.Frame(card, bg="#F9FAFB", height=42)
        header.pack(fill="x")
        header.pack_propagate(False)
        cols = [("Название", 3), ("Версия", 1), ("Категория", 2),
                ("Лицензия", 1), ("Компьютеры", 1), ("Статус", 1),
                ("Действия", 1)]
        for title, w in cols:
            tk.Label(header, text=title, font=(FONT, 10, "bold"),
                     fg=C["text_dim"], bg="#F9FAFB", anchor="w").pack(
                         side="left", fill="x", expand=True, padx=14, pady=12)

        wrap = tk.Frame(card, bg=C["card"])
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, bg=C["card"], highlightthickness=0)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=C["card"])
        self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(
                self.canvas.find_all()[0], width=e.width))

        self.refresh()

    def refresh(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()
        search = self.search_var.get().strip().lower()
        if search == "поиск по названию, версии...":
            search = ""
        sql = "SELECT * FROM software"
        params = ()
        if search:
            sql += (" WHERE LOWER(name) LIKE ? OR LOWER(version) LIKE ?"
                    " OR LOWER(category) LIKE ?")
            params = (f"%{search}%",) * 3
        sql += " ORDER BY id DESC"
        rows = self.db.q(sql, params)
        if not rows:
            tk.Label(self.rows_frame, text="Ничего не найдено",
                     font=(FONT, 11), fg=C["text_dim"],
                     bg=C["card"]).pack(pady=40)
            return
        for r in rows:
            self._make_row(r)

    def _make_row(self, r):
        row = tk.Frame(self.rows_frame, bg=C["card"], height=52)
        row.pack(fill="x")
        row.pack_propagate(False)
        tk.Frame(self.rows_frame, bg=C["border"], height=1).pack(fill="x")

        def enter(_):
            for w in row.winfo_children():
                try: w.configure(bg=C["row_hover"])
                except Exception: pass
            row.configure(bg=C["row_hover"])
        def leave(_):
            for w in row.winfo_children():
                try: w.configure(bg=C["card"])
                except Exception: pass
            row.configure(bg=C["card"])
        row.bind("<Enter>", enter)
        row.bind("<Leave>", leave)

        name_cell = tk.Frame(row, bg=C["card"])
        name_cell.pack(side="left", fill="x", expand=True, padx=14)
        icon = tk.Label(name_cell, text=r["name"][:1].upper(),
                        bg=C["accent_soft"], fg=C["accent"],
                        font=(FONT, 11, "bold"), width=3, height=1)
        icon.pack(side="left", pady=11, ipady=3)
        name_lbl = tk.Label(name_cell, text=r["name"], font=(FONT, 11),
                            fg=C["text"], bg=C["card"], anchor="w",
                            cursor="hand2")
        name_lbl.pack(side="left", padx=(10, 0), fill="x", expand=True)
        name_lbl.bind("<Button-1>", lambda e, sid=r["id"]: self.detail_dialog(sid))

        tk.Label(row, text=r["version"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)
        tk.Label(row, text=r["category"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        lic_text = "Да" if r["has_license"] else "Нет"
        lic_color = C["accent"] if r["has_license"] else C["red"]
        tk.Label(row, text=lic_text, font=(FONT, 10, "bold"),
                 fg=lic_color, bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        cnt = self.db.q(
            "SELECT COUNT(*) c FROM software_computers WHERE software_id=?",
            (r["id"],))[0]["c"]
        tk.Label(row, text=str(cnt), font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        st_txt, st_fg, st_bg = status_of(r)
        st_wrap = tk.Frame(row, bg=C["card"])
        st_wrap.pack(side="left", fill="x", expand=True, padx=14)
        tk.Label(st_wrap, text=st_txt, font=(FONT, 9, "bold"),
                 fg=st_fg, bg=st_bg, padx=10, pady=3).pack(anchor="w")

        act = tk.Frame(row, bg=C["card"])
        act.pack(side="left", fill="x", expand=True, padx=14)
        edit = tk.Label(act, text="✎", fg=C["accent"], bg=C["card"],
                        font=(FONT, 11), cursor="hand2")
        edit.pack(side="left")
        edit.bind("<Button-1>", lambda e, sid=r["id"]: self.edit_dialog(sid))
        dele = tk.Label(act, text="🗑", fg=C["red"], bg=C["card"],
                        font=(FONT, 11), cursor="hand2")
        dele.pack(side="left", padx=(10, 0))
        dele.bind("<Button-1>", lambda e, sid=r["id"]: self.delete(sid))

    def add_dialog(self):
        SoftwareDialog(self, self.db, None, self.refresh)

    def edit_dialog(self, sid):
        SoftwareDialog(self, self.db, sid, self.refresh)

    def detail_dialog(self, sid):
        SoftwareDialog(self, self.db, sid, self.refresh, readonly=True)

    def delete(self, sid):
        if not messagebox.askyesno("Удаление", "Удалить программу?"):
            return
        self.db.x("DELETE FROM software WHERE id=?", (sid,))
        self.refresh()


class SoftwareDialog(tk.Toplevel):
    def __init__(self, parent, db, sid, on_save, readonly=False):
        super().__init__(parent)
        self.db = db
        self.sid = sid
        self.on_save = on_save
        self.readonly = readonly
        self.title("Программа")
        self.configure(bg=C["card"])
        self.geometry("640x720")
        self.transient(parent)
        self.grab_set()

        wrap = tk.Frame(self, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        if readonly:
            title = "Просмотр программы"
        elif sid:
            title = "Редактирование программы"
        else:
            title = "Добавление программы"
        tk.Label(wrap, text=title, font=(FONT, 14, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(0, 4))
        tk.Label(wrap, text="Заполните поля и сохраните запись",
                 font=(FONT, 9), fg=C["text_dim"],
                 bg=C["card"]).pack(anchor="w")
        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x", pady=12)

        self.vars = {}
        form = tk.Frame(wrap, bg=C["card"])
        form.pack(fill="both", expand=True)

        self._field(form, "name", "Название программы *",
                    "Например: Microsoft Office")
        self._combo_field(form, "category", "Категория *", CATEGORIES)
        self._field(form, "version", "Версия", "Например: 2019 / 22H2")

        lic_row = tk.Frame(form, bg=C["card"])
        lic_row.pack(fill="x", pady=6)
        tk.Label(lic_row, text="Лицензия", font=(FONT, 10),
                 fg=C["text_dim"], bg=C["card"], width=22,
                 anchor="w").pack(side="left")
        self.var_lic = tk.StringVar(value="Да")
        tk.Radiobutton(lic_row, text="Да", variable=self.var_lic, value="Да",
                       bg=C["card"], fg=C["text"], selectcolor=C["card"],
                       activebackground=C["card"],
                       font=(FONT, 10)).pack(side="left")
        tk.Radiobutton(lic_row, text="Нет", variable=self.var_lic, value="Нет",
                       bg=C["card"], fg=C["text"], selectcolor=C["card"],
                       activebackground=C["card"],
                       font=(FONT, 10)).pack(side="left", padx=(10, 0))

        self._field(form, "license_key", "Ключ продукта",
                    "Введите ключ (необязательно)")
        self._field(form, "install_date", "Дата установки", "ГГГГ-ММ-ДД")
        self._field(form, "end_date", "Дата окончания лицензии", "ГГГГ-ММ-ДД")

        tk.Label(form, text="Описание", font=(FONT, 10),
                 fg=C["text_dim"], bg=C["card"], anchor="w").pack(
                     fill="x", pady=(6, 2))
        self.desc = tk.Text(form, height=4, font=(FONT, 10),
                            bg=C["input_bg"], fg=C["text"], relief="flat",
                            highlightthickness=1,
                            highlightbackground=C["input_border"],
                            highlightcolor=C["accent"], padx=8, pady=6)
        self.desc.pack(fill="x")

        tk.Label(form, text="Компьютеры", font=(FONT, 10),
                 fg=C["text_dim"], bg=C["card"], anchor="w").pack(
                     fill="x", pady=(10, 4))
        list_wrap = tk.Frame(form, bg=C["input_bg"],
                             highlightthickness=1,
                             highlightbackground=C["input_border"])
        list_wrap.pack(fill="both", expand=True)
        self.comp_vars = {}
        comps = self.db.q("SELECT * FROM computers ORDER BY hostname")
        inner_list = tk.Frame(list_wrap, bg=C["input_bg"])
        inner_list.pack(fill="both", expand=True, padx=6, pady=6)
        for c in comps:
            var = tk.BooleanVar()
            self.comp_vars[c["id"]] = var
            cb = tk.Checkbutton(
                inner_list,
                text=f"{c['hostname']} — {c['department']}",
                variable=var, bg=C["input_bg"], fg=C["text"],
                selectcolor=C["input_bg"],
                activebackground=C["input_bg"],
                font=(FONT, 10), anchor="w")
            cb.pack(fill="x")

        btns = tk.Frame(wrap, bg=C["card"])
        btns.pack(fill="x", pady=(12, 0))
        if not readonly:
            make_button(btns, "Сохранить", self.save,
                        "primary").pack(side="right")
        make_button(btns, "Отмена" if not readonly else "Закрыть",
                    self.destroy, "ghost").pack(side="right", padx=(0, 8))

        if sid:
            self.load()

    def _field(self, parent, key, label, placeholder):
        row = tk.Frame(parent, bg=C["card"])
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, font=(FONT, 10),
                 fg=C["text_dim"], bg=C["card"], width=22,
                 anchor="w").pack(side="left")
        var = tk.StringVar()
        self.vars[key] = var
        w = make_entry(row, var, placeholder=placeholder)
        w.pack(side="left", fill="x", expand=True)
        if self.readonly:
            w.entry.configure(state="disabled")

    def _combo_field(self, parent, key, label, values):
        row = tk.Frame(parent, bg=C["card"])
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, font=(FONT, 10),
                 fg=C["text_dim"], bg=C["card"], width=22,
                 anchor="w").pack(side="left")
        var = tk.StringVar()
        self.vars[key] = var
        cb = ttk.Combobox(row, textvariable=var, values=[""] + values,
                          state="disabled" if self.readonly else "readonly",
                          font=(FONT, 10))
        cb.pack(side="left", fill="x", expand=True)

    def load(self):
        r = self.db.q("SELECT * FROM software WHERE id=?", (self.sid,))[0]
        self.vars["name"].set(r["name"] or "")
        self.vars["category"].set(r["category"] or "")
        self.vars["version"].set(r["version"] or "")
        self.vars["license_key"].set(r["license_key"] or "")
        self.vars["install_date"].set(r["install_date"] or "")
        self.vars["end_date"].set(r["end_date"] or "")
        self.var_lic.set("Да" if r["has_license"] else "Нет")
        self.desc.delete("1.0", tk.END)
        self.desc.insert("1.0", r["description"] or "")
        if self.readonly:
            self.desc.configure(state="disabled")
        links = self.db.q(
            "SELECT computer_id FROM software_computers WHERE software_id=?",
            (self.sid,))
        for l in links:
            if l["computer_id"] in self.comp_vars:
                self.comp_vars[l["computer_id"]].set(True)

    def save(self):
        name = self.vars["name"].get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Название обязательно",
                                   parent=self)
            return
        category = self.vars["category"].get().strip()
        version = self.vars["version"].get().strip()
        has_lic = 1 if self.var_lic.get() == "Да" else 0
        key = self.vars["license_key"].get().strip()
        install = self.vars["install_date"].get().strip()
        end = self.vars["end_date"].get().strip()
        if key == "Введите ключ (необязательно)":
            key = ""
        if install == "ГГГГ-ММ-ДД":
            install = ""
        if end == "ГГГГ-ММ-ДД":
            end = ""
        for d, label in ((install, "Дата установки"),
                         (end, "Дата окончания")):
            if d:
                try:
                    datetime.strptime(d, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning(
                        "Ошибка", f"{label}: формат ГГГГ-ММ-ДД", parent=self)
                    return
        desc = self.desc.get("1.0", tk.END).strip()

        if self.sid:
            self.db.x("""UPDATE software SET name=?,category=?,version=?,
                         has_license=?,license_key=?,install_date=?,end_date=?,
                         description=? WHERE id=?""",
                      (name, category, version, has_lic, key, install,
                       end, desc, self.sid))
        else:
            self.sid = self.db.x("""INSERT INTO software
                (name,category,version,has_license,license_key,
                 install_date,end_date,description)
                VALUES(?,?,?,?,?,?,?,?)""",
                (name, category, version, has_lic, key, install, end, desc))

        self.db.x("DELETE FROM software_computers WHERE software_id=?",
                  (self.sid,))
        for cid, var in self.comp_vars.items():
            if var.get():
                self.db.x(
                    "INSERT OR IGNORE INTO software_computers"
                    "(software_id,computer_id) VALUES(?,?)",
                    (self.sid, cid))
        self.on_save()
        self.destroy()


class ComputersPage(tk.Frame):
    def __init__(self, parent, db, navigate, app):
        super().__init__(parent, bg=C["bg"])
        self.db = db
        self.navigate = navigate
        self.app = app

        TopBar(self, "Компьютеры", "Учёт рабочих станций",
               app=app).pack(fill="x")
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        top = tk.Frame(body, bg=C["bg"])
        top.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        sw = make_entry(top, self.search_var, placeholder="Поиск по имени ПК...")
        sw.pack(side="left", fill="x", expand=True, padx=(0, 12))
        make_button(top, "+ Добавить компьютер", self.add_dialog,
                    "primary").pack(side="right")

        card = card_frame(body)
        card.pack(fill="both", expand=True)
        header = tk.Frame(card, bg="#F9FAFB", height=42)
        header.pack(fill="x")
        header.pack_propagate(False)
        cols = [("Имя ПК", 2), ("Отдел", 2), ("Пользователь", 2),
                ("Программ", 1), ("Лицензий", 1), ("Действия", 1)]
        for title, w in cols:
            tk.Label(header, text=title, font=(FONT, 10, "bold"),
                     fg=C["text_dim"], bg="#F9FAFB", anchor="w").pack(
                         side="left", fill="x", expand=True, padx=14, pady=12)

        wrap = tk.Frame(card, bg=C["card"])
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, bg=C["card"], highlightthickness=0)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=C["card"])
        self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(
                self.canvas.find_all()[0], width=e.width))

        self.refresh()

    def refresh(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()
        search = self.search_var.get().strip().lower()
        if search == "поиск по имени пк...":
            search = ""
        sql = "SELECT * FROM computers"
        params = ()
        if search:
            sql += (" WHERE LOWER(hostname) LIKE ? OR LOWER(department) LIKE ?"
                    " OR LOWER(user) LIKE ?")
            params = (f"%{search}%",) * 3
        sql += " ORDER BY hostname"
        rows = self.db.q(sql, params)
        for c in rows:
            self._make_row(c)

    def _make_row(self, c):
        row = tk.Frame(self.rows_frame, bg=C["card"], height=52)
        row.pack(fill="x")
        row.pack_propagate(False)
        tk.Frame(self.rows_frame, bg=C["border"], height=1).pack(fill="x")

        def enter(_):
            for w in row.winfo_children():
                try: w.configure(bg=C["row_hover"])
                except Exception: pass
            row.configure(bg=C["row_hover"])
        def leave(_):
            for w in row.winfo_children():
                try: w.configure(bg=C["card"])
                except Exception: pass
            row.configure(bg=C["card"])
        row.bind("<Enter>", enter)
        row.bind("<Leave>", leave)

        host_cell = tk.Frame(row, bg=C["card"])
        host_cell.pack(side="left", fill="x", expand=True, padx=14)
        icon = tk.Label(host_cell, text="🖥", bg=C["accent_soft"],
                        fg=C["accent"], font=(FONT, 11), width=3, height=1)
        icon.pack(side="left", pady=11, ipady=3)
        tk.Label(host_cell, text=c["hostname"], font=(FONT, 11, "bold"),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", padx=(10, 0))

        tk.Label(row, text=c["department"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)
        tk.Label(row, text=c["user"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        cnt_all = self.db.q(
            "SELECT COUNT(*) c FROM software_computers WHERE computer_id=?",
            (c["id"],))[0]["c"]
        cnt_lic = self.db.q(
            """SELECT COUNT(*) c FROM software_computers sc
               JOIN software s ON s.id=sc.software_id
               WHERE sc.computer_id=? AND s.has_license=1""",
            (c["id"],))[0]["c"]
        tk.Label(row, text=str(cnt_all), font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)
        tk.Label(row, text=str(cnt_lic), font=(FONT, 10, "bold"),
                 fg=C["accent"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        act = tk.Frame(row, bg=C["card"])
        act.pack(side="left", fill="x", expand=True, padx=14)
        edit = tk.Label(act, text="✎", fg=C["accent"], bg=C["card"],
                        font=(FONT, 11), cursor="hand2")
        edit.pack(side="left")
        edit.bind("<Button-1>", lambda e, cid=c["id"]: self.edit_dialog(cid))
        dele = tk.Label(act, text="🗑", fg=C["red"], bg=C["card"],
                        font=(FONT, 11), cursor="hand2")
        dele.pack(side="left", padx=(10, 0))
        dele.bind("<Button-1>", lambda e, cid=c["id"]: self.delete(cid))

    def add_dialog(self):
        ComputerDialog(self, self.db, None, self.refresh)

    def edit_dialog(self, cid):
        ComputerDialog(self, self.db, cid, self.refresh)

    def delete(self, cid):
        if not messagebox.askyesno("Удаление", "Удалить компьютер?"):
            return
        self.db.x("DELETE FROM computers WHERE id=?", (cid,))
        self.refresh()


class ComputerDialog(tk.Toplevel):
    def __init__(self, parent, db, cid, on_save):
        super().__init__(parent)
        self.db = db
        self.cid = cid
        self.on_save = on_save
        self.title("Компьютер")
        self.configure(bg=C["card"])
        self.geometry("480x340")
        self.transient(parent)
        self.grab_set()

        wrap = tk.Frame(self, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        title = "Добавление компьютера" if not cid else "Редактирование компьютера"
        tk.Label(wrap, text=title, font=(FONT, 14, "bold"),
                 fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(0, 12))

        self.vars = {}
        for key, label, ph in [
            ("hostname", "Имя ПК *", "PC-01"),
            ("department", "Отдел", "Отдел продаж"),
            ("user", "Пользователь", "Иванов И.И."),
        ]:
            row = tk.Frame(wrap, bg=C["card"])
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, font=(FONT, 10),
                     fg=C["text_dim"], bg=C["card"], width=16,
                     anchor="w").pack(side="left")
            var = tk.StringVar()
            self.vars[key] = var
            e = make_entry(row, var, placeholder=ph)
            e.pack(side="left", fill="x", expand=True)

        btns = tk.Frame(wrap, bg=C["card"])
        btns.pack(fill="x", pady=(16, 0))
        make_button(btns, "Сохранить", self.save,
                    "primary").pack(side="right")
        make_button(btns, "Отмена", self.destroy,
                    "ghost").pack(side="right", padx=(0, 8))

        if cid:
            r = self.db.q("SELECT * FROM computers WHERE id=?", (cid,))[0]
            for k in self.vars:
                self.vars[k].set(r[k] or "")

    def save(self):
        host = self.vars["hostname"].get().strip()
        if not host or host == "PC-01":
            messagebox.showwarning("Ошибка", "Введите имя ПК", parent=self)
            return
        dept = self.vars["department"].get().strip()
        user = self.vars["user"].get().strip()
        if dept == "Отдел продаж":
            dept = ""
        if user == "Иванов И.И.":
            user = ""
        try:
            if self.cid:
                self.db.x(
                    "UPDATE computers SET hostname=?,department=?,user=? "
                    "WHERE id=?",
                    (host, dept, user, self.cid))
            else:
                self.db.x(
                    "INSERT INTO computers(hostname,department,user) "
                    "VALUES(?,?,?)",
                    (host, dept, user))
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка",
                                 "Компьютер с таким именем уже есть",
                                 parent=self)
            return
        self.on_save()
        self.destroy()


class LicensesPage(tk.Frame):
    def __init__(self, parent, db, navigate, app):
        super().__init__(parent, bg=C["bg"])
        self.db = db
        self.navigate = navigate
        self.app = app

        TopBar(self, "Лицензии", "Ключи продуктов и сроки действия",
               app=app).pack(fill="x")
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        top = tk.Frame(body, bg=C["bg"])
        top.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        sw = make_entry(top, self.search_var,
                        placeholder="Поиск по программе, ключу...")
        sw.pack(side="left", fill="x", expand=True, padx=(0, 12))

        card = card_frame(body)
        card.pack(fill="both", expand=True)
        header = tk.Frame(card, bg="#F9FAFB", height=42)
        header.pack(fill="x")
        header.pack_propagate(False)
        cols = [("Программа", 3), ("Версия", 1), ("Ключ продукта", 3),
                ("Дата установки", 2), ("Дата окончания", 2),
                ("Компьютеров", 1), ("Статус", 2)]
        for title, w in cols:
            tk.Label(header, text=title, font=(FONT, 10, "bold"),
                     fg=C["text_dim"], bg="#F9FAFB", anchor="w").pack(
                         side="left", fill="x", expand=True, padx=14, pady=12)

        wrap = tk.Frame(card, bg=C["card"])
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, bg=C["card"], highlightthickness=0)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=C["card"])
        self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(
                self.canvas.find_all()[0], width=e.width))

        self.refresh()

    def refresh(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()
        search = self.search_var.get().strip().lower()
        if search == "поиск по программе, ключу...":
            search = ""
        sql = "SELECT * FROM software WHERE has_license=1"
        params = ()
        if search:
            sql += " AND (LOWER(name) LIKE ? OR LOWER(license_key) LIKE ?)"
            params = (f"%{search}%",) * 2
        sql += (" ORDER BY CASE WHEN end_date IS NULL THEN 1 ELSE 0 END, "
                "date(end_date)")
        rows = self.db.q(sql, params)
        for s in rows:
            self._make_row(s)

    def _make_row(self, s):
        row = tk.Frame(self.rows_frame, bg=C["card"], height=52)
        row.pack(fill="x")
        row.pack_propagate(False)
        tk.Frame(self.rows_frame, bg=C["border"], height=1).pack(fill="x")

        def enter(_):
            for w in row.winfo_children():
                try: w.configure(bg=C["row_hover"])
                except Exception: pass
            row.configure(bg=C["row_hover"])
        def leave(_):
            for w in row.winfo_children():
                try: w.configure(bg=C["card"])
                except Exception: pass
            row.configure(bg=C["card"])
        row.bind("<Enter>", enter)
        row.bind("<Leave>", leave)

        name_cell = tk.Frame(row, bg=C["card"])
        name_cell.pack(side="left", fill="x", expand=True, padx=14)
        icon = tk.Label(name_cell, text=s["name"][:1].upper(),
                        bg=C["accent_soft"], fg=C["accent"],
                        font=(FONT, 11, "bold"), width=3, height=1)
        icon.pack(side="left", pady=11, ipady=3)
        tk.Label(name_cell, text=s["name"], font=(FONT, 11, "bold"),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", padx=(10, 0))

        tk.Label(row, text=s["version"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        key = s["license_key"] or "—"
        tk.Label(row, text=key, font=("Consolas", 9),
                 fg=C["text_dim"] if not s["license_key"] else C["text"],
                 bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        tk.Label(row, text=s["install_date"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)
        tk.Label(row, text=s["end_date"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        cnt = self.db.q(
            "SELECT COUNT(*) c FROM software_computers WHERE software_id=?",
            (s["id"],))[0]["c"]
        tk.Label(row, text=str(cnt), font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        st_txt, st_fg, st_bg = status_of(s)
        st_wrap = tk.Frame(row, bg=C["card"])
        st_wrap.pack(side="left", fill="x", expand=True, padx=14)
        tk.Label(st_wrap, text=st_txt, font=(FONT, 9, "bold"),
                 fg=st_fg, bg=st_bg, padx=10, pady=3).pack(anchor="w")


class DeadlinesPage(tk.Frame):
    def __init__(self, parent, db, navigate, app):
        super().__init__(parent, bg=C["bg"])
        self.db = db
        self.navigate = navigate
        self.app = app

        TopBar(self, "Сроки окончания лицензий", "Контроль дедлайнов",
               app=app).pack(fill="x")
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        top = tk.Frame(body, bg=C["bg"])
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text="Период:", font=(FONT, 10),
                 fg=C["text_dim"], bg=C["bg"]).pack(side="left", padx=(0, 6))
        self.period = tk.StringVar(value="Ближайшие 30 дней")
        cb = ttk.Combobox(top, textvariable=self.period, state="readonly",
                          values=["Все", "Ближайшие 30 дней",
                                  "Ближайшие 60 дней", "Ближайшие 90 дней",
                                  "Только просроченные"],
                          font=(FONT, 10), width=24)
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        card = card_frame(body)
        card.pack(fill="both", expand=True)
        header = tk.Frame(card, bg="#F9FAFB", height=42)
        header.pack(fill="x")
        header.pack_propagate(False)
        cols = [("Программа", 3), ("Версия", 1), ("Компьютеры", 1),
                ("Окончание", 2), ("Осталось", 2)]
        for title, w in cols:
            tk.Label(header, text=title, font=(FONT, 10, "bold"),
                     fg=C["text_dim"], bg="#F9FAFB", anchor="w").pack(
                         side="left", fill="x", expand=True, padx=14, pady=12)

        wrap = tk.Frame(card, bg=C["card"])
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, bg=C["card"], highlightthickness=0)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=C["card"])
        self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(
                self.canvas.find_all()[0], width=e.width))

        self.refresh()

    def refresh(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()
        today = date.today()
        sql = """SELECT * FROM software WHERE has_license=1
                 AND end_date IS NOT NULL AND end_date != ''"""
        params = []
        p = self.period.get()
        if p == "Ближайшие 30 дней":
            sql += " AND date(end_date) BETWEEN date(?) AND date(?, '+30 day')"
            params = [today.isoformat(), today.isoformat()]
        elif p == "Ближайшие 60 дней":
            sql += " AND date(end_date) BETWEEN date(?) AND date(?, '+60 day')"
            params = [today.isoformat(), today.isoformat()]
        elif p == "Ближайшие 90 дней":
            sql += " AND date(end_date) BETWEEN date(?) AND date(?, '+90 day')"
            params = [today.isoformat(), today.isoformat()]
        elif p == "Только просроченные":
            sql += " AND date(end_date) < date(?)"
            params = [today.isoformat()]
        sql += " ORDER BY date(end_date)"
        rows = self.db.q(sql, tuple(params))

        if not rows:
            tk.Label(self.rows_frame,
                     text="Нет лицензий в выбранном периоде",
                     font=(FONT, 11), fg=C["text_dim"],
                     bg=C["card"]).pack(pady=40)
            return

        for s in rows:
            dl = days_left(s["end_date"])
            row = tk.Frame(self.rows_frame, bg=C["card"], height=52)
            row.pack(fill="x")
            row.pack_propagate(False)
            tk.Frame(self.rows_frame, bg=C["border"], height=1).pack(fill="x")

            name_cell = tk.Frame(row, bg=C["card"])
            name_cell.pack(side="left", fill="x", expand=True, padx=14)
            icon = tk.Label(name_cell, text=s["name"][:1].upper(),
                            bg=C["accent_soft"], fg=C["accent"],
                            font=(FONT, 11, "bold"), width=3, height=1)
            icon.pack(side="left", pady=11, ipady=3)
            tk.Label(name_cell, text=s["name"], font=(FONT, 11, "bold"),
                     fg=C["text"], bg=C["card"], anchor="w").pack(
                         side="left", padx=(10, 0))

            tk.Label(row, text=s["version"] or "—", font=(FONT, 10),
                     fg=C["text"], bg=C["card"], anchor="w").pack(
                         side="left", fill="x", expand=True, padx=14)

            cnt = self.db.q(
                "SELECT COUNT(*) c FROM software_computers WHERE software_id=?",
                (s["id"],))[0]["c"]
            tk.Label(row, text=str(cnt), font=(FONT, 10),
                     fg=C["text"], bg=C["card"], anchor="w").pack(
                         side="left", fill="x", expand=True, padx=14)

            try:
                pretty = datetime.strptime(s["end_date"], "%Y-%m-%d").strftime("%d.%m.%Y")
            except Exception:
                pretty = s["end_date"]
            tk.Label(row, text=pretty, font=(FONT, 10),
                     fg=C["text"], bg=C["card"], anchor="w").pack(
                         side="left", fill="x", expand=True, padx=14)

            if dl is None:
                txt, fg, bg = "—", C["text_dim"], "#F2F4F7"
            elif dl < 0:
                txt, fg, bg = f"просрочено ({-dl} дн.)", C["red"], C["red_bg"]
            elif dl <= 14:
                txt, fg, bg = f"{dl} дн.", C["red"], C["red_bg"]
            elif dl <= 30:
                txt, fg, bg = f"{dl} дн.", C["orange"], C["orange_bg"]
            else:
                txt, fg, bg = f"{dl} дн.", C["green"], C["green_bg"]
            wrap_lbl = tk.Frame(row, bg=C["card"])
            wrap_lbl.pack(side="left", fill="x", expand=True, padx=14)
            tk.Label(wrap_lbl, text=txt, font=(FONT, 9, "bold"),
                     fg=fg, bg=bg, padx=10, pady=3).pack(anchor="w")


class FilterPage(tk.Frame):
    def __init__(self, parent, db, navigate, app):
        super().__init__(parent, bg=C["bg"])
        self.db = db
        self.navigate = navigate
        self.app = app

        TopBar(self, "Фильтрация", "Расширенный поиск",
               app=app).pack(fill="x")
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        panel = card_frame(body)
        panel.pack(fill="x", pady=(0, 12))
        grid = tk.Frame(panel, bg=C["card"])
        grid.pack(fill="x", padx=20, pady=16)
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1)

        self.f_name = tk.StringVar()
        self.f_category = tk.StringVar(value="Все категории")
        self.f_license = tk.StringVar(value="Все")
        self.f_computer = tk.StringVar(value="Все компьютеры")
        self.f_period = tk.StringVar(value="Все")
        self.f_days = tk.StringVar()

        def add_field(row, col, label, widget):
            box = tk.Frame(grid, bg=C["card"])
            box.grid(row=row, column=col, sticky="ew", padx=8, pady=8)
            tk.Label(box, text=label, font=(FONT, 10),
                     fg=C["text_dim"], bg=C["card"], anchor="w").pack(
                         fill="x", pady=(0, 4))
            widget.pack(fill="x")

        e_name = make_entry(grid, self.f_name,
                            placeholder="Введите название...")
        add_field(0, 0, "Название программы", e_name)

        cats = ["Все категории"] + CATEGORIES
        cb_cat = ttk.Combobox(grid, textvariable=self.f_category,
                              values=cats, state="readonly", font=(FONT, 10))
        add_field(0, 1, "Категория", cb_cat)

        comps = ["Все компьютеры"] + [
            c["hostname"] for c in self.db.q(
                "SELECT hostname FROM computers ORDER BY hostname")]
        cb_comp = ttk.Combobox(grid, textvariable=self.f_computer,
                               values=comps, state="readonly",
                               font=(FONT, 10))
        add_field(0, 2, "Компьютер", cb_comp)

        cb_lic = ttk.Combobox(grid, textvariable=self.f_license,
                              values=["Все", "Только с лицензией",
                                      "Без лицензии"],
                              state="readonly", font=(FONT, 10))
        add_field(1, 0, "Статус лицензии", cb_lic)

        cb_period = ttk.Combobox(
            grid, textvariable=self.f_period,
            values=["Все", "Просроченные", "Истекают в 30 дней",
                    "Истекают в 90 дней", "Действующие (>90 дней)"],
            state="readonly", font=(FONT, 10))
        add_field(1, 1, "Дата окончания лицензии", cb_period)

        e_days = make_entry(grid, self.f_days, placeholder="Например: 30")
        add_field(1, 2, "Истекает в ближайшие (дней)", e_days)

        btns = tk.Frame(panel, bg=C["card"])
        btns.pack(fill="x", padx=20, pady=(0, 16))
        make_button(btns, "Сбросить", self.reset,
                    "ghost").pack(side="right", padx=(8, 0))
        make_button(btns, "Применить", self.apply,
                    "primary").pack(side="right")

        card = card_frame(body)
        card.pack(fill="both", expand=True)

        header = tk.Frame(card, bg="#F9FAFB", height=42)
        header.pack(fill="x")
        header.pack_propagate(False)
        cols = [("Программа", 3), ("Категория", 2), ("Версия", 1),
                ("Лицензия", 1), ("Окончание", 2), ("Компьютеры", 1),
                ("Статус", 2)]
        for title, w in cols:
            tk.Label(header, text=title, font=(FONT, 10, "bold"),
                     fg=C["text_dim"], bg="#F9FAFB", anchor="w").pack(
                         side="left", fill="x", expand=True, padx=14, pady=12)

        self.summary = tk.Label(card, text="", font=(FONT, 9),
                                fg=C["text_dim"], bg=C["card"], anchor="w")
        self.summary.pack(fill="x", padx=14, pady=(6, 0))

        wrap = tk.Frame(card, bg=C["card"])
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, bg=C["card"], highlightthickness=0)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=C["card"])
        self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(
                self.canvas.find_all()[0], width=e.width))

        self.apply()

    def reset(self):
        self.f_name.set("")
        self.f_category.set("Все категории")
        self.f_license.set("Все")
        self.f_computer.set("Все компьютеры")
        self.f_period.set("Все")
        self.f_days.set("")
        self.apply()

    def apply(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()
        name = self.f_name.get().strip()
        if name == "Введите название...":
            name = ""
        cat = self.f_category.get()
        lic = self.f_license.get()
        comp = self.f_computer.get()
        period = self.f_period.get()
        days = self.f_days.get().strip()
        if days == "Например: 30":
            days = ""

        sql = "SELECT * FROM software WHERE 1=1"
        params = []
        if name:
            sql += " AND LOWER(name) LIKE ?"
            params.append(f"%{name.lower()}%")
        if cat and cat != "Все категории":
            sql += " AND category=?"
            params.append(cat)
        if lic == "Только с лицензией":
            sql += " AND has_license=1"
        elif lic == "Без лицензии":
            sql += " AND has_license=0"
        if comp and comp != "Все компьютеры":
            sql += (""" AND id IN (SELECT sc.software_id
                       FROM software_computers sc
                       JOIN computers c ON c.id=sc.computer_id
                       WHERE c.hostname=?)""")
            params.append(comp)
        today = date.today()
        if period == "Просроченные":
            sql += " AND has_license=1 AND date(end_date) < date(?)"
            params.append(today.isoformat())
        elif period == "Истекают в 30 дней":
            sql += (" AND has_license=1 AND date(end_date) BETWEEN "
                    "date(?) AND date(?, '+30 day')")
            params.extend([today.isoformat(), today.isoformat()])
        elif period == "Истекают в 90 дней":
            sql += (" AND has_license=1 AND date(end_date) BETWEEN "
                    "date(?) AND date(?, '+90 day')")
            params.extend([today.isoformat(), today.isoformat()])
        elif period == "Действующие (>90 дней)":
            sql += " AND has_license=1 AND date(end_date) > date(?, '+90 day')"
            params.append(today.isoformat())
        if days:
            try:
                n = int(days)
                sql += (" AND has_license=1 AND date(end_date) BETWEEN "
                        "date(?) AND date(?, ?)")
                params.extend([today.isoformat(), today.isoformat(),
                               f"+{n} day"])
            except ValueError:
                pass
        sql += " ORDER BY id DESC"
        rows = self.db.q(sql, tuple(params))

        if not rows:
            tk.Label(self.rows_frame, text="Ничего не найдено",
                     font=(FONT, 11), fg=C["text_dim"],
                     bg=C["card"]).pack(pady=40)
            self.summary.config(text="Найдено: 0")
            return

        ok = soon = expired = 0
        for s in rows:
            dl = days_left(s["end_date"])
            if s["has_license"]:
                if dl is not None and dl < 0:
                    expired += 1
                elif dl is not None and dl <= 30:
                    soon += 1
                else:
                    ok += 1
            self._make_row(s)

        self.summary.config(
            text=f"Найдено: {len(rows)}   ✔ активных: {ok}   "
                 f"⚠ истекает скоро: {soon}   ⛔ просрочено: {expired}")

    def _make_row(self, s):
        row = tk.Frame(self.rows_frame, bg=C["card"], height=52)
        row.pack(fill="x")
        row.pack_propagate(False)
        tk.Frame(self.rows_frame, bg=C["border"], height=1).pack(fill="x")

        name_cell = tk.Frame(row, bg=C["card"])
        name_cell.pack(side="left", fill="x", expand=True, padx=14)
        icon = tk.Label(name_cell, text=s["name"][:1].upper(),
                        bg=C["accent_soft"], fg=C["accent"],
                        font=(FONT, 11, "bold"), width=3, height=1)
        icon.pack(side="left", pady=11, ipady=3)
        tk.Label(name_cell, text=s["name"], font=(FONT, 11, "bold"),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", padx=(10, 0))

        tk.Label(row, text=s["category"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)
        tk.Label(row, text=s["version"] or "—", font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        lic_text = "Да" if s["has_license"] else "Нет"
        lic_color = C["accent"] if s["has_license"] else C["red"]
        tk.Label(row, text=lic_text, font=(FONT, 10, "bold"),
                 fg=lic_color, bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        end = s["end_date"] or "—"
        if end != "—":
            try:
                end = datetime.strptime(end, "%Y-%m-%d").strftime("%d.%m.%Y")
            except Exception:
                pass
        tk.Label(row, text=end, font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        cnt = self.db.q(
            "SELECT COUNT(*) c FROM software_computers WHERE software_id=?",
            (s["id"],))[0]["c"]
        tk.Label(row, text=str(cnt), font=(FONT, 10),
                 fg=C["text"], bg=C["card"], anchor="w").pack(
                     side="left", fill="x", expand=True, padx=14)

        st_txt, st_fg, st_bg = status_of(s)
        st_wrap = tk.Frame(row, bg=C["card"])
        st_wrap.pack(side="left", fill="x", expand=True, padx=14)
        tk.Label(st_wrap, text=st_txt, font=(FONT, 9, "bold"),
                 fg=st_fg, bg=st_bg, padx=10, pady=3).pack(anchor="w")


# ===================== ГЛАВНОЕ ОКНО =====================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IT-Инвентарь")
        self.geometry("1400x820")
        self.minsize(1200, 700)
        self.configure(bg=C["bg"])

        self.db = DB()

        self.sidebar = Sidebar(self, self.navigate)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self, bg=C["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {}
        self.current = None

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.navigate("home")

    def _make_page(self, key):
        if key in self.pages:
            return self.pages[key]
        if key == "home":
            p = HomePage(self.content, self.db, self.navigate, self)
        elif key == "software":
            p = SoftwarePage(self.content, self.db, self.navigate, self)
        elif key == "computers":
            p = ComputersPage(self.content, self.db, self.navigate, self)
        elif key == "licenses":
            p = LicensesPage(self.content, self.db, self.navigate, self)
        elif key == "deadlines":
            p = DeadlinesPage(self.content, self.db, self.navigate, self)
        elif key == "filter":
            p = FilterPage(self.content, self.db, self.navigate, self)
        else:
            return None
        self.pages[key] = p
        return p

    def navigate(self, key):
        # Динамические страницы пересоздаются, статичные — только refresh
        if key in ("home", "deadlines", "filter") and key in self.pages:
            self.pages[key].destroy()
            del self.pages[key]
        if key in ("software", "computers", "licenses") and key in self.pages:
            try:
                self.pages[key].refresh()
            except Exception:
                pass

        page = self._make_page(key)
        if page is None:
            return
        if self.current is not None and self.current is not page:
            self.current.pack_forget()
        page.pack(fill="both", expand=True)
        self.current = page
        self.sidebar.set_active(key)

    def refresh_all_topbars(self):
        """Обновить шапки, чтобы подтянуть изменения профиля."""
        for key in list(self.pages.keys()):
            try:
                self.pages[key].destroy()
            except Exception:
                pass
            del self.pages[key]
        self.current = None
        self.navigate("home")

    def _on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()