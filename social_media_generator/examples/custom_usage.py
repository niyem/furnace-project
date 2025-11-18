#!/usr/bin/env python3
"""
Example: Using the Social Media Generator Programmatically

This script shows how to use the generator as a Python library
for custom workflows, batch processing, or integration with other tools.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.infographic_generator import InfographicGenerator
from src.content_generator import ContentGenerator
from src.hashtag_manager import HashtagManager
from src.utils import load_templates


def example_1_basic_usage():
    """Example 1: Basic infographic generation"""
    print("\n" + "="*60)
    print("Example 1: Basic Infographic Generation")
    print("="*60 + "\n")

    # Initialize generator
    gen = InfographicGenerator()

    # Define your scores
    sections = {
        'Reading': {'score': 28, 'max': 30},
        'Listening': {'score': 29, 'max': 30},
        'Speaking': {'score': 26, 'max': 30},
        'Writing': {'score': 27, 'max': 30}
    }

    universities = {
        'Harvard University': '105+',
        'MIT': '100+',
        'Stanford University': '100+'
    }

    # Generate infographic
    image_path = gen.create_score_infographic(
        test_type='TOEFL',
        total_score=110,
        max_score=120,
        sections=sections,
        universities=universities,
        platform='instagram',
        background_image_path=None
    )

    print(f"✅ Created: {image_path}\n")


def example_2_content_generation():
    """Example 2: Generate text content"""
    print("\n" + "="*60)
    print("Example 2: Content Generation")
    print("="*60 + "\n")

    # Initialize generator
    content_gen = ContentGenerator()

    # Generate Instagram post
    instagram_post = content_gen.generate_instagram_post(
        score=110,
        max_score=120,
        sections={'Reading': 28, 'Listening': 29, 'Speaking': 26, 'Writing': 27},
        universities={'Harvard': '105+', 'MIT': '100+'}
    )

    print("Instagram Caption:")
    print("-" * 60)
    print(instagram_post['content'])
    print("-" * 60)
    print(f"\nAlt Text: {instagram_post['alt_text']}")
    print(f"Character Count: {instagram_post['character_count']}\n")


def example_3_hashtag_management():
    """Example 3: Hashtag suggestions"""
    print("\n" + "="*60)
    print("Example 3: Hashtag Management")
    print("="*60 + "\n")

    # Initialize manager
    hashtag_mgr = HashtagManager()

    # Get hashtags for different platforms
    for platform in ['instagram', 'twitter', 'linkedin', 'facebook']:
        hashtags = hashtag_mgr.get_hashtags_for_test('TOEFL', platform)
        formatted = hashtag_mgr.format_hashtags(hashtags, platform)

        print(f"{platform.capitalize()}:")
        print(f"  Count: {len(hashtags)}")
        print(f"  Tags: {formatted}")
        print()


def example_4_batch_generation():
    """Example 4: Batch generate for multiple scores"""
    print("\n" + "="*60)
    print("Example 4: Batch Generation")
    print("="*60 + "\n")

    gen = InfographicGenerator()

    # Different score scenarios
    scenarios = [
        {'name': 'Excellent', 'score': 110, 'sections': {'Reading': 28, 'Listening': 29, 'Speaking': 26, 'Writing': 27}},
        {'name': 'Very Good', 'score': 100, 'sections': {'Reading': 25, 'Listening': 26, 'Speaking': 24, 'Writing': 25}},
        {'name': 'Good', 'score': 90, 'sections': {'Reading': 23, 'Listening': 24, 'Speaking': 21, 'Writing': 22}},
    ]

    templates = load_templates()
    universities = templates['universities']

    for scenario in scenarios:
        print(f"Generating for {scenario['name']} range (Score: {scenario['score']})...")

        # Convert sections to proper format
        sections_formatted = {
            k: {'score': v, 'max': 30} for k, v in scenario['sections'].items()
        }

        # Generate Instagram version only
        image_path = gen.create_score_infographic(
            test_type='TOEFL',
            total_score=scenario['score'],
            max_score=120,
            sections=sections_formatted,
            universities=universities,
            platform='instagram',
            background_image_path=None
        )

        print(f"  ✅ {Path(image_path).name}\n")


def example_5_custom_styling():
    """Example 5: Customize colors and appearance"""
    print("\n" + "="*60)
    print("Example 5: Custom Styling (Advanced)")
    print("="*60 + "\n")

    print("To customize colors and styling:")
    print("1. Edit config/config.json")
    print("2. Modify the 'colors' section")
    print("3. Adjust font sizes in 'fonts' section")
    print("4. Change image dimensions in 'image_sizes'\n")

    print("Example color scheme (edit config.json):")
    print("""{
  "colors": {
    "primary": "#8B0000",    // Dark red
    "secondary": "#FFD700",  // Gold
    "accent": "#FFFFFF",     // White
    "text_dark": "#000000"
  }
}""")
    print()


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("🎓 SOCIAL MEDIA GENERATOR - PROGRAMMATIC EXAMPLES")
    print("="*60)

    examples = [
        ("Basic Infographic", example_1_basic_usage),
        ("Content Generation", example_2_content_generation),
        ("Hashtag Management", example_3_hashtag_management),
        ("Batch Generation", example_4_batch_generation),
        ("Custom Styling", example_5_custom_styling),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n  0. Run all examples")
    print()

    try:
        choice = input("Select example (0-5): ").strip()

        if choice == '0':
            for name, func in examples:
                func()
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            examples[int(choice) - 1][1]()
        else:
            print("Invalid choice!")
            return

        print("\n" + "="*60)
        print("✅ Examples completed!")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\nCancelled by user.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
