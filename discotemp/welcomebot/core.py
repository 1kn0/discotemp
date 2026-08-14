
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Union

import discord

from .renderer import render_welcome
from .schema import SchemaError, validate

logger = logging.getLogger("discordtemplates.welcomebot")


class WelcomeBot:


    def __init__(
        self,
        channel_id: int,
        template: Union[str, Path, dict],
        guild_id: Optional[int] = None,
    ):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.template_data = self._load_template(template)

        try:
            validate(self.template_data)
        except SchemaError as e:
            raise SchemaError(f"Invalid welcome template: {e}") from e


    @staticmethod
    def _load_template(template: Union[str, Path, dict]) -> dict:
        if isinstance(template, dict):
            return template

        if isinstance(template, Path):
            return json.loads(template.read_text(encoding="utf-8"))

        if isinstance(template, str):
            stripped = template.strip()
            # Looks like inline JSON rather than a file path
            if stripped.startswith("{"):
                return json.loads(stripped)
            path = Path(template)
            if not path.exists():
                raise FileNotFoundError(f"Welcome template not found: {template}")
            return json.loads(path.read_text(encoding="utf-8"))

        raise TypeError(
            f"template must be a dict, str, or Path, got {type(template).__name__}"
        )

    # -- sending --------------------------------------------------------

    async def send(self, member: discord.Member) -> Optional[discord.Message]:

        if self.guild_id is not None and member.guild.id != self.guild_id:
            return None

        channel = member.guild.get_channel(self.channel_id)
        if channel is None:
            try:
                channel = await member.guild.fetch_channel(self.channel_id)
            except discord.HTTPException:
                logger.warning(
                    "WelcomeBot: channel %s not found in guild %s",
                    self.channel_id,
                    member.guild.id,
                )
                return None

        rendered = render_welcome(self.template_data, member)
        send_kwargs = {}
        if rendered.get("view") is not None:
            send_kwargs["view"] = rendered["view"]
        if rendered.get("embed") is not None:
            send_kwargs["embed"] = rendered["embed"]

        return await channel.send(**send_kwargs)

    # -- wiring into a bot ------------------------------------------------

    def attach(self, bot: discord.Client) -> None:

        @bot.listen("on_member_join")
        async def _welcomebot_on_member_join(member: discord.Member):
            await self.send(member)
