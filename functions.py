from datetime import datetime
import sqlite3
import tkinter as tk

def create_sqlite_database(database_name):
  try:
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(
      "CREATE TABLE IF NOT EXISTS EXPENSES ("
      "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
      "NAME TEXT NOT NULL,"
      "UNITY_PRICE FLOAT NOT NULL,"
      "QUANTITY INTEGER NOT NULL,"
      "TOTAL_PRICE FLOAT NOT NULL,"
      "DATE TEXT NOT NULL"
      ")"
    )
    conn.commit()
    return conn
  except sqlite3.Error as e:
    print(e)
    return None

def parse_date(date_str: str):
  for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
    try:
      # Parses the date string using the specified formats
      return datetime.strptime(date_str, fmt).date()
    except ValueError:
      # Continues to the next format if the current format is not matched
      continue
  raise ValueError("Formato de data inválido. Use dd/mm/yyyy ou dd-mm-yyyy.")

def insert_expense(
  conn, expense: str, unity_price: float,
  quantity: int, total_value: float, date
):
  # Creates a cursor object to interact with the database.
  cursor = conn.cursor()

  # Inserts a new expense record
  cursor.execute(
    "INSERT INTO EXPENSES ("
    "NAME,"
    "UNITY_PRICE,"
    "QUANTITY,"
    "TOTAL_PRICE,"
    "DATE"
    ") VALUES (?, ?, ?, ?, ?)",
    (expense, unity_price, quantity, total_value, date)
  )
  conn.commit()

def remove_trailing_spaces(
  expense_entry, value_entry, quantity_entry, date_entry
):
  # Removes spaces in the beginning and/or end of each entry if there is any.
  expense = expense_entry.get().strip()
  value_str = value_entry.get().strip()
  quantity_str = quantity_entry.get().strip()
  date_str = date_entry.get().strip()

  return expense, value_str, quantity_str, date_str

def clear_input_fields(expense_entry, value_entry, quantity_entry, date_entry):
  expense_entry.delete(0, tk.END)
  value_entry.delete(0, tk.END)
  quantity_entry.delete(0, tk.END)
  date_entry.delete(0, tk.END)

def update_combobox(expense_combobox, conn):
  # Creates a cursor object to interact with the database.
  cursor = conn.cursor()

  # Retrieves distinct expense names from the database.
  cursor.execute("SELECT DISTINCT NAME FROM EXPENSES")
  expenses = cursor.fetchall()

  # Sorts the expenses in alphabetical order.
  unique_expenses = sorted(name for name, in expenses)

  # Displays the expenses in the combobox.
  expense_combobox['values'] = unique_expenses

def on_combobox_select(event, expense_entry, combobox):
  # Retrieves the selected item from the combobox.
  selected_expense = combobox.get()

  # Clears the entry, if there is any.
  expense_entry.delete(0, tk.END)

  # Inserts what was selected in the combobox.
  expense_entry.insert(0, selected_expense)

  # Clears the value on the combobox.
  combobox.set('')

def show_expenses_on_screen(conn, console_output) -> None:
  # Creates a cursor object to interact with the database.
  cursor = conn.cursor()

  # Retrieves all expenses from the database.
  cursor.execute("SELECT NAME, TOTAL_PRICE, DATE FROM EXPENSES")
  expenses = cursor.fetchall()

  # Groups expenses by name and sorts them by date.
  grouped_expenses = {}
  for name, total_price, date in expenses:
    if name not in grouped_expenses:
      grouped_expenses[name] = []
    grouped_expenses[name].append({'value': total_price, 'date': date})

  # Configures the console output widget and clears it.
  console_output.config(state="normal")
  console_output.delete("1.0", tk.END)
  console_output.insert(tk.END, "Despesas registradas:\n")

  for name, items in grouped_expenses.items():
    # Sorts items by date in descending order.
    items.sort(
      key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
      reverse=True
    )

    # Inserts the expense name into the console output.
    console_output.insert(tk.END, f"{name}:\n")

    for item in items:
      value_str = f"{item['value']:.2f}"

      # Adds spaces to ensure the value string has exactly 8 characters.
      if len(value_str) < 7:
        padded_value_str = '  ' * (7 - len(value_str)) + value_str
      else:
        padded_value_str = value_str

      # Inserts the formatted expense value and date into the console output.
      console_output.insert(
        tk.END,
        f"    - Valor: {padded_value_str}, gasto em: "
        f"{datetime.strptime(item['date'], '%Y-%m-%d').strftime('%d/%m/%Y')}\n"
      )

  console_output.config(state="disabled") # Disables the console output widget.

def validate_expense(expense: str) -> str:
  if not expense:
    return "Preencha todos os campos."
  return None

def validate_cost(value_str: str) -> tuple[float, str]:
  try:
    return float(value_str), None
  except ValueError:
    return None, "O campo 'Valor unitário'\ndeve ser um número válido."

def validate_quantity(quantity_str: str) -> tuple[int, str]:
  try:
    return int(quantity_str), None
  except ValueError:
    return None, "O campo 'Quantidade'\ndeve ser um número inteiro."

def validate_date(date_str: str) -> tuple[datetime.date, str]:
  try:
    return parse_date(date_str), None
  except ValueError:
    return None, "Data inválida."

def validate_form(
  expense_entry, value_entry, quantity_entry, date_entry, message,
  conn, expense_combobox, console_output
):
  # Retrieves and strips trailing spaces from the input fields.
  expense, value_str, quantity_str, date_str = remove_trailing_spaces(
    expense_entry, value_entry, quantity_entry, date_entry
  )

  error_message = validate_expense(expense)
  if error_message:
    message.config(text=error_message, fg="red")
    return

  value_unity, error_message = validate_cost(value_str)
  if error_message:
    message.config(text=error_message, fg="red")
    return

  quantity, error_message = validate_quantity(quantity_str)
  if error_message:
    message.config(text=error_message, fg="red")
    return

  date, error_message = validate_date(date_str)
  if error_message:
    message.config(text=error_message, fg="red")
    return

  total_value = value_unity * quantity

  # Inserts the expense record into the database.
  insert_expense(conn, expense, value_unity, quantity, total_value, date)

  # Updates the message label and clears input fields.
  message.config(text="Despesa registrada com sucesso.", fg="green")
  clear_input_fields(expense_entry, value_entry, quantity_entry, date_entry)

  # Updates the console output and combobox.
  show_expenses_on_screen(conn, console_output)
  update_combobox(expense_combobox, conn)

def show_date_info(console_output):
  # Ensures the console output widget is visible.
  console_output.pack(fill=tk.BOTH, expand=True)

  # Configures the console output widget and clears it.
  console_output.config(state="normal")
  console_output.delete("1.0", tk.END)

  # Inserts the date format information into the console output.
  console_output.insert(
    tk.END,
    "Formatos válidos de data:\n\n"
    "dd/mm/aaaa\n"
    "dd-mm-aaaa\n"
  )

  console_output.config(state="disabled") # Disables the console output widget.

def show_total_spent(conn, console_output):
  # Creates a cursor object to interact with the database.
  cursor = conn.cursor()

  # Retrieves the total spent from the database.
  cursor.execute("SELECT SUM(TOTAL_PRICE) FROM EXPENSES")
  total_spent = cursor.fetchone()[0]
  console_output.insert(tk.END, f"Total gasto: {total_spent}\n")

  # Clear previous content and insert new total spent
  console_output.config(state="normal")
  console_output.delete("1.0", tk.END)  # Clear previous content
  console_output.insert(tk.END, f"Total gasto: {total_spent:.2f}\n")
  console_output.config(state="disabled")  # Re-disable the widget

def show_total_spent_filtered(conn, console_output, expense):
  # Creates a cursor object to interact with the database.
  cursor = conn.cursor()

  # Retrieves the total spent for the given expense from the database.
  cursor.execute(
    "SELECT SUM(TOTAL_PRICE) FROM EXPENSES WHERE NAME = ?", (expense)
  )
  total_spent = cursor.fetchone()[0]

  # Clear previous content and insert new total spent
  console_output.config(state="normal")
  console_output.delete("1.0", tk.END)  # Clear previous content
  console_output.insert(
    tk.END, f"Total gasto com {expense}: {total_spent:.2f}\n"
  )
  console_output.config(state="disabled")  # Re-disable the widget

# Decide which function will be called when the button is pressed.
def total_or_subtotal_handler(expense_entry, console_output, conn):
  # Removes trailing spaces from the expense name if there is any.
  expense = expense_entry.get().strip()
  cursor = conn.cursor()

  # If there is anything in the input field:
  if expense:
    # Checks if the entry exists in the database
    cursor.execute(
      "SELECT 1 FROM EXPENSES WHERE NAME = ? LIMIT 1", 
      (expense)
    )
    exists = cursor.fetchone()
    
    if exists:
      show_total_spent_filtered(conn, console_output, expense)
    else:
      console_output.config(state="normal")
      console_output.delete("1.0", tk.END)
      console_output.insert(tk.END, f"Despesa '{expense}' não encontrada.\n")
      console_output.config(state="disabled")
  else:
    show_total_spent(conn, console_output)
