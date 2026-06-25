# SIN Office Cog

A Red-DiscordBot cog for automated daily SIN Corporation office announcements.

## Features

- Daily automatic SIN Corp office bulletin
- Random posting time between configurable hours
- Pretty Discord embeds
- Random lore incident reports
- Positive CEO reminders
- Optional Dweller Quote from one chosen public channel
- Quote filtering to ignore commands, links, bots, short messages, and overly long messages
- Prefix commands and slash commands

## Install

```text
[p]repo add sinoffice-cog https://github.com/PoutyJinx/sinoffice-cog
[p]cog install sinoffice-cog sinoffice
[p]load sinoffice
```

If you already added the repo:

```text
[p]repo update sinoffice-cog
[p]cog install sinoffice-cog sinoffice
[p]reload sinoffice
```

## Slash Commands

After loading or updating the cog, sync slash commands:

```text
[p]slash sync
```

If your Red version uses guild sync:

```text
[p]slash sync guild
```

Discord can take a few minutes to show new slash commands.

## Setup

Prefix commands:

```text
[p]sinoffice setpostchannel #announcements
[p]sinoffice setquotechannel #general
[p]sinoffice time 10 13
[p]sinoffice chatquotes true
[p]sinoffice toggle true
[p]sinoffice test
```

Slash commands:

```text
/sinoffice setpostchannel
/sinoffice setquotechannel
/sinoffice time
/sinoffice chatquotes
/sinoffice toggle
/sinoffice test
/sinoffice status
/sinoffice clearquotes
```

## Notes

Dweller Quotes are only collected from the channel set with `setquotechannel`. This prevents private or mod-only channels from being used.
