from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from awardwallet.client import AwardWalletAPIError
from awardwallet.server import (
    _handle_api_error,
    get_account_details,
    get_connected_user_details,
    get_member_details,
    get_provider_info,
    list_connected_users,
    list_members,
    list_providers,
)


def _make_model_mock(**dump_data: object) -> MagicMock:
    """Return a mock Pydantic model whose model_dump() returns *dump_data*."""
    m = MagicMock()
    m.model_dump.return_value = dump_data
    return m


class TestListTools:
    @patch("awardwallet.server._client")
    def test_list_providers(self, mock_client):
        mock_client.list_providers.return_value = [
            _make_model_mock(code="aa", displayName="American Airlines"),
            _make_model_mock(code="ua", displayName="United Airlines"),
        ]
        result = list_providers()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["code"] == "aa"
        assert result[1]["code"] == "ua"

    @patch("awardwallet.server._client")
    def test_list_connected_users(self, mock_client):
        mock_client.list_connected_users.return_value = [
            _make_model_mock(user_id=10, email="a@b.com"),
        ]
        result = list_connected_users()
        assert len(result) == 1
        assert result[0]["user_id"] == 10

    @patch("awardwallet.server._client")
    def test_list_members(self, mock_client):
        mock_client.list_members.return_value = [
            _make_model_mock(member_id=1, full_name="Alice"),
        ]
        result = list_members()
        assert len(result) == 1
        assert result[0]["member_id"] == 1


class TestGetDetailsTools:
    @patch("awardwallet.server._client")
    def test_get_provider_info(self, mock_client):
        mock_client.get_provider_info.return_value = _make_model_mock(
            code="aa", kind=1
        )
        result = get_provider_info("aa")
        assert result == {"code": "aa", "kind": 1}
        mock_client.get_provider_info.assert_called_once_with("aa")

    @patch("awardwallet.server._client")
    def test_get_connected_user_details(self, mock_client):
        mock_client.get_connected_user_details.return_value = _make_model_mock(
            user_id=10, full_name="Carol"
        )
        result = get_connected_user_details(10)
        assert result == {"user_id": 10, "full_name": "Carol"}
        mock_client.get_connected_user_details.assert_called_once_with(10)

    @patch("awardwallet.server._client")
    def test_get_member_details(self, mock_client):
        mock_client.get_member_details.return_value = _make_model_mock(
            member_id=42, full_name="Bob"
        )
        result = get_member_details(42)
        assert result == {"member_id": 42, "full_name": "Bob"}
        mock_client.get_member_details.assert_called_once_with(42)

    @patch("awardwallet.server._client")
    def test_get_account_details(self, mock_client):
        mock_client.get_account_details.return_value = _make_model_mock(
            account_id=99, balance="1000"
        )
        result = get_account_details(99)
        assert result == {"account_id": 99, "balance": "1000"}
        mock_client.get_account_details.assert_called_once_with(99)


class TestMcpErrorHandling:
    _TOOLS_WITH_ARGS: list[tuple[object, tuple, str]] = [
        (list_providers, (), "list_providers"),
        (list_connected_users, (), "list_connected_users"),
        (list_members, (), "list_members"),
        (get_provider_info, ("aa",), "get_provider_info"),
        (get_connected_user_details, (1,), "get_connected_user_details"),
        (get_member_details, (1,), "get_member_details"),
        (get_account_details, (1,), "get_account_details"),
    ]

    def test_preserves_status_code(self):
        err = AwardWalletAPIError("not found", status_code=404)
        with pytest.raises(ToolError, match="404"):
            _handle_api_error(err)

    @pytest.mark.parametrize(
        ("tool_fn", "args", "client_method"),
        _TOOLS_WITH_ARGS,
        ids=[m for _, _, m in _TOOLS_WITH_ARGS],
    )
    @patch("awardwallet.server._client")
    def test_converts_to_tool_error(
        self, mock_client, tool_fn, args, client_method
    ):
        getattr(mock_client, client_method).side_effect = AwardWalletAPIError(
            "boom", status_code=500
        )

        with pytest.raises(ToolError, match="boom"):
            tool_fn(*args)
