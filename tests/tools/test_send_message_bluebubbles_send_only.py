"""Standalone BlueBubbles sends must not start the webhook listener."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from tools.send_message_tool import _send_bluebubbles


def test_send_bluebubbles_connects_send_only_then_sends_and_disconnects():
    fake_adapter = MagicMock()
    fake_adapter.connect = AsyncMock(return_value=True)
    fake_adapter.send = AsyncMock(
        return_value=SimpleNamespace(success=True, message_id="bb-msg-1", error=None)
    )
    fake_adapter.disconnect = AsyncMock()

    with (
        patch(
            "gateway.platforms.bluebubbles.check_bluebubbles_requirements",
            return_value=True,
        ),
        patch(
            "gateway.platforms.bluebubbles.BlueBubblesAdapter",
            return_value=fake_adapter,
        ),
    ):
        result = asyncio.run(
            _send_bluebubbles(
                {"server_url": "http://127.0.0.1:1234", "password": "x"},
                "chat-1",
                "hello",
            )
        )

    fake_adapter.connect.assert_awaited_once_with(send_only=True)
    fake_adapter.send.assert_awaited_once_with("chat-1", "hello")
    fake_adapter.disconnect.assert_awaited_once()
    assert result.get("success") is True
    assert result.get("platform") == "bluebubbles"
    assert result.get("message_id") == "bb-msg-1"
