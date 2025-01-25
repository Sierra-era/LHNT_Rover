# experimental UI code - currently have issues staying connected to server
import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from bleak import BleakClient
from functools import partial
import win32com.client
import pywintypes
# BLE Configuration
BLE_ADDRESS = "2c:bc:bb:4c:57:3a"  # ESP32 BLE MAC address
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
DEVICE_NAME = "ESP32-Rover"  # The name your ESP32 broadcasts
class FuturisticController:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(":rocket: Quantum Drive Controller")
        self.window.configure(bg='#1C1C1E')
        # Make window full screen by default
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}")
        # Initialize BLE client
        self.client = None
        self.connected = False
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Futuristic.TFrame', background='#1C1C1E')
        # Create main container
        self.main_frame = ttk.Frame(self.window, style='Futuristic.TFrame')
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        # Add connect button
        self.connect_button = tk.Button(
            self.main_frame,
            text="Connect to ESP32",
            command=self.initiate_connection,
            font=("Consolas", 12),
            bg="#1C1C1E",
            fg="#00FF00",
            activebackground="#2C2C2E",
            activeforeground="#00FF00",
            relief=tk.RAISED,
            padx=20,
            pady=10
        )
        self.connect_button.pack(pady=10)
        # Status display
        self.status_frame = tk.Frame(self.main_frame, bg='#1C1C1E')
        self.status_frame.pack(fill='x', pady=10)
        self.connection_status = tk.Label(
            self.status_frame,
            text="● DISCONNECTED",
            font=("Consolas", 14),
            fg="#FFFF00",
            bg="#1C1C1E"
        )
        self.connection_status.pack(side='left', padx=10)
        # Command display
        self.command_frame = tk.Frame(self.main_frame, bg='#1C1C1E')
        self.command_frame.pack(expand=True, fill='both')
        self.direction_label = tk.Label(
            self.command_frame,
            text='READY',
            font=("Consolas", 40, "bold"),
            fg="#00FFFF",
            bg="#1C1C1E"
        )
        self.direction_label.pack(expand=True)
        # Control hints
        self.controls_frame = tk.Frame(self.main_frame, bg='#1C1C1E')
        self.controls_frame.pack(fill='x', pady=20)
        controls_text = """
        [↑/W] Forward   [↓/S] Reverse   [←] Rotate Left   [→] Rotate Right
        [A] Strafe Left   [D] Strafe Right   [SPACE] Emergency Stop
        """
        self.controls_label = tk.Label(
            self.controls_frame,
            text=controls_text,
            font=("Consolas", 12),
            fg="#666666",
            bg="#1C1C1E"
        )
        self.controls_label.pack()
        # Initialize command history
        self.command_history = []
        # Start the pulse animation
        self.pulse_animation()
        # Bind controls
        self.bind_controls()
    def pair_with_device(self):
        """Force Windows to pair with the ESP32"""
        try:
            # Create a Windows Bluetooth API object
            bluetooth = win32com.client.Dispatch("BluetoothAPIs.BluetoothDeviceHelper")
            # Try to find and pair with the device
            device = bluetooth.FindDevice(DEVICE_NAME)
            if not device.Authenticated:
                result = device.Authenticate()
                if result:
                    messagebox.showinfo("Success", f"Successfully paired with {DEVICE_NAME}")
                    return True
                else:
                    messagebox.showerror("Error", f"Failed to pair with {DEVICE_NAME}")
                    return False
            return True
        except pywintypes.com_error as e:
            messagebox.showerror("Error", f"Could not find or pair with {DEVICE_NAME}. Make sure the device is in pairing mode.")
            return False
    def initiate_connection(self):
        """Handle the connection button press"""
        self.update_status("PAIRING...")
        self.connect_button.configure(state='disabled')
        # Start pairing process in a separate thread
        threading.Thread(target=self.connection_sequence, daemon=True).start()
    def connection_sequence(self):
        """Run the full connection sequence"""
        if self.pair_with_device():
            # Start BLE connection
            self.ble_thread = threading.Thread(target=self.run_ble_loop, daemon=True)
            self.ble_thread.start()
        else:
            self.connect_button.configure(state='normal')
            self.update_status("PAIRING FAILED", error=True)
    async def connect_ble(self):
        """Establish BLE connection"""
        try:
            self.client = BleakClient(BLE_ADDRESS)
            await self.client.connect()
            self.connected = True
            self.window.after(0, lambda: self.connect_button.configure(state='disabled'))
            self.update_status("SYSTEM ONLINE")
        except Exception as e:
            self.window.after(0, lambda: self.connect_button.configure(state='normal'))
            self.update_status(f"Connection Error: {e}", error=True)
    def run_ble_loop(self):
        """Run the asyncio event loop for BLE operations"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_ble())
        loop.run_forever()
    async def send_ble_command(self, command):
        """Send a command via BLE"""
        if self.connected and self.client:
            try:
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, str(command).encode())
                self.command_history.append(command)
                self.update_status(f"Command sent: {command}")
            except Exception as e:
                self.update_status(f"Error: {e}", error=True)
        else:
            self.update_status("Not connected to device", error=True)
    def pulse_animation(self):
        """Creates a pulsing effect for the status indicator"""
        current_color = self.connection_status.cget("fg")
        new_color = "#008800" if current_color == "#00FF00" else "#00FF00"
        if self.connected:
            self.connection_status.configure(fg=new_color)
        self.window.after(1000, self.pulse_animation)
    def update_status(self, message, error=False):
        """Update the status display with message"""
        color = "#FF0000" if error else "#00FF00"
        self.connection_status.configure(text=f"● {message}", fg=color)
    def update_direction(self, text, color):
        """Update the direction display with visual feedback"""
        self.direction_label.configure(text=text, fg=color)
    def handle_movement(self, event):
        """Handle movement commands with visual feedback"""
        if not self.connected:
            self.update_status("Please connect to ESP32 first", error=True)
            return
        command_map = {
            'Up': (1, '↑ FORWARD', "#00FF00"),
            'w': (1, '↑ FORWARD', "#00FF00"),
            'Down': (2, '↓ BACKWARD', "#FF4500"),
            's': (2, '↓ BACKWARD', "#FF4500"),
            'Left': (3, '← LEFT SPIN', "#1E90FF"),
            'Right': (4, '→ RIGHT SPIN', "#FFD700"),
            'a': (5, '⇦ STRAFE LEFT', "#FF00FF"),
            'd': (6, '⇨ STRAFE RIGHT', "#00FFFF")
        }
        if event.keysym in command_map:
            command, text, color = command_map[event.keysym]
            self.update_direction(text, color)
            asyncio.run_coroutine_threadsafe(
                self.send_ble_command(command),
                asyncio.get_event_loop()
            )
    def handle_stop(self, event):
        """Handle emergency stop command"""
        if not self.connected:
            self.update_status("Please connect to ESP32 first", error=True)
            return
        asyncio.run_coroutine_threadsafe(
            self.send_ble_command(0),
            asyncio.get_event_loop()
        )
        self.update_direction('STOP', "#FF1493")
        # Emergency stop flash effect
        for i in range(3):
            self.window.after(i*200, lambda: self.direction_label.configure(bg="#FF1493"))
            self.window.after(i*200+100, lambda: self.direction_label.configure(bg="#1C1C1E"))
    def bind_controls(self):
        """Bind all control keys"""
        movement_keys = ['<Up>', '<Down>', '<Left>', '<Right>',
                        'w', 's', 'a', 'd']
        for key in movement_keys:
            self.window.bind(key, self.handle_movement)
        self.window.bind('<space>', self.handle_stop)
    def run(self):
        """Start the application"""
        self.window.mainloop()
if __name__ == "__main__":
    app = FuturisticController()
    app.run()
