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
async def get_relevant_subreddits(topic: str, limit: int = 10) -> list[dict]:
    """This tool retrieves a list of relevant subreddits related to a given topic.

    The 'topic' is a string that describes the topic of the subreddits to be retrieved.
    The 'limit' is an integer that specifies the maximum number of subreddits to retrieve.
    
    Args:
        topic (str): The topic to search for subreddits.
        limit (int): The maximum number of subreddits to retrieve.

    Returns:
        list[dict]: A list of dictionaries containing subreddit names and descriptions.
    """
    try:
        # Create Reddit instance
        reddit = await create_reddit()

        # Use Reddit's search API to get subreddits related to the topic
        subreddits = reddit.subreddits.search(topic, limit=limit)
        
        # Create a list to store subreddit names
        subreddit_list = []
        
        # Collect relevant subreddits
        async for subreddit in subreddits:
            subreddit_list.append(
                {
                    "subreddit": subreddit.display_name, 
                    "description": subreddit.public_description
                 }
                )
        
        return subreddit_list
    
    except Exception as e:
        # Log more detailed error information for debugging
        print(f"Error occurred: {e}")
        return f"An error occurred: {e}"
    
@mcp.tool()
async def get_relevant_threads(subreddit_name: str, limit: int = 5, sort_by: str = 'hot') -> list[dict]:
    """This tool retrieves relevant threads (posts) from a given subreddit.
    You can specify the sorting method (hot, new, top) and the number of posts to retrieve.

    Args:
        subreddit_name (str): The name of the subreddit to retrieve threads from.
        limit (int): The maximum number of posts to retrieve.
        sort_by (str): The sorting method to use 
                       Options: 'hot', 'new', 'top'.

    Returns:
        list[dict]: A list of dictionaries containing thread titles, URLs, scores, comments, authors, creation times, and subreddit names.
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
                'post_id': post.id,
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
    

@mcp.tool()
async def get_comments_from_post(post_id: str, limit: int = 10) -> list[dict]:
    """This tool retrieves comments from a given Reddit post using the post's ID.

    Args:
        post_id (str): The ID of the post to retrieve comments from.
        limit (int): The maximum number of comments to retrieve.

    Returns:
        list[dict]: A list of dictionaries containing comment author, score, body, and ID.
    """
    try:
        # Create Reddit instance
        reddit = await create_reddit()
        post = await reddit.submission(id=post_id)

        # Fetch the comments for the post (the .comments attribute returns a PRAW object for comments)
        post_comments = post.comments

        # Make sure the comments are fully populated (i.e., load more if necessary)
        await post.comments.replace_more(limit=None)

        # Limit the number of comments to return
        comments_list = []
        for comment in post_comments[:limit]:
            comments_list.append({
                'author': comment.author.name if comment.author else 'Unknown',
                'score': comment.score,
                'body': comment.body,
                'id': comment.id
            })

        return comments_list
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"An error occurred: {e}"

@mcp.prompt()
async def get_reddit_post_summary(topic: str, num_subreddits: int = 10, num: int = 5) -> str:
    """Generate a prompt for Claude to find and discuss academic papers on a specific topic."""
    
    return f"""Search for relevant discussions about '{topic}' on Reddit using the get_relevant_subreddits and get_relevant_threads tools.

    Follow these instructions:
    
    1. First, use the `get_relevant_subreddits` tool to find `{num_subreddits}` subreddits related to the topic '{topic}'.
       - Choose the subreddits that are most relevant to the topic and the users are most likely to be interested in. Use the `description` to help you make this decision.

    2. For each subreddit you keep from step 1, invoke the tool `get_relevant_threads` to fetch the top `{num}` posts:
       - Top posts are the posts with the highest score (upvotes) and the most comments (engagement).

    3. For each post, invoke the tool `get_comments_from_post` to fetch the top `{num}` comments

    4. After collecting posts and comments, analyze the data:
         - Common themes across posts and comments related to '{topic}'
         - Sentiment trends (positive, negative, or neutral)
         - Most discussed subtopics or areas of focus (e.g., trends, needs, pain points)
         - Keywords or phrases that emerge frequently across posts and comments

    5. **Provide a Comprehensive Summary**:
       - **Overview**: Provide a high-level summary of the main discussions about '{topic}'.
       - **Key Insights**: Highlight actionable insights such as:
         - What people are excited about or frustrated with
         - Any common product or service needs mentioned
         - Popular subtopics, opinions, or customer pain points
       - **Relevance to Advertising**: Suggest how these insights could guide potential advertising content or campaigns. For example, which areas might be worth targeting in ads, which media formats are popular, and how sentiment can guide messaging.

    """

# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')






