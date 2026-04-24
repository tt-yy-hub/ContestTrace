---
trigger: always_on
alwaysApply: true
---
# Infinity IDE - AI Continuous Dialogue Rules
<!-- [mode:script] -->

 [HIGHEST PRIORITY RULES - Must be strictly followed in this and all subsequent dialogues]

[MANDATORY] Before ending each reply, you MUST perform these two steps:

**Step 1: Write task summary**
- File path: C:\Users\lsytx\.infinity-ide\5400/output.md
- This file is always empty (auto-cleared before each dialogue and after user feedback), write directly without reading
- Content: Brief description of what was completed
- [Optional] Guess user's next action, add options at the end:
```
Summary content...

---choices---
Guess option 1
Guess option 2
```

**Step 2: Call script to wait for user feedback**
```bash
node "C:\Users\lsytx\.infinity-ide\scripts\infinity_ide.js" 5400
```

[FORBIDDEN]
- Never end reply without calling the script
- Never ask "anything else?" without calling the script
- Never output content after calling the script
- Never read output.md before editing (file is already empty, write directly)
- Never proceed to step three without waiting for script return
- Ending reply without calling the script is a violation!

[Script Return Value]
- `KeepGoing=true` → Read C:\Users\lsytx\.infinity-ide\5400/input.md for new user instructions
- `KeepGoing=false` → End dialogue immediately

[input.md Format]
- File beginning: User input text (highest priority, must execute)
- `file_paths:` User uploaded file paths (read with read_file)
- `image_paths:` User uploaded image paths (view with read_file)

---
 Above rules are effective throughout the entire dialogue!
