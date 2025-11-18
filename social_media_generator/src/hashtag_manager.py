"""
Hashtag manager for social media posts
"""
from typing import List, Dict, Set
import random


class HashtagManager:
    """Manage and suggest hashtags for different platforms and test types"""

    def __init__(self):
        """Initialize hashtag manager with predefined hashtag sets"""
        self.hashtags = {
            'TOEFL': {
                'primary': [
                    '#TOEFL',
                    '#TOEFLPrep',
                    '#TOEFLPreparation',
                    '#TOEFLScore',
                    '#TOEFLTest',
                    '#TOEFLiBT'
                ],
                'study_related': [
                    '#StudyAbroad',
                    '#InternationalStudent',
                    '#InternationalStudents',
                    '#TestPrep',
                    '#TestPreparation',
                    '#EnglishLearning',
                    '#EnglishTest',
                    '#ESL',
                    '#StudyInUSA',
                    '#StudyInUK'
                ],
                'achievement': [
                    '#SuccessStory',
                    '#AchievementUnlocked',
                    '#Goals',
                    '#Success',
                    '#Milestone',
                    '#Accomplished',
                    '#DreamBig'
                ],
                'education': [
                    '#HigherEducation',
                    '#UniversityAdmissions',
                    '#CollegeAdmissions',
                    '#GraduateSchool',
                    '#EducationGoals',
                    '#AcademicSuccess',
                    '#StudentLife',
                    '#FutureStudent'
                ],
                'company': [
                    '#GroupeBM'
                ]
            },
            'GRE': {
                'primary': [
                    '#GRE',
                    '#GREPrep',
                    '#GRETest',
                    '#GREScore',
                    '#GREPreparation'
                ],
                'study_related': [
                    '#GraduateSchool',
                    '#GradSchool',
                    '#TestPrep',
                    '#StudyAbroad',
                    '#InternationalStudent'
                ],
                'achievement': [
                    '#SuccessStory',
                    '#Goals',
                    '#Success',
                    '#Milestone'
                ],
                'education': [
                    '#HigherEducation',
                    '#MastersProgram',
                    '#PhDJourney',
                    '#AcademicSuccess'
                ],
                'company': [
                    '#GroupeBM'
                ]
            },
            'GMAT': {
                'primary': [
                    '#GMAT',
                    '#GMATPrep',
                    '#GMATScore',
                    '#GMATTest'
                ],
                'study_related': [
                    '#BusinessSchool',
                    '#MBA',
                    '#MBAJourney',
                    '#TestPrep'
                ],
                'achievement': [
                    '#SuccessStory',
                    '#Goals',
                    '#Success'
                ],
                'education': [
                    '#HigherEducation',
                    '#BusinessEducation',
                    '#MBAAdmissions'
                ],
                'company': [
                    '#GroupeBM'
                ]
            },
            'IELTS': {
                'primary': [
                    '#IELTS',
                    '#IELTSPrep',
                    '#IELTSScore',
                    '#IELTSTest',
                    '#IELTSPreparation'
                ],
                'study_related': [
                    '#StudyAbroad',
                    '#InternationalStudent',
                    '#EnglishTest',
                    '#TestPrep',
                    '#StudyInUK',
                    '#StudyInCanada',
                    '#StudyInAustralia'
                ],
                'achievement': [
                    '#SuccessStory',
                    '#Goals',
                    '#Success',
                    '#Milestone'
                ],
                'education': [
                    '#HigherEducation',
                    '#UniversityAdmissions',
                    '#AcademicSuccess'
                ],
                'company': [
                    '#GroupeBM'
                ]
            }
        }

        # Platform-specific hashtag limits
        self.platform_limits = {
            'instagram': 30,
            'twitter': 5,
            'linkedin': 10,
            'facebook': 15
        }

    def get_hashtags_for_test(
        self,
        test_type: str,
        platform: str = 'instagram',
        include_trending: bool = True
    ) -> List[str]:
        """
        Get recommended hashtags for a specific test and platform

        Args:
            test_type: Type of test (TOEFL, GRE, GMAT, IELTS)
            platform: Target platform
            include_trending: Whether to include trending educational hashtags

        Returns:
            List of recommended hashtags
        """
        test_type = test_type.upper()
        if test_type not in self.hashtags:
            test_type = 'TOEFL'  # Default

        hashtag_sets = self.hashtags[test_type]
        limit = self.platform_limits.get(platform, 10)

        # Combine hashtags with priority
        selected = []

        # Always include all primary hashtags
        selected.extend(hashtag_sets['primary'])

        # Add company hashtag
        selected.extend(hashtag_sets['company'])

        # Calculate remaining slots
        remaining = limit - len(selected)

        # Distribute remaining slots
        if remaining > 0:
            # Add from other categories
            pool = []
            pool.extend(hashtag_sets['study_related'][:3])
            pool.extend(hashtag_sets['achievement'][:2])
            pool.extend(hashtag_sets['education'][:2])

            # Add trending if requested
            if include_trending:
                trending = self.get_trending_education_hashtags()
                pool.extend(trending[:2])

            # Randomly select from pool
            random.shuffle(pool)
            selected.extend(pool[:remaining])

        return selected[:limit]

    def get_trending_education_hashtags(self) -> List[str]:
        """Get currently trending education-related hashtags"""
        return [
            '#EducationMatters',
            '#FutureLeader',
            '#LearnAndGrow',
            '#HigherEd',
            '#StudentSuccess',
            '#AcademicExcellence',
            '#EducationFirst',
            '#KnowledgeIsPower'
        ]

    def format_hashtags(
        self,
        hashtags: List[str],
        platform: str = 'instagram',
        as_string: bool = True
    ) -> str or List[str]:
        """
        Format hashtags for a specific platform

        Args:
            hashtags: List of hashtags (with or without #)
            platform: Target platform
            as_string: Return as single string or list

        Returns:
            Formatted hashtags as string or list
        """
        # Ensure hashtags start with #
        formatted = [f"#{tag.lstrip('#')}" for tag in hashtags]

        # Platform-specific formatting
        if platform == 'twitter':
            # Twitter: space-separated on same line
            separator = ' '
        elif platform == 'linkedin':
            # LinkedIn: space-separated
            separator = ' '
        elif platform == 'instagram':
            # Instagram: can be on multiple lines or same line
            separator = ' '
        else:
            # Default: space-separated
            separator = ' '

        if as_string:
            return separator.join(formatted)
        return formatted

    def generate_custom_hashtags(
        self,
        keywords: List[str],
        max_count: int = 5
    ) -> List[str]:
        """
        Generate custom hashtags from keywords

        Args:
            keywords: List of keywords to convert to hashtags
            max_count: Maximum number of hashtags to generate

        Returns:
            List of hashtags
        """
        hashtags = []
        for keyword in keywords[:max_count]:
            # Remove spaces and special characters
            clean = ''.join(e for e in keyword if e.isalnum() or e == ' ')
            # Convert to camelCase
            words = clean.split()
            if words:
                hashtag = '#' + words[0].capitalize() + ''.join(w.capitalize() for w in words[1:])
                hashtags.append(hashtag)

        return hashtags

    def get_all_platform_hashtags(
        self,
        test_type: str = 'TOEFL'
    ) -> Dict[str, List[str]]:
        """
        Get hashtags for all platforms

        Returns:
            Dictionary mapping platform names to hashtag lists
        """
        return {
            'instagram': self.get_hashtags_for_test(test_type, 'instagram'),
            'twitter': self.get_hashtags_for_test(test_type, 'twitter'),
            'linkedin': self.get_hashtags_for_test(test_type, 'linkedin'),
            'facebook': self.get_hashtags_for_test(test_type, 'facebook')
        }

    def analyze_hashtag_effectiveness(
        self,
        hashtags: List[str]
    ) -> Dict[str, any]:
        """
        Analyze hashtag effectiveness (simplified version)

        Returns:
            Dictionary with analysis metrics
        """
        return {
            'total_count': len(hashtags),
            'has_branded': any('GroupeBM' in tag for tag in hashtags),
            'has_primary': any(tag in ['#TOEFL', '#GRE', '#GMAT', '#IELTS'] for tag in hashtags),
            'diversity_score': len(set(tag.lower() for tag in hashtags)) / len(hashtags) if hashtags else 0,
            'recommendations': self._get_recommendations(hashtags)
        }

    def _get_recommendations(self, hashtags: List[str]) -> List[str]:
        """Get recommendations for improving hashtag selection"""
        recommendations = []

        if len(hashtags) < 5:
            recommendations.append("Consider adding more hashtags to increase reach")

        if not any('GroupeBM' in tag for tag in hashtags):
            recommendations.append("Add branded hashtag #GroupeBM for brand awareness")

        if len(hashtags) > 30:
            recommendations.append("Instagram allows max 30 hashtags - you may want to reduce")

        return recommendations
