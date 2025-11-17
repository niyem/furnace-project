"""
Utility functions for the social media generator
"""
import json
import os
from typing import Dict, Any, Tuple
from pathlib import Path


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config" / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_templates() -> Dict[str, Any]:
    """Load content templates from templates.json"""
    templates_path = Path(__file__).parent.parent / "config" / "templates.json"
    with open(templates_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def ensure_output_dirs():
    """Ensure output directories exist"""
    output_base = Path(__file__).parent.parent / "outputs"
    (output_base / "images").mkdir(parents=True, exist_ok=True)
    (output_base / "content").mkdir(parents=True, exist_ok=True)
    return output_base


def calculate_grade(score: int, max_score: int) -> str:
    """Calculate grade based on percentage"""
    percentage = (score / max_score) * 100
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B+"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C+"
    else:
        return "C"


def get_performance_level(score: int, max_score: int) -> str:
    """Get performance level description"""
    percentage = (score / max_score) * 100
    if percentage >= 90:
        return "Excellent"
    elif percentage >= 80:
        return "Very Good"
    elif percentage >= 70:
        return "Good"
    elif percentage >= 60:
        return "Satisfactory"
    else:
        return "Needs Improvement"


def save_json(data: Dict[str, Any], filename: str, subfolder: str = "content"):
    """Save data as JSON file"""
    output_base = ensure_output_dirs()
    filepath = output_base / subfolder / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def save_text(content: str, filename: str, subfolder: str = "content"):
    """Save content as text file"""
    output_base = ensure_output_dirs()
    filepath = output_base / subfolder / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath
