"""
Simple test to check if we can access the exercise database.
This helps verify database connectivity before running full AI tests.
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/repple')

print("="*60)
print("🔍 CHECKING DATABASE ACCESS")
print("="*60)
print(f"\nDatabase URL: {DATABASE_URL}")
print("\nTo run this test, you need:")
print("1. SQLAlchemy installed: pip install sqlalchemy psycopg2-binary")
print("2. DATABASE_URL in .env file")
print("3. Database server running")
print("\nDo you have access to the backend database?")
print("If yes, make sure DATABASE_URL is set in .env")
print("If no, we can use the mock database for testing")
