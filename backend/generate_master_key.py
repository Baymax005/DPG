"""
Generate Master Encryption Key
Run this ONCE to generate a secure master key for wallet encryption
"""
import secrets
import base64
import os
from pathlib import Path


def generate_master_key() -> str:
    """Generate a cryptographically secure 32-byte master key"""
    key = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(key).decode()


def update_env_file(master_key: str):
    """Update .env file with new master key"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"❌ .env file not found at {env_path}")
        return False
    
    # Read current .env content
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update or add WALLET_MASTER_KEY
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('WALLET_MASTER_KEY='):
            lines[i] = f'WALLET_MASTER_KEY={master_key}\n'
            updated = True
            break
    
    if not updated:
        # Add to end of file
        if lines and not lines[-1].endswith('\n'):
            lines.append('\n')
        lines.append(f'\n# Master encryption key for wallet private keys\n')
        lines.append(f'WALLET_MASTER_KEY={master_key}\n')
    
    # Write back to .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True


def main():
    """Main function"""
    print("=" * 70)
    print("🔐 DPG Master Encryption Key Generator")
    print("=" * 70)
    print()
    
    # Check if master key already exists
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'WALLET_MASTER_KEY=' in content:
                for line in content.split('\n'):
                    if line.startswith('WALLET_MASTER_KEY=') and len(line.strip()) > len('WALLET_MASTER_KEY='):
                        print("⚠️  WARNING: WALLET_MASTER_KEY already exists in .env!")
                        print()
                        print("🔴 IMPORTANT: Changing the master key will make ALL existing")
                        print("   encrypted wallets UNRECOVERABLE!")
                        print()
                        response = input("Continue and generate NEW master key? (yes/no): ").lower().strip()
                        
                        if response != 'yes':
                            print("\n✅ Operation cancelled. Existing key preserved.")
                            return
                        
                        print("\n⚠️  Generating NEW master key...")
                        print("⚠️  All existing wallets will need to be re-imported!")
                        print()
                        break
    
    # Generate master key
    master_key = generate_master_key()
    
    print("✅ Master key generated successfully!")
    print()
    print("🔑 Your master key:")
    print("-" * 70)
    print(master_key)
    print("-" * 70)
    print()
    
    # Try to update .env automatically
    print("📝 Updating backend/.env file...")
    if update_env_file(master_key):
        print("✅ .env file updated successfully!")
        print()
        print("🎉 Setup complete!")
        print()
        print("📋 Next steps:")
        print("1. ✅ Master key saved to backend/.env")
        print("2. 🔄 Restart your backend server")
        print("3. 💾 BACKUP this key in a secure location (password manager)")
        print("4. 🚫 Never commit .env to Git")
        print()
        print("⚠️  CRITICAL: If you lose this key, encrypted wallets CANNOT be recovered!")
        print()
    else:
        print("⚠️  Could not automatically update .env")
        print()
        print("📋 Manual steps:")
        print("1. Open backend/.env")
        print("2. Add this line:")
        print(f"   WALLET_MASTER_KEY={master_key}")
        print("3. Save and restart backend")
        print()
    
    # Security reminders
    print("=" * 70)
    print("🔒 SECURITY BEST PRACTICES")
    print("=" * 70)
    print("✓ Store master key in password manager (1Password, LastPass, etc.)")
    print("✓ Make encrypted backup of .env file")
    print("✓ Never share master key with anyone")
    print("✓ Never commit .env to version control")
    print("✓ Rotate key periodically in production")
    print("✓ Use different keys for dev/staging/production")
    print()
    print("📚 For key rotation: python backend/rotate_master_key.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
