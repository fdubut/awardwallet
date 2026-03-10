import os
from typing import Never

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from awardwallet import AwardWalletClient
from awardwallet.client import AwardWalletAPIError

__all__ = ["main"]

_api_key = os.environ.get("AWARDWALLET_API_KEY")
if not _api_key:
    raise RuntimeError("AWARDWALLET_API_KEY environment variable is not set.")

_client = AwardWalletClient(_api_key)

mcp = FastMCP("awardwallet")


def _handle_api_error(e: AwardWalletAPIError) -> Never:
    """Convert AwardWallet API errors to MCP tool errors."""
    raise ToolError(str(e))


@mcp.tool()
def get_account_details(account_id: int) -> dict:
    """MCP tool mapping to get_account_details."""
    try:
        return _client.get_account_details(account_id).model_dump()
    except AwardWalletAPIError as e:
        _handle_api_error(e)


@mcp.tool()
def list_members() -> list[dict]:
    """MCP tool mapping to list_members."""
    try:
        return [m.model_dump() for m in _client.list_members()]
    except AwardWalletAPIError as e:
        _handle_api_error(e)


@mcp.tool()
def get_member_details(member_id: int) -> dict:
    """MCP tool mapping to get_member_details."""
    try:
        return _client.get_member_details(member_id).model_dump()
    except AwardWalletAPIError as e:
        _handle_api_error(e)


@mcp.tool()
def list_connected_users() -> list[dict]:
    """MCP tool mapping to list_connected_users."""
    try:
        return [u.model_dump() for u in _client.list_connected_users()]
    except AwardWalletAPIError as e:
        _handle_api_error(e)


@mcp.tool()
def get_connected_user_details(user_id: int) -> dict:
    """MCP tool mapping to get_connected_user_details."""
    try:
        return _client.get_connected_user_details(user_id).model_dump()
    except AwardWalletAPIError as e:
        _handle_api_error(e)


@mcp.tool()
def list_providers() -> list[dict]:
    """MCP tool mapping to list_providers."""
    try:
        return [p.model_dump() for p in _client.list_providers()]
    except AwardWalletAPIError as e:
        _handle_api_error(e)


@mcp.tool()
def get_provider_info(provider_code: str) -> dict:
    """MCP tool mapping to get_provider_info."""
    try:
        return _client.get_provider_info(provider_code).model_dump()
    except AwardWalletAPIError as e:
        _handle_api_error(e)


def main() -> None:
    mcp.run()
