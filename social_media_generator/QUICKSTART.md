# 🚀 Quick Start Guide

Get up and running in under 5 minutes!

## Step 1: Install Dependencies (30 seconds)

```bash
cd social_media_generator
pip install -r requirements.txt
```

## Step 2: Generate Your First Content (10 seconds)

```bash
python main.py
```

That's it! Your content is ready in the `outputs/` folder.

## Step 3: Review Your Content

Check these locations:

```bash
# View generated images
ls outputs/images/

# View text content
cat outputs/content/toefl_linkedin_110.txt
```

## What You Get

After running the command, you'll have:

**Images** (in `outputs/images/`):
- `toefl_instagram_110.jpg` - Square format (1080x1080)
- `toefl_linkedin_110.jpg` - Landscape (1200x627)
- `toefl_facebook_110.jpg` - Landscape (1200x627)
- `toefl_twitter_110.jpg` - Landscape (1200x675)

**Content** (in `outputs/content/`):
- `toefl_linkedin_110.txt` - Professional LinkedIn post
- `toefl_instagram_110.txt` - Visual-friendly Instagram caption
- `toefl_twitter_110.txt` - Twitter thread (5 tweets)
- `toefl_facebook_110.txt` - Community-focused Facebook post
- `toefl_content_110.json` - All content in JSON format
- `toefl_hashtags_110.json` - Platform-specific hashtags

## Customize Your Score

```bash
# Different total score
python main.py --score 105

# Custom section scores
python main.py --score 110 --reading 29 --listening 30 --speaking 25 --writing 26

# Without background image (faster)
python main.py --no-background
```

## Other Test Types

```bash
# Interactive mode for GRE, GMAT, or IELTS
python main.py --custom
```

Then select your test type and enter scores when prompted.

## Optional: Add Background Images

To use real photos from Unsplash:

1. Get a free API key from [Unsplash Developers](https://unsplash.com/developers)
2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your key:
   ```
   UNSPLASH_ACCESS_KEY=your_key_here
   ```
4. Run again:
   ```bash
   python main.py
   ```

## Next Steps

1. ✅ Review generated content
2. ✅ Customize if needed
3. ✅ Upload to social media
4. ✅ Use the alt text for accessibility
5. ✅ Engage with your audience!

## Need Help?

- Full documentation: `README.md`
- Detailed guide: `USAGE_GUIDE.md`
- See all options: `python main.py --help`

## Common Commands Cheat Sheet

```bash
# Default TOEFL (score 110)
python main.py

# Custom score
python main.py --score 105

# No background image
python main.py --no-background

# Other tests (interactive)
python main.py --custom

# See all options
python main.py --help

# Check outputs
ls outputs/images/
ls outputs/content/
```

**Happy posting! 🎉**
