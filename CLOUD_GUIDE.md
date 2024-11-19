# Working with Cloud (GitHub) 🌥️

## Basic Cloud Commands

### Save to Cloud
```bash
git add .                    # Get files ready
git commit -m "Message"      # Save changes locally
git cloud                    # Send to Cloud (replaces 'git push')
```

### Get from Cloud
```bash
git pull                     # Download latest changes from Cloud
```

### Undo Changes
```bash
git restore <filename>       # Undo changes in one file
git restore .               # Undo all changes
```

### Branches (Different Versions)
```bash
git checkout -b new-feature  # Create new version to test changes
git checkout main           # Go back to main version
git merge new-feature       # Combine changes if they worked
```

### Check Status
```bash
git status                  # See what's changed
```

Remember:
- Always pull from Cloud before making changes
- Commit often with clear messages
- Cloud keeps your code safe and backed up

Your Cloud repository: https://github.com/Supremeesimon/Octavia_v3
