# this code uses the same system to control the rover (by sending integers to the esp32 through wifi),
# except it has a UI and takes keyboard inputs that are mapped to the different integers before sending the commands to the esp32

import tkinter as tk
from tkinter import ttk
import socket
import threading
import time
# ESP32 Configuration
ESP32_IP = "192.168.4.1"
ESP32_PORT = 1234
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
class FuturisticController:
   def __init__(self):
       self.window = tk.Tk()
       self.window.title(":rocket: Quantum Drive Controller")
       self.window.configure(bg='#1C1C1E')
       # Make window full screen by default
       screen_width = self.window.winfo_screenwidth()
       screen_height = self.window.winfo_screenheight()
       self.window.geometry(f"{screen_width}x{screen_height}")
       # Style configuration
       self.style = ttk.Style()
       self.style.configure('Futuristic.TFrame', background='#1C1C1E')
       # Create main container
       self.main_frame = ttk.Frame(self.window, style='Futuristic.TFrame')
       self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
       # Status display
       self.status_frame = tk.Frame(self.main_frame, bg='#1C1C1E')
       self.status_frame.pack(fill='x', pady=10)
       self.connection_status = tk.Label(
           self.status_frame,
           text="● SYSTEM ONLINE",
           font=("Consolas", 14),
           fg="#00FF00",
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
       # Start monitoring thread
       self.monitoring_thread = threading.Thread(target=self.monitor_system, daemon=True)
       self.monitoring_thread.start()
   def pulse_animation(self):
       """Creates a pulsing effect for the status indicator"""
       current_color = self.connection_status.cget("fg")
       new_color = "#008800" if current_color == "#00FF00" else "#00FF00"
       self.connection_status.configure(fg=new_color)
       self.window.after(1000, self.pulse_animation)
   def send_command(self, command):
       """Send a command to the ESP32 with visual feedback"""
       try:
           sock.sendto(str(command).encode(), (ESP32_IP, ESP32_PORT))
           self.command_history.append(command)
           self.update_status(f"Command sent: {command}")
       except Exception as e:
           self.update_status(f"Error: {e}", error=True)
   def update_status(self, message, error=False):
       """Update the status display with message"""
       color = "#FF0000" if error else "#00FF00"
       self.connection_status.configure(text=f"● {message}", fg=color)
   def update_direction(self, text, color):
       """Update the direction display with visual feedback"""
       self.direction_label.configure(text=text, fg=color)
   def handle_movement(self, event):
       """Handle movement commands with visual feedback"""
       if event.keysym in ['Up', 'w']:
           self.update_direction('↑ FORWARD', "#00FF00")
           self.send_command(1)
       elif event.keysym in ['Down', 's']:
           self.update_direction('↓ BACKWARD', "#FF4500")
           self.send_command(2)
       elif event.keysym == 'Left':
           self.update_direction('← LEFT SPIN', "#1E90FF")
           self.send_command(3)
       elif event.keysym == 'Right':
           self.update_direction('→ RIGHT SPIN', "#FFD700")
           self.send_command(4)
       elif event.keysym == 'a':
           self.update_direction('⇦ STRAFE LEFT', "#FF00FF")
           self.send_command(5)
       elif event.keysym == 'd':
           self.update_direction('⇨ STRAFE RIGHT', "#00FFFF")
           self.send_command(6)
   def handle_stop(self, event):
       """Handle emergency stop command"""
       self.send_command(0)
       self.update_direction('STOP', "#FF1493")
       # Emergency stop flash effect
       for i in range(3):
           self.window.after(i*200, lambda: self.direction_label.configure(bg="#FF1493"))
           self.window.after(i*200+100, lambda: self.direction_label.configure(bg="#1C1C1E"))
   def monitor_system(self):
       """Monitor system status and update display"""
       while True:
           time.sleep(1)
           # Add any monitoring logic here
           pass
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
