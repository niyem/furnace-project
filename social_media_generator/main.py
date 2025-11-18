#!/usr/bin/env python3
"""
Social Media Content Generator - Main Script
Generate professional social media posts and infographics for test scores

Usage:
    python main.py --score 110 --test TOEFL
    python main.py --score 110 --test TOEFL --no-background
    python main.py --custom
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.infographic_generator import InfographicGenerator
from src.content_generator import ContentGenerator
from src.hashtag_manager import HashtagManager
from src.utils import load_templates, load_config, ensure_output_dirs


def create_toefl_content(
    score: int = 110,
    reading: int = 28,
    listening: int = 29,
    speaking: int = 26,
    writing: int = 27,
    fetch_background: bool = True
):
    """Create TOEFL social media content with default or custom scores"""

    print("\n" + "="*60)
    print("🎓 TOEFL SOCIAL MEDIA CONTENT GENERATOR 🎓")
    print("="*60 + "\n")

    # Load templates
    templates = load_templates()
    universities = templates['universities']

    # Initialize generators
    print("📝 Initializing generators...")
    infographic_gen = InfographicGenerator()
    content_gen = ContentGenerator()
    hashtag_mgr = HashtagManager()

    # Prepare section scores
    sections = {
        'Reading': reading,
        'Listening': listening,
        'Speaking': speaking,
        'Writing': writing
    }

    sections_with_max = {
        'Reading': {'score': reading, 'max': 30},
        'Listening': {'score': listening, 'max': 30},
        'Speaking': {'score': speaking, 'max': 30},
        'Writing': {'score': writing, 'max': 30}
    }

    print(f"\n📊 Generating content for TOEFL score: {score}/120")
    print(f"   Reading: {reading} | Listening: {listening} | Speaking: {speaking} | Writing: {writing}\n")

    # Generate infographics
    print("🎨 Creating infographics for all platforms...")
    infographics = infographic_gen.create_all_platform_infographics(
        test_type="TOEFL",
        total_score=score,
        max_score=120,
        sections=sections_with_max,
        universities=universities,
        fetch_background=fetch_background
    )

    print("\n📱 Generating social media content...")
    # Generate content
    all_content = content_gen.generate_all_content(
        score=score,
        max_score=120,
        sections=sections,
        universities=universities
    )

    # Save content
    content_gen.save_all_content(all_content, "TOEFL", score)

    # Generate hashtag recommendations
    print("\n🏷️  Generating hashtag recommendations...")
    hashtags = hashtag_mgr.get_all_platform_hashtags("TOEFL")

    hashtag_output = ensure_output_dirs() / "content" / f"toefl_hashtags_{score}.json"
    with open(hashtag_output, 'w') as f:
        json.dump(hashtags, f, indent=2)

    print(f"   Saved to: {hashtag_output}")

    # Print summary
    print("\n" + "="*60)
    print("✅ GENERATION COMPLETE!")
    print("="*60)
    print("\n📁 Output Location:")
    output_dir = ensure_output_dirs()
    print(f"   Images: {output_dir / 'images'}")
    print(f"   Content: {output_dir / 'content'}")

    print("\n🖼️  Generated Infographics:")
    for platform, filepath in infographics.items():
        print(f"   • {platform.capitalize()}: {Path(filepath).name}")

    print("\n📝 Generated Content Files:")
    print(f"   • LinkedIn: toefl_linkedin_{score}.txt")
    print(f"   • Instagram: toefl_instagram_{score}.txt")
    print(f"   • Twitter/X: toefl_twitter_{score}.txt (Thread format)")
    print(f"   • Facebook: toefl_facebook_{score}.txt")
    print(f"   • All content JSON: toefl_content_{score}.json")
    print(f"   • Hashtags: toefl_hashtags_{score}.json")

    print("\n💡 Pro Tips:")
    print("   • Review alt text in content files for accessibility")
    print("   • Customize the content before posting")
    print("   • Schedule posts at optimal times for each platform")
    print("   • Engage with comments to boost reach")

    print("\n🎯 Next Steps:")
    print("   1. Review generated images and content")
    print("   2. Customize if needed")
    print("   3. Upload to your social media platforms")
    print("   4. Use the provided alt text for accessibility")
    print("   5. Monitor engagement and adjust strategy")

    print("\n" + "="*60 + "\n")


def create_custom_content():
    """Interactive mode for custom test scores"""

    print("\n" + "="*60)
    print("🎓 CUSTOM TEST SCORE CONTENT GENERATOR 🎓")
    print("="*60 + "\n")

    # Get test type
    print("Select test type:")
    print("1. TOEFL")
    print("2. GRE")
    print("3. GMAT")
    print("4. IELTS")

    test_choice = input("\nEnter choice (1-4): ").strip()
    test_types = {'1': 'TOEFL', '2': 'GRE', '3': 'GMAT', '4': 'IELTS'}
    test_type = test_types.get(test_choice, 'TOEFL')

    print(f"\n✅ Selected: {test_type}\n")

    # Get scores based on test type
    if test_type == 'TOEFL':
        score = int(input("Total score (0-120): ") or "110")
        reading = int(input("Reading score (0-30): ") or "28")
        listening = int(input("Listening score (0-30): ") or "29")
        speaking = int(input("Speaking score (0-30): ") or "26")
        writing = int(input("Writing score (0-30): ") or "27")

        sections = {
            'Reading': {'score': reading, 'max': 30},
            'Listening': {'score': listening, 'max': 30},
            'Speaking': {'score': speaking, 'max': 30},
            'Writing': {'score': writing, 'max': 30}
        }
        max_score = 120

    elif test_type == 'GRE':
        score = int(input("Total score (260-340): ") or "320")
        verbal = int(input("Verbal Reasoning (130-170): ") or "160")
        quant = int(input("Quantitative Reasoning (130-170): ") or "165")
        writing_score = float(input("Analytical Writing (0-6): ") or "4.5")

        sections = {
            'Verbal': {'score': verbal, 'max': 170},
            'Quantitative': {'score': quant, 'max': 170},
            'Writing': {'score': writing_score, 'max': 6}
        }
        max_score = 340

    elif test_type == 'IELTS':
        score = float(input("Overall band score (0-9): ") or "7.5")
        listening = float(input("Listening (0-9): ") or "8.0")
        reading = float(input("Reading (0-9): ") or "7.5")
        writing = float(input("Writing (0-9): ") or "7.0")
        speaking = float(input("Speaking (0-9): ") or "7.5")

        sections = {
            'Listening': {'score': listening, 'max': 9},
            'Reading': {'score': reading, 'max': 9},
            'Writing': {'score': writing, 'max': 9},
            'Speaking': {'score': speaking, 'max': 9}
        }
        max_score = 9

    else:  # GMAT
        score = int(input("Total score (200-800): ") or "720")
        quant = int(input("Quantitative (0-60): ") or "48")
        verbal = int(input("Verbal (0-60): ") or "42")
        writing_score = float(input("Analytical Writing (0-6): ") or "5.0")

        sections = {
            'Quantitative': {'score': quant, 'max': 60},
            'Verbal': {'score': verbal, 'max': 60},
            'Writing': {'score': writing_score, 'max': 6}
        }
        max_score = 800

    # Ask about background
    use_background = input("\nFetch background image from Unsplash? (y/n): ").lower().strip() == 'y'

    print(f"\n🚀 Generating content for {test_type}...")

    # Load templates
    templates = load_templates()
    universities = templates.get('universities', {})

    # Initialize generators
    infographic_gen = InfographicGenerator()
    content_gen = ContentGenerator()
    hashtag_mgr = HashtagManager()

    # Generate infographics
    print("\n🎨 Creating infographics...")
    infographics = infographic_gen.create_all_platform_infographics(
        test_type=test_type,
        total_score=score,
        max_score=max_score,
        sections=sections,
        universities=universities,
        fetch_background=use_background
    )

    print("\n📱 Generating content...")
    # For content, we need to convert sections to simple dict
    simple_sections = {k: v['score'] for k, v in sections.items()}

    all_content = content_gen.generate_all_content(
        score=score,
        max_score=max_score,
        sections=simple_sections,
        universities=universities
    )

    content_gen.save_all_content(all_content, test_type, score)

    # Generate hashtags
    print("\n🏷️  Generating hashtags...")
    hashtags = hashtag_mgr.get_all_platform_hashtags(test_type)

    hashtag_output = ensure_output_dirs() / "content" / f"{test_type.lower()}_hashtags_{score}.json"
    with open(hashtag_output, 'w') as f:
        json.dump(hashtags, f, indent=2)

    print("\n✅ Generation complete! Check the outputs folder.\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate social media content for test scores',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate TOEFL content with default scores (110/120)
  python main.py

  # Generate TOEFL content with custom score
  python main.py --score 105

  # Generate with custom section scores
  python main.py --score 110 --reading 28 --listening 29 --speaking 26 --writing 27

  # Generate without Unsplash background image
  python main.py --no-background

  # Interactive custom mode
  python main.py --custom

  # Specify test type
  python main.py --test GRE --score 320
        """
    )

    parser.add_argument('--test', type=str, default='TOEFL',
                        choices=['TOEFL', 'GRE', 'GMAT', 'IELTS'],
                        help='Test type (default: TOEFL)')
    parser.add_argument('--score', type=int, default=110,
                        help='Total score (default: 110 for TOEFL)')
    parser.add_argument('--reading', type=int, default=28,
                        help='Reading score (TOEFL only, default: 28)')
    parser.add_argument('--listening', type=int, default=29,
                        help='Listening score (TOEFL only, default: 29)')
    parser.add_argument('--speaking', type=int, default=26,
                        help='Speaking score (TOEFL only, default: 26)')
    parser.add_argument('--writing', type=int, default=27,
                        help='Writing score (TOEFL only, default: 27)')
    parser.add_argument('--no-background', action='store_true',
                        help='Skip fetching background image from Unsplash')
    parser.add_argument('--custom', action='store_true',
                        help='Run in interactive custom mode')

    args = parser.parse_args()

    try:
        if args.custom:
            create_custom_content()
        elif args.test == 'TOEFL':
            create_toefl_content(
                score=args.score,
                reading=args.reading,
                listening=args.listening,
                speaking=args.speaking,
                writing=args.writing,
                fetch_background=not args.no_background
            )
        else:
            print(f"\n⚠️  {args.test} mode not fully implemented in command-line.")
            print("    Use --custom for interactive mode with other test types.\n")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
