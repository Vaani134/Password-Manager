from app import create_app, db
from app.models import User, User_passwords

def test_database():
    """Test both User and User_passwords models"""
    print("Testing Database Models...")
    
    app = create_app()
    
    with app.app_context():
        # Test 1: Check if tables are created
        print("\nTest 1: Creating Database Tables")
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return
        
        # Test 2: Create a test user
        print("\n👤 Test 2: Creating Test User")
        try:
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='dsasd',
                Salted_masterkey='afdfsfgdffad'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully!")
            print(f"   User ID: {test_user.id}")
            print(f"   Username: {test_user.username}")
            print(f"   Created: {test_user.create_time}")
        except Exception as e:
            print(f"Error creating user: {e}")
            return
        
        # Test 3: Create password entries for the user
        print("\nTest 3: Creating Password Entries")
        try:
            # Gmail password entry
            gmail_entry = User_passwords(
                user_id=test_user.id,
                encrypted_password='ashdg,jhsgjh',
                website_name='Gmail',
                website_url='https://gmail.com',
                username='testuser@gmail.com',
                notes='Personal email account'
            )
            
            # Facebook password entry
            facebook_entry = User_passwords(
                user_id=test_user.id,
                encrypted_password='dsgkajsdjhgs',
                website_name='Facebook',
                website_url='https://facebook.com',
                username='testuser.facebook',
                notes='Social media account'
            )
            
            db.session.add(gmail_entry)
            db.session.add(facebook_entry)
            db.session.commit()
            
            print("Password entries created successfully!")
            print(f"   Gmail entry ID: {gmail_entry.id}")
            print(f"   Facebook entry ID: {facebook_entry.id}")
        except Exception as e:
            print(f"Error creating password entries: {e}")
            return
        
        # Test 4: Test Relationship - Get all passwords for user
        print("\nTest 4: Testing User-Password Relationship")
        try:
            user = User.query.filter_by(username='testuser').first()
            user_passwords = user.passwords
            
            print(f"Found {len(user_passwords)} passwords for user '{user.username}':")
            for pwd in user_passwords:
                print(f"   - {pwd.website_name}: {pwd.username}")
        except Exception as e:
            print(f"Error testing relationship: {e}")
        
        # Test 5: Test Backref - Get user from password entry
        print("\nTest 5: Testing Password-User Backref")
        try:
            password = User_passwords.query.filter_by(website_name='Gmail').first()
            owner = password.owner
            
            print(f"Gmail password belongs to user: {owner.username}")
        except Exception as e:
            print(f"Error testing backref: {e}")
        
        # Test 6: Query tests
        print("\nTest 6: Advanced Queries")
        try:
            # Count total users
            user_count = User.query.count()
            print(f"Total users: {user_count}")
            
            # Count total password entries
            password_count = User_passwords.query.count()
            print(f"Total password entries: {password_count}")
            
            # Find passwords by website
            gmail_passwords = User_passwords.query.filter_by(website_name='Gmail').all()
            print(f"Gmail passwords found: {len(gmail_passwords)}")
        except Exception as e:
            print(f"Error in queries: {e}")
        
        # Test 7: Cleanup
        print("\nTest 7: Cleanup")
        try:
            # Delete password entries first (due to foreign key)
            User_passwords.query.delete()
            User.query.delete()
            db.session.commit()
            print("All test data cleaned up!")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    print("\nAll database tests completed!")

if __name__ == "__main__":
    test_database()