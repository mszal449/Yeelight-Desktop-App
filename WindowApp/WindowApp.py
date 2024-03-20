import tkinter as tk
from tkinter import ttk
import threading

LARGEFONT = ("Arial", 35)


class WindowApp(tk.Tk):
    """main application window"""

    def __init__(self, device_controller, *args, **kwargs):
        """Initialize the main application window.

        Args:
            device_controller: The controller for managing devices.
            *args, **kwargs: Additional arguments and keyword arguments.
            """
        tk.Tk.__init__(self, *args, **kwargs)
        self.device_controller = device_controller

        # Add frame container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        # Iterate through page layouts and initialize them
        self.frames = {}
        for F in [StartPage]:
            frame = F(container, self.device_controller)

            # Initialize frame
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self, page):
        """Show the specified frame

        Args:
            page: The frame class to show."""
        frame = self.frames[page]
        frame.tkraise()


class StartPage(tk.Frame):
    """Start page of the application."""

    def __init__(self, parent, device_controller):
        """Initialize the start page.

        Args:
            parent: The parent widget (eg. main window frame).
            device_controller: The instance of the controller for managing devices.
        """
        tk.Frame.__init__(self, parent)
        self.find_devices_button = None
        self.power_toggle_button = None
        self.set_color_button = None
        self.device_controller = device_controller
        self.page_label = None
        self.buttons_frame = None
        self.rgb_fields = None
        self.devices_tree = None
        self.devices = None
        self.selected_device = None

        # Page label
        self.page_label = ttk.Label(self, text="Devices", font=LARGEFONT)
        self.page_label.grid(row=0, column=0, padx=10, pady=10)

        # Devices table
        self.create_devices_table()

        # Color picker
        self.color_picker_frame = ttk.Frame(self)
        self.color_picker_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.create_color_picker()

        # Buttons
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.grid(row=1, column=1, padx=10, pady=10)
        self.create_buttons()

        # Initial search for devices
        self.find_and_display_devices_thread()

    def create_buttons(self):
        """Create buttons."""
        # Toggle light button
        self.power_toggle_button = ttk.Button(
            self.buttons_frame, text="Toggle power",
            command=lambda: self.selected_device.toggle() if self.selected_device else None)

        # Find devies button
        self.find_devices_button = ttk.Button(
            self.buttons_frame, text="Find Devices",
            command=self.find_and_display_devices_thread)

        # Set color button
        self.set_color_button = ttk.Button(
            self.buttons_frame, text="Set Color",
            command=self.set_color
        )

        # Button placement
        self.power_toggle_button.grid(row=0, column=0, padx=10, pady=10)
        self.find_devices_button.grid(row=1, column=0, padx=10, pady=10)
        self.set_color_button.grid(row=2, column=0, padx=10, pady=10)

    def set_color(self):
        """Set color functionality."""
        r_value = self.rgb_fields['r'].get()
        g_value = self.rgb_fields['g'].get()
        b_value = self.rgb_fields['b'].get()

        if r_value and g_value and b_value:
            if all(value is not None and value.isdigit() for value in (r_value, g_value, b_value)):
                # Convert values to integers
                r_value = int(r_value)
                g_value = int(g_value)
                b_value = int(b_value)

                # Check if the values are within the range of 0 to 255
                if all(0 <= value <= 255 for value in (r_value, g_value, b_value)):
                    # All values are numbers within the range
                    # Proceed with setting the color
                    print("Setting color:", (r_value, g_value, b_value))
                    self.selected_device.set_rgb(r_value, g_value, b_value)
                else:
                    # At least one value is not in the range
                    print("One or more RGB values are not in the range of 0 to 255.")
        else:
            print("Missing one or more RGB values.")

    def create_color_picker(self):
        """Create color picker text fields."""
        # RGB input fields
        self.rgb_fields = {
            'r': ttk.Entry(self.color_picker_frame),
            'g': ttk.Entry(self.color_picker_frame),
            'b': ttk.Entry(self.color_picker_frame)
        }

        self.rgb_fields['r'].grid(row=1, column=1, padx=10, pady=0)
        self.rgb_fields['g'].grid(row=1, column=2, padx=10, pady=0)
        self.rgb_fields['b'].grid(row=1, column=3, padx=10, pady=0)

        # Labels
        ttk.Label(self.color_picker_frame, text="R:").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.color_picker_frame, text="G:").grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(self.color_picker_frame, text="B:").grid(row=0, column=3, padx=5, pady=5)

    def create_devices_table(self):
        """Create devices table."""

        devices_tree = ttk.Treeview(self, columns=("IP Address", "Port"), selectmode="browse")
        devices_tree.heading("IP Address", text="IP Address")
        devices_tree.heading("Port", text="Port")
        devices_tree.column("#0", width=0, stretch=tk.NO)
        devices_tree.column("IP Address", width=150)
        devices_tree.column("Port", width=100)
        devices_tree.grid(row=1, column=0, padx=10, pady=10)
        devices_tree.bind("<ButtonRelease-1>", self.on_select)
        self.devices_tree = devices_tree

    def on_select(self, event):
        """Handle selection in the devices table."""

        if self.devices_tree.selection():
            item = self.devices_tree.selection()[0]

            # Retrievie data from selected element
            ip_address = self.devices_tree.item(item, 'values')[0]
            print("Selected IP Address:", ip_address)
            self.selected_device = self.device_controller.devices[ip_address]['instance']

    def find_and_display_devices_thread(self):
        """Start a thread to find and display devices."""
        threading.Thread(target=self.find_and_display_devices).start()

    def find_and_display_devices(self):
        """Find and display devices."""
        self.selected_device = None

        # Clear previous devices
        for item in self.devices_tree.get_children():
            self.devices_tree.delete(item)

        # Search for new devices
        self.device_controller.find_devices()
        for device in self.device_controller.devices.values():
            self.devices_tree.insert("", "end", values=(device["ip"], device["port"]))
