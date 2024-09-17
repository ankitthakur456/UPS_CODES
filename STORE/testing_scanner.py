import serial
import serial.tools.list_ports


def read_barcode():
    # Replace 'COM3' with your actual port (e.g., '/dev/ttyUSB0' for Linux)
    ports = serial.tools.list_ports.comports()
    port = [p.device for p in ports if "USB" in p.description]
    port = port[0]
    baud_rate = 9600  # Typically, barcode scanners use 9600 baud rate

    # Open the serial port
    with serial.Serial(port, baud_rate, timeout=1) as ser:
        print(f"Connected to {ser.name}")
        while True:
            try:
                if ser.in_waiting > 0:
                    a = ser.readline()
                    print()
                    barcode_data = ser.readline().decode('utf-8').strip()
                    return barcode_data  # Return the barcode data
            except Exception as e:
                print(f"Error: {e}")
                return None  # Return None if an error occurs


if __name__ == "__main__":
    while True:
        scanner_data = read_barcode()
        print(type(scanner_data))
        print(scanner_data)
