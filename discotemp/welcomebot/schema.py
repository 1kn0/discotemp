from __future__ import annotations

VALID_BLOCK_TYPES = {
    "gallery", "separator", "text", "heading", "subtext", "section", "thumbnail", "file",
}
VALID_SPACING = {"small", "large"}


class SchemaError(ValueError):
    """Raised when the welcome JSON does not match the expected schema."""


def detect_format(data: dict) -> str:
    explicit = data.get("type")
    if explicit in ("layout", "embed"):
        return explicit
    if "blocks" in data:
        return "layout"
    return "embed"


def validate(data: dict) -> str:

    if not isinstance(data, dict):
        raise SchemaError("Welcome JSON root must be an object.")

    fmt = detect_format(data)

    if fmt == "layout":
        _validate_layout(data)
    else:
        _validate_embed(data)

    return fmt


def _validate_layout(data: dict) -> None:
    blocks = data.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise SchemaError('Layout JSON must have a non-empty "blocks" list.')

    for i, block in enumerate(blocks):
        if not isinstance(block, dict):
            raise SchemaError(f"blocks[{i}] must be an object.")
        btype = block.get("type")
        if btype not in VALID_BLOCK_TYPES:
            raise SchemaError(
                f'blocks[{i}].type "{btype}" is not one of {sorted(VALID_BLOCK_TYPES)}.'
            )

        if btype == "gallery":
            items = block.get("items")
            if not isinstance(items, list) or not items:
                raise SchemaError(f'blocks[{i}] (gallery) needs a non-empty "items" list.')
            for j, item in enumerate(items):
                if "url" not in item:
                    raise SchemaError(f'blocks[{i}].items[{j}] is missing "url".')

        elif btype == "separator":
            spacing = block.get("spacing", "small")
            if spacing not in VALID_SPACING:
                raise SchemaError(
                    f'blocks[{i}] (separator) spacing must be one of {sorted(VALID_SPACING)}.'
                )

        elif btype == "text":
            if "content" not in block:
                raise SchemaError(f'blocks[{i}] (text) is missing "content".')

        elif btype == "heading":
            if "content" not in block:
                raise SchemaError(f'blocks[{i}] (heading) is missing "content".')
            level = block.get("level", 1)
            if level not in (1, 2, 3):
                raise SchemaError(f'blocks[{i}] (heading) level must be 1, 2, or 3.')

        elif btype == "subtext":
            if "content" not in block:
                raise SchemaError(f'blocks[{i}] (subtext) is missing "content".')

        elif btype == "section":
            text = block.get("text")
            if not isinstance(text, list) or not text:
                raise SchemaError(f'blocks[{i}] (section) needs a non-empty "text" list.')
            button = block.get("button")
            thumbnail = block.get("thumbnail")
            if button is None and thumbnail is None:
                raise SchemaError(
                    f'blocks[{i}] (section) needs a "button" or "thumbnail" accessory.'
                )
            if button is not None:
                _validate_button(button, f"blocks[{i}].button")

        elif btype == "thumbnail":
            if "url" not in block:
                raise SchemaError(f'blocks[{i}] (thumbnail) is missing "url".')

        elif btype == "file":
            if "url" not in block:
                raise SchemaError(f'blocks[{i}] (file) is missing "url".')


def _validate_button(button: dict, path: str) -> None:
    if not isinstance(button, dict):
        raise SchemaError(f"{path} must be an object.")

    if "label" not in button and "emoji" not in button:
        raise SchemaError(f'{path} needs a "label" and/or an "emoji" (Discord allows emoji-only buttons).')

    if "emoji" in button:
        _validate_emoji(button["emoji"], f"{path}.emoji")

    style = _normalize_style(button.get("style", 5))
    if style == 5 and "url" not in button:
        raise SchemaError(f'{path} has style link (5) but is missing "url".')
    if style != 5 and "url" in button:
        raise SchemaError(f'{path} has a "url" but style is not link — link buttons must use style 5/"link".')

    row = button.get("row")
    if row is not None and (not isinstance(row, int) or not (0 <= row <= 4)):
        raise SchemaError(f'{path}.row must be an integer 0-4.')


def _normalize_style(style) -> int:
    if isinstance(style, int):
        return style
    names = {
        "primary": 1, "blurple": 1,
        "secondary": 2, "grey": 2, "gray": 2,
        "success": 3, "green": 3,
        "danger": 4, "red": 4,
        "link": 5, "url": 5,
    }
    if isinstance(style, str) and style.lower() in names:
        return names[style.lower()]
    raise SchemaError(
        f'Unknown button style "{style}". Use 1-5, or one of '
        f'"primary"/"secondary"/"success"/"danger"/"link".'
    )


def _validate_emoji(emoji, path: str) -> None:
    if isinstance(emoji, str):
        return
    if isinstance(emoji, dict):
        if "name" not in emoji:
            raise SchemaError(f'{path} object form needs at least "name".')
        return
    raise SchemaError(f'{path} must be a string (unicode emoji or "<:name:id>") or an object with "name"/"id".')


def _validate_embed(data: dict) -> None:
    if "title" not in data and "description" not in data:
        raise SchemaError('Embed JSON needs at least a "title" or "description".')
    if "button" in data:
        _validate_button(data["button"], "button")
    fields = data.get("fields")
    if fields is not None:
        if not isinstance(fields, list):
            raise SchemaError('Embed "fields" must be a list.')
        for i, field in enumerate(fields):
            if "name" not in field or "value" not in field:
                raise SchemaError(f'fields[{i}] needs "name" and "value".')