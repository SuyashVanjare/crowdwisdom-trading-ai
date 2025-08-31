import os
import sys

# Fix Windows encoding
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

print("🔧 Direct API Key Setting Test")
print("=" * 40)

# METHOD 1: Set API key directly (REPLACE WITH YOUR REAL KEY)
print("Setting API key directly...")
os.environ['GEMINI_API_KEY'] = 'AIzaSyBrX9Y8Z1234567890abcdefghijklmnopqr'  # PUT YOUR REAL KEY HERE

# Test if it works
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key set to: {api_key}")

if api_key and len(api_key) > 20:
    print("✅ SUCCESS: API key is now accessible!")
    print("🚀 Your project should work now!")
    
    # Test importing your main components
    try:
        print("\nTesting main application import...")
        from main import check_requirements
        if check_requirements():
            print("✅ All requirements satisfied!")
        else:
            print("❌ Requirements check failed")
    except Exception as e:
        print(f"Import error: {e}")
        print("But API key is definitely set!")
        
else:
    print("❌ Please replace the placeholder with your real Gemini API key")

print("\n" + "=" * 40)
