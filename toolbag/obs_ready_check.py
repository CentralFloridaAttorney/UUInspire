import obswebsocket
import time

# OBS WebSocket connection details
HOST = "0.0.0.0"
PORT = 4444
PASSWORD = "your_password"


def ready_check():
    # Connect to OBS WebSocket
    client = obswebsocket.obsws(HOST, PORT, PASSWORD)
    client.connect()

    # Show "Ready Check" scene
    client.call(obswebsocket.requests.SetCurrentScene('Ready Check'))
    time.sleep(5)  # Display the scene for 5 seconds

    # Switch back to the main scene
    client.call(obswebsocket.requests.SetCurrentScene('Main Scene'))

    client.disconnect()


if __name__ == "__main__":
    ready_check()
