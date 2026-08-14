
from __future__ import annotations

import json
from typing import Any, Dict, Optional, Union

import discord


class SchemaError(ValueError):
    pass


class welcomebot:
    def __init__(self, channel_id: int, template: Union[str, Dict[str, Any]]):
        self.channel_id = int(channel_id)
        self._raw_template = template
        self.template = self._load_template(template)
        self._bot: Optional[discord.Client] = None

    def _load_template(self, template: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(template, str):
            try:
                with open(template, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception as exc:  
                raise SchemaError(f"Failed to load template file {template}: {exc}")
        elif isinstance(template, dict):
            data = template
        else:
            raise SchemaError("template must be a path to a JSON file or a dict")

        if not isinstance(data, dict):
            raise SchemaError("template JSON must be an object at top level")

        return data

    def attach(self, bot: discord.Client) -> None:
        self._bot = bot
        bot.add_listener(self._on_member_join)

    async def send(self, member: discord.Member) -> None:
        if self._bot is None:
            raise RuntimeError("welcomebot is not attached to a bot. Call attach(bot) first.")

        guild = member.guild
        channel = self._bot.get_channel(self.channel_id)
        if channel is None:
            try:
                channel = await guild.fetch_channel(self.channel_id)
            except Exception:
                raise RuntimeError(f"Could not find channel with id {self.channel_id}")

        context = {
            "user": member.mention,
            "guild": guild.name,
            "member_count": guild.member_count,
            # convenience dotted placeholders
            "user.name": member.display_name,
            "user.tag": str(member),
            "user.id": str(member.id),
        }

        tpl = self.template
        ttype = tpl.get("type") if isinstance(tpl, dict) else None

        def render(s: str) -> str:
            for k, v in context.items():
                s = s.replace("{" + k + "}", str(v))
            return s

        if ttype == "embed" or (ttype is None and ("title" in tpl or "description" in tpl)):
            title = render(tpl.get("title", ""))
            description = render(tpl.get("description", ""))
            color = tpl.get("color")
            if color and isinstance(color, str) and color.startswith("#"):
                color = int(color.lstrip("#"), 16)
            embed = discord.Embed(title=title or None, description=description or None, color=color)
            if "image" in tpl:
                embed.set_image(url=tpl["image"])
            if "footer" in tpl:
                embed.set_footer(text=render(tpl["footer"]))
            if "fields" in tpl and isinstance(tpl["fields"], list):
                for f in tpl["fields"]:
                    embed.add_field(name=render(f.get("name", "")), value=render(f.get("value", "")), inline=f.get("inline", False))

            await channel.send(embed=embed)
        else:
            content = tpl.get("content") if isinstance(tpl, dict) else None
            if content is None:
                content = tpl if isinstance(self._raw_template, str) else ""
            content = render(content)
            await channel.send(content)

    async def _on_member_join(self, member: discord.Member) -> None:
        try:
            await self.send(member)
        except Exception:
            import traceback

            traceback.print_exc()
