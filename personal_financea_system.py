import pandas as pd
from datetime import datetime
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib
matplotlib.use('TkAgg')


class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Management System")
        self.geometry("1300x800")

        # Modern UI colors
        self.bg_color = "#f7f9fc"
        self.primary_color = "#3498db"
        self.secondary_color = "#2ecc71"
        self.accent_color = "#e74c3c"
        self.text_color = "#34495e"
        self.light_bg = "#ecf0f1"
        self.entry_color = "#ffffff"
        self.editing_transaction_id = None  # Track if a transaction is being edited
        self.configure(bg=self.bg_color)

        # Create SQLite database
        self.conn = sqlite3.connect('finance.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, amount REAL, date TEXT, description TEXT)''')
        self.conn.commit()

        # Main frame
        main_frame = tk.Frame(self, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)

        # Style for notebook and other widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TNotebook',
                        background=self.bg_color, tabmargins=[2, 5, 2, 0])
        style.configure('Modern.TNotebook.Tab', padding=[
                        15, 15], background=self.primary_color, foreground=self.bg_color, font=('Helvetica', 18, 'bold'))  # Larger tabs
        style.map('Modern.TNotebook.Tab', background=[
                  ('selected', self.accent_color)], foreground=[('selected', self.bg_color)])

        style.configure('TLabel', font=('Helvetica', 16), background=self.bg_color,
                        foreground=self.text_color)  # Increased font size for labels
        style.configure('TButton', font=('Helvetica', 16), background=self.primary_color,
                        foreground=self.bg_color)  # Increased font size for buttons
        # Increased font size for entries
        style.configure('TEntry', font=('Helvetica', 16),
                        fieldbackground=self.entry_color)

        # Increase font size for Treeview (Table)
        style.configure("Treeview", font=('Helvetica', 16), rowheight=30)
        style.configure("Treeview.Heading", font=(
            'Helvetica', 18, 'bold'))  # Set font for table headers

        # Transaction Tab
        transaction_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(transaction_tab, text='Transactions')

        # Center the form and table
        form_frame = tk.Frame(transaction_tab, bg=self.bg_color)
        form_frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        # Transaction Widgets (Modernized)
        self.create_label(form_frame, "Transaction Type:", 0, 0)
        self.type_var = tk.StringVar()
        self.type_dropdown = ttk.Combobox(form_frame, textvariable=self.type_var, values=[
                                          'Income', 'Expense'], font=('Helvetica', 16))
        self.type_dropdown.grid(row=0, column=1, columnspan=2,
                                padx=20, pady=20, sticky='ew')  # Increased padding

        self.create_label(form_frame, "Amount:", 1, 0)
        self.amount_entry = self.create_entry(
            form_frame, 1, 1, columnspan=2)

        self.create_label(form_frame, "Date:", 2, 0)
        self.date_entry = DateEntry(form_frame, font=(
            'Helvetica', 16), date_pattern='dd-mm-yyyy', background=self.light_bg, foreground=self.text_color)
        self.date_entry.grid(row=2, column=1, columnspan=2, padx=20, pady=20)

        self.create_label(form_frame, "Description:", 3, 0)
        self.description_entry = self.create_entry(
            form_frame, 3, 1, columnspan=2)

        # Add transaction buttons with flat style
        button_frame = tk.Frame(transaction_tab, bg=self.bg_color)
        button_frame.grid(row=4, column=0, columnspan=3,
                          padx=20, pady=20, sticky='ew')

        add_button = self.create_button(
            button_frame, "Add", self.add_transaction, 0, 0)
        edit_button = self.create_button(
            button_frame, "Edit", self.edit_transaction, 0, 1)
        delete_button = self.create_button(
            button_frame, "Delete", self.delete_transaction, 0, 2)

        # Treeview (Modernized) with increased font size
        self.tree = ttk.Treeview(transaction_tab, columns=(
            'ID', 'Type', 'Amount', 'Date', 'Description'), show='headings', height=12)
        self.tree.heading('ID', text='ID')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Amount', text='Amount')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Description', text='Description')
        self.tree.grid(row=5, column=0, columnspan=3, padx=20,
                       pady=20, sticky='nsew')  # Increased padding

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            transaction_tab, orient='vertical', command=self.tree.yview)
        scrollbar.grid(row=5, column=3, sticky='ns')
        self.tree.configure(yscroll=scrollbar.set)

        # Dashboard Tab
        dashboard_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(dashboard_tab, text='Dashboard')

        # Dashboard Widgets
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(16, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, master=dashboard_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Balance Label
        self.balance_label = tk.Label(dashboard_tab, text="Total Balance: $0.00", font=(
            'Helvetica', 24, 'bold'), bg=self.bg_color, fg=self.text_color)
        self.balance_label.pack(pady=30)

        # Now you can safely call update_treeview
        self.update_treeview()

        # Initialize the dashboard
        self.update_dashboard()

    def update_treeview(self):
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch transactions from the database
        self.cursor.execute("SELECT * FROM transactions ORDER BY id")
        transactions = self.cursor.fetchall()

        # Insert transactions into the treeview
        for transaction in transactions:
            self.tree.insert('', 'end', values=transaction)

    def create_label(self, parent, text, row, column):
        label = ttk.Label(parent, text=text)
        label.grid(row=row, column=column, padx=20,
                   pady=20, sticky='w')  # Increased padding
        return label

    def create_entry(self, parent, row, column, columnspan=1):
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=column, columnspan=columnspan,
                   padx=20, pady=20, sticky='ew')  # Increased padding
        return entry

    def create_button(self, parent, text, command, row, column, columnspan=1):
        button = ttk.Button(parent, text=text,
                            command=command, style='TButton')
        button.grid(row=row, column=column, columnspan=columnspan,
                    padx=20, pady=20, sticky='ew')  # Increased padding
        return button

    def add_transaction(self):
        transaction_type = self.type_var.get()
        amount_str = self.amount_entry.get()
        date = self.date_entry.get_date().strftime('%d-%m-%Y')
        description = self.description_entry.get()

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid amount.")
            return

        if self.editing_transaction_id:  # If editing a transaction
            try:
                # Update the existing transaction
                self.cursor.execute("UPDATE transactions SET type = ?, amount = ?, date = ?, description = ? WHERE id = ?",
                                    (transaction_type, amount, date, description, self.editing_transaction_id))
                self.conn.commit()
                messagebox.showinfo(
                    "Success", "Transaction updated successfully!")
            except Exception as e:
                messagebox.showerror(
                    "Database Error", f"Failed to update transaction: {e}")
        else:
            # Add a new transaction
            self.cursor.execute("INSERT INTO transactions (type, amount, date, description) VALUES (?, ?, ?, ?)",
                                (transaction_type, amount, date, description))
            self.conn.commit()
            messagebox.showinfo("Success", "Transaction added successfully!")

        # Clear the editing state
        self.editing_transaction_id = None

        # Clear the input fields
        self.clear_entries()

        # Update the treeview and dashboard
        self.update_treeview()
        self.update_dashboard()

    def edit_transaction(self):
        selected = self.tree.focus()  # Get the currently selected item in the treeview
        if not selected:
            messagebox.showerror(
                "Error", "Please select a transaction to edit.")
            return

        # Get the selected transaction's ID and details
        transaction_details = self.tree.item(selected)['values']
        # Store the transaction ID
        self.editing_transaction_id = transaction_details[0]

        # Populate the input fields with the selected transaction's details
        self.type_var.set(transaction_details[1])
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, transaction_details[2])
        self.date_entry.set_date(datetime.strptime(
            transaction_details[3], '%d-%m-%Y'))
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, transaction_details[4])

        messagebox.showinfo(
            "Info", "Transaction details loaded. Make changes and click 'Add' to save.")

    def delete_transaction(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror(
                "Error", "Please select a transaction to delete.")
            return

        # Get the selected transaction's ID
        transaction_id = self.tree.item(selected)['values'][0]

        if not transaction_id:
            messagebox.showerror("Error", "Unable to retrieve transaction ID.")
            return

        # Delete the transaction from the database
        self.cursor.execute(
            "DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()

        # Verify deletion
        self.cursor.execute(
            "SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        result = self.cursor.fetchone()
        if result:
            messagebox.showerror("Error", "Failed to delete the transaction.")
        else:
            messagebox.showinfo("Success", "Transaction deleted successfully!")
            self.update_treeview()
            self.update_dashboard()

    def clear_entries(self):
        self.type_var.set('')
        self.amount_entry.delete(0, tk.END)
        self.date_entry.set_date(datetime.now())
        self.description_entry.delete(0, tk.END)

    def update_dashboard(self):
        self.ax1.clear()
        self.ax2.clear()

        transactions = self.cursor.execute(
            "SELECT type, amount FROM transactions").fetchall()
        income = sum(amount for ttype,
                     amount in transactions if ttype == 'Income')
        expense = sum(amount for ttype,
                      amount in transactions if ttype == 'Expense')

        balance = income - expense
        self.balance_label.config(text=f"Total Balance: ${balance:.2f}")

        if income > 0 or expense > 0:
            labels = []
            sizes = []
            colors = []

            if income > 0:
                labels.append('Income')
                sizes.append(income)
                colors.append(self.secondary_color)

            if expense > 0:
                labels.append('Expense')
                sizes.append(expense)
                colors.append(self.accent_color)

            if sizes:
                self.ax1.pie(sizes, labels=labels, colors=colors,
                             autopct='%1.1f%%', startangle=90)
                self.ax1.set_title("Income vs Expense")
        else:
            self.ax1.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                          verticalalignment='center', transform=self.ax1.transAxes, fontsize=24, color=self.text_color)

        # Cash Flow Over Time
        transactions = self.cursor.execute(
            "SELECT type, amount, date FROM transactions ORDER BY date").fetchall()

        income_dates = [datetime.strptime(
            date, '%d-%m-%Y') for ttype, amount, date in transactions if ttype == 'Income']
        income_amounts = [amount for ttype, amount,
                          date in transactions if ttype == 'Income']

        expense_dates = [datetime.strptime(
            date, '%d-%m-%Y') for ttype, amount, date in transactions if ttype == 'Expense']
        expense_amounts = [amount for ttype, amount,
                           date in transactions if ttype == 'Expense']

        if income_dates or expense_dates:
            self.ax2.plot(income_dates, income_amounts, marker='o',
                          linestyle='-', color=self.secondary_color, label='Income')
            self.ax2.plot(expense_dates, expense_amounts, marker='o',
                          linestyle='-', color=self.accent_color, label='Expense')
            self.ax2.set_title("Cash Flow Over Time")
            self.ax2.set_ylabel("Amount ($)")
            self.ax2.set_xlabel("Date")
            self.ax2.legend()
        else:
            self.ax2.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                          verticalalignment='center', transform=self.ax2.transAxes, fontsize=24, color=self.text_color)

        self.canvas.draw()


if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
