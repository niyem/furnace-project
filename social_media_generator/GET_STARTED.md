# 🎉 Welcome to Your TOEFL Social Media Content Generator!

Everything is ready to use! Here's how to get started immediately.

## ✅ What's Included

Your complete social media content generation system includes:

### 📱 Content for 4 Platforms
- **LinkedIn**: Professional posts with detailed breakdowns
- **Instagram**: Visual-friendly captions with emojis
- **Twitter/X**: Engaging threads (5 tweets)
- **Facebook**: Community-focused, shareable posts

### 🎨 Professional Infographics
- Custom sizes for each platform
- Score breakdowns with progress bars
- University requirements comparison
- Modern, education-themed design
- Groupe BM branding

### 🏷️ Smart Hashtags
- Platform-optimized hashtag sets
- Test-type specific tags
- Trending educational hashtags
- #GroupeBM for brand awareness

### ♿ Accessibility
- Alt text for all images
- High contrast designs
- Mobile-friendly layouts

## 🚀 Quick Start (2 Minutes)

### Step 1: Install
```bash
cd social_media_generator
pip install -r requirements.txt
```

### Step 2: Generate Content
```bash
python main.py
```

### Step 3: Find Your Content
```bash
cd outputs/
ls images/      # Your infographics
ls content/     # Your post text
```

**That's it!** You now have professional content ready to post.

## 📂 Your Generated Files

After running the generator, you'll find:

```
outputs/
├── images/
│   ├── toefl_instagram_110.jpg  ← Upload to Instagram
│   ├── toefl_linkedin_110.jpg   ← Upload to LinkedIn
│   ├── toefl_facebook_110.jpg   ← Upload to Facebook
│   └── toefl_twitter_110.jpg    ← Upload to Twitter
│
└── content/
    ├── toefl_instagram_110.txt  ← Copy/paste caption
    ├── toefl_linkedin_110.txt   ← Copy/paste post
    ├── toefl_twitter_110.txt    ← Copy/paste thread
    ├── toefl_facebook_110.txt   ← Copy/paste post
    ├── toefl_content_110.json   ← All content in JSON
    └── toefl_hashtags_110.json  ← Hashtag recommendations
```

## 🎯 Common Use Cases

### For Your TOEFL Score (110)
```bash
python main.py
```

### For a Different Score
```bash
python main.py --score 105
```

### Custom Section Scores
```bash
python main.py --score 110 --reading 29 --listening 30 --speaking 25 --writing 26
```

### Other Test Types (GRE, GMAT, IELTS)
```bash
python main.py --custom
```
Then follow the interactive prompts.

### Without Background Images (Faster)
```bash
python main.py --no-background
```

## 🎨 Customization

### Change Colors
Edit `config/config.json`:
```json
{
  "colors": {
    "primary": "#1e3a8a",    ← Change this
    "secondary": "#3b82f6",  ← And this
    "accent": "#fbbf24"      ← And this
  }
}
```

### Modify Post Content
Edit `config/templates.json`:
- Change study tips
- Adjust call-to-action
- Update university lists
- Customize messages

### Adjust Image Sizes
Edit `config/config.json`:
```json
{
  "image_sizes": {
    "instagram": [1080, 1080],  ← Modify dimensions
    "linkedin": [1200, 627]
  }
}
```

## 📖 Documentation

We've included comprehensive guides:

1. **QUICKSTART.md** ← Start here! (5 min read)
2. **README.md** ← Full documentation
3. **USAGE_GUIDE.md** ← Platform-specific tips
4. **PROJECT_SUMMARY.md** ← Technical overview

## 🎓 Sample Output

Here's what the LinkedIn post looks like:

```
🎓 TOEFL Success Story: 110/120 Achieved!

I'm thrilled to share that I've achieved a score of 110
on the TOEFL iBT exam! This milestone brings me one step
closer to my dream of studying at top universities...

📊 Score Breakdown:
• Reading: 28/30
• Listening: 29/30
• Speaking: 26/30
• Writing: 27/30

🎯 This score exceeds the requirements for:
• Harvard University: 105+
• MIT: 100+
• Stanford University: 100+

💡 Key Strategies That Helped:
• Practiced with official ETS materials daily
• Joined English conversation groups
• Watched TED Talks for listening practice
...

#TOEFL #StudyAbroad #GroupeBM
```

## 🌟 Pro Tips

### Posting Strategy
1. **LinkedIn**: Post Tuesday-Thursday, 10 AM - 12 PM
2. **Instagram**: Post Wednesday-Friday, 7 PM - 9 PM
3. **Twitter**: Post Monday-Friday, 12 PM - 1 PM
4. **Facebook**: Post Wednesday-Friday, 1 PM - 4 PM

### Engagement Tips
- Reply to comments within the first hour
- Use ALL the generated hashtags
- Post to Stories/Reels for extra reach
- Tag Groupe BM if they have social accounts

### Customization Tips
- Add your personal story to make it authentic
- Include specific study resources you used
- Mention your target universities
- Share your preparation timeline

## 🔧 Advanced Features

### Batch Processing
Generate content for multiple scores:
```python
for score in [100, 105, 110, 115]:
    python main.py --score {score} --no-background
```

### Unsplash Integration
For beautiful background photos:
1. Get free API key: https://unsplash.com/developers
2. Create `.env`: `cp .env.example .env`
3. Add your key to `.env`
4. Run: `python main.py`

### Programmatic Usage
Use as a Python library:
```python
from src import InfographicGenerator, ContentGenerator

gen = InfographicGenerator()
content = ContentGenerator()

# Your custom code here
```

See `examples/custom_usage.py` for more examples.

## ❓ Need Help?

### Quick Answers
```bash
# See all options
python main.py --help

# View example code
python examples/custom_usage.py

# Check your outputs
ls -lh outputs/images/
ls -lh outputs/content/
```

### Documentation
- Quick questions? → `QUICKSTART.md`
- Detailed info? → `README.md`
- Platform tips? → `USAGE_GUIDE.md`
- Technical details? → `PROJECT_SUMMARY.md`

### Common Issues

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"Font warnings"**
```bash
# Ignore them - fallback fonts work fine!
# Or install: sudo apt-get install fonts-liberation
```

**"No Unsplash images"**
```bash
# Use gradient backgrounds instead:
python main.py --no-background
```

## 🎉 You're All Set!

Everything is ready to go. Just run:

```bash
python main.py
```

And you'll have professional social media content in seconds!

## 📞 Support

Questions about:
- **Installation**: Check `README.md` installation section
- **Usage**: See `QUICKSTART.md` or `USAGE_GUIDE.md`
- **Customization**: Edit files in `config/` folder
- **Errors**: Check troubleshooting in `README.md`

---

**Made with ❤️ for Groupe BM**

**Happy posting! 🚀**

---

## Quick Command Reference

```bash
# Basic usage
python main.py                    # Default TOEFL 110
python main.py --score 105        # Custom score
python main.py --no-background    # No Unsplash
python main.py --custom           # Interactive mode

# View outputs
ls outputs/images/                # See images
cat outputs/content/*.txt         # Read content

# Customize
nano config/config.json           # Edit colors/settings
nano config/templates.json        # Edit content templates

# Get help
python main.py --help             # Show all options
cat README.md                     # Full docs
cat QUICKSTART.md                 # Quick guide
```

**Now go create amazing content! 🎓✨**
