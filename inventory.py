import customtkinter as ctk
import mysql.connector
from tkinter import messagebox
from datetime import datetime

from database import get_connection


# THEME
BG = "#F5F8F6"
WHITE = "#FFFFFF"
GREEN = "#087B45"
DARK_GREEN = "#075B35"
LIGHT_GREEN = "#E8F5ED"
TEXT = "#172B20"
MUTED = "#718078"
BORDER = "#E7EEE9"
RED = "#B83A3A"


class InventoryPage(ctk.CTkFrame):

    def __init__(self, parent, db_path=None):
        super().__init__(parent, fg_color=BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # HEADER
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(5, 15))

        ctk.CTkLabel(
            header,
            text="Medicine Inventory",
            font=("Segoe UI", 27, "bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Manage medicines, stock levels and expiry dates",
            font=("Segoe UI", 12),
            text_color=MUTED
        ).pack(anchor="w", pady=(3, 0))

        # ADD MEDICINE CARD
        form = ctk.CTkFrame(
            self,
            fg_color=WHITE,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            form,
            text="Add New Medicine",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT
        ).grid(
            row=0, column=0, columnspan=2,
            sticky="w", padx=20, pady=(17, 10)
        )

        self.fields = {}

        field_data = [
            ("Medicine Name", "name"),
            ("Category", "category"),
            ("Batch Number", "batch"),
            ("Purchase Price (₹)", "purchase"),
            ("Selling Price (₹)", "selling"),
            ("Quantity", "quantity"),
            ("Expiry Date (YYYY-MM-DD)", "expiry")
        ]

        for index, (label, key) in enumerate(field_data):

            row = 1 + (index // 2) * 2
            col = index % 2

            ctk.CTkLabel(
                form,
                text=label,
                font=("Segoe UI", 11, "bold"),
                text_color=MUTED
            ).grid(
                row=row,
                column=col,
                sticky="w",
                padx=20,
                pady=(7, 3)
            )

            entry = ctk.CTkEntry(
                form,
                height=38,
                corner_radius=10,
                border_color=BORDER,
                fg_color="#FAFCFA",
                text_color=TEXT,
                placeholder_text=label,
                font=("Segoe UI", 12)
            )

            entry.grid(
                row=row + 1,
                column=col,
                sticky="ew",
                padx=20,
                pady=(0, 5)
            )

            self.fields[key] = entry

        # MESSAGE
        self.message = ctk.CTkLabel(
            form,
            text="",
            font=("Segoe UI", 11),
            text_color=RED
        )
        self.message.grid(
            row=8,
            column=0,
            columnspan=2,
            pady=(5, 0)
        )

        # SAVE BUTTON
        ctk.CTkButton(
            form,
            text="＋  Save Medicine",
            height=42,
            corner_radius=11,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            font=("Segoe UI", 13, "bold"),
            command=self.add_medicine
        ).grid(
            row=9,
            column=0,
            columnspan=2,
            padx=20,
            pady=(8, 18),
            sticky="ew"
        )

        # SEARCH BAR
        search_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        search_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 10)
        )
        search_frame.grid_columnconfigure(0, weight=1)

        self.search = ctk.CTkEntry(
            search_frame,
            height=42,
            corner_radius=12,
            border_color=BORDER,
            fg_color=WHITE,
            text_color=TEXT,
            placeholder_text="Search by medicine name...",
            font=("Segoe UI", 12)
        )
        self.search.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10)
        )

        self.search.bind(
            "<KeyRelease>",
            lambda event: self.refresh()
        )

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=105,
            height=42,
            corner_radius=11,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            command=self.refresh
        ).grid(row=0, column=1)

        # MEDICINE LIST
        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=WHITE,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )
        self.list_frame.grid(
            row=3,
            column=0,
            sticky="nsew"
        )

        self.refresh()

    # ADD MEDICINE

    def add_medicine(self):

        connection = None
        cursor = None

        try:
            name = self.fields["name"].get().strip()
            category = self.fields["category"].get().strip()
            batch = self.fields["batch"].get().strip()
            purchase = float(self.fields["purchase"].get())
            selling = float(self.fields["selling"].get())
            quantity = int(self.fields["quantity"].get())
            expiry = self.fields["expiry"].get().strip()

            if not all([name, category, batch, expiry]):
                raise ValueError("Please fill in all fields.")

            if purchase < 0 or selling < 0 or quantity < 0:
                raise ValueError("Values cannot be negative.")

            if selling < purchase:
                raise ValueError(
                    "Selling price cannot be below purchase price."
                )

            try:
                datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    "Expiry date must use YYYY-MM-DD format."
                )

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO medicines
                (
                    name, batch_number, category,
                    purchase_price, selling_price,
                    quantity, expiry_date, mrp
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                name,
                batch,
                category,
                purchase,
                selling,
                quantity,
                expiry,
                selling
            ))

            connection.commit()

            for entry in self.fields.values():
                entry.delete(0, "end")

            self.message.configure(
                text="Medicine saved successfully!",
                text_color=GREEN
            )

            self.refresh()

        except mysql.connector.IntegrityError:
            self.message.configure(
                text="Batch number already exists!",
                text_color=RED
            )

        except (ValueError, TypeError) as error:
            self.message.configure(
                text=str(error),
                text_color=RED
            )

        except mysql.connector.Error as error:
            self.message.configure(
                text="Database error: " + str(error),
                text_color=RED
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # REFRESH MEDICINE LIST

    def refresh(self):

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        search_text = self.search.get().strip()

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    id, name, category, batch_number,
                    selling_price, quantity, expiry_date
                FROM medicines
                WHERE name LIKE %s AND is_active = 1
                ORDER BY name
            """, ("%" + search_text + "%",))

            medicines = cursor.fetchall()

        except mysql.connector.Error as error:

            ctk.CTkLabel(
                self.list_frame,
                text="Database error: " + str(error),
                text_color=RED
            ).pack(pady=20)

            return

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

        # EMPTY STATE
        if not medicines:
            ctk.CTkLabel(
                self.list_frame,
                text="No medicines found",
                font=("Segoe UI", 15, "bold"),
                text_color=MUTED
            ).pack(pady=(35, 5))

            ctk.CTkLabel(
                self.list_frame,
                text="Add a medicine or try another search.",
                font=("Segoe UI", 11),
                text_color=MUTED
            ).pack(pady=(0, 30))

            return

        # LIST HEADER
        ctk.CTkLabel(
            self.list_frame,
            text="  MEDICINE DETAILS",
            font=("Segoe UI", 11, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=15, pady=(12, 5))

        for medicine in medicines:

            (
                med_id,
                name,
                category,
                batch,
                price,
                quantity,
                expiry
            ) = medicine

            row = ctk.CTkFrame(
                self.list_frame,
                fg_color="#F7FAF8",
                corner_radius=12,
                border_width=1,
                border_color=BORDER
            )
            row.pack(
                fill="x",
                padx=10,
                pady=5
            )

            details_frame = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            details_frame.pack(
                side="left",
                fill="both",
                expand=True,
                padx=14,
                pady=12
            )

            ctk.CTkLabel(
                details_frame,
                text=name,
                font=("Segoe UI", 14, "bold"),
                text_color=TEXT
            ).pack(anchor="w")

            ctk.CTkLabel(
                details_frame,
                text=category + "  |  Batch: " + str(batch),
                font=("Segoe UI", 11),
                text_color=MUTED
            ).pack(anchor="w", pady=(3, 5))

            info = (
                "Selling Price: Rs. {:.2f}   |   "
                "Stock: {}   |   Expiry: {}"
            ).format(float(price), quantity, expiry)

            ctk.CTkLabel(
                details_frame,
                text=info,
                font=("Segoe UI", 11),
                text_color=GREEN if quantity > 10 else RED
            ).pack(anchor="w")

            ctk.CTkButton(
                row,
                text="Delete",
                width=75,
                height=32,
                corner_radius=9,
                fg_color="#FCECEC",
                hover_color="#F5D5D5",
                text_color=RED,
                font=("Segoe UI", 11, "bold"),
                command=lambda mid=med_id: self.delete_medicine(mid)
            ).pack(
                side="right",
                padx=12
            )

    # DELETE MEDICINE

    def delete_medicine(self, medicine_id):

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Remove this medicine from the active inventory?"
        )

        if not confirm:
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            # Mark inactive instead of permanently deleting.
            cursor.execute(
                "UPDATE medicines SET is_active = 0 WHERE id = %s",
                (medicine_id,)
            )

            connection.commit()

            self.message.configure(
                text="Medicine removed from active inventory.",
                text_color=GREEN
            )

            self.refresh()

        except mysql.connector.Error as error:

            self.message.configure(
                text="Delete failed: " + str(error),
                text_color=RED
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()