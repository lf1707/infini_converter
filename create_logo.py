#!/usr/bin/env python3
"""
Create a simple logo for Infini Converter
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    """Create a simple logo for Infini Converter"""
    # Create a 200x60 image with a gradient background
    width, height = 200, 60
    image = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Create gradient background
    for y in range(height):
        color_value = int(255 * (y / height))
        color = (color_value, color_value, 255)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Draw icon (infinity symbol)
    center_x, center_y = 40, height // 2
    icon_radius = 15
    # Left circle
    draw.ellipse([center_x - icon_radius, center_y - icon_radius//2, 
                  center_x, center_y + icon_radius//2], fill=(255, 255, 255))
    # Right circle
    draw.ellipse([center_x, center_y - icon_radius//2, 
                  center_x + icon_radius, center_y + icon_radius//2], fill=(255, 255, 255))
    
    # Add text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    text = "Infini Converter"
    text_position = (70, height // 2 - 10)
    draw.text(text_position, text, fill=(255, 255, 255), font=font)
    
    # Save the logo
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    image.save(logo_path)
    print(f"Logo created at: {logo_path}")
    
    return logo_path

if __name__ == "__main__":
    create_logo()