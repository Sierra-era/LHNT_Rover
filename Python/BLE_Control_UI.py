# THIS CODE WORKS 
# might have a slower response time than Wifi
import asyncio
from bleak import BleakClient
import tkinter as tk
from tkinter import ttk
import threading
import time
# ESP32 BLE Configuration (replace with your ESP32's MAC address)
BLE_ADDRESS = "2c:bc:bb:4c:57:3a"
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
class FuturisticController:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(":rocket: Quantum Drive Controller")
        self.window.configure(bg='#1C1C1E')
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}")
        self.style = ttk.Style()
        self.style.configure('Futuristic.TFrame', background='#1C1C1E')
        # Main frame
        self.main_frame = ttk.Frame(self.window, style='Futuristic.TFrame')
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        # Status frame
        self.status_frame = tk.Frame(self.main_frame, bg='#1C1C1E')
        self.status_frame.pack(fill='x', pady=10)
        self.connection_status = tk.Label(
            self.status_frame,
            text="● SYSTEM OFFLINE",
            font=("Consolas", 14),
            fg="#FF0000",
            bg="#1C1C1E"
        )
        self.connection_status.pack(side='left', padx=10)
        # Command frame
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
        # Controls frame
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
        self.command_history = []
        self.connected = False
        self.client = None
        self.loop = asyncio.new_event_loop()  # Create an asyncio event loop
        threading.Thread(target=self.connect_ble, daemon=True).start()
        self.pulse_animation()
        self.bind_controls()
    def pulse_animation(self):
        """Create a 'pulsing' effect on the status label."""
        current_color = self.connection_status.cget("fg")
        new_color = "#008800" if current_color == "#00FF00" else "#00FF00"
        self.connection_status.configure(fg=new_color)
        self.window.after(1000, self.pulse_animation)
    def connect_ble(self):
        """Run BLE connection in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_device())
    async def connect_to_device(self):
        """Establish BLE connection to ESP32."""
        try:
            print("Connecting to BLE device...")
            async with BleakClient(BLE_ADDRESS) as client:
                self.client = client
                if self.client.is_connected:
                    self.connected = True
                    print("Connected to ESP32 BLE device!")
                    self.update_status("SYSTEM ONLINE", False)
                    while True:
                        await asyncio.sleep(1)
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.update_status("CONNECTION FAILED", True)
            self.connected = False
    async def send_command(self, command):
        """Send a command to the ESP32 via BLE."""
        if self.client and self.connected:
            try:
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, str(command).encode())
                print(f"Sent '{command}' to the ESP32")
                self.command_history.append(command)
                self.update_status(f"Command sent: {command}")
            except Exception as e:
                self.update_status(f"Send Error: {e}", True)
        else:
            self.update_status("Not connected to ESP32", True)
    def update_status(self, message, error=False):
        """Update UI status."""
        color = "#FF0000" if error else "#00FF00"
        self.connection_status.configure(text=f"● {message}", fg=color)
    def update_direction(self, text, color):
        """Update UI with movement direction."""
        self.direction_label.configure(text=text, fg=color)
    def handle_movement(self, event):
        """Handle keyboard inputs and send corresponding BLE commands."""
        command_map = {
            'Up': ('↑ FORWARD', "#00FF00", 1),
            'w': ('↑ FORWARD', "#00FF00", 1),
            'Down': ('↓ BACKWARD', "#FF4500", 2),
            's': ('↓ BACKWARD', "#FF4500", 2),
            'Left': ('← LEFT SPIN', "#1E90FF", 3),
            'Right': ('→ RIGHT SPIN', "#FFD700", 4),
            'a': ('⇦ STRAFE LEFT', "#FF00FF", 5),
            'd': ('⇨ STRAFE RIGHT', "#00FFFF", 6),
        }
        if event.keysym in command_map:
            direction_text, color, command = command_map[event.keysym]
            self.update_direction(direction_text, color)
            self.loop.create_task(self.send_command(command))  # Non-blocking send
    def handle_stop(self, event):
        """Handle emergency stop command."""
        self.loop.create_task(self.send_command(0))
        self.update_direction('STOP', "#FF1493")
    def bind_controls(self):
        """Bind keyboard keys to actions."""
        movement_keys = ['<Up>', '<Down>', '<Left>', '<Right>', 'w', 's', 'a', 'd']
        for key in movement_keys:
            self.window.bind(key, self.handle_movement)
        self.window.bind('<space>', self.handle_stop)
    def run(self):
        """Start the GUI."""
        self.window.mainloop()
if __name__ == "__main__":
    app = FuturisticController()
    app.run()
