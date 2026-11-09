
import os
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk
import mysql.connector

from database import get_connection
from modules.invoice import create_invoice_pdf


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


class BillingPage(ctk.CTkFrame):

    def __init__(self, parent, db_path=None):
        super().__init__(parent, fg_color=BG)

        self.cart = []
        self.medicines = []
        self.medicine_options = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # HEADER
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(5, 14))

        ctk.CTkLabel(
            header,
            text="Customer Billing",
            font=("Segoe UI", 27, "bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Create bills and generate customer invoices",
            font=("Segoe UI", 12),
            text_color=MUTED
        ).pack(anchor="w", pady=(3, 0))

        # CUSTOMER AND MEDICINE CARD
        form = ctk.CTkFrame(
            self,
            fg_color=WHITE,
            corner_radius=17,
            border_width=1,
            border_color=BORDER
        )
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            form,
            text="New Customer Bill",
            font=("Segoe UI", 17, "bold"),
            text_color=TEXT
        ).grid(
            row=0, column=0, columnspan=2,
            sticky="w", padx=18, pady=(15, 8)
        )

        ctk.CTkLabel(
            form,
            text="Customer Name",
            font=("Segoe UI", 11, "bold"),
            text_color=MUTED
        ).grid(
            row=1, column=0, sticky="w",
            padx=18, pady=(5, 3)
        )

        ctk.CTkLabel(
            form,
            text="Select Medicine",
            font=("Segoe UI", 11, "bold"),
            text_color=MUTED
        ).grid(
            row=1, column=1, sticky="w",
            padx=18, pady=(5, 3)
        )

        self.customer_entry = ctk.CTkEntry(
            form,
            height=38,
            corner_radius=10,
            border_color=BORDER,
            fg_color="#FAFCFA",
            text_color=TEXT,
            placeholder_text="Customer name",
            font=("Segoe UI", 12)
        )
        self.customer_entry.grid(
            row=2, column=0,
            sticky="ew", padx=18, pady=(0, 8)
        )

        self.medicine_menu = ctk.CTkOptionMenu(
            form,
            values=["Loading medicines..."],
            height=38,
            corner_radius=10,
            fg_color=GREEN,
            button_color=DARK_GREEN,
            button_hover_color="#064629",
            font=("Segoe UI", 11)
        )
        self.medicine_menu.grid(
            row=2, column=1,
            sticky="ew", padx=18, pady=(0, 8)
        )

        ctk.CTkLabel(
            form,
            text="Quantity",
            font=("Segoe UI", 11, "bold"),
            text_color=MUTED
        ).grid(
            row=3, column=0,
            sticky="w", padx=18, pady=(4, 3)
        )

        self.quantity_entry = ctk.CTkEntry(
            form,
            height=38,
            corner_radius=10,
            border_color=BORDER,
            fg_color="#FAFCFA",
            text_color=TEXT,
            placeholder_text="Enter quantity",
            font=("Segoe UI", 12)
        )
        self.quantity_entry.grid(
            row=4, column=0,
            sticky="ew", padx=18, pady=(0, 12)
        )

        ctk.CTkButton(
            form,
            text="+  Add to Bill",
            height=38,
            corner_radius=10,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            font=("Segoe UI", 12, "bold"),
            command=self.add_to_cart
        ).grid(
            row=4, column=1,
            sticky="ew", padx=18, pady=(0, 12)
        )

        self.message = ctk.CTkLabel(
            form,
            text="",
            font=("Segoe UI", 11),
            text_color=RED
        )
        self.message.grid(
            row=5, column=0,
            columnspan=2, pady=(0, 8)
        )

        # CART
        self.cart_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=WHITE,
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
            label_text="  BILL ITEMS"
        )
        self.cart_frame.grid(
            row=2, column=0,
            sticky="nsew", pady=(0, 10)
        )

        # BOTTOM TOTAL AND GENERATE BUTTON
        bottom = ctk.CTkFrame(
            self,
            fg_color=WHITE,
            corner_radius=15,
            border_width=1,
            border_color=BORDER
        )
        bottom.grid(
            row=3, column=0,
            sticky="ew", pady=(0, 5)
        )

        bottom.grid_columnconfigure(0, weight=1)

        total_box = ctk.CTkFrame(
            bottom,
            fg_color="transparent"
        )
        total_box.pack(
            side="left", padx=18, pady=12
        )

        ctk.CTkLabel(
            total_box,
            text="GRAND TOTAL",
            font=("Segoe UI", 10, "bold"),
            text_color=MUTED
        ).pack(anchor="w")

        self.total_label = ctk.CTkLabel(
            total_box,
            text="Rs. 0.00",
            font=("Segoe UI", 23, "bold"),
            text_color=GREEN
        )
        self.total_label.pack(anchor="w")

        ctk.CTkButton(
            bottom,
            text="Generate Invoice",
            width=180,
            height=43,
            corner_radius=11,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            font=("Segoe UI", 13, "bold"),
            command=self.generate_bill
        ).pack(
            side="right", padx=18, pady=12
        )

        self.refresh_medicines()
        self.refresh_cart()

    # LOAD MEDICINES

    def refresh_medicines(self):

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    id, name, batch_number,
                    selling_price, quantity
                FROM medicines
                WHERE quantity > 0
                  AND is_active = 1
                ORDER BY name
            """)

            self.medicines = cursor.fetchall()
            self.medicine_options = {}

            for medicine in self.medicines:

                med_id, name, batch, price, quantity = medicine

                label = "{} | {} | Stock: {}".format(
                    name, batch, quantity
                )

                self.medicine_options[label] = medicine

            options = list(self.medicine_options.keys())

            if options:
                self.medicine_menu.configure(values=options)
                self.medicine_menu.set(options[0])
            else:
                self.medicine_menu.configure(
                    values=["No medicines available"]
                )
                self.medicine_menu.set("No medicines available")

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

    # ADD MEDICINE TO CART

    def add_to_cart(self):

        try:
            selected = self.medicine_menu.get()

            if selected not in self.medicine_options:
                raise ValueError(
                    "Please select an available medicine."
                )

            medicine = self.medicine_options[selected]

            medicine_id, name, batch, price, stock = medicine

            quantity_text = self.quantity_entry.get().strip()

            if not quantity_text:
                raise ValueError("Please enter a quantity.")

            quantity = int(quantity_text)

            if quantity <= 0:
                raise ValueError(
                    "Quantity must be greater than zero."
                )

            already_added = sum(
                item["quantity"]
                for item in self.cart
                if item["id"] == medicine_id
            )

            if already_added + quantity > stock:
                raise ValueError(
                    "Not enough stock available. Available: {}".format(
                        stock - already_added
                    )
                )

            self.cart.append({
                "id": medicine_id,
                "name": name,
                "batch": batch,
                "price": float(price),
                "quantity": quantity
            })

            self.quantity_entry.delete(0, "end")

            self.message.configure(
                text="Medicine added successfully!",
                text_color=GREEN
            )

            self.refresh_cart()

        except (ValueError, TypeError) as error:

            self.message.configure(
                text=str(error),
                text_color=RED
            )

    # REMOVE CART ITEM

    def remove_item(self, index):

        if 0 <= index < len(self.cart):
            self.cart.pop(index)

        self.refresh_cart()

    # DISPLAY CART

    def refresh_cart(self):

        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        if not self.cart:

            ctk.CTkLabel(
                self.cart_frame,
                text="Your bill is empty",
                font=("Segoe UI", 15, "bold"),
                text_color=MUTED
            ).pack(pady=(35, 5))

            ctk.CTkLabel(
                self.cart_frame,
                text="Select a medicine and add it to the bill.",
                font=("Segoe UI", 11),
                text_color=MUTED
            ).pack(pady=(0, 30))

            self.total_label.configure(text="Rs. 0.00")
            return

        total = 0

        for index, item in enumerate(self.cart):

            subtotal = item["price"] * item["quantity"]
            total += subtotal

            row = ctk.CTkFrame(
                self.cart_frame,
                fg_color="#F7FAF8",
                corner_radius=11,
                border_width=1,
                border_color=BORDER
            )
            row.pack(
                fill="x", padx=7, pady=5
            )

            details = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            details.pack(
                side="left",
                fill="both",
                expand=True,
                padx=12, pady=9
            )

            ctk.CTkLabel(
                details,
                text=item["name"],
                font=("Segoe UI", 13, "bold"),
                text_color=TEXT
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text="Batch: {}  |  {} x Rs. {:.2f}".format(
                    item["batch"],
                    item["quantity"],
                    item["price"]
                ),
                font=("Segoe UI", 10),
                text_color=MUTED
            ).pack(anchor="w", pady=(3, 0))

            ctk.CTkLabel(
                row,
                text="Rs. {:.2f}".format(subtotal),
                font=("Segoe UI", 13, "bold"),
                text_color=GREEN
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                row,
                text="Remove",
                width=65,
                height=30,
                corner_radius=8,
                fg_color="#FCECEC",
                hover_color="#F5D5D5",
                text_color=RED,
                font=("Segoe UI", 10, "bold"),
                command=lambda i=index: self.remove_item(i)
            ).pack(side="right", padx=10)

        self.total_label.configure(
            text="Rs. {:.2f}".format(total)
        )

    # GENERATE AND SAVE BILL

    def generate_bill(self):

        if not self.cart:
            self.message.configure(
                text="Please add medicines first.",
                text_color=RED
            )
            return

        customer = self.customer_entry.get().strip()

        if not customer:
            customer = "Walk-in Customer"

        bill_items = [item.copy() for item in self.cart]

        total = sum(
            item["price"] * item["quantity"]
            for item in bill_items
        )

        connection = None
        cursor = None

        try:
            connection = get_connection()
            connection.start_transaction()
            cursor = connection.cursor()

            # DEDUCT STOCK SAFELY

            for item in bill_items:

                cursor.execute("""
                    UPDATE medicines
                    SET quantity = quantity - %s
                    WHERE id = %s
                      AND quantity >= %s
                      AND is_active = 1
                """, (
                    item["quantity"],
                    item["id"],
                    item["quantity"]
                ))

                if cursor.rowcount != 1:
                    raise ValueError(
                        "Insufficient stock for " + item["name"]
                    )

            bill_date = datetime.now()

            # SAVE BILL

            cursor.execute("""
                INSERT INTO bills (
                    customer_name,
                    total,
                    bill_date
                )
                VALUES (%s, %s, %s)
            """, (
                customer,
                total,
                bill_date.strftime("%Y-%m-%d %H:%M:%S")
            ))

            bill_id = cursor.lastrowid

            # SAVE BILL ITEMS

            for item in bill_items:

                subtotal = item["price"] * item["quantity"]

                cursor.execute("""
                    INSERT INTO bill_items (
                        bill_id,
                        medicine_id,
                        medicine_name,
                        batch_number,
                        quantity,
                        unit_price,
                        subtotal
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    bill_id,
                    item["id"],
                    item["name"],
                    item["batch"],
                    item["quantity"],
                    item["price"],
                    subtotal
                ))

            # COMMIT TRANSACTION

            connection.commit()

            self.cart.clear()
            self.customer_entry.delete(0, "end")

            self.refresh_cart()
            self.refresh_medicines()

            self.message.configure(
                text="Bill saved successfully!",
                text_color=GREEN
            )

            # GENERATE PDF

            try:
                pdf_path = create_invoice_pdf(
                    bill_id,
                    customer,
                    bill_items,
                    total,
                    bill_date
                )

                save_copy = messagebox.askyesno(
                    "Invoice Generated",
                    "Bill saved successfully!\n\n"
                    "Would you like to save a PDF copy elsewhere?"
                )

                if save_copy:

                    destination = filedialog.asksaveasfilename(
                        title="Save Customer Invoice",
                        defaultextension=".pdf",
                        initialfile=os.path.basename(pdf_path),
                        filetypes=[("PDF Files", "*.pdf")]
                    )

                    if destination:
                        shutil.copy2(pdf_path, destination)

                        messagebox.showinfo(
                            "PDF Saved",
                            "Invoice saved successfully:\n" + destination
                        )

                else:
                    messagebox.showinfo(
                        "Invoice Ready",
                        "Invoice saved here:\n" + pdf_path
                    )

            except Exception as pdf_error:

                messagebox.showerror(
                    "PDF Generation Error",
                    "The bill is saved in MySQL, but PDF generation "
                    "failed:\n\n" + str(pdf_error)
                )

        except (ValueError, mysql.connector.Error) as error:

            if connection and connection.is_connected():
                connection.rollback()

            self.message.configure(
                text=str(error),
                text_color=RED
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()


# ==========================================
# BILL HISTORY
# ==========================================

class BillHistoryPage(ctk.CTkFrame):

    def __init__(self, parent, db_path=None):

        super().__init__(parent, fg_color=BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # HEADER

        header = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        header.grid(
            row=0, column=0,
            sticky="ew", pady=(5, 15)
        )

        ctk.CTkLabel(
            header,
            text="Bill History",
            font=("Segoe UI", 27, "bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="View previous bills and download customer invoices",
            font=("Segoe UI", 12),
            text_color=MUTED
        ).pack(anchor="w", pady=(3, 0))

        # SEARCH

        search_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        search_frame.grid(
            row=1, column=0,
            sticky="ew", pady=(0, 10)
        )
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=40,
            corner_radius=11,
            fg_color=WHITE,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text="Search by customer name or bill number...",
            font=("Segoe UI", 11)
        )
        self.search_entry.grid(
            row=0, column=0,
            sticky="ew", padx=(0, 8)
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh()
        )

        ctk.CTkButton(
            search_frame,
            text="Refresh",
            width=95,
            height=40,
            corner_radius=10,
            fg_color=GREEN,
            hover_color=DARK_GREEN,
            command=self.refresh
        ).grid(row=0, column=1)

        # HISTORY LIST

        self.history_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=WHITE,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )
        self.history_frame.grid(
            row=2, column=0,
            sticky="nsew"
        )

        self.refresh()

    # LOAD HISTORY

    def refresh(self):

        for widget in self.history_frame.winfo_children():
            widget.destroy()

        search_text = self.search_entry.get().strip()

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id, customer_name, total, bill_date
                FROM bills
                WHERE customer_name LIKE %s
                   OR CAST(id AS CHAR) LIKE %s
                ORDER BY id DESC
            """, (
                "%" + search_text + "%",
                "%" + search_text + "%"
            ))

            bills = cursor.fetchall()

        except mysql.connector.Error as error:

            ctk.CTkLabel(
                self.history_frame,
                text="Database error: " + str(error),
                text_color=RED
            ).pack(pady=20)

            return

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

        if not bills:

            ctk.CTkLabel(
                self.history_frame,
                text="No bills found",
                font=("Segoe UI", 15, "bold"),
                text_color=MUTED
            ).pack(pady=(35, 5))

            ctk.CTkLabel(
                self.history_frame,
                text="Your saved invoices will appear here.",
                font=("Segoe UI", 11),
                text_color=MUTED
            ).pack(pady=(0, 30))

            return

        for bill in bills:

            bill_id, customer, total, date = bill

            row = ctk.CTkFrame(
                self.history_frame,
                fg_color="#F7FAF8",
                corner_radius=12,
                border_width=1,
                border_color=BORDER
            )
            row.pack(
                fill="x", padx=9, pady=6
            )

            details = ctk.CTkFrame(
                row, fg_color="transparent"
            )
            details.pack(
                side="left",
                fill="both",
                expand=True,
                padx=13, pady=11
            )

            ctk.CTkLabel(
                details,
                text="Bill #{}".format(bill_id),
                font=("Segoe UI", 13, "bold"),
                text_color=GREEN
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text=str(customer or "Walk-in Customer"),
                font=("Segoe UI", 12, "bold"),
                text_color=TEXT
            ).pack(anchor="w", pady=(3, 0))

            ctk.CTkLabel(
                details,
                text="{}  |  Rs. {:.2f}".format(
                    date, float(total or 0)
                ),
                font=("Segoe UI", 10),
                text_color=MUTED
            ).pack(anchor="w", pady=(3, 0))

            buttons = ctk.CTkFrame(
                row, fg_color="transparent"
            )
            buttons.pack(
                side="right", padx=10
            )

            ctk.CTkButton(
                buttons,
                text="View",
                width=65,
                height=32,
                corner_radius=8,
                fg_color=GREEN,
                hover_color=DARK_GREEN,
                command=lambda bid=bill_id: self.view_bill(bid)
            ).pack(pady=3)

            ctk.CTkButton(
                buttons,
                text="Download PDF",
                width=105,
                height=32,
                corner_radius=8,
                fg_color=LIGHT_GREEN,
                hover_color="#D1EBDD",
                text_color=DARK_GREEN,
                command=lambda bid=bill_id: self.download_bill(bid)
            ).pack(pady=3)

    # REBUILD PDF FROM SAVED DATABASE RECORD

    def get_saved_bill(self, bill_id):

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT customer_name, total, bill_date
                FROM bills
                WHERE id = %s
            """, (bill_id,))

            bill = cursor.fetchone()

            if not bill:
                raise ValueError("Bill not found in database.")

            customer, total, bill_date = bill

            cursor.execute("""
                SELECT
                    medicine_id,
                    medicine_name,
                    batch_number,
                    quantity,
                    unit_price
                FROM bill_items
                WHERE bill_id = %s
                ORDER BY id
            """, (bill_id,))

            saved_items = cursor.fetchall()

            if not saved_items:
                raise ValueError(
                    "No medicine details were found for this bill."
                )

            items = []

            for item in saved_items:

                medicine_id, name, batch, quantity, price = item

                items.append({
                    "id": medicine_id,
                    "name": name,
                    "batch": batch,
                    "quantity": quantity,
                    "price": float(price)
                })

            pdf_path = create_invoice_pdf(
                bill_id,
                customer or "Walk-in Customer",
                items,
                float(total),
                bill_date
            )

            return pdf_path

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # VIEW INVOICE

    def view_bill(self, bill_id):

        try:
            pdf_path = self.get_saved_bill(bill_id)

            if not os.path.exists(pdf_path):
                raise FileNotFoundError(
                    "Invoice PDF could not be found."
                )

            os.startfile(pdf_path)

        except Exception as error:

            messagebox.showerror(
                "Unable to Open Invoice",
                str(error)
            )

    # DOWNLOAD INVOICE

    def download_bill(self, bill_id):

        try:
            pdf_path = self.get_saved_bill(bill_id)

            if not os.path.exists(pdf_path):
                raise FileNotFoundError(
                    "Invoice PDF could not be found."
                )

            destination = filedialog.asksaveasfilename(
                title="Download Customer Invoice",
                defaultextension=".pdf",
                initialfile=os.path.basename(pdf_path),
                filetypes=[("PDF Files", "*.pdf")]
            )

            if destination:

                shutil.copy2(pdf_path, destination)

                messagebox.showinfo(
                    "Download Complete",
                    "Invoice downloaded successfully:\n" + destination
                )

        except Exception as error:

            messagebox.showerror(
                "Download Error",
                str(error)
            )
