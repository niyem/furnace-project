"""
Content generator for social media platforms
"""
from typing import Dict, List, Any
import random
from .utils import load_templates, load_config, save_text, save_json


class ContentGenerator:
    """Generate platform-specific social media content"""

    def __init__(self):
        """Initialize the content generator"""
        self.templates = load_templates()
        self.config = load_config()

    def format_study_tips(self, tips: List[str], style: str = "full") -> str:
        """
        Format study tips based on style

        Args:
            tips: List of study tips
            style: Style of formatting (full, short, tweet)

        Returns:
            Formatted study tips string
        """
        if style == "full":
            return "\n".join([f"• {tip}" for tip in tips])
        elif style == "short":
            return "\n".join(tips)
        elif style == "tweet":
            return "\n".join([f"→ {tip}" for tip in tips[:3]])  # Max 3 for tweets
        return "\n".join(tips)

    def format_university_list(self, universities: Dict[str, str]) -> str:
        """Format university list for display"""
        selected = list(universities.items())[:5]  # Top 5
        return "\n".join([f"• {name}: {req}" for name, req in selected])

    def generate_linkedin_post(
        self,
        score: int,
        max_score: int,
        sections: Dict[str, int],
        universities: Dict[str, str],
        custom_tips: List[str] = None
    ) -> Dict[str, str]:
        """Generate LinkedIn post content"""
        template = self.templates['linkedin']
        tips = custom_tips or self.templates['study_tips']

        content = template['template'].format(
            score=score,
            reading=sections.get('Reading', 0),
            listening=sections.get('Listening', 0),
            speaking=sections.get('Speaking', 0),
            writing=sections.get('Writing', 0),
            university_list=self.format_university_list(universities),
            study_tips=self.format_study_tips(tips, style="full"),
            company_name=self.config['company_name'],
            cta=template['cta'],
            hashtags=template['hashtags']
        )

        # Generate alt text
        alt_text = (
            f"TOEFL score infographic showing {score}/{max_score} total score. "
            f"Section scores - Reading: {sections.get('Reading', 0)}, "
            f"Listening: {sections.get('Listening', 0)}, "
            f"Speaking: {sections.get('Speaking', 0)}, "
            f"Writing: {sections.get('Writing', 0)}. "
            f"Exceeds requirements for top universities."
        )

        return {
            'content': content,
            'alt_text': alt_text,
            'character_count': len(content),
            'platform': 'LinkedIn'
        }

    def generate_instagram_post(
        self,
        score: int,
        max_score: int,
        sections: Dict[str, int],
        universities: Dict[str, str],
        custom_tips: List[str] = None
    ) -> Dict[str, str]:
        """Generate Instagram post content"""
        template = self.templates['instagram']
        tips = custom_tips or self.templates['study_tips_short']

        content = template['template'].format(
            score=score,
            reading=sections.get('Reading', 0),
            listening=sections.get('Listening', 0),
            speaking=sections.get('Speaking', 0),
            writing=sections.get('Writing', 0),
            study_tips_short=self.format_study_tips(tips, style="short"),
            cta=template['cta'],
            hashtags=template['hashtags']
        )

        alt_text = (
            f"TOEFL score achievement post: {score} out of {max_score}. "
            f"Reading {sections.get('Reading', 0)}, "
            f"Listening {sections.get('Listening', 0)}, "
            f"Speaking {sections.get('Speaking', 0)}, "
            f"Writing {sections.get('Writing', 0)}. "
            f"Study abroad success story."
        )

        return {
            'content': content,
            'alt_text': alt_text,
            'character_count': len(content),
            'platform': 'Instagram'
        }

    def generate_twitter_post(
        self,
        score: int,
        max_score: int,
        sections: Dict[str, int],
        universities: Dict[str, str],
        custom_tips: List[str] = None,
        as_thread: bool = True
    ) -> Dict[str, Any]:
        """Generate Twitter/X post content"""
        template = self.templates['twitter']
        tips = custom_tips or self.templates['study_tips']

        if as_thread:
            # Generate thread
            thread_tweets = []
            for tweet_template in template['thread']:
                tweet = tweet_template.format(
                    score=score,
                    reading=sections.get('Reading', 0),
                    listening=sections.get('Listening', 0),
                    speaking=sections.get('Speaking', 0),
                    writing=sections.get('Writing', 0),
                    study_tips_tweet=self.format_study_tips(tips[:3], style="tweet"),
                    cta=template['cta'],
                    hashtags=template['hashtags']
                )
                thread_tweets.append(tweet)

            result = {
                'content': thread_tweets,
                'is_thread': True,
                'tweet_count': len(thread_tweets),
                'platform': 'Twitter/X'
            }
        else:
            # Single tweet
            content = template['template'].format(
                score=score,
                reading=sections.get('Reading', 0),
                listening=sections.get('Listening', 0),
                speaking=sections.get('Speaking', 0),
                writing=sections.get('Writing', 0),
                cta=template['cta'],
                hashtags=template['hashtags']
            )

            result = {
                'content': content,
                'is_thread': False,
                'character_count': len(content),
                'platform': 'Twitter/X'
            }

        return result

    def generate_facebook_post(
        self,
        score: int,
        max_score: int,
        sections: Dict[str, int],
        universities: Dict[str, str],
        custom_tips: List[str] = None
    ) -> Dict[str, str]:
        """Generate Facebook post content"""
        template = self.templates['facebook']
        tips = custom_tips or self.templates['study_tips']

        content = template['template'].format(
            score=score,
            reading=sections.get('Reading', 0),
            listening=sections.get('Listening', 0),
            speaking=sections.get('Speaking', 0),
            writing=sections.get('Writing', 0),
            university_list=self.format_university_list(universities),
            study_tips=self.format_study_tips(tips, style="full"),
            cta=template['cta'],
            hashtags=template['hashtags']
        )

        alt_text = (
            f"TOEFL achievement infographic: Score {score}/{max_score}. "
            f"Breakdown - Reading: {sections.get('Reading', 0)}/30, "
            f"Listening: {sections.get('Listening', 0)}/30, "
            f"Speaking: {sections.get('Speaking', 0)}/30, "
            f"Writing: {sections.get('Writing', 0)}/30. "
            f"Exceeds top university requirements."
        )

        return {
            'content': content,
            'alt_text': alt_text,
            'character_count': len(content),
            'platform': 'Facebook'
        }

    def generate_all_content(
        self,
        score: int,
        max_score: int,
        sections: Dict[str, int],
        universities: Dict[str, str],
        custom_tips: List[str] = None,
        twitter_as_thread: bool = True
    ) -> Dict[str, Dict]:
        """
        Generate content for all platforms

        Returns:
            Dictionary mapping platform names to content dictionaries
        """
        results = {
            'linkedin': self.generate_linkedin_post(score, max_score, sections, universities, custom_tips),
            'instagram': self.generate_instagram_post(score, max_score, sections, universities, custom_tips),
            'twitter': self.generate_twitter_post(score, max_score, sections, universities, custom_tips, twitter_as_thread),
            'facebook': self.generate_facebook_post(score, max_score, sections, universities, custom_tips)
        }

        return results

    def save_all_content(
        self,
        content_dict: Dict[str, Dict],
        test_type: str = "TOEFL",
        score: int = 0
    ):
        """Save all generated content to files"""
        # Save as JSON
        json_filename = f"{test_type.lower()}_content_{score}.json"
        save_json(content_dict, json_filename)

        # Save individual text files
        for platform, content_data in content_dict.items():
            filename = f"{test_type.lower()}_{platform}_{score}.txt"

            if content_data.get('is_thread'):
                # Save thread as numbered tweets
                thread_content = "\n\n---TWEET BREAK---\n\n".join(
                    [f"Tweet {i+1}:\n{tweet}" for i, tweet in enumerate(content_data['content'])]
                )
                save_text(thread_content, filename)
            else:
                text_content = content_data['content']
                if 'alt_text' in content_data:
                    text_content += f"\n\n---\nALT TEXT:\n{content_data['alt_text']}"
                save_text(text_content, filename)

        print(f"✅ Content saved for all platforms")
