# Reddit MCP

A Python-based MCP (Model Control Protocol) server that provides tools for interacting with Reddit's API. This project allows you to search for relevant subreddits and retrieve threads from specific subreddits.

## Features

- Search for relevant subreddits based on a topic
- Retrieve threads from specific subreddits with various sorting options (hot, new, top)

## Prerequisites

- Python 3.10 or higher
- UV package manager
- Reddit API credentials (Client ID and Client Secret)

## Setup

1. Create a `.env` file in your project directory with your Reddit API credentials:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

2. Add the following configuration to your `config_file.json`:
```json
{
  "reddit": {
    "command": "uvx",
    "args": ["--from", "git+https://github.com/juanpi19/mcp-reddit.git", "mcp-reddit"],
    "env": {}
  }
}
```

## Dependencies

- asyncpraw >= 7.8.1
- mcp[cli] >= 1.9.3
- python-dotenv >= 1.1.0


