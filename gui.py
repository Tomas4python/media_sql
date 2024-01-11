# Import libraries
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import io

# Import functions and classes from other modules of the app
from scraping import WebDriverContext
from file_operations import shallow_scrape_wrapper, deep_scrape_wrapper
from db_operations import execute_query as db_execute_query
from config import Config

# Global variable for tooltip window
tooltip_window = None
current_item = None

# Global dictionary to store image references - prevent garbage collector
image_references = {}


def run_gui():
    """Launches the graphical user interface for the application."""

    def execute_query(query: str) -> list[tuple]:
        """Execute a query on the specified databases and return the combined results."""
        return db_execute_query(query, [Config.database_epika, Config.database_mediateka])

    def update_treeview():
        """Updates Treeview with query results"""
        global image_references

        # Check if the Entry widget has a query; if not, use the ComboBox selection
        query = sql_entry.get() if sql_entry.get() != entry_placeholder else sql_combo.get()

        # Check if the query is not the placeholder text
        if query not in [entry_placeholder, combo_placeholder]:
            try:
                results = execute_query(query)
                treeview.delete(*treeview.get_children())
                image_references.clear()  # Clear previous image references

                for ind, row in enumerate(results):
                    image_blob = row[2]
                    thumbnail = get_thumbnail(image_blob)
                    if thumbnail:
                        image_references[ind] = thumbnail
                        row_data = ('',) + row
                        treeview.insert('', 'end', image=thumbnail, values=row)
            except Exception as e:
                print(f"Error executing query: {e}")
        else:
            print("Please enter a valid SQL query.")

    def get_thumbnail(image_blob) -> ImageTk.PhotoImage:
        """Convert the image blob to a PhotoImage object and resize."""
        try:
            with Image.open(io.BytesIO(image_blob)) as img:
                # Resize the image
                img.thumbnail((220, 135), Image.Resampling.LANCZOS)

                with io.BytesIO() as output:
                    img.save(output, format=img.format)
                    output.seek(0)
                    thumbnail = ImageTk.PhotoImage(image=Image.open(output))
                    image_references[id(thumbnail)] = thumbnail
                    return thumbnail
        except Exception as e:
            print(f"Error in get_thumbnail: {e}")
            return None

    def show_tooltip(event):
        global tooltip_window, current_item
        item_id = treeview.identify_row(event.y)
        if item_id and item_id != current_item:
            if tooltip_window:
                tooltip_window.destroy()

            current_item = item_id
            item = treeview.item(item_id, 'values')
            description = item[3]

            tooltip_font = tkFont.Font(family="Helvetica", size=12)  # Adjust size as needed
            tooltip_window = tk.Toplevel()
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.geometry(f"+{event.x_root}+{event.y_root}")
            label = tk.Label(tooltip_window, text=description, background="white",
                             anchor='w', justify=tk.LEFT, font=tooltip_font)
            label.pack(fill='both', expand=True)

    def hide_tooltip(event):
        global tooltip_window, current_item
        if tooltip_window and current_item != treeview.identify_row(event.y):
            tooltip_window.destroy()
            tooltip_window = None
            current_item = None

    def on_combobox_click(event):
        """Clears the placeholder text in a combobox when it receives focus."""
        if event.widget.get() == combo_placeholder:
            event.widget.set('')

    def on_focusout_combobox(event):
        """Restores the placeholder text if the combobox is empty when it loses focus."""
        if not event.widget.get():
            event.widget.set(combo_placeholder)

    def on_entry_click(event, default_text):
        """Clears the placeholder text in an entry when it receives focus."""
        if event.widget.get() == default_text:
            event.widget.delete(0, tk.END)
            event.widget.config(fg='black')

    def on_focusout(event, default_text):
        """Restores the placeholder text if the entry is empty when it loses focus."""
        if not event.widget.get():
            event.widget.insert(0, default_text)
            event.widget.config(fg='grey')

    # Functions for menu commands
    def proceed_shallow_scrape_epika() -> None:
        """Perform shallow scrape of epika.lrt.lt"""
        with WebDriverContext() as driver:
            shallow_scrape_wrapper(driver, Config.database_epika, filename='shallow_scrape_result_epika.csv')

    def proceed_deep_scrape_epika() -> None:
        """Perform deep scrape of epika.lrt.lt"""
        with WebDriverContext() as driver:
            deep_scrape_wrapper(driver, Config.database_epika, shallow_filename='shallow_scrape_result_epika.csv')

    def proceed_shallow_scrape_mediateka() -> None:
        """Perform shallow scrape of lrt.lt/tema/filmai"""
        with WebDriverContext() as driver:
            shallow_scrape_wrapper(driver, Config.database_mediateka, filename='shallow_scrape_result_mediateka.csv')

    def proceed_deep_scrape_mediateka() -> None:
        """Perform deep scrape of lrt.lt/tema/filmai"""
        with WebDriverContext() as driver:
            deep_scrape_wrapper(driver, Config.database_mediateka, shallow_filename='shallow_scrape_result_mediateka'
                                                                                    '.csv')

    # Main application window
    root = tk.Tk()
    root.geometry("1900x800")

    # Menu
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Adding menu items
    scrape_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Scrape menu", menu=scrape_menu)
    scrape_menu.add_command(label="Shallow Scrape Epika", command=lambda: proceed_shallow_scrape_epika())
    scrape_menu.add_command(label="Deep Scrape Epika", command=lambda: proceed_deep_scrape_epika())
    scrape_menu.add_command(label="Shallow Scrape Mediateka", command=lambda: proceed_shallow_scrape_mediateka())
    scrape_menu.add_command(label="Deep Scrape Mediateka", command=lambda: proceed_deep_scrape_mediateka())

    # Placeholder text for Entry and Combobox
    entry_placeholder = 'Write here your SQL query'
    combo_placeholder = 'Select SQL query from predefined samples'

    # SQL Combobox with placeholder
    sql_combo = ttk.Combobox(root, width=100)
    sql_combo['values'] = [''] + Config.sample_queries
    sql_combo.set(combo_placeholder)
    sql_combo.bind('<FocusIn>', on_combobox_click)
    sql_combo.bind('<FocusOut>', on_focusout_combobox)
    sql_combo.grid(row=0, column=0, sticky='ew')

    # Bind the '<<ComboboxSelected>>' event to the update_treeview function
    sql_combo.bind('<<ComboboxSelected>>', lambda event: update_treeview())

    # SQL Entry with placeholder
    sql_entry = tk.Entry(root, fg='grey')
    sql_entry.grid(row=1, column=0, sticky='ew')
    sql_entry.insert(0, entry_placeholder)
    sql_entry.bind('<FocusIn>', lambda event, default_text=entry_placeholder: on_entry_click(event, default_text))
    sql_entry.bind('<FocusOut>', lambda event, default_text=entry_placeholder: on_focusout(event, default_text))
    sql_entry.grid(row=1, column=0, sticky='ew')
    execute_button = ttk.Button(root, text="Execute", command=update_treeview)
    execute_button.grid(row=1, column=1, sticky='ew')

    # Treeview for database results
    columns = ("id", "title", "image", "description", "release_year", "duration", "genre", "url",
               "date_of_first_finding", "date_of_disappearance", "related_persons", "views_count", "is_memorable")

    treeview = ttk.Treeview(root, columns=columns, selectmode='none', height=7)
    treeview.grid(row=2, column=0, columnspan=2, sticky='nsew')

    # Scrollbar for Treeview
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=treeview.yview)
    scrollbar.grid(row=2, column=2, sticky='ns')
    style = ttk.Style()
    style.configure('Treeview', rowheight=135)
    treeview.configure(yscrollcommand=scrollbar.set)

    # Defining column attributes
    # Total width: 1900 pixels
    # Adjust other column definitions as needed
    treeview.heading('#0', text="Screenshot", anchor='center')
    treeview.heading('#1', text="id", anchor='center')
    treeview.heading('#2', text="title", anchor='center')
    treeview.heading('#3', text="image", anchor='center')
    treeview.heading('#4', text="description", anchor='center')
    treeview.heading('#5', text="release_year", anchor='center')
    treeview.heading('#6', text="duration", anchor='center')
    treeview.heading('#7', text="genre", anchor='center')
    treeview.heading('#8', text="url", anchor='center')
    treeview.heading('#9', text="date_of_first_finding", anchor='center')
    treeview.heading('#10', text="date_of_disappearance", anchor='center')
    treeview.heading('#11', text="related_persons", anchor='center')
    treeview.heading('#12', text="views_count", anchor='center')
    treeview.heading('#13', text="is_memorable", anchor='center')
    treeview.column("id", width=20, anchor='center')
    treeview.column("title", width=200, anchor='w')
    treeview.column("image", width=50, anchor='center')
    treeview.column("description", width=600, anchor='w')
    treeview.column("release_year", width=20, anchor='center')
    treeview.column("duration", width=50, anchor='center')
    treeview.column("genre", width=100, anchor='w')
    treeview.column("url", width=50, anchor='w')
    treeview.column("date_of_first_finding", width=50, anchor='w')
    treeview.column("date_of_disappearance", width=20, anchor='w')
    treeview.column("related_persons", width=50, anchor='w')
    treeview.column("views_count", width=20, anchor='center')
    treeview.column("is_memorable", width=20, anchor='center')

    # Ensure the total width is close to or slightly less than 1900 pixels

    # Setting column headings
    for col in columns:
        treeview.heading(col, text=col.replace('_', ' ').title())

    # Bind events for showing and hiding the tooltip
    treeview.bind("<Motion>", show_tooltip)
    treeview.bind("<Leave>", hide_tooltip)

    # Configure the grid
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(2, weight=1)

    root.mainloop()
