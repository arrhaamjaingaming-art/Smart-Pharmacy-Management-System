
import customtkinter as ctk
from local_config import ADMIN_USERNAME, ADMIN_PASSWORD


# SMART PHARMACY - RESPONSIVE LOGIN

BG = "#F5F8F6"
WHITE = "#FFFFFF"
GREEN = "#087B45"
DARK_GREEN = "#075B35"
TEXT = "#172B20"
MUTED = "#718078"
BORDER = "#E7EEE9"
RED = "#C03939"


class LoginPage(ctk.CTkFrame):

    def __init__(self, parent, on_login):
        super().__init__(parent, fg_color=BG)

        self.on_login = on_login

        # RESPONSIVE LOGIN CARD

        parent.update_idletasks()

        self.card = ctk.CTkFrame(
            self,
            corner_radius=25,
            fg_color=WHITE,
            border_width=1,
            border_color=BORDER
        )

        self.card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        self.card.grid_columnconfigure(0, weight=0)
        self.card.grid_columnconfigure(1, weight=1)
        self.card.grid_rowconfigure(0, weight=1)

        # LEFT BRANDING PANEL

        self.brand_panel = ctk.CTkFrame(
            self.card,
            corner_radius=22,
            fg_color=DARK_GREEN
        )

        self.brand_panel.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.brand_panel.grid_propagate(False)

        self.brand_icon = ctk.CTkLabel(
            self.brand_panel,
            text="+",
            font=("Segoe UI", 65, "bold"),
            text_color=WHITE,
            fg_color=GREEN,
            width=100,
            height=100,
            corner_radius=28
        )
        self.brand_icon.pack(pady=(85, 25))

        self.brand_title = ctk.CTkLabel(
            self.brand_panel,
            text="SMART\nPHARMACY",
            font=("Segoe UI", 29, "bold"),
            text_color=WHITE,
            justify="center"
        )
        self.brand_title.pack(pady=5)

        self.brand_subtitle = ctk.CTkLabel(
            self.brand_panel,
            text="MEDICINE & PHARMACY\nMANAGEMENT SYSTEM",
            font=("Segoe UI", 10, "bold"),
            text_color="#BCE8CB",
            justify="center"
        )
        self.brand_subtitle.pack(pady=(12, 30))

        self.brand_line = ctk.CTkFrame(
            self.brand_panel,
            width=65,
            height=3,
            fg_color="#73C997",
            corner_radius=5
        )
        self.brand_line.pack(pady=5)

        self.brand_description = ctk.CTkLabel(
            self.brand_panel,
            text="Manage your pharmacy.\nSimplify your daily work.",
            font=("Segoe UI", 13),
            text_color="#D7F0DF",
            justify="center"
        )
        self.brand_description.pack(pady=25)

        self.brand_footer = ctk.CTkLabel(
            self.brand_panel,
            text="SMART PHARMACY  •  CSC PROJECT",
            font=("Segoe UI", 9, "bold"),
            text_color="#A9D8B9"
        )
        self.brand_footer.pack(
            side="bottom",
            pady=25
        )

        # RIGHT LOGIN PANEL

        self.login_panel = ctk.CTkFrame(
            self.card,
            fg_color="transparent"
        )

        self.login_panel.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.login_panel.grid_columnconfigure(0, weight=1)

        self.welcome_label = ctk.CTkLabel(
            self.login_panel,
            text="Welcome back",
            font=("Segoe UI", 29, "bold"),
            text_color=TEXT
        )
        self.welcome_label.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(25, 5)
        )

        self.subtitle_label = ctk.CTkLabel(
            self.login_panel,
            text="Sign in to continue to your pharmacy dashboard.",
            font=("Segoe UI", 12),
            text_color=MUTED
        )
        self.subtitle_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 30)
        )

        # USERNAME

        ctk.CTkLabel(
            self.login_panel,
            text="USERNAME",
            font=("Segoe UI", 11, "bold"),
            text_color=TEXT
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=(5, 7)
        )

        self.username = ctk.CTkEntry(
            self.login_panel,
            height=48,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            fg_color=BG,
            text_color=TEXT,
            placeholder_text="Enter your username",
            font=("Segoe UI", 13)
        )
        self.username.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        # PASSWORD

        ctk.CTkLabel(
            self.login_panel,
            text="PASSWORD",
            font=("Segoe UI", 11, "bold"),
            text_color=TEXT
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=(0, 7)
        )

        self.password = ctk.CTkEntry(
            self.login_panel,
            height=48,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            fg_color=BG,
            text_color=TEXT,
            placeholder_text="Enter your password",
            show="*",
            font=("Segoe UI", 13)
        )
        self.password.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        # SHOW PASSWORD

        self.show_password = ctk.CTkCheckBox(
            self.login_panel,
            text="Show password",
            font=("Segoe UI", 11),
            text_color=MUTED,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            command=self.toggle_password
        )
        self.show_password.grid(
            row=6,
            column=0,
            sticky="w",
            pady=(0, 12)
        )

        # ERROR MESSAGE

        self.message = ctk.CTkLabel(
            self.login_panel,
            text="",
            font=("Segoe UI", 11),
            text_color=RED,
            wraplength=360
        )
        self.message.grid(
            row=7,
            column=0,
            sticky="w",
            pady=3
        )

        # LOGIN BUTTON

        self.login_button = ctk.CTkButton(
            self.login_panel,
            text="Sign In",
            height=49,
            corner_radius=13,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            text_color=WHITE,
            font=("Segoe UI", 14, "bold"),
            command=self.authenticate
        )
        self.login_button.grid(
            row=8,
            column=0,
            sticky="ew",
            pady=(12, 15)
        )

        ctk.CTkLabel(
            self.login_panel,
            text="Secure Administrator Access",
            font=("Segoe UI", 10),
            text_color=MUTED
        ).grid(
            row=9,
            column=0,
            pady=(5, 0)
        )

        # KEYBOARD SUPPORT

        self.username.bind(
            "<Return>",
            lambda event: self.password.focus()
        )

        self.password.bind(
            "<Return>",
            lambda event: self.authenticate()
        )

        self.username.focus()

        # AUTOMATIC RESIZING

        self.bind("<Configure>", self.resize_login)

        self.after(100, self.resize_login)

    def resize_login(self, event=None):

        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Calculate available space

        card_width = min(900, width - 40)
        card_height = min(550, height - 40)

        card_width = max(500, card_width)
        card_height = max(400, card_height)

        # Responsive scale

        scale = min(
            card_width / 900.0,
            card_height / 550.0
        )

        scale = min(1.0, scale)

        # Resize main card

        self.card.configure(
            width=card_width,
            height=card_height
        )

        self.card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Resize branding panel

        brand_width = int(card_width * 0.36)

        self.brand_panel.configure(
            width=brand_width
        )

        # Adjust branding sizes

        self.brand_icon.configure(
            width=int(100 * scale),
            height=int(100 * scale),
            font=("Segoe UI", max(38, int(65 * scale)), "bold")
        )

        self.brand_title.configure(
            font=("Segoe UI", max(19, int(29 * scale)), "bold")
        )

        self.brand_subtitle.configure(
            font=("Segoe UI", max(8, int(10 * scale)), "bold")
        )

        self.brand_description.configure(
            font=("Segoe UI", max(10, int(13 * scale)))
        )

        self.brand_footer.configure(
            font=("Segoe UI", max(7, int(9 * scale)), "bold")
        )

        # Adjust branding spacing

        self.brand_icon.pack_configure(
            pady=(max(25, int(85 * scale)), max(10, int(25 * scale)))
        )

        self.brand_subtitle.pack_configure(
            pady=(max(5, int(12 * scale)), max(10, int(30 * scale)))
        )

        self.brand_description.pack_configure(
            pady=max(10, int(25 * scale))
        )

        self.brand_footer.pack_configure(
            pady=max(10, int(25 * scale))
        )

        # Adjust login panel spacing

        self.login_panel.grid_configure(
            padx=max(18, int(55 * scale)),
            pady=max(15, int(45 * scale))
        )

        self.welcome_label.configure(
            font=("Segoe UI", max(19, int(29 * scale)), "bold")
        )

        self.subtitle_label.configure(
            font=("Segoe UI", max(9, int(12 * scale)))
        )

    def toggle_password(self):

        if self.show_password.get():
            self.password.configure(show="")
        else:
            self.password.configure(show="*")

    def authenticate(self):

        username = self.username.get().strip()
        password = self.password.get()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            self.login_button.configure(state="disabled")
            self.on_login()

        else:

            self.message.configure(
                text="Invalid username or password. Please try again."
            )

            self.password.delete(0, "end")
            self.password.focus()