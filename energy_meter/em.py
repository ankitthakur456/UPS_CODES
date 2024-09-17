from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import logging

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

def read_energy_meter():
    # Set up the Modbus RTU client
    client = ModbusClient(
        method='rtu',          # Communication method: RTU
        port='/dev/ttyUSB1',           # Replace with your serial port, e.g., COM4 or /dev/ttyUSB0
        baudrate=19200,         # Replace with your baud rate
        parity='E',            # Parity: None, Even, Odd
        stopbits=1,            # Stop bits
        bytesize=8,            # Data bits (usually 8)
        timeout=1              # Timeout for reading
    )

    # Connect to the Modbus device
    connection = client.connect()
    if connection:
        print("Connected to the Modbus device.")
    else:
        print("Failed to connect.")
        return

    try:
        # Replace with the actual slave address, register address, and number of registers
        SLAVE_ID = 1            # Modbus slave ID
        START_REGISTER = 3690      # Starting register address
        NUM_REGISTERS = 1       # Number of registers to read

        # Send a request to read holding registers
        result = client.read_holding_registers(START_REGISTER, NUM_REGISTERS, unit=SLAVE_ID)

        # Check if the read was successful
        if not result.isError():
            print(f"Registers: {result.registers}")
        else:
            print(f"Error reading registers: {result}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the connection
        client.close()

if __name__ == "__main__":
    read_energy_meter()
