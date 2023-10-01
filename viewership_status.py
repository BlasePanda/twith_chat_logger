import asyncio
import datetime
import aiohttp
import os

async def fetch_data(channels):
    twitch_authorization = os.environ.get("TWITCH_AUTHORIZATION")
    twitch_client_id = os.environ.get("TWITCH_CLIENT_ID")

    if not twitch_authorization or not twitch_client_id:
        raise EnvironmentError("Twitch API credentials not set in environment variables.")

    url = 'https://api.twitch.tv/helix/streams'
    headers = {
        'Authorization': f'Bearer {twitch_authorization}',
        'Client-Id': f'{twitch_client_id}'
    }


    statuses = {}

    async with aiohttp.ClientSession() as session:
        for channel in channels:
            params = {
                'user_login': channel
            }
            try:
                print(f"Checking channel {channel}...")
                timeout = aiohttp.ClientTimeout(total=300)
                async with session.get(url, headers=headers, params=params, timeout=timeout) as response:
                    data = await response.json()
                    print(f"Response for channel {channel}: {data}")

                    if "data" in data and data["data"]:
                        game_name = data["data"][0]["game_name"]
                        viewer_count = data["data"][0]["viewer_count"]
                        time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

                        with open(f"{channel}_game_log.txt", "a") as file:
                            file.write(f"{time_now} - {game_name} - {viewer_count}\n")

                        print(game_name)
                        print(viewer_count, time_now)
                        statuses[channel] = "User is Online"
                    else:
                        statuses[channel] = "User is offline"

            except aiohttp.client_exceptions.ClientConnectorError:
                print("Connection failed. Retrying...")
                await asyncio.sleep(5)  # Wait for 5 seconds before retrying

    return statuses
