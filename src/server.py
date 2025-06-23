from mcp.server.fastmcp import FastMCP
from redditwarp.SYNC import Client

mcp = FastMCP("reddit-mcp")
client = Client()

def _build_post(post):
  return {
          'post_id': getattr(post, 'id', None),
          'post_author': getattr(post, 'author_display_name', None),
          'post_title': getattr(post, 'title', None),
          'post_body': getattr(post, 'body', None),
          'post_comment_count': getattr(post, 'comment_count', None)   
          }

def _build_comment(comment):
  return getattr(comment.value, 'body', None)

@mcp.tool()
def get_subreddit_list_info(subreddit_topic: str) -> dict:
    """This function retrieves information about a given subreddit.

    Args:
        subreddit_topic (str): The name of the subreddit to retrieve information about."""

    try:
        sub = client.p.subreddit.fetch_by_name(subreddit_topic)
        return {
            "subreddit_name": getattr(sub, 'name', None),
            "subreddit_description": getattr(sub, 'public_description', None),
            "subreddit_subscriber_count": getattr(sub, 'subscriber_count', None),
            "subreddit_active_users": sub.b.active_user_count
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

@mcp.tool()
def get_relevant_threads(subreddit_name: str, limit: int = 5) -> dict[str, list[dict]]:
    """This tool retrieves relevant threads (posts) from a given subreddit across multiple categories (hot, new, top, controversial).
    It fetches a set number of posts for each category and returns a dictionary of posts organized by category.

    Args:
        subreddit_name (str): The name of the subreddit to retrieve threads from.
        limit (int): The maximum number of posts to retrieve for each category (default is 5).

    Returns:
        dict: A dictionary where the keys are category names ('hot', 'new', 'top', 'controversial') and 
              the values are lists of dictionaries containing details of the posts, such as titles, URLs, scores, comments, authors, creation times, and subreddit names.
    """
    try:
        categories = ['hot', 'new', 'top', 'controversial']
        fetch_methods = {
            'hot': client.p.subreddit.pull.hot,
            'new': client.p.subreddit.pull.new,
            'top': client.p.subreddit.pull.top,
            'controversial': client.p.subreddit.pull.controversial
        }

        posts_dict = {}
        for category in categories:
            posts = fetch_methods[category](subreddit_name, limit)
            posts_dict[category] = [_build_post(post) for post in posts]

        return posts_dict

    except Exception as e:
        print(f"Error occurred: {e}")
        return {}

@mcp.tool()
def get_posts_comments(post_ids: list[int], limit: int =10) -> dict[str, list[str]]:
    """This tool retrieves comments from a given Reddit post using the post's ID.

    Args:
        post_id (str): The ID of the post to retrieve comments from.
        limit (int): The maximum number of comments to retrieve.

    Returns:
        list[dict]: A list of dictionaries containing comment author, score, body, and ID.
    """
    comments_dict = {}
    
    for post_id in post_ids:
        comments = []
        tree_node = client.p.comment_tree.fetch(post_id, sort='top', limit=limit)
        
        for node in tree_node.children:
            comment = _build_comment(node)
            if comment:
                comments.append(comment)
        
        comments_dict[post_id] = comments
    
    return comments_dict


@mcp.prompt()
async def get_reddit_post_summary(topic: str, limit: int = 10) -> str:
    """Generate a prompt for Claude to find and discuss posts on reddit about a specific topic."""
    
    return f"""Search the web to find relevant subreddits about '{topic}' and compile 3 subreddits. Once you have the subreddits, follow these instructions:
    
    1. First, use the `get_relevant_threads` for each subreddit tool to find relevant posts'.
       
    2. For each post you obtained from step 1, keep top `{limit}` posts:
       - Top posts are the ones with the highest score (upvotes) and the most comments (engagement).

    3. For each post, invoke the tool `get_posts_comments` to fetch the top `{limit}` comments.

    4. After collecting posts and comments, analyze the data:
         - Common themes across posts and comments related to '{topic}'
         - Most discussed subtopics or areas of focus (e.g., trends, needs, pain points)
         - Keywords or phrases that emerge frequently across posts and comments

    5. Provide a high-level summary of the main discussions about '{topic}'.
       - Highlight insights such as:
         - What people are excited about or frustrated with
         - Popular subtopics, opinions, or customer pain points
    """


# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
