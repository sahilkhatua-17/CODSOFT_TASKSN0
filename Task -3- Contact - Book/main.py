import tkinter as tk
from tkinter import ttk, messagebox
from database import ContactDatabase


class ContactBook:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Book")
        self.root.geometry("1060x650")
        self.root.minsize(920, 560)
        self.db = ContactDatabase()
        self.selected_id = None
        self.contacts_data = []

        self.setup_style()
        self.build_screen()
        self.load_contacts()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Palette
        bg_main = "#f1f5f9"        # Slate 100
        card_bg = "#ffffff"        # Clean white
        text_primary = "#0f172a"   # Slate 900
        text_muted = "#64748b"     # Slate 500

        # General ttk widget backgrounds
        style.configure(".", background=bg_main, foreground=text_primary, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg_main)
        style.configure("Card.TFrame", background=card_bg)

        # Labels
        style.configure("TLabel", background=bg_main, foreground=text_primary, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=card_bg, foreground=text_primary, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=bg_main, font=("Segoe UI", 20, "bold"), foreground="#0f172a")
        style.configure("Sub.TLabel", background=bg_main, font=("Segoe UI", 10), foreground=text_muted)
        style.configure("CardTitle.TLabel", background=card_bg, font=("Segoe UI", 13, "bold"), foreground="#1e293b")
        style.configure("FieldLabel.TLabel", background=card_bg, font=("Segoe UI", 9, "bold"), foreground="#475569")
        style.configure("Status.TLabel", background=card_bg, font=("Segoe UI", 9), foreground="#2563eb")

        # LabelFrame styling (seamless matching background)
        style.configure("TLabelframe", background=card_bg, bordercolor="#cbd5e1", relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=card_bg, foreground="#1e293b",
                        font=("Segoe UI", 11, "bold"))

        # Buttons
        style.configure("TButton", font=("Segoe UI", 9), padding=(12, 7))
        
        # Primary Save Button
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background="#2563eb", foreground="white")
        style.map("Primary.TButton",
                  background=[("pressed", "#1d4ed8"), ("active", "#3b82f6")],
                  foreground=[("pressed", "white"), ("active", "white")])

        # Update Button
        style.configure("Update.TButton", font=("Segoe UI", 9, "bold"), background="#0d9488", foreground="white")
        style.map("Update.TButton",
                  background=[("pressed", "#0f766e"), ("active", "#14b8a6")],
                  foreground=[("pressed", "white"), ("active", "white")])

        # Danger / Delete Button
        style.configure("Danger.TButton", font=("Segoe UI", 9), background="#ef4444", foreground="white")
        style.map("Danger.TButton",
                  background=[("pressed", "#b91c1c"), ("active", "#f87171")],
                  foreground=[("pressed", "white"), ("active", "white")])

        # Secondary / Clear Button
        style.configure("Secondary.TButton", font=("Segoe UI", 9), background="#e2e8f0", foreground="#1e293b")
        style.map("Secondary.TButton",
                  background=[("pressed", "#cbd5e1"), ("active", "#cbd5e1")],
                  foreground=[("pressed", "#0f172a"), ("active", "#0f172a")])

        # Table (Treeview)
        style.configure("Treeview",
                        font=("Segoe UI", 10),
                        rowheight=32,
                        background="white",
                        fieldbackground="white",
                        foreground="#1e293b",
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"),
                        background="#e2e8f0",
                        foreground="#1e293b",
                        padding=(10, 8))
        style.map("Treeview.Heading", background=[("active", "#cbd5e1")])
        style.map("Treeview",
                  background=[("selected", "#2563eb")],
                  foreground=[("selected", "white")])

    def build_screen(self):
        self.root.configure(bg="#f1f5f9")
        page = ttk.Frame(self.root, padding=(24, 20))
        page.pack(fill="both", expand=True)

        # Header Section
        header = ttk.Frame(page)
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(header, text="Contact Book", style="Title.TLabel").pack(anchor="w")

        # Main Split Body
        body = ttk.Frame(page)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0, minsize=320)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # --- LEFT PANEL: Contact Form Card ---
        form_card = ttk.LabelFrame(body, text=" Contact Details ", padding=18)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        form_card.columnconfigure(0, weight=1)

        # Mode status indicator
        self.status_label = ttk.Label(form_card, text="Mode: New Contact", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.entries = {}
        fields = [
            ("Name *", "name"),
            ("Phone number *", "phone"),
            ("Email address", "email"),
            ("Address", "address")
        ]

        curr_row = 1
        for label_text, key in fields:
            ttk.Label(form_card, text=label_text, style="FieldLabel.TLabel").grid(
                row=curr_row, column=0, sticky="w", pady=(6 if curr_row > 1 else 0, 3)
            )
            entry = ttk.Entry(form_card, font=("Segoe UI", 10))
            entry.grid(row=curr_row + 1, column=0, sticky="ew", ipady=5)
            self.entries[key] = entry
            curr_row += 2

        # Primary Action Buttons
        btn_grid_top = ttk.Frame(form_card, style="Card.TFrame")
        btn_grid_top.grid(row=curr_row, column=0, sticky="ew", pady=(18, 0))
        btn_grid_top.columnconfigure((0, 1), weight=1)

        self.btn_save = ttk.Button(btn_grid_top, text="Save contact", style="Primary.TButton",
                                   command=self.save_contact)
        self.btn_save.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_clear = ttk.Button(btn_grid_top, text="Clear form", style="Secondary.TButton",
                                    command=self.clear_form)
        self.btn_clear.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Secondary / Management Buttons
        self.btn_update = ttk.Button(form_card, text="Update selected", style="Update.TButton",
                                     command=self.update_contact)
        self.btn_update.grid(row=curr_row + 1, column=0, sticky="ew", pady=(10, 0))

        self.btn_delete = ttk.Button(form_card, text="Delete selected", style="Danger.TButton",
                                     command=self.delete_contact)
        self.btn_delete.grid(row=curr_row + 2, column=0, sticky="ew", pady=(8, 0))

        # --- RIGHT PANEL: Search & Contacts Table ---
        table_panel = ttk.Frame(body)
        table_panel.grid(row=0, column=1, sticky="nsew")
        table_panel.rowconfigure(1, weight=1)
        table_panel.columnconfigure(0, weight=1)

        # Search Bar Area
        search_card = ttk.Frame(table_panel)
        search_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        search_card.columnconfigure(0, weight=0)
        search_card.columnconfigure(1, weight=1)

        # Dropdown list for search criteria
        self.search_field_var = tk.StringVar(value="All Fields")
        self.search_field_combo = ttk.Combobox(
            search_card,
            textvariable=self.search_field_var,
            values=["All Fields", "Name", "Phone Number", "Email Address", "Address"],
            state="readonly",
            width=14,
            font=("Segoe UI", 10)
        )
        self.search_field_combo.grid(row=0, column=0, padx=(0, 8), ipady=5)
        self.search_field_combo.bind("<<ComboboxSelected>>", self.on_search_criteria_change)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_card, textvariable=self.search_var, font=("Segoe UI", 10))
        self.search_entry.grid(row=0, column=1, sticky="ew", ipady=6)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.load_contacts())

        # Placeholder handler
        self.placeholder_text = "Search contacts by name, phone, email, or address..."
        self.update_placeholder_text()
        self.set_search_placeholder()
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)

        ttk.Button(search_card, text="Reset", style="Secondary.TButton",
                   command=self.reset_search).grid(row=0, column=2, padx=(8, 0))

        # Table Card Frame
        table_frame = ttk.Frame(table_panel)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Columns include ADDRESS now
        columns = ("name", "phone", "email", "address")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.table.heading("name", text="Name", anchor="w",
                           command=lambda: self.sort_by_column("name", False))
        self.table.heading("phone", text="Phone Number", anchor="w",
                           command=lambda: self.sort_by_column("phone", False))
        self.table.heading("email", text="Email", anchor="w",
                           command=lambda: self.sort_by_column("email", False))
        self.table.heading("address", text="Address", anchor="w",
                           command=lambda: self.sort_by_column("address", False))

        self.table.column("name", width=140, minwidth=100, stretch=True, anchor="w")
        self.table.column("phone", width=125, minwidth=100, stretch=False, anchor="w")
        self.table.column("email", width=175, minwidth=130, stretch=True, anchor="w")
        self.table.column("address", width=220, minwidth=140, stretch=True, anchor="w")

        self.table.grid(row=0, column=0, sticky="nsew")
        self.table.bind("<<TreeviewSelect>>", self.on_select)

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.table.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Footer Status / Count
        footer = ttk.Frame(table_panel)
        footer.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.count_label = ttk.Label(footer, text="0 contacts", style="Sub.TLabel")
        self.count_label.pack(side="left")

        tip_label = ttk.Label(footer, text="Click a contact to view/edit details", style="Sub.TLabel")
        tip_label.pack(side="right")

    # Placeholder & Search helpers
    def update_placeholder_text(self):
        field = self.search_field_var.get()
        if field == "All Fields":
            self.placeholder_text = "Search contacts by name, phone, email, or address..."
        else:
            self.placeholder_text = f"Search contacts by {field.lower()}..."

    def on_search_criteria_change(self, _event=None):
        current_val = self.search_entry.get().strip()
        is_placeholder = (not current_val or current_val == getattr(self, "placeholder_text", ""))
        self.update_placeholder_text()
        if is_placeholder:
            self.search_entry.delete(0, tk.END)
            self.set_search_placeholder()
        self.load_contacts()

    def set_search_placeholder(self):
        if not self.search_var.get():
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(foreground="#94a3b8")

    def on_search_focus_in(self, _event):
        if self.search_entry.get() == self.placeholder_text:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground="#0f172a")

    def on_search_focus_out(self, _event):
        if not self.search_entry.get().strip():
            self.search_entry.delete(0, tk.END)
            self.set_search_placeholder()

    def get_search_query(self):
        val = self.search_var.get().strip()
        return "" if val == self.placeholder_text else val

    def get_form_data(self):
        return {key: entry.get().strip() for key, entry in self.entries.items()}

    def validate(self, data):
        if not data["name"]:
            messagebox.showwarning("Missing Name", "Please enter a contact name.")
            self.entries["name"].focus_set()
            return False
        if not data["phone"]:
            messagebox.showwarning("Missing Phone Number", "Please enter a phone number.")
            self.entries["phone"].focus_set()
            return False
        return True

    def save_contact(self):
        data = self.get_form_data()
        if not self.validate(data):
            return
        try:
            self.db.add_contact(data)
        except Exception as error:
            messagebox.showerror("Error", f"Could not save contact:\n{error}")
            return
        self.clear_form()
        self.load_contacts()
        messagebox.showinfo("Saved", f"Contact '{data['name']}' has been saved successfully.")

    def update_contact(self):
        if self.selected_id is None:
            messagebox.showinfo("Select Contact", "Please select a contact from the table list first.")
            return
        data = self.get_form_data()
        if not self.validate(data):
            return
        try:
            self.db.update_contact(self.selected_id, data)
        except Exception as error:
            messagebox.showerror("Error", f"Could not update contact:\n{error}")
            return
        self.clear_form()
        self.load_contacts()
        messagebox.showinfo("Updated", f"Contact details for '{data['name']}' have been updated.")

    def delete_contact(self):
        if self.selected_id is None:
            messagebox.showinfo("Select Contact", "Please select a contact from the table list first.")
            return
        contact = self.db.get_contact(self.selected_id)
        name = contact["name"] if contact else "this contact"
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{name}'?"):
            self.db.delete_contact(self.selected_id)
            self.clear_form()
            self.load_contacts()
            messagebox.showinfo("Deleted", f"Contact '{name}' has been deleted.")

    def load_contacts(self):
        query = self.get_search_query()
        search_by = self.search_field_var.get()
        for item in self.table.get_children():
            self.table.delete(item)

        self.contacts_data = self.db.search_contacts(query, search_by=search_by)
        for contact in self.contacts_data:
            self.table.insert(
                "", "end", iid=str(contact["id"]),
                values=(
                    contact["name"],
                    contact["phone"],
                    contact.get("email") or "",
                    contact.get("address") or ""
                )
            )

        count = len(self.contacts_data)
        text = f"{count} contact" + ("" if count == 1 else "s")
        if query:
            field_suffix = "" if search_by == "All Fields" else f" in {search_by}"
            text += f" found matching '{query}'{field_suffix}"
        self.count_label.config(text=text)

    def sort_by_column(self, col, reverse):
        contacts = list(self.contacts_data)
        contacts.sort(key=lambda x: (x.get(col) or "").lower(), reverse=reverse)

        for item in self.table.get_children():
            self.table.delete(item)

        for contact in contacts:
            self.table.insert(
                "", "end", iid=str(contact["id"]),
                values=(
                    contact["name"],
                    contact["phone"],
                    contact.get("email") or "",
                    contact.get("address") or ""
                )
            )

        self.table.heading(col, command=lambda: self.sort_by_column(col, not reverse))

    def on_select(self, _event):
        selection = self.table.selection()
        if not selection:
            return
        self.selected_id = int(selection[0])
        contact = self.db.get_contact(self.selected_id)
        if contact:
            for key, entry in self.entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, contact.get(key) or "")
            self.status_label.config(
                text=f"Editing: {contact['name']} (ID: {self.selected_id})",
                foreground="#0d9488"
            )

    def clear_form(self):
        self.selected_id = None
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for item in self.table.selection():
            self.table.selection_remove(item)
        self.status_label.config(text="Mode: New Contact", foreground="#2563eb")
        self.entries["name"].focus_set()

    def reset_search(self):
        self.search_field_var.set("All Fields")
        self.update_placeholder_text()
        self.search_entry.delete(0, tk.END)
        self.set_search_placeholder()
        self.load_contacts()


if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBook(root)
    root.mainloop()
