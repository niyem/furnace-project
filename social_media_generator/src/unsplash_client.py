"""
Unsplash API client for fetching background images
"""
import requests
import os
from typing import Optional
from pathlib import Path
import random


class UnsplashClient:
    """Client for interacting with Unsplash API"""

    def __init__(self, access_key: Optional[str] = None):
        """
        Initialize Unsplash client

        Args:
            access_key: Unsplash API access key (or set UNSPLASH_ACCESS_KEY env var)
        """
        self.access_key = access_key or os.getenv('UNSPLASH_ACCESS_KEY')
        self.base_url = "https://api.unsplash.com"

    def fetch_random_image(
        self,
        query: str = "university graduation",
        orientation: str = "landscape",
        save_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Fetch a random image from Unsplash

        Args:
            query: Search query for images
            orientation: Image orientation (landscape, portrait, squarish)
            save_path: Path to save the image (optional)

        Returns:
            Path to saved image or None if API key not available
        """
        if not self.access_key:
            print("⚠️  No Unsplash API key found. Using fallback gradient background.")
            print("   To use Unsplash images, set UNSPLASH_ACCESS_KEY environment variable.")
            return None

        try:
            # Fetch random image
            url = f"{self.base_url}/photos/random"
            params = {
                'query': query,
                'orientation': orientation,
                'content_filter': 'high'
            }
            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                image_url = data['urls']['regular']
                photographer = data['user']['name']
                photo_link = data['links']['html']

                # Download image
                if save_path:
                    img_response = requests.get(image_url, timeout=10)
                    if img_response.status_code == 200:
                        with open(save_path, 'wb') as f:
                            f.write(img_response.content)

                        print(f"✅ Image downloaded from Unsplash")
                        print(f"   Photo by {photographer}")
                        print(f"   {photo_link}")

                        return str(save_path)
            else:
                print(f"⚠️  Unsplash API returned status {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error fetching image from Unsplash: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")
            return None

    def get_fallback_keywords(self) -> list:
        """Get list of fallback keywords for image search"""
        return [
            "university campus",
            "graduation ceremony",
            "student success",
            "education achievement",
            "academic success",
            "university building",
            "study abroad",
            "college graduation"
        ]
