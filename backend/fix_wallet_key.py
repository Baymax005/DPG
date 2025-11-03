"""
Wallet Encryption Key Manager
Fixes wallet decryption issues by setting a permanent encryption key
"""
import os
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet

load_dotenv()

print("\n" + "="*70)
print("🔐 DPG Wallet Encryption Key Manager")
print("="*70 + "\n")

env_file = os.path.join(os.path.dirname(__file__), '.env')

# Check current key
current_key = os.getenv("WALLET_ENCRYPTION_KEY")

if current_key:
    print(f"✅ Current key in .env: {current_key[:20]}...")
    print("\nYour encryption key is already set!")
    print("\n⚠️  IMPORTANT: Keep this key safe!")
    print("If you lose it, you cannot decrypt existing wallets.")
else:
    print("❌ No WALLET_ENCRYPTION_KEY found in .env\n")
    print("Options:")
    print("1. Generate a new key (will need to re-import all wallets)")
    print("2. Use the temporary key from backend startup logs")
    print("3. Cancel\n")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        # Generate new key
        new_key = Fernet.generate_key().decode()
        print(f"\n✅ Generated new key: {new_key}\n")
        
        # Add to .env
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            if 'WALLET_ENCRYPTION_KEY=' in content:
                # Replace empty key
                content = content.replace('WALLET_ENCRYPTION_KEY=', f'WALLET_ENCRYPTION_KEY={new_key}')
            else:
                # Add new key
                content += f"\nWALLET_ENCRYPTION_KEY={new_key}\n"
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Added to backend/.env file!")
            print("\n📝 Next steps:")
            print("1. Restart your backend: python main.py")
            print("2. Delete old wallets (they can't be decrypted)")
            print("3. Re-import your wallets with the new key")
            print("4. Your new wallets will use this permanent key\n")
            
        except Exception as e:
            print(f"❌ Error updating .env: {e}")
            print(f"\n📝 Manually add this to backend/.env:")
            print(f"WALLET_ENCRYPTION_KEY={new_key}\n")
    
    elif choice == "2":
        print("\n📋 Copy the temporary key from backend startup logs")
        print("It looks like this:")
        print("⚠️  Using temporary key: abcd1234...")
        print("\nThe full key will be displayed in the console.\n")
        
        temp_key = input("Paste the full key here: ").strip()
        
        if temp_key and len(temp_key) > 20:
            try:
                # Validate it's a valid Fernet key
                Fernet(temp_key.encode())
                
                # Add to .env
                with open(env_file, 'r') as f:
                    content = f.read()
                
                if 'WALLET_ENCRYPTION_KEY=' in content:
                    content = content.replace('WALLET_ENCRYPTION_KEY=', f'WALLET_ENCRYPTION_KEY={temp_key}')
                else:
                    content += f"\nWALLET_ENCRYPTION_KEY={temp_key}\n"
                
                with open(env_file, 'w') as f:
                    f.write(content)
                
                print("\n✅ Key saved to backend/.env!")
                print("\n📝 Next steps:")
                print("1. Restart your backend: python main.py")
                print("2. Your existing wallets should now decrypt correctly!\n")
                
            except Exception as e:
                print(f"❌ Invalid key format: {e}\n")
        else:
            print("❌ Invalid key (too short)\n")
    
    else:
        print("\n❌ Cancelled\n")

print("="*70)
print("Done!")
print("="*70 + "\n")
