from mcp.server.fastmcp import FastMCP
import asyncpraw
from dotenv import load_dotenv
import os
import asyncio
import aiohttp

load_dotenv()

# Create an MCP server
mcp = FastMCP("reddit-mcp")

# Set up Async Reddit API client using asyncpraw
async def create_reddit():
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)  # Ensure the event loop is set

    # Create an aiohttp TCP connector using the event loop
    connector = aiohttp.TCPConnector(limit_per_host=10, loop=loop)
    
    reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent='mcp-reddit-tool/0.1',
        connector=connector
    )
    
    return reddit

@mcp.tool()
async def get_relevant_subreddits(topic: str):
    """
    This tool retrieves a list of relevant subreddits related to a given topic.
    This version is designed for asynchronous environments.
    """
    try:
        # Create Reddit instance
        reddit = await create_reddit()

        # Use Reddit's search API to get subreddits related to the topic
        subreddits = reddit.subreddits.search(topic, limit=10)
        
        # Create a list to store subreddit names
        subreddit_list = []
        
        # Collect relevant subreddits asynchronously
        async for subreddit in subreddits:
            subreddit_list.append(subreddit.display_name)
        
        return subreddit_list
    
    except Exception as e:
        # Log more detailed error information for debugging
        print(f"Error occurred: {e}")
        return f"An error occurred: {e}"
    
@mcp.tool()
async def get_relevant_threads(subreddit_name: str, limit: int = 5, sort_by: str = 'hot'):
    """
    This tool retrieves relevant threads (posts) from a given subreddit.
    You can specify the sorting method (hot, new, top) and the number of posts to retrieve.
    """
    try:
        # Create Reddit instance
        reddit = await create_reddit()

        # Get the subreddit object
        subreddit = await reddit.subreddit(subreddit_name)
        
        # Fetch posts based on the sorting method
        if sort_by == 'hot':
            posts = subreddit.hot(limit=limit)
        elif sort_by == 'new':
            posts = subreddit.new(limit=limit)
        elif sort_by == 'top':
            posts = subreddit.top(limit=limit)
        else:
            return f"Invalid sort method: {sort_by}. Choose from 'hot', 'new', or 'top'."
        
        # Create a list to store thread titles and URLs
        thread_list = []
        
        # Collect relevant threads asynchronously
        async for post in posts:
            thread_list.append({
                'title': post.title,
                'url': post.url,
                'score': post.score,
                'comments': post.num_comments,
                'author': post.author,
                'created_utc': post.created_utc,
                'subreddit': post.subreddit.display_name,
                'body': post.selftext
            })
        
        return thread_list
    
    except Exception as e:
        # Log more detailed error information for debugging
        print(f"Error occurred: {e}")
        return f"An error occurred: {e}"

async def main():
    try:
        # Run the server within the event loop
        mcp.run(transport='stdio')
    except Exception as e:
        print(f"Error in main execution: {e}")

# Instead of calling asyncio.run(main()), just run the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')






