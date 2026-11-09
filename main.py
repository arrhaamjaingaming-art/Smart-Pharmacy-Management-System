
import customtkinter as ctk
from tkinter import messagebox

from database import (
    initialize_database,
    get_connection,
    get_business_profile
)

from modules.login import LoginPage
from modules.dashboard import DashboardPage
from modules.inventory import InventoryPage
from modules.billing import BillingPage, BillHistoryPage
from modules.company_details import CompanyDetailsPage


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class SmartPharmacyApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SMART PHARMACY MANAGEMENT SYSTEM")
        self.geometry("1150x750")
        self.minsize(950, 650)
        self.configure(fg_color="#F4F7F5")

        initialize_database()

        self.show_login()

    # WINDOW MANAGEMENT

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    # LOGIN

    def show_login(self):
        self.clear_window()

        login_page = LoginPage(
            self,
            self.check_company_registration
        )

        login_page.pack(fill="both", expand=True)

    # FIRST-TIME COMPANY REGISTRATION

    def check_company_registration(self):

        try:
            profile = get_business_profile()

            if not profile or profile.get("setup_locked") != 1:
                self.show_company_registration()
            else:
                self.show_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Registration Check Error",
                "Could not check company registration:\n\n"
                + str(error)
            )

            self.show_login()

    def show_company_registration(self):

        self.clear_window()

        registration_page = CompanyDetailsPage(
            self,
            on_saved=self.show_dashboard
        )

        registration_page.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

    # MAIN DASHBOARD

    def show_dashboard(self):

        self.clear_window()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()

        self.content = ctk.CTkFrame(
            self,
            fg_color="#F4F7F5",
            corner_radius=0
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=25,
            pady=20
        )

        self.show_page("Dashboard")

    # SIDEBAR

    def create_sidebar(self):

        sidebar = ctk.CTkFrame(
            self,
            width=225,
            corner_radius=0,
            fg_color="#124D34"
        )

        sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="SMART\nPHARMACY",
            font=("Arial", 25, "bold"),
            text_color="white"
        ).pack(pady=(35, 45))

        navigation = [
            ("Dashboard", "Dashboard"),
            ("Medicine Inventory", "Inventory"),
            ("Customer Billing", "Billing"),
            ("Bill History", "History"),
            ("Company Details", "Company")
        ]

        for label, page in navigation:

            ctk.CTkButton(
                sidebar,
                text=label,
                height=46,
                anchor="w",
                fg_color="transparent",
                hover_color="#287A55",
                text_color="white",
                font=("Arial", 14),
                command=lambda p=page: self.show_page(p)
            ).pack(
                fill="x",
                padx=14,
                pady=6
            )

        ctk.CTkButton(
            sidebar,
            text="LOGOUT",
            height=42,
            fg_color="#A83C3C",
            hover_color="#852D2D",
            command=self.show_login
        ).pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=25
        )

    # PAGE CONTROLLER

    def show_page(self, page_name):

        for widget in self.content.winfo_children():
            widget.destroy()

        if page_name == "Dashboard":

            page = DashboardPage(
                self.content,
                self.get_statistics
            )

        elif page_name == "Inventory":

            page = InventoryPage(
                self.content,
                None
            )

        elif page_name == "Billing":

            page = BillingPage(
                self.content,
                None
            )

        elif page_name == "History":

            page = BillHistoryPage(
                self.content,
                None
            )

        elif page_name == "Company":

            page = CompanyDetailsPage(
                self.content,
                None
            )

        else:
            return

        page.pack(fill="both", expand=True)

    # DASHBOARD STATISTICS

    def get_statistics(self):

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute(
                "SELECT COUNT(*) FROM medicines"
            )
            medicine_types = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM medicines"
            )
            stock_units = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM medicines WHERE quantity <= 10"
            )
            low_stock = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM bills"
            )
            total_bills = cursor.fetchone()[0]

            return (
                medicine_types,
                stock_units,
                low_stock,
                total_bills
            )

        finally:
            cursor.close()
            connection.close()


if __name__ == "__main__":

    app = SmartPharmacyApp()
    app.mainloop()
