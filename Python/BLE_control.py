# this code for sure works to send just integers no UI 
import asyncio
from bleak import BleakClient
# Replace with your ESP32's BLE MAC address or BLE device identifier.
# Example (Linux/macOS): address = "AA:BB:CC:11:22:33"
# On Windows, it might be something like: "00000000-0000-0000-0000-000000000000"
address = "2c:bc:bb:4c:57:3a" # MAKE SURE TO CHANGE/CHECK THIS IP 
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
async def main():
    print("Connecting to BLE device...")
    async with BleakClient(address) as client:
        if client.is_connected:
            print("Connected to BLE device!")
            while True:
                val = input("Enter a number 1-5 (or 'q' to quit): ")
                if val.lower() == 'q':
                    print("Quitting...")
                    break
                # Ensure the input is one of the valid strings
                if val in ['1', '2', '3', '4', '5']:
                    # Write the string (as bytes) to the characteristic
                    await client.write_gatt_char(CHARACTERISTIC_UUID, val.encode())
                    print(f"Sent '{val}' to the ESP32.")
                else:
                    print("Invalid input. Please enter a digit between 1 and 5, or 'q' to quit.")
asyncio.run(main())
