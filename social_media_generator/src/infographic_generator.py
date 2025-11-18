"""
Infographic generator for test scores using Pillow
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import random
from .utils import load_config, hex_to_rgb, ensure_output_dirs
from .unsplash_client import UnsplashClient


class InfographicGenerator:
    """Generate professional infographics for test scores"""

    def __init__(self):
        """Initialize the infographic generator"""
        self.config = load_config()
        self.colors = {k: hex_to_rgb(v) for k, v in self.config['colors'].items()}
        self.output_dir = ensure_output_dirs() / "images"
        self.unsplash_client = UnsplashClient()

    def create_gradient_background(
        self,
        size: Tuple[int, int],
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int]
    ) -> Image.Image:
        """Create a gradient background"""
        base = Image.new('RGB', size, color1)
        top = Image.new('RGB', size, color2)

        mask = Image.new('L', size)
        mask_data = []
        for y in range(size[1]):
            for x in range(size[0]):
                mask_data.append(int(255 * (y / size[1])))
        mask.putdata(mask_data)

        base.paste(top, (0, 0), mask)
        return base

    def add_rounded_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        xy: Tuple[int, int, int, int],
        radius: int,
        fill: Tuple[int, int, int, int]
    ):
        """Draw a rounded rectangle"""
        x1, y1, x2, y2 = xy
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)

    def get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get a font with the specified size"""
        try:
            # Try to use Helvetica or Arial
            font_names = [
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]

            for font_name in font_names:
                try:
                    return ImageFont.truetype(font_name, size)
                except:
                    continue

            # Fallback to default
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()

    def draw_text_centered(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        y: int,
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int],
        width: int
    ):
        """Draw text centered horizontally"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font, fill=color)

    def create_score_infographic(
        self,
        test_type: str,
        total_score: int,
        max_score: int,
        sections: Dict[str, Dict[str, int]],
        universities: Dict[str, str],
        platform: str = "instagram",
        background_image_path: Optional[str] = None
    ) -> str:
        """
        Create a professional infographic for test scores

        Args:
            test_type: Type of test (TOEFL, GRE, GMAT, etc.)
            total_score: Total score achieved
            max_score: Maximum possible score
            sections: Dictionary of section scores {name: {"score": X, "max": Y}}
            universities: Dictionary of universities and their requirements
            platform: Target platform (instagram, linkedin, facebook, twitter)
            background_image_path: Optional path to background image

        Returns:
            Path to generated infographic
        """
        # Get dimensions for platform
        width, height = self.config['image_sizes'].get(platform, [1080, 1080])

        # Create base image
        if background_image_path and Path(background_image_path).exists():
            try:
                img = Image.open(background_image_path)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                # Add a semi-transparent overlay
                overlay = Image.new('RGBA', (width, height), (*self.colors['primary'], 200))
                img = img.convert('RGBA')
                img = Image.alpha_composite(img, overlay)
            except:
                img = self.create_gradient_background(
                    (width, height),
                    self.colors['primary'],
                    self.colors['secondary']
                )
        else:
            img = self.create_gradient_background(
                (width, height),
                self.colors['primary'],
                self.colors['secondary']
            )

        # Convert to RGB for saving as JPEG
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
            img = rgb_img

        draw = ImageDraw.Draw(img)

        # Fonts
        title_font = self.get_font(self.config['fonts']['title_size'], bold=True)
        score_font = self.get_font(self.config['fonts']['score_size'], bold=True)
        section_font = self.get_font(self.config['fonts']['section_size'], bold=True)
        uni_font = self.get_font(self.config['fonts']['university_size'])
        company_font = self.get_font(self.config['fonts']['company_size'], bold=True)

        current_y = 60

        # Draw title
        self.draw_text_centered(draw, f"{test_type} Score Achievement", current_y, title_font, self.colors['white'], width)
        current_y += 120

        # Draw main score in a card
        card_height = 180
        card_padding = 60
        card_width = width - (card_padding * 2)

        # Create semi-transparent white card
        card_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card_overlay)
        self.add_rounded_rectangle(
            card_draw,
            (card_padding, current_y, card_padding + card_width, current_y + card_height),
            30,
            (*self.colors['white'], 230)
        )

        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img = Image.alpha_composite(img, card_overlay)
        img = img.convert('RGB')
        draw = ImageDraw.Draw(img)

        # Draw score
        score_text = f"{total_score}/{max_score}"
        self.draw_text_centered(draw, score_text, current_y + 40, score_font, self.colors['primary'], width)

        current_y += card_height + 50

        # Draw section scores
        section_card_height = len(sections) * 70 + 60
        card_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card_overlay)
        self.add_rounded_rectangle(
            card_draw,
            (card_padding, current_y, card_padding + card_width, current_y + section_card_height),
            30,
            (*self.colors['white'], 230)
        )

        img = img.convert('RGBA')
        img = Image.alpha_composite(img, card_overlay)
        img = img.convert('RGB')
        draw = ImageDraw.Draw(img)

        current_y += 30

        # Section scores
        for section_name, scores in sections.items():
            section_text = f"{section_name}: {scores['score']}/{scores['max']}"
            bbox = draw.textbbox((0, 0), section_text, font=section_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, current_y), section_text, font=section_font, fill=self.colors['text_dark'])

            # Progress bar
            bar_width = 400
            bar_height = 12
            bar_x = (width - bar_width) // 2
            bar_y = current_y + 45

            # Background bar
            draw.rounded_rectangle(
                [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                radius=6,
                fill=self.colors['text_light']
            )

            # Progress bar
            progress = (scores['score'] / scores['max']) * bar_width
            draw.rounded_rectangle(
                [bar_x, bar_y, bar_x + int(progress), bar_y + bar_height],
                radius=6,
                fill=self.colors['accent']
            )

            current_y += 70

        current_y += 30

        # Draw universities
        if universities and len(universities) > 0:
            # Select top universities to display (max 4 to fit)
            selected_unis = list(universities.items())[:4]

            uni_card_height = len(selected_unis) * 50 + 80
            card_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            card_draw = ImageDraw.Draw(card_overlay)
            self.add_rounded_rectangle(
                card_draw,
                (card_padding, current_y, card_padding + card_width, current_y + uni_card_height),
                30,
                (*self.colors['accent'], 230)
            )

            img = img.convert('RGBA')
            img = Image.alpha_composite(img, card_overlay)
            img = img.convert('RGB')
            draw = ImageDraw.Draw(img)

            current_y += 25
            self.draw_text_centered(draw, "Exceeds Requirements For:", current_y, section_font, self.colors['text_dark'], width)
            current_y += 50

            for uni_name, requirement in selected_unis:
                uni_text = f"✓ {uni_name}: {requirement}"
                bbox = draw.textbbox((0, 0), uni_text, font=uni_font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, current_y), uni_text, font=uni_font, fill=self.colors['text_dark'])
                current_y += 50

        # Add company branding at bottom
        current_y = height - 80
        company_text = f"Powered by {self.config['company_name']}"
        self.draw_text_centered(draw, company_text, current_y, company_font, self.colors['white'], width)

        # Save image
        filename = f"{test_type.lower()}_{platform}_{total_score}.jpg"
        filepath = self.output_dir / filename
        img.save(filepath, 'JPEG', quality=95)

        print(f"✅ Infographic created: {filepath}")
        return str(filepath)

    def create_all_platform_infographics(
        self,
        test_type: str,
        total_score: int,
        max_score: int,
        sections: Dict[str, Dict[str, int]],
        universities: Dict[str, str],
        fetch_background: bool = True
    ) -> Dict[str, str]:
        """
        Create infographics for all platforms

        Returns:
            Dictionary mapping platform names to image file paths
        """
        results = {}

        # Fetch background image if requested
        background_path = None
        if fetch_background:
            temp_bg_path = self.output_dir / "temp_background.jpg"
            background_path = self.unsplash_client.fetch_random_image(
                query="university graduation success",
                orientation="landscape",
                save_path=temp_bg_path
            )

        # Generate for each platform
        for platform in ['instagram', 'linkedin', 'facebook', 'twitter']:
            filepath = self.create_score_infographic(
                test_type=test_type,
                total_score=total_score,
                max_score=max_score,
                sections=sections,
                universities=universities,
                platform=platform,
                background_image_path=background_path
            )
            results[platform] = filepath

        return results
