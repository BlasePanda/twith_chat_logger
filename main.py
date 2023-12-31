import asyncio
import aiohttp
import aioconsole
from TwitchChatLogger import start_logging_async  # Assuming these are in a module named TwitchChatLogger
from viewership_status import fetch_data
import datetime
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# Function to check internet connectivity
async def is_internet_up():
    url = "http://www.google.com"
    timeout = 5
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                return True
    except (aiohttp.ClientError, asyncio.TimeoutError, OSError):
        return False


Base = declarative_base()


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


DATABASE_URL = "sqlite:///./channel_names.db"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # Ensure all tables are created
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_all_channels(db):
    return db.query(Channel.name).all()


async def clear():
    print("\n" * 100)


async def manage_channels():
    db = SessionLocal()
    active = True  # Add a flag to control whether we're accepting input

    while True:
        if active:
            print("Type 'add' to add a channel, 'remove' to remove a channel, 'list' to list channels,"
                  " 'stop' to stop managing, or 'start' to start managing:")
            command = await aioconsole.ainput()

            if command == 'clear':
                await clear()
                continue

            if command == 'add':
                channel_name = await aioconsole.ainput("Enter the channel name to add: ")
                new_channel = Channel(name=channel_name)
                db.add(new_channel)
                db.commit()
                print(f"Added channel: {channel_name}")

            elif command == 'remove':
                channel_name = await aioconsole.ainput("Enter the channel name to remove: ")
                channel = db.query(Channel).filter(Channel.name == channel_name).first()
                if channel:
                    db.delete(channel)
                    db.commit()
                    print(f"Removed channel: {channel_name}")
                else:
                    print("Channel not found")

            elif command == 'list':
                channels = db.query(Channel.name).all()
                print("Channels:", channels)

            elif command == 'stop':
                active = False
                print("Management stopped. Type 'start' to begin managing channels again.")

            else:
                print("Invalid command")
        else:
            # If we're not active, check if the user wants to start managing channels again
            command = await aioconsole.ainput("Type 'start' to begin managing channels: ")
            if command == 'start':
                active = True
                print("Management started. Type 'stop' to stop managing channels.")

        # Add a short delay to prevent the loop from running too fast when not active
        await asyncio.sleep(0.1)

    db.close()


async def main():
    logging_tasks = {}
    asyncio.create_task(manage_channels())

    while True:
        if await is_internet_up():
            db = SessionLocal()
            channels = get_all_channels(db)
            db.close()
            channels = [channel[0] for channel in channels]

            statuses = await fetch_data(channels)
            online_channels = {channel for channel, status in statuses.items()}

            for channel in online_channels:
                if channel not in logging_tasks:
                    stream_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    task = asyncio.create_task(start_logging_async(channel, stream_id))
                    logging_tasks[channel] = task

            for channel in list(logging_tasks):
                if channel not in online_channels:
                    logging_tasks[channel].cancel()
                    del logging_tasks[channel]

            await asyncio.sleep(60)  # Wait for 60 seconds
        else:
            print("Internet is down. Waiting for reconnection...")
            for task in logging_tasks.values():
                task.cancel()
            logging_tasks.clear()
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())