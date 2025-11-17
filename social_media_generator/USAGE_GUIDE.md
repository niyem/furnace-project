# 📘 Detailed Usage Guide

This guide provides comprehensive examples and best practices for using the Social Media Content Generator.

## Table of Contents

1. [Getting Started](#getting-started)
2. [TOEFL Content Generation](#toefl-content-generation)
3. [Other Test Types](#other-test-types)
4. [Customizing Content](#customizing-content)
5. [Platform-Specific Guidelines](#platform-specific-guidelines)
6. [Advanced Workflows](#advanced-workflows)
7. [Tips for Maximum Engagement](#tips-for-maximum-engagement)

## Getting Started

### First-Time Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the installation:**
   ```bash
   python main.py --help
   ```

3. **Generate your first content:**
   ```bash
   python main.py
   ```

### Understanding the Output

After running the generator, check these locations:

```
outputs/
├── images/          # Your infographics (.jpg files)
└── content/         # Your post text (.txt and .json files)
```

## TOEFL Content Generation

### Example 1: Quick Generation with Defaults

```bash
python main.py
```

**What this does:**
- Generates content for TOEFL score 110/120
- Section scores: R:28, L:29, S:26, W:27
- Creates infographics for all 4 platforms
- Generates text content for all platforms
- Attempts to fetch Unsplash background image

**Output files:**
- `toefl_instagram_110.jpg`
- `toefl_linkedin_110.jpg`
- `toefl_facebook_110.jpg`
- `toefl_twitter_110.jpg`
- `toefl_instagram_110.txt`
- `toefl_linkedin_110.txt`
- `toefl_facebook_110.txt`
- `toefl_twitter_110.txt`
- `toefl_content_110.json`
- `toefl_hashtags_110.json`

### Example 2: Custom Score

```bash
python main.py --score 105
```

**Use case:** You achieved 105/120 on TOEFL

### Example 3: All Custom Section Scores

```bash
python main.py --score 115 --reading 30 --listening 29 --speaking 28 --writing 28
```

**Use case:** You want to showcase specific section strengths

### Example 4: Without Unsplash Background

```bash
python main.py --score 110 --no-background
```

**Benefits:**
- Faster generation (no API call)
- No internet required
- Consistent gradient background
- No API key needed

**When to use:**
- Testing
- Batch processing
- No Unsplash API key
- Prefer consistent design

### Example 5: Multiple Score Scenarios

Create a bash script `generate_multiple.sh`:

```bash
#!/bin/bash

# Generate for different score ranges
python main.py --score 100 --no-background
python main.py --score 105 --no-background
python main.py --score 110 --no-background
python main.py --score 115 --no-background

echo "All score variations generated!"
```

Run with:
```bash
chmod +x generate_multiple.sh
./generate_multiple.sh
```

## Other Test Types

### GRE Content Generation

```bash
python main.py --custom
```

Then enter:
```
Select test type: 2 (GRE)
Total score: 325
Verbal Reasoning: 163
Quantitative Reasoning: 162
Analytical Writing: 4.5
Fetch background: y
```

### IELTS Content Generation

```bash
python main.py --custom
```

Then enter:
```
Select test type: 4 (IELTS)
Overall band score: 7.5
Listening: 8.0
Reading: 7.5
Writing: 7.0
Speaking: 7.5
Fetch background: y
```

### GMAT Content Generation

```bash
python main.py --custom
```

Then enter:
```
Select test type: 3 (GMAT)
Total score: 720
Quantitative: 48
Verbal: 42
Analytical Writing: 5.0
Fetch background: y
```

## Customizing Content

### Modifying Post Templates

Edit `config/templates.json`:

**Example: Add your personal touch to LinkedIn posts**

```json
{
  "linkedin": {
    "template": "🎓 TOEFL Success Story: {score}/120 Achieved!\n\nI'm beyond excited to share...\n\n[Your custom message here]\n\n{hashtags}"
  }
}
```

### Changing Study Tips

In `config/templates.json`, modify the `study_tips` array:

```json
{
  "study_tips": [
    "Your custom tip #1",
    "Your custom tip #2",
    "Your custom tip #3"
  ]
}
```

### Customizing Colors

Edit `config/config.json`:

**Example: Use school colors**

```json
{
  "colors": {
    "primary": "#8B0000",      // Crimson red
    "secondary": "#FFD700",    // Gold
    "accent": "#FFFFFF",       // White
    "text_dark": "#000000"
  }
}
```

### Adding Universities

Edit `config/templates.json`:

```json
{
  "universities": {
    "Your University": "100+",
    "Dream School": "105+",
    "Target School": "95+"
  }
}
```

## Platform-Specific Guidelines

### LinkedIn Best Practices

**Generated content includes:**
- Professional narrative
- Detailed score breakdown
- Study strategies
- Call-to-action

**How to use:**
1. Copy content from `toefl_linkedin_110.txt`
2. Upload `toefl_linkedin_110.jpg`
3. Add alt text (included in .txt file)
4. Post during business hours
5. Engage with comments

**Optimal posting times:**
- Tuesday-Thursday
- 10 AM - 12 PM
- 5 PM - 6 PM

**Engagement tips:**
- Ask a question at the end
- Tag Groupe BM (if they have a LinkedIn page)
- Share in relevant groups
- Respond to comments within 1 hour

### Instagram Best Practices

**Generated content includes:**
- Emoji-rich caption
- Concise score display
- Visual-friendly format
- Maximum hashtags (30)

**How to use:**
1. Upload `toefl_instagram_110.jpg`
2. Copy caption from `toefl_instagram_110.txt`
3. Add alt text for accessibility
4. Consider creating Stories/Reels with same content

**Optimal posting times:**
- Wednesday-Friday
- 11 AM - 1 PM
- 7 PM - 9 PM

**Engagement tips:**
- Use all 30 hashtags
- Post to Stories with poll: "What's your target score?"
- Create a Reel with tips
- Save as Highlight

**Instagram-specific additions:**
- Create carousel with individual section scores
- Add stickers and GIFs to Stories
- Use interactive elements (polls, questions)

### Twitter/X Best Practices

**Generated content includes:**
- Thread format (5 tweets)
- Concise messaging
- Strategic hashtags (5)

**How to use:**
1. Upload `toefl_twitter_110.jpg` to first tweet
2. Copy thread from `toefl_twitter_110.txt`
3. Post as thread (numbered tweets)
4. Quote tweet yourself with additional insights

**Optimal posting times:**
- Monday-Friday
- 9 AM - 3 PM
- Peak: 12 PM - 1 PM

**Engagement tips:**
- Pin the thread to profile
- Reply to your own thread with study resources
- Use trending hashtags if relevant
- Engage with test prep community

**Thread structure:**
```
Tweet 1: Announcement + image
Tweet 2: Score breakdown
Tweet 3: Study tips
Tweet 4: Thanks to Groupe BM
Tweet 5: Call-to-action
```

### Facebook Best Practices

**Generated content includes:**
- Community-focused narrative
- Shareable format
- Motivational elements
- Balanced hashtags

**How to use:**
1. Create a new post
2. Upload `toefl_facebook_110.jpg`
3. Copy content from `toefl_facebook_110.txt`
4. Tag friends preparing for TOEFL
5. Share to relevant groups

**Optimal posting times:**
- Wednesday-Friday
- 1 PM - 4 PM
- Weekend: 12 PM - 1 PM

**Engagement tips:**
- Encourage shares: "Tag someone preparing for TOEFL!"
- Create Facebook Event for study group
- Go live to discuss preparation
- Post in test prep groups

## Advanced Workflows

### Workflow 1: Complete Campaign Launch

```bash
# 1. Generate all content
python main.py --score 110

# 2. Review and customize
# - Edit text files in outputs/content/
# - Adjust if needed

# 3. Schedule posts
# - LinkedIn: Tuesday 10 AM
# - Instagram: Wednesday 7 PM
# - Twitter: Thursday 12 PM
# - Facebook: Friday 2 PM

# 4. Monitor engagement
# - First hour: Reply to all comments
# - Day 1: Share to Stories/Reels
# - Week 1: Analyze performance
```

### Workflow 2: A/B Testing

```bash
# Generate version A (with background)
python main.py --score 110

# Move to separate folder
mkdir -p outputs/version_a
mv outputs/images/* outputs/version_a/
mv outputs/content/* outputs/version_a/

# Generate version B (without background)
python main.py --score 110 --no-background

# Move to separate folder
mkdir -p outputs/version_b
mv outputs/images/* outputs/version_b/
mv outputs/content/* outputs/version_b/

# Test both versions on Instagram Stories and see which performs better
```

### Workflow 3: Series of Posts

Create a series for different score ranges:

```python
# create_series.py
from main import create_toefl_content

score_ranges = [
    {"name": "Excellent", "score": 110, "r": 28, "l": 29, "s": 26, "w": 27},
    {"name": "Very Good", "score": 100, "r": 25, "l": 26, "s": 24, "w": 25},
    {"name": "Good", "score": 90, "r": 23, "l": 24, "s": 21, "w": 22},
]

for range_data in score_ranges:
    print(f"\nGenerating for {range_data['name']} range...")
    create_toefl_content(
        score=range_data['score'],
        reading=range_data['r'],
        listening=range_data['l'],
        speaking=range_data['s'],
        writing=range_data['w'],
        fetch_background=False
    )
```

Run:
```bash
python create_series.py
```

### Workflow 4: Multilingual Content

While the tool generates in English, you can translate:

1. Generate English content
2. Use translation services for captions
3. Keep hashtags in English (better reach)
4. Maintain image as is (universal appeal)

Example for French:
```bash
# Generate
python main.py --score 110

# Then manually translate the content files
# Keep hashtags: #TOEFL #TOEFLPrep work in all languages
```

## Tips for Maximum Engagement

### Visual Optimization

**Do:**
- ✅ Use high-resolution images
- ✅ Ensure text is readable on mobile
- ✅ Maintain consistent branding
- ✅ Use contrasting colors for text

**Don't:**
- ❌ Overcrowd the infographic
- ❌ Use too many fonts
- ❌ Make text too small
- ❌ Skip alt text

### Content Optimization

**Do:**
- ✅ Personalize the generated content
- ✅ Add your authentic story
- ✅ Include specific study resources
- ✅ Engage with commenters

**Don't:**
- ❌ Post the same content on all platforms simultaneously
- ❌ Use all generated content without review
- ❌ Ignore comments
- ❌ Over-hashtag on Twitter

### Hashtag Strategy

**Research:**
```bash
# Check hashtag analysis
cat outputs/content/toefl_hashtags_110.json
```

**Strategy:**
- Use all platform-specific hashtags
- Mix popular and niche hashtags
- Create branded hashtag: #MyGroupeBMJourney
- Track performance of each hashtag

**Platform limits:**
- Instagram: Use all 30
- Twitter: Use 3-5 (max readability)
- LinkedIn: Use 5-10
- Facebook: Use 10-15

### Engagement Tactics

**First Hour:**
- Reply to every comment
- Like relevant comments
- Ask follow-up questions
- Share to Stories

**First Day:**
- Cross-promote on other platforms
- Share in relevant groups
- Tag study partners
- Create engagement posts (polls, questions)

**First Week:**
- Analyze metrics
- Respond to DMs
- Create follow-up content
- Thank sharers

### Content Calendar

**Example 4-week campaign:**

**Week 1: Announcement**
- Monday: LinkedIn post
- Wednesday: Instagram post
- Thursday: Twitter thread
- Friday: Facebook post

**Week 2: Deep Dive**
- Detailed study tips (one per platform)
- Behind-the-scenes Stories
- Q&A session

**Week 3: University Focus**
- Highlight target universities
- Application tips
- Success stories

**Week 4: Community**
- Feature other test-takers
- Study group formation
- Resource sharing

## Troubleshooting Scenarios

### Scenario 1: Low Engagement

**Diagnosis:**
- Wrong posting time
- Poor hashtag selection
- Not engaging with audience

**Solution:**
```bash
# Generate new version with trending keywords
python main.py --score 110

# Update hashtags in templates.json with trending ones
# Repost at optimal time
# Engage in first hour
```

### Scenario 2: Image Quality Issues

**Diagnosis:**
- Blurry on mobile
- Text too small
- Poor color contrast

**Solution:**
- Edit `config/config.json` to increase font sizes
- Adjust colors for better contrast
- Regenerate images

### Scenario 3: Platform Rejection

**Diagnosis:**
- Too many hashtags (Twitter)
- Content too long
- Image dimensions wrong

**Solution:**
- Check platform-specific limits
- Edit content files before posting
- Use platform-appropriate image size

## Measuring Success

### Key Metrics to Track

**Engagement Rate:**
- Likes + Comments + Shares / Followers
- Target: 2-5% for good engagement

**Reach:**
- How many people saw your post
- Track hashtag performance

**Conversions:**
- DMs received
- Study group sign-ups
- Groupe BM inquiries

### Tools for Analytics

- **LinkedIn**: Native analytics
- **Instagram**: Insights (business account)
- **Twitter**: Twitter Analytics
- **Facebook**: Page Insights

### Optimization Cycle

```
Generate → Post → Measure → Analyze → Adjust → Repeat
```

**Example:**
```bash
# Week 1: Original
python main.py --score 110

# Measure: 500 impressions, 2% engagement

# Week 2: Adjusted (better posting time, more hashtags)
python main.py --score 110
# Edit templates.json with insights

# Measure: 1000 impressions, 4% engagement

# Week 3: Optimized
# Continue refining based on data
```

## Conclusion

This tool provides a foundation for professional social media content. The key to success is:

1. **Consistency**: Post regularly
2. **Authenticity**: Add your personal touch
3. **Engagement**: Interact with your audience
4. **Analysis**: Track what works
5. **Adaptation**: Continuously improve

Remember: The generated content is a starting point. Your personal story and engagement are what truly drive results!

---

**Questions?** Review the main README.md or check the code comments for detailed information.

**Need help?** Contact Groupe BM support team.

**Happy posting! 🚀**
