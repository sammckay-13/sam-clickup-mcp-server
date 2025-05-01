from clickup_mcp_server.client import ClickUpClient
import os
import json

# Get API key from environment
api_key = os.environ.get('CLICKUP_API_KEY')
if not api_key:
    print("Error: CLICKUP_API_KEY not found in environment")
    exit(1)

# Create client
client = ClickUpClient(api_key)

# Direct API call to get comments
task_id = "86dwnff2v"
try:
    # Make direct request to API
    response = client._make_request("GET", f"/task/{task_id}/comment")
    comments = response.get("comments", [])
    
    # Print raw response for debugging
    print(f"Found {len(comments)} comments")
    print(json.dumps(comments, indent=2))
    
    # Check first comment's structure
    if comments:
        first = comments[0]
        print("\nFirst comment keys:", list(first.keys()))
        print("Date value:", first.get("date"), "Type:", type(first.get("date")))
except Exception as e:
    print(f"Error: {e}")
