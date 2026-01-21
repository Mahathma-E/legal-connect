import bcrypt

# Test the test user password
test_password = "password123"
stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8HqHqGq"

print("Testing password verification...")
print(f"Test password: {test_password}")
print(f"Stored hash: {stored_hash}")

# Test bcrypt verification
try:
    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
    print(f"Password verification result: {is_valid}")
    
    if is_valid:
        print("✅ Password verification successful!")
    else:
        print("❌ Password verification failed!")
        
except Exception as e:
    print(f"❌ Error during password verification: {e}")

# Test creating a new hash
print("\nTesting hash creation...")
try:
    new_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"New hash created: {new_hash}")
    
    # Verify the new hash
    is_new_valid = bcrypt.checkpw(test_password.encode('utf-8'), new_hash.encode('utf-8'))
    print(f"New hash verification: {is_new_valid}")
    
except Exception as e:
    print(f"❌ Error during hash creation: {e}")
