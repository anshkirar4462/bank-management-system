import streamlit as st
import json
import secrets
import string
import hashlib
import re
from pathlib import Path


# =========================================================
# CONFIGURATION
# =========================================================

DATABASE = "data.json"


# =========================================================
# BANK CLASS
# =========================================================

class Bank:

    def __init__(self):
        self.database = DATABASE
        self.data = self.load_data()

    # -----------------------------------------------------
    # Load data from JSON
    # -----------------------------------------------------

    def load_data(self):
        try:
            if Path(self.database).exists():

                with open(self.database, "r") as file:
                    content = file.read().strip()

                    if content:
                        return json.loads(content)

                    return []

            else:
                with open(self.database, "w") as file:
                    json.dump([], file)

                return []

        except Exception as error:
            st.error(f"Error loading database: {error}")
            return []

    # -----------------------------------------------------
    # Update JSON database
    # -----------------------------------------------------

    def update_database(self):

        try:
            with open(self.database, "w") as file:
                json.dump(self.data, file, indent=4)

        except Exception as error:
            st.error(f"Database update failed: {error}")

    # -----------------------------------------------------
    # Hash PIN
    # -----------------------------------------------------

    @staticmethod
    def hash_pin(pin):

        return hashlib.sha256(
            pin.encode()
        ).hexdigest()

    # -----------------------------------------------------
    # Verify PIN
    # -----------------------------------------------------

    @staticmethod
    def verify_pin(pin, stored_pin):

        hashed_pin = Bank.hash_pin(pin)

        # New accounts store hashed PIN
        if isinstance(stored_pin, str):

            return secrets.compare_digest(
                hashed_pin,
                stored_pin
            )

        # Compatibility with old database
        # where PIN was stored as integer
        try:
            return int(pin) == int(stored_pin)

        except:
            return False

    # -----------------------------------------------------
    # Generate unique account number
    # -----------------------------------------------------

    def generate_account_number(self):

        while True:

            letters = ''.join(
                secrets.choice(string.ascii_uppercase)
                for _ in range(3)
            )

            numbers = ''.join(
                secrets.choice(string.digits)
                for _ in range(4)
            )

            account_number = letters + numbers

            if not any(
                user["account no"] == account_number
                for user in self.data
            ):
                return account_number

    # -----------------------------------------------------
    # Find user
    # -----------------------------------------------------

    def find_user(self, account_number, pin):

        for user in self.data:

            if (
                user["account no"] == account_number
                and self.verify_pin(pin, user["pin"])
            ):
                return user

        return None

    # -----------------------------------------------------
    # Validate email
    # -----------------------------------------------------

    @staticmethod
    def valid_email(email):

        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        return re.match(pattern, email) is not None

    # =====================================================
    # CREATE ACCOUNT
    # =====================================================

    def create_account(self, name, age, email, pin):

        account_number = self.generate_account_number()

        new_user = {
            "name": name,
            "age": age,
            "email": email,
            "pin": self.hash_pin(pin),
            "account no": account_number,
            "Balance": 0
        }

        self.data.append(new_user)

        self.update_database()

        return account_number

    # =====================================================
    # DEPOSIT
    # =====================================================

    def deposit(self, account_number, pin, amount):

        user = self.find_user(
            account_number,
            pin
        )

        if user is None:
            return False, "Invalid account number or PIN."

        if amount <= 0:
            return False, "Amount must be greater than ₹0."

        if amount > 10000:
            return False, "Maximum deposit allowed is ₹10,000."

        user["Balance"] += amount

        self.update_database()

        return True, f"₹{amount:,} deposited successfully."

    # =====================================================
    # WITHDRAW
    # =====================================================

    def withdraw(self, account_number, pin, amount):

        user = self.find_user(
            account_number,
            pin
        )

        if user is None:
            return False, "Invalid account number or PIN."

        if amount <= 0:
            return False, "Amount must be greater than ₹0."

        if amount > user["Balance"]:
            return False, "Insufficient balance."

        user["Balance"] -= amount

        self.update_database()

        return True, f"₹{amount:,} withdrawn successfully."

    # =====================================================
    # GET DETAILS
    # =====================================================

    def get_details(self, account_number, pin):

        user = self.find_user(
            account_number,
            pin
        )

        if user is None:
            return None

        return user

    # =====================================================
    # UPDATE DETAILS
    # =====================================================

    def update_details(
        self,
        account_number,
        pin,
        name,
        email,
        new_pin
    ):

        user = self.find_user(
            account_number,
            pin
        )

        if user is None:
            return False, "Invalid account number or PIN."

        if name:
            user["name"] = name

        if email:

            if not self.valid_email(email):
                return False, "Invalid email address."

            user["email"] = email

        if new_pin:
            user["pin"] = self.hash_pin(new_pin)

        self.update_database()

        return True, "Account details updated successfully."

    # =====================================================
    # DELETE ACCOUNT
    # =====================================================

    def delete_account(self, account_number, pin):

        user = self.find_user(
            account_number,
            pin
        )

        if user is None:
            return False, "Invalid account number or PIN."

        if user["Balance"] > 0:
            return False, (
                "You cannot delete an account "
                "with remaining balance."
            )

        self.data.remove(user)

        self.update_database()

        return True, "Account deleted successfully."


# =========================================================
# STREAMLIT CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="centered"
)


# =========================================================
# INITIALIZE BANK
# =========================================================

bank = Bank()


# =========================================================
# HEADER
# =========================================================

st.title("🏦 Bank Management System")

st.write(
    "A simple banking application built using "
    "Python, JSON and Streamlit."
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Bank Menu")

menu = st.sidebar.radio(
    "Select an operation",
    [
        "🏠 Home",
        "➕ Create Account",
        "💰 Deposit Money",
        "💸 Withdraw Money",
        "👤 Account Details",
        "✏️ Update Details",
        "🗑️ Delete Account"
    ]
)


# =========================================================
# HOME
# =========================================================

if menu == "🏠 Home":

    st.subheader("Welcome to the Bank")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Accounts",
            len(bank.data)
        )

    with col2:

        total_balance = sum(
            user["Balance"]
            for user in bank.data
        )

        st.metric(
            "Total Balance",
            f"₹{total_balance:,}"
        )

    with col3:

        st.metric(
            "Database",
            "JSON"
        )

    st.info(
        "Select an operation from the sidebar "
        "to continue."
    )


# =========================================================
# CREATE ACCOUNT
# =========================================================

elif menu == "➕ Create Account":

    st.subheader("Create New Account")

    with st.form("create_account_form"):

        name = st.text_input(
            "Full Name"
        )

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=18
        )

        email = st.text_input(
            "Email Address"
        )

        pin = st.text_input(
            "Create 4-digit PIN",
            type="password",
            max_chars=4
        )

        submit = st.form_submit_button(
            "Create Account"
        )

        if submit:

            if not name.strip():
                st.error("Please enter your name.")

            elif age < 18:
                st.error(
                    "You must be at least 18 years old."
                )

            elif not bank.valid_email(email):
                st.error(
                    "Please enter a valid email."
                )

            elif not pin.isdigit() or len(pin) != 4:
                st.error(
                    "PIN must contain exactly 4 digits."
                )

            else:

                account_number = bank.create_account(
                    name.strip(),
                    int(age),
                    email.strip(),
                    pin
                )

                st.success(
                    "Account created successfully!"
                )

                st.info(
                    f"Your Account Number is: **{account_number}**"
                )

                st.warning(
                    "Please save your account number safely."
                )


# =========================================================
# DEPOSIT
# =========================================================

elif menu == "💰 Deposit Money":

    st.subheader("Deposit Money")

    account_number = st.text_input(
        "Account Number"
    )

    pin = st.text_input(
        "PIN",
        type="password",
        max_chars=4
    )

    amount = st.number_input(
        "Amount",
        min_value=1,
        max_value=10000,
        step=100
    )

    if st.button("Deposit Money"):

        if not account_number:
            st.error("Enter your account number.")

        elif not pin.isdigit():
            st.error("Enter a valid PIN.")

        else:

            success, message = bank.deposit(
                account_number,
                pin,
                amount
            )

            if success:
                st.success(message)

            else:
                st.error(message)


# =========================================================
# WITHDRAW
# =========================================================

elif menu == "💸 Withdraw Money":

    st.subheader("Withdraw Money")

    account_number = st.text_input(
        "Account Number"
    )

    pin = st.text_input(
        "PIN",
        type="password",
        max_chars=4
    )

    amount = st.number_input(
        "Amount",
        min_value=1,
        step=100
    )

    if st.button("Withdraw Money"):

        if not account_number:
            st.error("Enter your account number.")

        elif not pin.isdigit():
            st.error("Enter a valid PIN.")

        else:

            success, message = bank.withdraw(
                account_number,
                pin,
                amount
            )

            if success:
                st.success(message)

            else:
                st.error(message)


# =========================================================
# ACCOUNT DETAILS
# =========================================================

elif menu == "👤 Account Details":

    st.subheader("Account Details")

    account_number = st.text_input(
        "Account Number"
    )

    pin = st.text_input(
        "PIN",
        type="password",
        max_chars=4
    )

    if st.button("Show Details"):

        user = bank.get_details(
            account_number,
            pin
        )

        if user is None:

            st.error(
                "Invalid account number or PIN."
            )

        else:

            st.success("Account found!")

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Name:**",
                    user["name"]
                )

                st.write(
                    "**Age:**",
                    user["age"]
                )

                st.write(
                    "**Email:**",
                    user["email"]
                )

            with col2:

                st.write(
                    "**Account Number:**",
                    user["account no"]
                )

                st.write(
                    "**Balance:**",
                    f"₹{user['Balance']:,}"
                )


# =========================================================
# UPDATE DETAILS
# =========================================================

elif menu == "✏️ Update Details":

    st.subheader("Update Account Details")

    account_number = st.text_input(
        "Account Number"
    )

    pin = st.text_input(
        "Current PIN",
        type="password",
        max_chars=4
    )

    st.write("Leave fields empty if you don't want to change them.")

    new_name = st.text_input(
        "New Name"
    )

    new_email = st.text_input(
        "New Email"
    )

    new_pin = st.text_input(
        "New 4-digit PIN",
        type="password",
        max_chars=4
    )

    if st.button("Update Account"):

        if not account_number or not pin:

            st.error(
                "Account number and current PIN are required."
            )

        elif new_pin and (
            not new_pin.isdigit()
            or len(new_pin) != 4
        ):

            st.error(
                "New PIN must contain exactly 4 digits."
            )

        else:

            success, message = bank.update_details(
                account_number,
                pin,
                new_name.strip(),
                new_email.strip(),
                new_pin
            )

            if success:
                st.success(message)

            else:
                st.error(message)


# =========================================================
# DELETE ACCOUNT
# =========================================================

elif menu == "🗑️ Delete Account":

    st.subheader("Delete Account")

    st.warning(
        "An account can only be deleted when its balance is ₹0."
    )

    account_number = st.text_input(
        "Account Number"
    )

    pin = st.text_input(
        "PIN",
        type="password",
        max_chars=4
    )

    confirm = st.checkbox(
        "I understand that this action cannot be undone."
    )

    if st.button(
        "Delete Account",
        disabled=not confirm
    ):

        success, message = bank.delete_account(
            account_number,
            pin
        )

        if success:
            st.success(message)

        else:
            st.error(message)