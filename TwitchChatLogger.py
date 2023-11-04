import websockets
import datetime
import sqlite3
import backoff
import os

twitch_oauth_token = os.environ.get("TWICH_OAUTH_TOKEN")
# Twitch IRC server details
server = 'wss://irc-ws.chat.twitch.tv:443'
oauth_token = f'oauth:{twitch_oauth_token}'


def create_logger(channel):
    conn = sqlite3.connect('twitch_logs.db')  # Create a connection to the SQLite database
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute(f'''
    CREATE TABLE IF NOT EXISTS twitch_{channel} (
        stream_id TEXT,
        timestamp TEXT,
        username TEXT,
        message TEXT
    )
    ''')

    conn.commit()  # Save (commit) the changes

    return conn, c


@backoff.on_exception(backoff.expo,
                      websockets.WebSocketException,
                      max_time=300)
async def twitch_chat_listener(db_conn, db_cursor, channel, stream_id):
    uri = server

    async with websockets.connect(uri) as websocket:
        await websocket.send(f'PASS {oauth_token}')
        await websocket.send('NICK justinfan123')
        await websocket.send(f'JOIN #{channel}')

        while True:
            try:
                response = await websocket.recv()
                if response.startswith('PING'):
                    await websocket.send('PONG :tmi.twitch.tv')
                    continue

                if 'PRIVMSG' in response:
                    received_channel = response.split('PRIVMSG #')[1].split(' :')[0]
                    if received_channel == channel:
                        username = response.split('!', 1)[0][1:]
                        message = response.split('PRIVMSG', 1)[1].split(':', 1)[1].strip()
                        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

                        # Insert stream_id along with the other data
                        db_cursor.execute(f"INSERT INTO twitch_{channel} VALUES (?, ?, ?, ?)",
                                          (stream_id, current_time, username, message))  # Insert a row of data
                        db_conn.commit()  # Save (commit) the changes

            except Exception as e:
                print(f'An unexpected error occurred: {e}')
                continue


def start_logging(channel, stream_id):
    db_conn, db_cursor = create_logger(channel)
    return twitch_chat_listener(db_conn, db_cursor, channel, stream_id)


async def start_logging_async(channel, stream_id):
    db_conn, db_cursor = create_logger(channel)
    await twitch_chat_listener(db_conn, db_cursor, channel, stream_id)