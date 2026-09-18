import asyncio
import websockets
import sys

async def chat_client(client_id):
    uri = f"ws://127.0.0.1:8000/ws/chat/1"
    print(f"Connecting to {uri} as Client {client_id}...")
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Client {client_id} connected!")
            
            async def receive_messages():
                try:
                    while True:
                        message = await websocket.recv()
                        print(f"\nReceived: {message}")
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")

            async def send_messages():
                while True:
                    message = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                    if message.strip():
                        await websocket.send(f"Client {client_id}: {message.strip()}")

            await asyncio.gather(receive_messages(), send_messages())
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        client_id = sys.argv[1]
    else:
        client_id = "1"
    
    try:
        asyncio.run(chat_client(client_id))
    except KeyboardInterrupt:
        print("\nExiting...")
