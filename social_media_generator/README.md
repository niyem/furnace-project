# 🎓 Social Media Content Generator for Test Scores

A comprehensive Python tool to generate professional social media posts and infographics for standardized test achievements (TOEFL, GRE, GMAT, IELTS). Built for **Groupe BM** admission services.

## ✨ Features

- 📊 **Professional Infographics**: Generate high-quality, platform-optimized images with score breakdowns and university comparisons
- 📱 **Multi-Platform Content**: Automatically create tailored posts for LinkedIn, Instagram, Twitter/X, and Facebook
- 🎨 **Smart Design**: Modern, education-themed design with customizable colors and layouts
- 🖼️ **Background Integration**: Optional Unsplash API integration for stunning background images
- 🏷️ **Hashtag Management**: Intelligent hashtag suggestions optimized for each platform
- ♿ **Accessibility**: Automatic alt text generation for all images
- 🔧 **Highly Customizable**: Easy to adapt for different test types and scores
- 📝 **Complete Documentation**: Clear examples and usage instructions

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this project**

```bash
cd social_media_generator
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Optional: Set up Unsplash API** (for background images)

   - Get a free API key from [Unsplash Developers](https://unsplash.com/developers)
   - Create a `.env` file:

   ```bash
   cp .env.example .env
   ```

   - Edit `.env` and add your API key:

   ```
   UNSPLASH_ACCESS_KEY=your_actual_api_key_here
   ```

   *Note: If you skip this step, the generator will use gradient backgrounds instead.*

### Basic Usage

**Generate TOEFL content with default scores (110/120):**

```bash
python main.py
```

**Generate with custom score:**

```bash
python main.py --score 105
```

**Generate with custom section scores:**

```bash
python main.py --score 110 --reading 28 --listening 29 --speaking 26 --writing 27
```

**Generate without background image:**

```bash
python main.py --no-background
```

**Interactive mode for any test type:**

```bash
python main.py --custom
```

## 📖 Detailed Usage

### Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  --test TYPE          Test type: TOEFL, GRE, GMAT, IELTS (default: TOEFL)
  --score SCORE        Total score (default: 110)
  --reading SCORE      Reading section score (default: 28)
  --listening SCORE    Listening section score (default: 29)
  --speaking SCORE     Speaking section score (default: 26)
  --writing SCORE      Writing section score (default: 27)
  --no-background      Skip Unsplash background image
  --custom             Interactive mode for custom scores
  -h, --help           Show help message
```

### Examples

**1. TOEFL with specific scores:**
```bash
python main.py --score 115 --reading 30 --listening 29 --speaking 28 --writing 28
```

**2. GRE (interactive mode):**
```bash
python main.py --custom
# Then select: 2 (GRE)
# Enter your scores when prompted
```

**3. Quick generation without Unsplash:**
```bash
python main.py --score 108 --no-background
```

## 📁 Project Structure

```
social_media_generator/
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                    # This file
│
├── config/
│   ├── config.json              # General configuration
│   └── templates.json           # Content templates for each platform
│
├── src/
│   ├── __init__.py
│   ├── infographic_generator.py # Image generation with Pillow
│   ├── content_generator.py     # Platform-specific content
│   ├── hashtag_manager.py       # Hashtag recommendations
│   ├── unsplash_client.py       # Unsplash API integration
│   └── utils.py                 # Utility functions
│
└── outputs/
    ├── images/                  # Generated infographics
    └── content/                 # Generated text content
```

## 🎨 Generated Content

### Infographics

For each platform, a customized infographic is created:

- **Instagram**: 1080x1080 (square)
- **LinkedIn**: 1200x627 (landscape)
- **Facebook**: 1200x627 (landscape)
- **Twitter/X**: 1200x675 (landscape)

Each infographic includes:
- ✅ Overall score prominently displayed
- 📊 Section score breakdown with progress bars
- 🎯 Top university requirements comparison
- 🏢 Groupe BM branding
- 🎨 Professional, modern design

### Text Content

Platform-specific posts are generated with:

#### LinkedIn
- Professional, detailed narrative
- Full score breakdown
- University list
- Study tips and strategies
- Call-to-action for engagement
- Professional hashtags (limit: 10)

#### Instagram
- Visual-friendly format with emojis
- Concise score presentation
- Quick study tips
- Engaging call-to-action
- Extended hashtag set (limit: 30)

#### Twitter/X
- **Single tweet** or **thread** format
- Concise messaging
- Section breakdown
- Brief tips
- Relevant hashtags (limit: 5)

#### Facebook
- Community-focused content
- Detailed score breakdown
- Motivational elements
- Shareable format
- Balanced hashtags (limit: 15)

### Additional Files

- **JSON summary**: Complete content data for all platforms
- **Hashtag recommendations**: Platform-specific hashtag lists
- **Alt text**: Accessibility descriptions for all images

## 🔧 Customization

### Modifying Templates

Edit `config/templates.json` to customize:
- Post templates for each platform
- Study tips
- Call-to-action messages
- Hashtags
- University requirements

### Changing Colors

Edit `config/config.json` to modify:
```json
{
  "colors": {
    "primary": "#1e3a8a",      // Main blue
    "secondary": "#3b82f6",    // Lighter blue
    "accent": "#fbbf24",       // Gold accent
    "white": "#ffffff",
    "text_dark": "#1f2937",
    "text_light": "#6b7280"
  }
}
```

### Image Sizes

Modify platform-specific dimensions in `config/config.json`:
```json
{
  "image_sizes": {
    "instagram": [1080, 1080],
    "linkedin": [1200, 627],
    "facebook": [1200, 627],
    "twitter": [1200, 675]
  }
}
```

### Adding New Test Types

1. Add templates to `config/templates.json`
2. Add hashtags to `src/hashtag_manager.py`
3. Update `main.py` to handle the new test type

Example for adding SAT:
```python
# In hashtag_manager.py
'SAT': {
    'primary': ['#SAT', '#SATScore', '#SATPrep'],
    'study_related': ['#CollegePrep', '#TestPrep'],
    # ... etc
}
```

## 📊 Output Examples

After running the generator, you'll find:

```
outputs/
├── images/
│   ├── toefl_instagram_110.jpg
│   ├── toefl_linkedin_110.jpg
│   ├── toefl_facebook_110.jpg
│   └── toefl_twitter_110.jpg
│
└── content/
    ├── toefl_content_110.json      # Complete data
    ├── toefl_linkedin_110.txt
    ├── toefl_instagram_110.txt
    ├── toefl_twitter_110.txt       # Thread format
    ├── toefl_facebook_110.txt
    └── toefl_hashtags_110.json
```

## 🎯 Best Practices

### For Social Media Success

1. **Timing**: Schedule posts at peak engagement times for each platform
2. **Engagement**: Respond to comments within the first hour
3. **Hashtags**: Use the generated hashtags but consider adding trending ones
4. **Customization**: Personalize the generated content before posting
5. **Consistency**: Post regularly to build audience

### Platform-Specific Tips

**LinkedIn**:
- Post during business hours (Tuesday-Thursday, 10 AM - 12 PM)
- Engage with comments professionally
- Share in relevant groups

**Instagram**:
- Use all 30 hashtags
- Post Stories with swipe-up links
- Create carousel posts with tips

**Twitter/X**:
- Use the thread format for better engagement
- Reply to your own thread with additional context
- Retweet with comments

**Facebook**:
- Post during evenings and weekends
- Encourage sharing
- Create Facebook Events for test prep sessions

## 🛠️ Advanced Usage

### Using as a Python Library

```python
from src import InfographicGenerator, ContentGenerator, HashtagManager

# Initialize
infographic_gen = InfographicGenerator()
content_gen = ContentGenerator()
hashtag_mgr = HashtagManager()

# Generate infographic
sections = {
    'Reading': {'score': 28, 'max': 30},
    'Listening': {'score': 29, 'max': 30},
    'Speaking': {'score': 26, 'max': 30},
    'Writing': {'score': 27, 'max': 30}
}

universities = {
    'Harvard University': '105+',
    'MIT': '100+',
    'Stanford': '100+'
}

# Create infographic
image_path = infographic_gen.create_score_infographic(
    test_type='TOEFL',
    total_score=110,
    max_score=120,
    sections=sections,
    universities=universities,
    platform='instagram'
)

# Generate content
content = content_gen.generate_instagram_post(
    score=110,
    max_score=120,
    sections={'Reading': 28, 'Listening': 29, 'Speaking': 26, 'Writing': 27},
    universities=universities
)

print(content['content'])
print(content['alt_text'])

# Get hashtags
hashtags = hashtag_mgr.get_hashtags_for_test('TOEFL', 'instagram')
print(hashtags)
```

### Batch Processing

Create a script to generate content for multiple scores:

```python
from main import create_toefl_content

scores = [100, 105, 110, 115]

for score in scores:
    create_toefl_content(
        score=score,
        fetch_background=False  # Use gradient to speed up
    )
```

## 🔍 Troubleshooting

### Common Issues

**1. ImportError or ModuleNotFoundError**
```bash
# Make sure you're in the correct directory
cd social_media_generator
# Reinstall dependencies
pip install -r requirements.txt
```

**2. Font not found warnings**
- The generator will use fallback fonts automatically
- To use custom fonts, install liberation fonts:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install fonts-liberation
  ```

**3. Unsplash API errors**
- Check your API key in `.env`
- Verify your API key is active at [Unsplash Developers](https://unsplash.com/developers)
- Use `--no-background` flag to skip Unsplash integration

**4. Permission errors**
- Ensure the `outputs/` directory is writable
- Run with appropriate permissions

## 🤝 Contributing

To extend this tool:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Ideas for Enhancement

- [ ] Add video generation for Instagram Reels/TikTok
- [ ] Integrate with social media APIs for direct posting
- [ ] Add A/B testing for different post variants
- [ ] Include analytics tracking
- [ ] Support for more test types (SAT, ACT, etc.)
- [ ] Multi-language support
- [ ] Scheduling functionality

## 📄 License

This project is created for Groupe BM. Please ensure you have appropriate usage rights.

## 🙏 Acknowledgments

- **Pillow**: Python Imaging Library for image generation
- **Unsplash**: Beautiful free stock photos
- **Groupe BM**: For providing admission services

## 📞 Support

For questions or issues:
1. Check this README
2. Review the code comments
3. Check the example outputs
4. Contact Groupe BM support team

## 🎓 About Groupe BM

Groupe BM is a leading admission services provider, helping international students achieve their dreams of studying at top universities worldwide.

---

**Made with ❤️ for international students aspiring to study abroad**

---

## Quick Reference Card

```bash
# Most common commands:

# 1. Generate with defaults
python main.py

# 2. Custom TOEFL score
python main.py --score 105

# 3. All custom sections
python main.py --score 110 --reading 29 --listening 30 --speaking 26 --writing 25

# 4. Without Unsplash
python main.py --no-background

# 5. Other test types
python main.py --custom

# 6. See all options
python main.py --help
```

**Output Location**: `outputs/images/` and `outputs/content/`

**Customization Files**: `config/config.json` and `config/templates.json`

**Environment**: `.env` (copy from `.env.example`)
