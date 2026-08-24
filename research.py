import logging
import os
import random
import sys
import requests
from mcp.server.fastmcp import FastMCP

name = "demo-mcp-server"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('/tmp/mcp_server.log')]  # Only file logging for stdio
)
logger = logging.getLogger(name)

logger.info("MCP Server Starting")

mcp = FastMCP(name)  # Remove port parameter

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    logger.info(f"Tool called: add({a}, {b})")
    return a + b

@mcp.tool()
def get_secret_word() -> str:
    """Get a random secret word"""
    logger.info("Tool called: get_secret_word()")
    return random.choice(["apple", "banana", "cherry"])

@mcp.tool()
def get_current_weather(city: str) -> str:
    """Get current weather for a city"""
    logger.info(f"Tool called: get_current_weather({city})")
    try:
        endpoint = "https://wttr.in"
        response = requests.get(f"{endpoint}/{city}", timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return f"Error fetching weather data: {str(e)}"

# Updated DuckDuckGo search function
@mcp.tool()
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo"""
    logger.info(f"Tool called: search_web({query})")
    try:
        from ddgs import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return "No results found"
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. {result['title']}\n"
                f"   URL: {result['href']}\n"
                f"   {result['body']}\n"
            )
        
        return "\n".join(formatted_results)
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return f"Search error: {str(e)}"

@mcp.tool()
def list_dir(path: str):
    return os.listdir(path)

@mcp.tool()
def read_file(path: str):
    return open(path).read()


if __name__ == "__main__":
    logger.info("Starting MCP Server in stdio mode...")
    mcp.run()