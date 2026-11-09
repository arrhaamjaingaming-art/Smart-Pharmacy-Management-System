
import os
import mysql.connector
from mysql.connector import Error

DB_HOST = "localhost"
DB_USER = "root"
DB_NAME = "smart_pharmacy"

# Load the password from a private local file.
try:
    from local_config import DB_PASSWORD
except ImportError:
    DB_PASSWORD = os.environ.get("SMART_PHARMACY_DB_PASSWORD", "")


def get_connection():
    if not DB_PASSWORD:
        raise RuntimeError(
            "MySQL password is missing. "
            "Create local_config.py with your DB_PASSWORD."
        )

    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def initialize_database():
    connection = None
    cursor = None

    try:
        if not DB_PASSWORD:
            raise RuntimeError(
                "MySQL password is missing. "
                "Create local_config.py with your DB_PASSWORD."
            )

        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + DB_NAME)
        cursor.execute("USE " + DB_NAME)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                category VARCHAR(100),
                batch VARCHAR(100) UNIQUE,
                purchase_price DECIMAL(10,2),
                selling_price DECIMAL(10,2),
                quantity INT DEFAULT 0,
                expiry_date VARCHAR(30)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(150),
                total DECIMAL(12,2),
                bill_date DATETIME
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bill_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bill_id INT NOT NULL,
                medicine_id INT,
                medicine_name VARCHAR(150) NOT NULL,
                batch_number VARCHAR(80),
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(12,2) NOT NULL,
                INDEX idx_bill_id (bill_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_profile (
                id INT PRIMARY KEY,
                business_name VARCHAR(200) NOT NULL,
                owner_name VARCHAR(150) NOT NULL,
                address TEXT NOT NULL,
                phone VARCHAR(30) NOT NULL,
                email VARCHAR(150),
                gstin VARCHAR(30),
                drug_license_1 VARCHAR(100),
                drug_license_2 VARCHAR(100),
                invoice_prefix VARCHAR(20) DEFAULT 'PP',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = 'business_profile'
              AND COLUMN_NAME = 'setup_locked'
        """, (DB_NAME,))

        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE business_profile
                ADD COLUMN setup_locked TINYINT(1) DEFAULT 0
            """)

        connection.commit()

        print("--------------------------------")
        print("MYSQL DATABASE READY!")
        print("Database:", DB_NAME)
        print("Business profile system ready!")
        print("--------------------------------")

    except Error as error:
        print("Database Initialization Error:", error)
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_business_profile():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM business_profile
            WHERE id = 1
        """)

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def save_business_profile(
    business_name,
    owner_name,
    address,
    phone,
    email="",
    gstin="",
    drug_license_1="",
    drug_license_2="",
    invoice_prefix="PP"
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT setup_locked
            FROM business_profile
            WHERE id = 1
        """)

        existing = cursor.fetchone()

        if existing and existing[0] == 1:
            raise ValueError(
                "Business registration is already locked."
            )

        if existing:
            cursor.execute("""
                UPDATE business_profile
                SET business_name = %s,
                    owner_name = %s,
                    address = %s,
                    phone = %s,
                    email = %s,
                    gstin = %s,
                    drug_license_1 = %s,
                    drug_license_2 = %s,
                    invoice_prefix = %s,
                    setup_locked = 1
                WHERE id = 1
            """, (
                business_name.strip(),
                owner_name.strip(),
                address.strip(),
                phone.strip(),
                email.strip(),
                gstin.strip(),
                drug_license_1.strip(),
                drug_license_2.strip(),
                invoice_prefix.strip()
            ))

        else:
            cursor.execute("""
                INSERT INTO business_profile (
                    id, business_name, owner_name, address,
                    phone, email, gstin, drug_license_1,
                    drug_license_2, invoice_prefix, setup_locked
                )
                VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """, (
                business_name.strip(),
                owner_name.strip(),
                address.strip(),
                phone.strip(),
                email.strip(),
                gstin.strip(),
                drug_license_1.strip(),
                drug_license_2.strip(),
                invoice_prefix.strip()
            ))

        connection.commit()
        return True

    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
