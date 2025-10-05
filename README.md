# Claude Code Account Switcher for Windows

## Features

- Add current Claude Code account to managed accounts
- List all managed accounts
- Switch between accounts
- Remove accounts

## Installation

### For users with Python installed:

1. Clone or download this repository
2. Ensure Python 3.6+ is installed on your system
3. No additional dependencies required (uses only built-in Python modules)

### For users without Python (using executable):

1. Clone or download this repository
2. Run the setup script to install the executable:
   - Double-click `setup.bat` or run from command line
   - The executable will be copied to `%USERPROFILE%\claude-switcher`
3. Add the installation directory to your system PATH to run from anywhere:
   - Run `setup.bat` and follow the instructions to add to PATH permanently
   - Or run from the installation directory directly

## Usage

### With Python:
```bash
python ccswitch.py [options]
```

### With Executable (after installation):
```bash
ccswitch [options]
```

### Available Options

- `--list`: List all managed accounts
- `--add-account`: Add current Claude Code account to managed accounts
- `--switch`: Switch to next account in sequence
- `--switch-to NUM|EMAIL`: Switch to specific account by number or email
- `--remove-account NUM|EMAIL`: Remove account by number or email

### Examples

```bash
# List all accounts
ccswitch --list

# Add current Claude Code account
ccswitch --add-account

# Switch to next account
ccswitch --switch

# Switch to account #2
ccswitch --switch-to 2

# Switch to account by email
ccswitch --switch-to user@example.com

# Remove account #2
ccswitch --remove-account 2
```

## Data Storage

The application stores data in the following locations:

- `%USERPROFILE%\.claude-switch-backup\sequence.json`: Main account sequence data
- `%USERPROFILE%\.claude-switch-backup\configs\`: Account configuration files
- `%USERPROFILE%\.claude-switch-backup\credentials\`: Account credential files
- `%USERPROFILE%\.claude.json`: Claude Code's main configuration file

## Security Note

Credentials are **not** encryped or altered, simply copied.
