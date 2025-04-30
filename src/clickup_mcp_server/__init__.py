import click
from pathlib import Path
import logging
import sys
import os
from dotenv import load_dotenv
from .server import serve


@click.command()
@click.option("--api-key", "-k", help="ClickUp API Key (overrides .env file)")
@click.option("-v", "--verbose", count=True)
def main(api_key: str | None, verbose: bool) -> None:
    """ClickUp MCP Server - ClickUp API functionality for MCP"""
    import asyncio

    # Configure logging
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    logger = logging.getLogger(__name__)

    # Load environment variables from .env file
    load_dotenv()
    
    # Use API key from arguments or from .env file
    clickup_api_key = api_key or os.getenv("CLICKUP_API_KEY")
    
    if not clickup_api_key:
        logger.error("No ClickUp API key provided. Use --api-key option or set CLICKUP_API_KEY in .env file")
        sys.exit(1)
    
    asyncio.run(serve(clickup_api_key))


if __name__ == "__main__":
    main()