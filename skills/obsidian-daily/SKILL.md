# Obsidian Daily Notes

Interact with Obsidian Daily Notes: create notes, append entries, read by date, and search content.

## Setup

Check if a default vault is configured:

```bash
obsidian-cli print-default --path-only 2>/dev/null && echo "OK" || echo "NOT_SET"
```

If NOT_SET, configure the vault:
```bash
obsidian-cli set-default "VAULT_NAME"
```

## Date Handling

Get current date:
```bash
date +%Y-%m-%d
```

Cross-platform relative dates:
```bash
Today        date +%Y-%m-%d
Yesterday    date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d
Last Friday  date -d "last friday" +%Y-%m-%d
3 days ago   date -d "3 days ago" +%Y-%m-%d
Next Monday  date -d "next monday" +%Y-%m-%d
```

## Commands

### Open/Create Today's Note

```bash
obsidian-cli daily
```

### Append Entry

```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' 'ENTRY_TEXT')" --append
```

### Read Note

```bash
# Today
obsidian-cli print "$(date +%Y-%m-%d).md"

# Specific date
obsidian-cli print "2025-01-10.md"

# Yesterday
obsidian-cli print "$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d).md"
```

### Search Content

```bash
obsidian-cli search-content "TERM"
```

## Use Cases

Journal entry:
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' '- Went to the doctor')" --append
```

Task:
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' '- [ ] Buy groceries')" --append
```

Timestamped log:
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' '- $(date +%H:%M) This is a log line')" --append
```

---

*Note: This skill works with Obsidian CLI (v1.12+). Configure vault path first.*
