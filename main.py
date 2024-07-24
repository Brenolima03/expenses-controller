import tkinter as tk
from tkinter.ttk import Combobox
from tkinter import PhotoImage
from functions import *
import sqlite3
import os

if __name__ == "__main__":
  # Defines the name of the database.
  db = "EXPENSES.db"
  # Checks if the database exists, otherwise creates it.
  if os.path.isfile(db):
    conn = sqlite3.connect(db)  # Connects to existing database.
  else:
    conn = create_sqlite_database(db)  # Creates and connect to new database.

  # Creates the main application window.
  window = tk.Tk()
  window.geometry("360x800")  # Set window size.
  window.title("Registro de Despesas")  # Set window title.
  window.configure(bg="#f0f0f0")  # Set background color.

  # Label for the material/service input field.
  tk.Label(
    window,
    text="Material/Serviço:",
    font=("Arial", 12, "bold"),
    bg="#f0f0f0"
  ).pack()

  # Combobox for selecting existing expenses.
  combobox = Combobox(window, font=("Arial", 12))
  combobox.pack()

  # Entry for inputting a new expense name.
  expense_entry = tk.Entry(window, font=("Arial", 12))
  expense_entry.pack()

  # Label for the cost input field.
  tk.Label(
    window,
    text="Valor unitário:",
    font=("Arial", 12, "bold"),
    bg="#f0f0f0"
  ).pack()

  # Entry for inputting the unit cost.
  value_entry = tk.Entry(window, font=("Arial", 12))
  value_entry.pack(pady=10)

  # Label for the quantity input field.
  tk.Label(
    window,
    text="Quantidade:",
    font=("Arial", 12, "bold"),
    bg="#f0f0f0"
  ).pack()

  # Entry for inputting the quantity.
  quantity_entry = tk.Entry(window, font=("Arial", 12))
  quantity_entry.pack(pady=10)

  # Frame to contain the date label and icon.
  date_frame = tk.Frame(window, bg="#f0f0f0")
  date_frame.pack()

  # Label for the date input field.
  tk.Label(
    date_frame,
    text="Data ",
    font=("Arial", 12, "bold"),
    bg="#f0f0f0"
  ).pack(side=tk.LEFT)

  icon = PhotoImage(file="info-icon.png") # Load and display the info icon.

  # Label to display the info icon and bind it to show date info.
  info_label = tk.Label(
    date_frame,
    image=icon,
    bg="#f0f0f0",
    cursor="hand2"
  )
  info_label.pack(side=tk.LEFT)
  info_label.bind("<Button-1>", lambda e: show_date_info(console_output))

  # Entry for inputting the date.
  date_entry = tk.Entry(window, font=("Arial", 12))
  date_entry.pack(pady=10)

  # Label to display messages to the user.
  message = tk.Label(
    window,
    text="",
    font=("Arial", 12),
    bg="#f0f0f0",
    fg="red"
  )
  message.pack()

  # Button to save the expense to the database.
  tk.Button(
    window,
    text="Guardar despesa",
    command=lambda: validate_form(
      expense_entry, value_entry, quantity_entry, date_entry,
      message, conn, combobox, console_output
    ),
    font=("Arial", 12),
    bg="#4CAF50",
    fg="white",
    padx=5
  ).pack(pady=5)

  # Button to show all expenses in the console.
  tk.Button(
    window,
    text="Mostrar despesas",
    command=lambda: (
      # Show and expand console.
      console_output.pack(fill=tk.BOTH, expand=True),
      show_expenses_on_screen(conn, console_output)
    ),
    font=("Arial", 12),
    bg="#2196F3",
    fg="white",
    padx=5
  ).pack(pady=5)

  # Button to show total spent.
  tk.Button(
    window,
    text="Total gasto",
    command=lambda: (
      console_output.pack(fill=tk.BOTH, expand=True),
      total_or_subtotal_handler(expense_entry, console_output, conn)
    ),
    font=("Arial", 12),
    bg="#2196F3",
    fg="white",
    padx=5
  ).pack(pady=5)

  # Button to clear the expense entry field.
  tk.Button(
    window,
    text="Limpar campos",
    command=lambda: clear_input_fields(
      expense_entry, value_entry, quantity_entry, date_entry
    ),
    font=("Arial", 12),
    bg="#FFC107",
    fg="black",
    padx=5
  ).pack(pady=5)

  # Updates combobox with expense names from the database.
  update_combobox(combobox, conn)
  combobox.bind(
    "<<ComboboxSelected>>",
    lambda event: on_combobox_select(event, expense_entry, combobox)
  )

  # Console output widget for displaying information, initially hidden.
  console_output = tk.Text(
    window,
    height=10,
    width=50,
    font=("Arial", 12),
    bg="#e8e8e8",
    padx=5
  )
  console_output.pack_forget()  # Initially hide the console.

  window.mainloop()  # Start the Tkinter event loop.
  conn.close()  # Close the database connection when the app closes.
