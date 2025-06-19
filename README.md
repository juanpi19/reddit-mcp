# Reddit MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Reddit's API through Claude Desktop. This server enables Claude to search subreddits, retrieve posts, analyze comments, and generate comprehensive Reddit content summaries.

## Prerequisites

- Python 3.10 or higher
- UV package manager
- Claude Desktop application
- Reddit API access (no credentials required for read-only operations)

## Installation & Setup

Add the following configuration to your Claude Desktop config file:

**Location of config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "reddit-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/juanpi19/reddit-mcp.git", "reddit-mcp"],
      "env": {}
    }
  }
}
```

Restart Claude Desktop after updating the config file.

## Usage Examples

Once configured, you can use these commands in Claude Desktop:

### Basic Subreddit Information
```
Can you get information about the r/MachineLearning subreddit?
```

### Find and Analyze Posts
```
Get the top 5 hot posts from r/technology and show me their titles and comment counts
```

### Comment Analysis
```
Fetch comments from Reddit post ID 12345 and summarize the main discussion points
```

### Comprehensive Topic Analysis
```
Use the Reddit post summary prompt to analyze discussions about "artificial intelligence" - find relevant subreddits, get top posts, and provide insights on what people are talking about
```

## Available Tools

### `get_subreddit_list_info(subreddit_topic: str)`
Retrieves detailed information about a specific subreddit.

### `get_relevant_threads(subreddit_name: str, limit: int = 5)`
Fetches posts from a subreddit across multiple categories (hot, new, top, controversial).

### `get_posts_comments(post_ids: list[int], limit: int = 10)`
Retrieves top comments from specific Reddit posts.

### `get_reddit_post_summary` (Prompt Template)
Generates a comprehensive analysis prompt for exploring Reddit discussions on any topic.

## Dependencies

- **mcp[cli]** >= 1.9.3 - Model Context Protocol framework
- **python-dotenv** >= 1.1.0 - Environment variable management  
- **redditwarp** >= 1.3.0 - Reddit API client