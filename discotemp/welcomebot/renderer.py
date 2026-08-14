
from __future__ import annotations

from typing import Optional

import discord
from discokit import Kit, Text, View

from .placeholders import build_context, render_any, render_text
from .schema import validate, _normalize_style


BUTTON_STYLES = {
    1: discord.ButtonStyle.primary,
    2: discord.ButtonStyle.secondary,
    3: discord.ButtonStyle.success,
    4: discord.ButtonStyle.danger,
    5: discord.ButtonStyle.link,
}

SPACING = {
    "small": discord.SeparatorSpacing.small,
    "large": discord.SeparatorSpacing.large,
}


def render_welcome(data: dict, member: discord.Member) -> dict:
    fmt = validate(data)
    context = build_context(member)
    data = render_any(data, context)

    if fmt == "layout":
        return {"view": _render_layout(data), "embed": None}
    return _render_embed(data)



def _render_layout(data: dict) -> View:
    blocks = data.get("blocks", [])
    accent = _parse_colour(data.get("accent_colour"))

    items = [_render_block(block) for block in blocks]
    container = Kit.container(*items, accent_colour=accent)
    return Kit.view(container)


def _render_block(block: dict):
    btype = block["type"]

    if btype == "gallery":
        gallery_items = [
            Kit.gallery_item(
                item["url"],
                description=item.get("description"),
                spoiler=item.get("spoiler", False),
            )
            for item in block["items"]
        ]
        return Kit.gallery(*gallery_items)

    if btype == "separator":
        spacing = SPACING.get(block.get("spacing", "small"), discord.SeparatorSpacing.small)
        return Kit.separator(visible=block.get("divider", True), spacing=spacing)

    if btype == "text":
        return Kit.text(block["content"])

    if btype == "heading":
        return Kit.heading(block["content"], level=block.get("level", 1))

    if btype == "subtext":
        return Kit.subtext(block["content"])

    if btype == "thumbnail":
        return Kit.thumbnail(
            block["url"],
            description=block.get("description"),
            spoiler=block.get("spoiler", False),
        )

    if btype == "file":
        return Kit.file(block["url"], spoiler=block.get("spoiler", False))

    if btype == "section":
        texts = block["text"]
        if isinstance(texts, str):
            texts = [texts]

        accessory = None
        if block.get("button"):
            accessory = _render_button(block["button"])
        elif block.get("thumbnail"):
            thumb = block["thumbnail"]
            url = thumb if isinstance(thumb, str) else thumb.get("url")
            accessory = Kit.thumbnail(url)

        return Kit.section(*texts, accessory=accessory)

    raise ValueError(f"Unknown block type: {btype}")


def _render_button(button: dict) -> discord.ui.Button:
    style_num = _normalize_style(button.get("style", 5))
    style = BUTTON_STYLES.get(style_num, discord.ButtonStyle.link)
    label = button.get("label")
    emoji = _resolve_emoji(button.get("emoji"))

    if style is discord.ButtonStyle.link:
        return Kit.link_button(
            label,
            button["url"],
            emoji=emoji,
            disabled=button.get("disabled", False),
            row_index=button.get("row"),
        )

    return Kit.button(
        label,
        style=style,
        emoji=emoji,
        custom_id=button.get("custom_id"),
        disabled=button.get("disabled", False),
        row_index=button.get("row"),
    )


def _resolve_style(style) -> int:
    return _normalize_style(style)


def _resolve_emoji(emoji):

    if emoji is None:
        return None

    if isinstance(emoji, dict):
        return discord.PartialEmoji(
            name=emoji.get("name"),
            id=emoji.get("id"),
            animated=emoji.get("animated", False),
        )

    if isinstance(emoji, str) and emoji.startswith("<") and emoji.endswith(">"):
        try:
            return discord.PartialEmoji.from_str(emoji)
        except Exception:
            return emoji 

    return emoji


def _parse_colour(value) -> Optional[discord.Colour]:
    if value is None:
        return None
    if isinstance(value, int):
        return discord.Colour(value)
    if isinstance(value, str):
        hexval = value.lstrip("#")
        return discord.Colour(int(hexval, 16))
    return None



def _render_embed(data: dict) -> dict:
    colour = _parse_colour(data.get("color") or data.get("colour"))

    embed = discord.Embed(
        title=data.get("title"),
        description=data.get("description"),
        colour=colour,
    )

    if data.get("image"):
        embed.set_image(url=data["image"])
    if data.get("thumbnail"):
        embed.set_thumbnail(url=data["thumbnail"])
    if data.get("footer"):
        embed.set_footer(text=data["footer"])
    if data.get("author"):
        author = data["author"]
        if isinstance(author, str):
            embed.set_author(name=author)
        else:
            embed.set_author(name=author.get("name", ""), icon_url=author.get("icon_url"))

    for field in data.get("fields", []):
        embed.add_field(
            name=field["name"],
            value=field["value"],
            inline=field.get("inline", False),
        )

    view = None
    if data.get("button"):
        btn = _render_button(data["button"])
        view = discord.ui.View()
        view.add_item(btn)

    return {"view": view, "embed": embed}