
import customtkinter as ctk


# SMART PHARMACY - MODERN EMERALD THEME

BG = "#F5F8F6"
WHITE = "#FFFFFF"
GREEN = "#087B45"
DARK_GREEN = "#075B35"
LIGHT_GREEN = "#E8F5ED"
TEXT = "#172B20"
MUTED = "#718078"
BORDER = "#E7EEE9"


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent, get_statistics):
        super().__init__(parent, fg_color=BG)

        self.get_statistics = get_statistics
        self.cards = []

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(4, weight=1)

        # HEADER

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.grid(
            row=0, column=0,
            columnspan=2,
            sticky="ew",
            padx=15, pady=(15, 12)
        )

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Good day, Administrator",
            font=("Segoe UI", 27, "bold"),
            text_color=TEXT
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Here's what's happening in your pharmacy today.",
            font=("Segoe UI", 13),
            text_color=MUTED
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        ctk.CTkButton(
            header,
            text="Refresh",
            width=105,
            height=36,
            corner_radius=12,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            font=("Segoe UI", 12, "bold"),
            command=self.refresh
        ).grid(row=0, column=1, rowspan=2, padx=5)

        # WELCOME BANNER

        banner = ctk.CTkFrame(
            self,
            fg_color=DARK_GREEN,
            corner_radius=20,
            height=145
        )
        banner.grid(
            row=1, column=0,
            columnspan=2,
            sticky="ew",
            padx=15, pady=12
        )
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            banner,
            text="SMART PHARMACY",
            font=("Segoe UI", 12, "bold"),
            text_color="#BCE8CB"
        ).grid(
            row=0, column=0,
            sticky="w",
            padx=25, pady=(20, 4)
        )

        ctk.CTkLabel(
            banner,
            text="Your pharmacy, under control.",
            font=("Segoe UI", 23, "bold"),
            text_color=WHITE
        ).grid(
            row=1, column=0,
            sticky="w", padx=25
        )

        ctk.CTkLabel(
            banner,
            text="Monitor stock, manage medicines and keep business moving.",
            font=("Segoe UI", 12),
            text_color="#D7F0DF"
        ).grid(
            row=2, column=0,
            sticky="w",
            padx=25, pady=(5, 15)
        )

        # STATISTICS

        card_data = [
            ("MEDICINE TYPES", "0", "Registered medicines", GREEN),
            ("TOTAL STOCK UNITS", "0", "Units available", "#2878B8"),
            ("LOW STOCK ITEMS", "0", "Items needing attention", "#D28A20"),
            ("TOTAL BILLS", "0", "Bills generated", "#8056B5")
        ]

        for index, (name, value, subtitle, accent) in enumerate(card_data):

            row = 2 + index // 2
            col = index % 2

            card = ctk.CTkFrame(
                self,
                fg_color=WHITE,
                corner_radius=18,
                border_width=1,
                border_color=BORDER,
                height=135
            )

            card.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=10,
                pady=9
            )

            card.grid_propagate(False)

            ctk.CTkFrame(
                card,
                fg_color=accent,
                width=5,
                corner_radius=5
            ).pack(side="left", fill="y", padx=(0, 14), pady=18)

            details = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            details.pack(
                side="left",
                fill="both",
                expand=True,
                pady=17
            )

            ctk.CTkLabel(
                details,
                text=name,
                font=("Segoe UI", 11, "bold"),
                text_color=MUTED
            ).pack(anchor="w")

            value_label = ctk.CTkLabel(
                details,
                text=value,
                font=("Segoe UI", 29, "bold"),
                text_color=TEXT
            )
            value_label.pack(anchor="w", pady=(2, 0))

            ctk.CTkLabel(
                details,
                text=subtitle,
                font=("Segoe UI", 11),
                text_color=MUTED
            ).pack(anchor="w", pady=(2, 0))

            self.cards.append(value_label)

        # BOTTOM INFORMATION PANEL

        overview = ctk.CTkFrame(
            self,
            fg_color=WHITE,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )

        overview.grid(
            row=4, column=0,
            columnspan=2,
            sticky="nsew",
            padx=10,
            pady=(15, 10)
        )

        ctk.CTkLabel(
            overview,
            text="Your workspace",
            font=("Segoe UI", 19, "bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=22, pady=(18, 5))

        ctk.CTkLabel(
            overview,
            text="Everything you need to manage your pharmacy in one place.",
            font=("Segoe UI", 12),
            text_color=MUTED
        ).pack(anchor="w", padx=22, pady=(0, 15))

        features = [
            ("01", "Inventory management",
             "Manage medicine details, batches and available stock."),
            ("02", "Billing and invoices",
             "Create customer bills and manage transactions."),
            ("03", "Business management",
             "Keep your pharmacy information organised.")
        ]

        for number, title, description in features:

            item = ctk.CTkFrame(
                overview,
                fg_color=BG,
                corner_radius=12
            )
            item.pack(
                fill="x",
                padx=18,
                pady=5
            )

            ctk.CTkLabel(
                item,
                text=number,
                font=("Segoe UI", 13, "bold"),
                text_color=GREEN
            ).pack(side="left", padx=15, pady=12)

            info = ctk.CTkFrame(
                item,
                fg_color="transparent"
            )
            info.pack(side="left", fill="x", expand=True, pady=9)

            ctk.CTkLabel(
                info,
                text=title,
                font=("Segoe UI", 12, "bold"),
                text_color=TEXT
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=description,
                font=("Segoe UI", 10),
                text_color=MUTED
            ).pack(anchor="w", pady=(2, 0))

        self.refresh()

    def refresh(self):

        try:
            statistics = self.get_statistics()

            for label, value in zip(self.cards, statistics):
                label.configure(text=str(value))

        except Exception as error:
            print("Dashboard refresh error:", error)
