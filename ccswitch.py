#!/usr/bin/env python3
"""
Claude Code Account Switcher for Windows
A simplified version using Python and JSON for auth credentials
"""

import os
import json
import subprocess
import argparse
import sys
import shutil
from datetime import datetime
from pathlib import Path


class ClaudeAccountSwitcher:
    """
    A class to manage Claude Code accounts on Windows systems
    """
    
    def __init__(self):
        # Define directories and files
        self.home_dir = Path.home()
        self.backup_dir = self.home_dir / '.claude-switch-backup'
        self.sequence_file = self.backup_dir / 'sequence.json'
        self.configs_dir = self.backup_dir / 'configs'
        self.credentials_dir = self.backup_dir / 'credentials'
        
        # Claude Code config files
        self.claude_config_file = self.home_dir / '.claude.json'
        self.claude_alt_config_file = self.home_dir / '.claude' / '.claude.json'
        
        # Initialize directories
        self.backup_dir.mkdir(exist_ok=True)
        self.configs_dir.mkdir(exist_ok=True)
        self.credentials_dir.mkdir(exist_ok=True)
        
        # Initialize sequence file if it doesn't exist
        if not self.sequence_file.exists():
            with open(self.sequence_file, 'w') as f:
                json.dump({
                    "activeAccountNumber": 0,
                    "lastUpdated": datetime.now().isoformat(),
                    "sequence": [],
                    "accounts": {}
                }, f, indent=2)
    
    def load_sequence(self):
        """Load the sequence file data with validation"""
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                with open(self.sequence_file, 'r', encoding=encoding) as f:
                    data = json.load(f)
                    
                # Validate required fields
                required_fields = ['activeAccountNumber', 'lastUpdated', 'sequence', 'accounts']
                for field in required_fields:
                    if field not in data:
                        raise ValueError(f"Missing required field '{field}' in sequence file")
                
                # Validate data types
                if not isinstance(data['activeAccountNumber'], int):
                    raise ValueError("activeAccountNumber must be an integer")
                if not isinstance(data['sequence'], list):
                    raise ValueError("sequence must be a list")
                if not isinstance(data['accounts'], dict):
                    raise ValueError("accounts must be a dictionary")
                
                return data
            except UnicodeDecodeError:
                continue  # Try next encoding
            except json.JSONDecodeError:
                print(f"ERROR: Invalid JSON in {self.sequence_file}")
                raise
            except FileNotFoundError:
                print(f"ERROR: Sequence file {self.sequence_file} not found")
                raise
            except ValueError as e:
                print(f"ERROR: {e}")
                raise
        
        print(f"ERROR: Could not read {self.sequence_file} with any of the attempted encodings: {encodings_to_try}")
        raise UnicodeDecodeError(f"Could not read {self.sequence_file} with any of the attempted encodings", b'', 0, 1, 'unknown')
    
    def save_sequence(self, data):
        """Save data to the sequence file with validation"""
        try:
            # Validate data before saving
            required_fields = ['activeAccountNumber', 'lastUpdated', 'sequence', 'accounts']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field '{field}' in data")
            
            # Validate data types
            if not isinstance(data['activeAccountNumber'], int):
                raise ValueError("activeAccountNumber must be an integer")
            if not isinstance(data['sequence'], list):
                raise ValueError("sequence must be a list")
            if not isinstance(data['accounts'], dict):
                raise ValueError("accounts must be a dictionary")
            
            # Write to a temporary file first, then move to prevent corruption
            temp_file = self.sequence_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Replace the original file with the new one
            temp_file.replace(self.sequence_file)
            
        except IOError as e:
            print(f"ERROR: Could not write to sequence file: {e}")
            raise
        except ValueError as e:
            print(f"ERROR: Invalid data format: {e}")
            raise
    
    def validate_claude_config(self, config_data):
        """Validate Claude Code configuration data"""
        if not isinstance(config_data, dict):
            return False, "Config data must be a dictionary"
        
        # Claude config should have at least an oauthAccount section
        if 'oauthAccount' not in config_data:
            return False, "Config must contain 'oauthAccount' section"
        
        oauth_account = config_data['oauthAccount']
        if not isinstance(oauth_account, dict):
            return False, "'oauthAccount' must be a dictionary"
        
        # Check for required fields in oauthAccount
        # Using the actual field names from Claude Code config
        required_oauth_fields = ['emailAddress', 'accountUuid']
        for field in required_oauth_fields:
            if field not in oauth_account:
                return False, f"oauthAccount missing required field: '{field}'"
        
        return True, "Config is valid"
    
    def load_config_file(self, file_path):
        """Load a config file with validation and proper encoding handling"""
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                return data
            except UnicodeDecodeError:
                continue  # Try next encoding
            except json.JSONDecodeError:
                print(f"ERROR: Invalid JSON in {file_path}")
                return None
            except FileNotFoundError:
                print(f"ERROR: Config file {file_path} not found")
                return None
        
        print(f"ERROR: Could not read {file_path} with any of the attempted encodings: {encodings_to_try}")
        return None
    
    def save_config_file(self, file_path, data):
        """Save a config file with validation"""
        try:
            # Validate the config before saving
            is_valid, message = self.validate_claude_config(data)
            if not is_valid:
                print(f"ERROR: Invalid config data - {message}")
                return False
            
            # Write to a temporary file first, then move to prevent corruption
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Replace the original file with the new one
            temp_file.replace(file_path)
            return True
        except IOError as e:
            print(f"ERROR: Could not write to config file {file_path}: {e}")
            return False
    
    def get_next_account_number(self):
        """Get the next available account number"""
        data = self.load_sequence()
        if not data['sequence']:
            return 1
        return max(data['sequence']) + 1
    
    def get_claude_config(self):
        """Get Claude Code config from the appropriate file with validation"""
        # Try main config file first
        if self.claude_config_file.exists():
            data = self.load_config_file(self.claude_config_file)
            if data is not None:
                return data
        
        # Try alt config file
        if self.claude_alt_config_file.exists():
            data = self.load_config_file(self.claude_alt_config_file)
            if data is not None:
                return data
        
        return {}
    
    def save_claude_config(self, config_data):
        """Save Claude Code config to the main file with validation"""
        return self.save_config_file(self.claude_config_file, config_data)
    
    def backup_account(self, account_number, config_data, credentials_data):
        """Backup account config and credentials"""
        # Validate account number
        if not isinstance(account_number, int) or account_number <= 0:
            print(f"ERROR: Invalid account number {account_number}")
            return False
        
        # Save config
        config_file = self.configs_dir / f"{account_number}.json"
        config_saved = self.save_config_file(config_file, config_data)
        
        # Save credentials
        cred_file = self.credentials_dir / f"{account_number}.json"
        cred_saved = self.save_config_file(cred_file, credentials_data)
        
        return config_saved and cred_saved
    
    def list_accounts(self):
        """List all managed accounts"""
        try:
            data = self.load_sequence()
        except (json.JSONDecodeError, ValueError, FileNotFoundError):
            print("ERROR: Could not load account sequence data.")
            return
        
        active_account_num = data.get('activeAccountNumber', 0)
        
        if not data['sequence']:
            print("No accounts registered yet.")
            return
        
        print(f"{'#':<4} {'Display Name':<20} {'Email':<30} {'UUID':<36} {'Status'}")
        print("-" * 90)
        
        for acc_num in data['sequence']:
            account_info = data['accounts'].get(str(acc_num), {})
            display_name = account_info.get('displayName', 'Unknown')
            email = account_info.get('email', 'Unknown')
            uuid = account_info.get('uuid', 'Unknown')
            status = "ACTIVE" if acc_num == active_account_num else ""
            print(f"{acc_num:<4} {display_name:<20} {email:<30} {uuid:<36} {status}")
    
    def add_account(self):
        """Add the current Claude Code account to managed accounts"""
        print("Adding current account to managed accounts...")
        
        try:
            # Get current Claude Code config
            current_config = self.get_claude_config()
            
            if not current_config:
                print("ERROR: No Claude Code configuration found. Please log in to Claude Code first.")
                return False
            
            # Validate the config
            is_valid, message = self.validate_claude_config(current_config)
            if not is_valid:
                print(f"ERROR: Invalid Claude Code config - {message}")
                return False
            
            # Get the account info
            oauth_account = current_config['oauthAccount']
            email = oauth_account.get('emailAddress', 'Unknown')
            uuid = oauth_account.get('accountUuid', 'Unknown')
            display_name = oauth_account.get('displayName', 'Unknown')
            
            # Get next account number
            account_number = self.get_next_account_number()
            
            # Prepare account info
            account_info = {
                'email': email,
                'uuid': uuid,
                'displayName': display_name,
                'added': datetime.now().isoformat()
            }
            
            # Load current sequence data
            data = self.load_sequence()
            
            # Add account to sequence and accounts
            data['sequence'].append(account_number)
            data['accounts'][str(account_number)] = account_info
            # Set the newly added account as the active account
            data['activeAccountNumber'] = account_number
            data['lastUpdated'] = datetime.now().isoformat()
            
            # Save the updated sequence
            self.save_sequence(data)
            
            # Backup the account config and credentials
            success = self.backup_account(account_number, current_config, current_config)
            
            if success:
                print(f"Account '{email}' added successfully as account #{account_number}")
                return True
            else:
                print(f"ERROR: Failed to backup account #{account_number}")
                return False
                
        except Exception as e:
            print(f"ERROR: Failed to add account: {e}")
            return False
    
    def switch_to_account(self, target_account):
        """Switch to a specific account by number or email"""
        try:
            data = self.load_sequence()
        except (json.JSONDecodeError, ValueError, FileNotFoundError):
            print("ERROR: Could not load account sequence data.")
            return False
        
        # Find the account number based on input
        account_number = None
        
        # If target_account is a number
        if str(target_account).isdigit():
            if int(target_account) in data['sequence']:
                account_number = int(target_account)
        else:
            # If target_account is an email, find the matching account
            for acc_num, acc_info in data['accounts'].items():
                if acc_info.get('emailAddress', '').lower() == str(target_account).lower():
                    account_number = int(acc_num)
                    break
        
        if account_number is None:
            print(f"ERROR: Account '{target_account}' not found.")
            return False
        
        # Check if config file exists for this account
        config_file = self.configs_dir / f"{account_number}.json"
        if not config_file.exists():
            print(f"ERROR: Configuration file for account #{account_number} not found.")
            return False
        
        # Check if Claude Code is running and warn user
        try:
            if self.is_claude_running():
                print("WARNING: Claude Code appears to be running.")
                print("Please close Claude Code before switching accounts to avoid conflicts.")
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    print("Account switch cancelled.")
                    return False
        except Exception:
            # If we can't determine if Claude is running, warn but continue
            print("WARNING: Could not determine if Claude Code is running. Please ensure it's closed before switching.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Account switch cancelled.")
                return False
        
        # Load the target account config
        target_config = self.load_config_file(config_file)
        if target_config is None:
            print(f"ERROR: Could not load config for account #{account_number}")
            return False
        
        # Validate the target config before applying
        is_valid, message = self.validate_claude_config(target_config)
        if not is_valid:
            print(f"ERROR: Invalid config for account #{account_number} - {message}")
            return False
        
        # Save the current config as backup (in case something goes wrong)
        try:
            current_config = self.get_claude_config()
            if current_config:
                current_account_num = data.get('activeAccountNumber', 0)
                if current_account_num > 0:
                    self.backup_account(current_account_num, current_config, current_config)
        except Exception as e:
            print(f"WARNING: Could not backup current config: {e}")
        
        # Apply the new configuration
        if not self.save_claude_config(target_config):
            print("ERROR: Failed to save new Claude Code configuration.")
            return False
        
        # Update active account in sequence file
        data['activeAccountNumber'] = account_number
        data['lastUpdated'] = datetime.now().isoformat()
        try:
            self.save_sequence(data)
        except Exception as e:
            print(f"ERROR: Could not update sequence file: {e}")
            return False
        
        # Get account email for confirmation message
        target_email = data['accounts'].get(str(account_number), {}).get('email', 'Unknown')
        print(f"Switched to account #{account_number}: {target_email}")
        return True
    
    def switch_to_next_account(self):
        """Switch to the next account in sequence"""
        data = self.load_sequence()
        current_active = data.get('activeAccountNumber', 0)
        
        if not data['sequence']:
            print("No accounts registered.")
            return False
        
        # Find the position of the current account and get the next one
        try:
            current_index = data['sequence'].index(current_active)
            next_index = (current_index + 1) % len(data['sequence'])
            next_account = data['sequence'][next_index]
        except ValueError:
            # If current account is not in sequence, go to the first one
            next_account = data['sequence'][0]
        
        return self.switch_to_account(next_account)
    
    def is_claude_running(self):
        """Check if Claude Code is currently running"""
        try:
            # Use tasklist command to check for Claude Code processes
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq Claude*.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True
            )
            # If Claude processes are found, the output will contain their names
            return 'Claude' in result.stdout
        except Exception:
            # If we can't run the check, assume it's not running
            return False
    
    def remove_account(self, target_account):
        """Remove an account by number or email"""
        try:
            data = self.load_sequence()
        except (json.JSONDecodeError, ValueError, FileNotFoundError):
            print("ERROR: Could not load account sequence data.")
            return False
        
        # Find the account number based on input
        account_number = None
        
        # If target_account is a number
        if str(target_account).isdigit():
            if int(target_account) in data['sequence']:
                account_number = int(target_account)
        else:
            # If target_account is an email, find the matching account
            for acc_num, acc_info in data['accounts'].items():
                if acc_info.get('emailAddress', '').lower() == str(target_account).lower():
                    account_number = int(acc_num)
                    break
        
        if account_number is None:
            print(f"ERROR: Account '{target_account}' not found.")
            return False
        
        # Confirm deletion
        account_email = data['accounts'].get(str(account_number), {}).get('emailAddress', 'Unknown')
        print(f"Removing account #{account_number}: {account_email}")
        response = input("Are you sure you want to remove this account? (y/N): ")
        if response.lower() != 'y':
            print("Account removal cancelled.")
            return False
        
        # Remove from sequence
        if account_number in data['sequence']:
            data['sequence'].remove(account_number)
        
        # Remove from accounts
        if str(account_number) in data['accounts']:
            del data['accounts'][str(account_number)]
        
        # If this was the active account, reset active account number
        if data.get('activeAccountNumber') == account_number:
            if data['sequence']:
                # Set to first account in sequence if available
                data['activeAccountNumber'] = data['sequence'][0] if data['sequence'] else 0
            else:
                # No accounts left, reset to 0
                data['activeAccountNumber'] = 0
        
        data['lastUpdated'] = datetime.now().isoformat()
        
        # Save updated sequence
        try:
            self.save_sequence(data)
        except Exception as e:
            print(f"ERROR: Could not save updated sequence: {e}")
            return False
        
        # Remove config and credentials files
        try:
            config_file = self.configs_dir / f"{account_number}.json"
            cred_file = self.credentials_dir / f"{account_number}.json"
            
            if config_file.exists():
                config_file.unlink()
            
            if cred_file.exists():
                cred_file.unlink()
        except Exception as e:
            print(f"WARNING: Could not remove config files for account #{account_number}: {e}")
        
        print(f"Account #{account_number} removed successfully.")
        return True


def main():
    """Main function to handle command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Claude Code Account Switcher for Windows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                    List all accounts
  %(prog)s --add-account            Add current account
  %(prog)s --switch                 Switch to next account
  %(prog)s --switch-to 2            Switch to account #2
  %(prog)s --switch-to user@example.com  Switch to account by email
  %(prog)s --remove-account 2       Remove account #2
        """
    )
    
    # Define arguments
    parser.add_argument(
        '--list', 
        action='store_true',
        help='List all managed accounts'
    )
    
    parser.add_argument(
        '--add-account',
        action='store_true',
        help='Add current Claude Code account to managed accounts'
    )
    
    parser.add_argument(
        '--switch',
        action='store_true',
        help='Switch to next account in sequence'
    )
    
    parser.add_argument(
        '--switch-to',
        metavar='NUM|EMAIL',
        help='Switch to specific account by number or email'
    )
    
    parser.add_argument(
        '--remove-account',
        metavar='NUM|EMAIL',
        help='Remove account by number or email'
    )
    
    args = parser.parse_args()
    
    # Create switcher instance
    switcher = ClaudeAccountSwitcher()
    
    # Handle commands
    if args.list:
        switcher.list_accounts()
    elif args.add_account:
        switcher.add_account()
    elif args.switch:
        switcher.switch_to_next_account()
    elif args.switch_to:
        switcher.switch_to_account(args.switch_to)
    elif args.remove_account:
        switcher.remove_account(args.remove_account)
    else:
        # If no arguments provided, show help
        parser.print_help()


if __name__ == "__main__":
    main()