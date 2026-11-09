
import customtkinter as ctk
from tkinter import messagebox

from database import get_business_profile, save_business_profile


BG = "#F5F8F6"
WHITE = "#FFFFFF"
GREEN = "#087B45"
DARK_GREEN = "#075B35"
TEXT = "#172B20"
MUTED = "#718078"
BORDER = "#E7EEE9"


class CompanyDetailsPage(ctk.CTkFrame):

    def __init__(self, parent, db_path=None, on_saved=None):
        super().__init__(parent, fg_color=BG)

        self.entries = {}
        self.on_saved = on_saved

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Company Registration & Details",
            font=("Segoe UI", 27, "bold"),
            text_color=TEXT
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 4))

        ctk.CTkLabel(
            self,
            text="Enter your pharmacy information for invoices.",
            font=("Segoe UI", 13),
            text_color=MUTED
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 18))

        card = ctk.CTkScrollableFrame(
            self,
            fg_color=WHITE,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )

        card.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=15,
            pady=5
        )

        self.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure((0, 1), weight=1)

        fields = [
            ("business_name", "Pharmacy / Company Name"),
            ("owner_name", "Owner Name"),
            ("phone", "Phone Number"),
            ("email", "Email Address"),
            ("gstin", "GSTIN"),
            ("drug_license_1", "Drug Licence Number 1"),
            ("drug_license_2", "Drug Licence Number 2"),
            ("invoice_prefix", "Invoice Prefix")
        ]

        for index, (key, label) in enumerate(fields):

            row = index // 2
            col = index % 2

            ctk.CTkLabel(
                card,
                text=label,
                font=("Segoe UI", 12, "bold"),
                text_color=TEXT
            ).grid(
                row=row * 2,
                column=col,
                sticky="w",
                padx=18,
                pady=(14, 4)
            )

            entry = ctk.CTkEntry(
                card,
                height=40,
                corner_radius=10,
                border_color=BORDER,
                fg_color=BG,
                text_color=TEXT,
                font=("Segoe UI", 12)
            )

            entry.grid(
                row=row * 2 + 1,
                column=col,
                sticky="ew",
                padx=18,
                pady=(0, 8)
            )

            self.entries[key] = entry

        ctk.CTkLabel(
            card,
            text="Business Address",
            font=("Segoe UI", 12, "bold"),
            text_color=TEXT
        ).grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(14, 4)
        )

        self.address = ctk.CTkTextbox(
            card,
            height=90,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
            fg_color=BG,
            text_color=TEXT,
            font=("Segoe UI", 12)
        )

        self.address.grid(
            row=9,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=18,
            pady=(0, 15)
        )

        self.save_button = ctk.CTkButton(
            card,
            text="Save Company Details",
            height=45,
            corner_radius=12,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            font=("Segoe UI", 13, "bold"),
            command=self.save_details
        )

        self.save_button.grid(
            row=10,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=18,
            pady=(5, 20)
        )

        self.load_details()

    def load_details(self):

        try:
            profile = get_business_profile()

            if not profile:
                return

            for key, entry in self.entries.items():
                entry.insert(0, str(profile.get(key) or ""))

            self.address.insert(
                "1.0",
                str(profile.get("address") or "")
            )

            if profile.get("setup_locked") == 1:
                self.disable_fields()

        except Exception as error:
            messagebox.showerror(
                "Company Details",
                "Could not load company details:\n" + str(error)
            )

    def disable_fields(self):

        for entry in self.entries.values():
            entry.configure(state="disabled")

        self.address.configure(state="disabled")

        self.save_button.configure(
            state="disabled",
            text="Registration Already Locked"
        )

    def save_details(self):

        values = {}

        for key, entry in self.entries.items():
            values[key] = entry.get().strip()

        address = self.address.get("1.0", "end").strip()

        if not values["business_name"]:
            messagebox.showwarning(
                "Required Field",
                "Please enter the pharmacy name."
            )
            return

        if not values["owner_name"]:
            messagebox.showwarning(
                "Required Field",
                "Please enter the owner's name."
            )
            return

        if not values["phone"]:
            messagebox.showwarning(
                "Required Field",
                "Please enter the phone number."
            )
            return

        if not address:
            messagebox.showwarning(
                "Required Field",
                "Please enter the business address."
            )
            return

        prefix = values["invoice_prefix"] or "PP"

        try:
            save_business_profile(
                business_name=values["business_name"],
                owner_name=values["owner_name"],
                address=address,
                phone=values["phone"],
                email=values["email"],
                gstin=values["gstin"],
                drug_license_1=values["drug_license_1"],
                drug_license_2=values["drug_license_2"],
                invoice_prefix=prefix
            )

            self.disable_fields()

            messagebox.showinfo(
                "Saved Successfully",
                "Company details have been saved successfully!"
            )

            if self.on_saved:
                self.on_saved()

        except Exception as error:
            messagebox.showerror(
                "Save Error",
                str(error)
            )
