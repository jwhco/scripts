# Quality Automation for Markdown Tasks

## Purpose 

- Find non-standard markdown tasks, fix them or highlight for user.

## Automation

- Find non-standard spacing. Look for Regex `-\t\[ \]` OR `-\s+\[\t\]` OR `- \[ \]\t` then replace with `- [ ] `, making standard format `- [ ] Description.`
- Clean up odd spacing, okay to be done with multiple passes. Regex `-\s{2}\[ \]\s` OR `- \[ \]\s{2}` would become `- [ ] ` on replacement

/EOF/