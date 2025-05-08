# test_password.py
import pytest
from jwt_auth import verify_password, get_password_hash

def test_password_hashing_and_verification():
    """Test that password hashing and verification work correctly"""
    
    # Test case 1: Normal password
    password = "test_password"
    hashed_password = get_password_hash(password)
    
    # Verify the password hash is different from the original password
    assert password != hashed_password
    
    # Verify the correct password matches the hash
    assert verify_password(password, hashed_password) == True
    
    # Verify wrong password doesn't match
    assert verify_password("wrong_password", hashed_password) == False
    
    # Test case 2: Empty password 
    empty_password = ""
    empty_hashed = get_password_hash(empty_password)
    
    # Verify empty password works with verification
    assert verify_password(empty_password, empty_hashed) == True
    assert verify_password("not_empty", empty_hashed) == False
    
    # Test case 3: Special characters
    special_password = "P@$$w0rd!#*&"
    special_hashed = get_password_hash(special_password)
    
    # Verify password with special characters works
    assert verify_password(special_password, special_hashed) == True
    assert verify_password("regular", special_hashed) == False

# Run the test with: pytest test_password.py -v