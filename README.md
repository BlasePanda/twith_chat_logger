# twith_chat_logger

![Tracking Image](https://ac3e-93-136-19-78.ngrok-free.app/tracking.png?repo=repository-name)
     
## Introduction

You can log multiple twitch channel at once, program also tracks viewership and current game

## Pre-requisites

Before running the main script, you need to set up the following environment variables with relevant keys:

- `TWITCH_AUTHORIZATION`: Your Twitch Authorization key.
- `TWITCH_CLIENT_ID`: Your Twitch Client ID.
- `TWITCH_OAUTH_TOKEN`: Your Twitch OAuth Token.

### How to Set Up Environment Variables

#### For Windows:

1. Search for "Environment Variables" in the Start menu.
2. Click on "Edit the system environment variables."
3. In the System Properties window, click "Environment Variables."
4. In the Environment Variables window, click "New" under the User variables section.
5. Enter the variable name and value, and click "OK."

#### For macOS/Linux:

You can set environment variables in the terminal session or add them to your shell initialization script (`~/.bashrc`, `~/.bash_profile`, `~/.zshrc`, etc.) for persistence.

1. Open the terminal.
2. To set environment variables for the current session, use the following commands:

```shell
export TWITCH_AUTHORIZATION="your_authorization_key"
export TWITCH_CLIENT_ID="your_client_id"
export TWITCH_OAUTH_TOKEN="your_oauth_token"
