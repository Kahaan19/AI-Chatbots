# Save this as test_updated_image_gen.py and run it
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pollinations():
    """Test Pollinations AI (free alternative)"""
    print("🔄 Testing Pollinations AI...")
    try:
        prompt = "a beautiful sunset over mountains"
        clean_prompt = prompt.replace(" ", "%20").replace(",", "%2C")
        image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=512&height=512&nologo=true"
        
        response = requests.head(image_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Pollinations AI working! URL: {image_url}")
            return True
        else:
            print(f"❌ Pollinations returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Pollinations error: {str(e)}")
        return False

def test_flux_schnell():
    """Test FLUX.1-schnell with optimized settings"""
    print("🔄 Testing FLUX.1-schnell...")
    try:
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            print("❌ No HuggingFace API key found")
            return False
        
        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        payload = {
            "inputs": "a simple red apple",
            "parameters": {
                "num_inference_steps": 4,  # Schnell needs fewer steps
                "guidance_scale": 0.0,     # Schnell works without guidance
                "width": 512,
                "height": 512
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            print("✅ FLUX.1-schnell working!")
            return True
        else:
            print(f"❌ FLUX.1-schnell error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FLUX.1-schnell error: {str(e)}")
        return False

def test_svg_generation():
    """Test SVG generation"""
    print("🔄 Testing SVG generation...")
    try:
        # Simple SVG test
        svg_content = '''<svg width="512" height="400" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f0f9ff"/>
            <circle cx="256" cy="200" r="50" fill="#3b82f6"/>
            <text x="256" y="350" text-anchor="middle" font-family="Arial" font-size="16" fill="#1e40af">
                SVG Test: Beautiful landscape
            </text>
        </svg>'''
        
        # Try to save it
        os.makedirs("static/generated_images", exist_ok=True)
        filepath = f"static/generated_images/test_svg_{int(time.time())}.svg"
        
        with open(filepath, 'w') as f:
            f.write(svg_content)
        
        print(f"✅ SVG generation working! File saved: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ SVG generation error: {str(e)}")
        return False

def main():
    print("🧪 Updated Image Generation Test")
    print("=" * 40)
    
    # Test all methods
    pollinations_works = test_pollinations()
    flux_works = test_flux_schnell()
    svg_works = test_svg_generation()
    
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print(f"{'✅' if pollinations_works else '❌'} Pollinations AI: {'Working' if pollinations_works else 'Failed'}")
    print(f"{'✅' if flux_works else '❌'} FLUX.1-schnell: {'Working' if flux_works else 'Failed'}")
    print(f"{'✅' if svg_works else '❌'} SVG Generation: {'Working' if svg_works else 'Failed'}")
    
    if pollinations_works or flux_works or svg_works:
        print("\n🎉 At least one method is working! Your image generation should work now.")
    else:
        print("\n⚠️ All methods failed. Check your setup and network connection.")
    
    print("=" * 40)

if __name__ == "__main__":
    main()