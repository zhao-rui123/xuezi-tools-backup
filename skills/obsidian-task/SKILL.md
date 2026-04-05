# Obsidian Task

Manage Obsidian tasks via obsidian-cli. List, toggle, create, and update tasks from the terminal.

## Commands

### List Tasks

```bash
# List all tasks
obsidian-cli tasks list

# List tasks in specific file
obsidian-cli tasks list "Daily Notes/2025-01-10.md"
```

### Toggle Task

```bash
# Toggle task status (done/undone)
obsidian-cli tasks toggle "Daily Notes/2025-01-10.md" --task "Buy groceries"
```

### Create Task

```bash
# Create new task
obsidian-cli create "Daily Notes/2025-01-10.md" --content "$(printf '\n%s' '- [ ] New task')" --append
```

### Update Task

```bash
# Add due date, tags, etc.
obsidian-cli tasks update "Daily Notes/2025-01-10.md" --task "Buy groceries" --due "2025-01-15"
```

## Task Format

Obsidian tasks use checkbox syntax:
- `[ ]` - Uncompleted task
- `[x]` - Completed task

## Examples

Create a task:
```bash
obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' '- [ ] Review quarterly report')" --append
```

Complete a task:
```bash
obsidian-cli tasks toggle "$(date +%Y-%m-%d).md" --task "Review quarterly report"
```

---

*Note: Requires Obsidian CLI (v1.12+) and Obsidian Tasks plugin.*
