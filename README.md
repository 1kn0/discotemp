# discordtemplates

Reusable, JSON-driven Discord bot building blocks.

The first template included is `welcomebot`: a drop-in welcome-message system
where the *message itself* lives in a JSON file, not in your bot code. It
supports Discord's modern Components V2 layout (galleries, separators, text
blocks, sections with buttons) via [`discokit`](https://pypi.org/project/discokit/),
as well as classic embeds — auto-detected from the JSON shape.

## Install

```bash
pip install discotemp.
```

Requires `discord.py>=2.6` and `discokit>=1.0.0` (installed automatically).

## Quick start

```python
from discotemp import welcomebot

welcome = welcomebot.WelcomeBot(
    channel_id=123456789012345678,
    template="welcome.json",
)
welcome.attach(bot)   # hooks on_member_join automatically
```

Or wire it manually:

```python
welcome = welcomebot.WelcomeBot(channel_id=..., template="welcome.json")

@bot.event
async def on_member_join(member):
    await welcome.send(member)
```

Remember to enable the `members` privileged intent:

```python
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
```

## Template format

`template` accepts a file path, a raw JSON string, or an already-parsed dict.

### Components V2 layout

```json
{
  "type": "layout",
  "accent_colour": "#5865F2",
  "blocks": [
    { "type": "gallery", "items": [
        { "url": "https://example.com/banner.png", "description": "Welcome banner", "spoiler": false }
    ]},
    { "type": "separator", "divider": true, "spacing": "small" },
    { "type": "text", "content": "# Welcome {user} to {guild}!" },
    { "type": "separator", "divider": true, "spacing": "small" },
    { "type": "section",
      "text": ["Thanks for joining our community.", "Read the rules and introduce yourself."],
      "button": { "label": "Rules", "style": 5, "url": "https://example.com/rules" }
    },
    { "type": "separator", "divider": true, "spacing": "small" }
  ]
}
```

Supported block `type`s: `gallery`, `separator`, `text`, `section`, `thumbnail`, `file`.

Button `style` follows Discord's `ButtonStyle` numbering: `1` primary,
`2` secondary, `3` success, `4` danger, `5` link (requires `url`).

### Classic embed

```json
{
  "type": "embed",
  "title": "Welcome {user.name}!",
  "description": "Welcome {user} to **{guild}**! We're now at {member_count} members.",
  "color": "#5865F2",
  "image": "https://example.com/banner.png",
  "footer": "Glad to have you here.",
  "fields": [{ "name": "Rules", "value": "Check #rules.", "inline": true }],
  "button": { "label": "Rules", "style": 5, "url": "https://example.com/rules" }
}
```

If `"type"` is omitted, the format is auto-detected: presence of `"blocks"`
means layout, otherwise embed.

## Placeholders

Usable inside any `text` / `content` / `title` / `description` string:

| Placeholder      | Value                                  |
|-------------------|-----------------------------------------|
| `{user}`          | mention, e.g. `<@123456789>`            |
| `{user.name}`     | display name / nickname                 |
| `{user.tag}`      | username                                |
| `{user.id}`       | raw user ID                             |
| `{user.avatar}`   | avatar URL                              |
| `{guild}`         | server name                             |
| `{guild.id}`      | server ID                               |
| `{member_count}`  | current member count                    |

## Validation

The JSON is validated at `welcomebot(...)` construction time (not on first
join), so config mistakes fail fast with a clear `SchemaError` message.

## Examples

See `examples/welcome.json`, `examples/welcome_embed.json`, and
`examples/bot.py` for a full runnable bot.

## License

MIT
