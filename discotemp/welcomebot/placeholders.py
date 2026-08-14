

from __future__ import annotations

import discord


def build_context(member: discord.Member) -> dict:
    guild = member.guild
    return {
        "user": member.mention,
        "user.name": member.display_name,
        "user.tag": str(member),
        "user.id": str(member.id),
        "user.avatar": str(member.display_avatar.url),
        "guild": guild.name if guild else "",
        "guild.id": str(guild.id) if guild else "",
        "member_count": str(guild.member_count) if guild else "",
    }


def render_text(template: str, context: dict) -> str:
    if not template:
        return template

    result = template
    for key, value in context.items():
        result = result.replace("{" + key + "}", value)
    return result


def render_any(value, context: dict):
    if isinstance(value, str):
        return render_text(value, context)
    if isinstance(value, list):
        return [render_any(v, context) for v in value]
    if isinstance(value, dict):
        return {k: render_any(v, context) for k, v in value.items()}
    return value
