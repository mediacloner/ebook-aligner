"""
Configuration module for bilingual EPUB generation.

This module provides configuration options for controlling the layout, styling,
and formatting of bilingual ebooks.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class LayoutMode(Enum):
    """Layout modes for bilingual text presentation."""
    BELOW = "below"           # Spanish below English (default)
    ABOVE = "above"           # Spanish above English
    SIDE_BY_SIDE = "side"     # Table-based side-by-side columns
    SPANISH_ONLY = "only"     # Replace English with Spanish only
    
    @classmethod
    def from_string(cls, value: str) -> 'LayoutMode':
        """Create LayoutMode from string value."""
        value = value.lower()
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"Invalid layout mode: {value}. Must be one of: {[m.value for m in cls]}")


class StyleMode(Enum):
    """Styling approaches for bilingual content."""
    CLASS_BASED = "class"     # Use CSS classes (default, backward compatible)
    INLINE = "inline"         # Use inline styles (conflict-free)
    HYBRID = "hybrid"         # Inline colors + class for other styles


@dataclass
class BilingualConfig:
    """Configuration for bilingual EPUB generation."""
    
    # Layout options
    layout_mode: LayoutMode = LayoutMode.BELOW
    
    # Side-by-side layout options
    column_gap_percentage: int = 10  # Gap between columns (5-30%)
    left_column_language: str = "english"  # "english" or "spanish"
    
    # Styling options
    style_mode: StyleMode = StyleMode.CLASS_BASED
    original_color: Optional[str] = None  # e.g., "#000000" or None
    translation_color: Optional[str] = None  # e.g., "#555555" or None
    
    # Separator options (for BELOW/ABOVE modes)
    use_br_separator: bool = True  # Use <br> vs separate paragraphs
    separator_class: str = "bilingual-separator"
    
    # Translation class (for backward compatibility)
    translation_class: str = "es-trans"
    
    # Advanced options (Phase 4)
    preserve_line_breaks: bool = False  # Enable line-break-aware alignment
    element_type_formatting: bool = False  # Use element-specific formatting
    use_placeholder_system: bool = True  # Reserve complex elements (SVG, Math, Code)
    
    # Filter captions (existing functionality)
    filter_captions: bool = True
    
    def validate(self):
        """Validate configuration values."""
        if not 5 <= self.column_gap_percentage <= 30:
            raise ValueError("column_gap_percentage must be between 5 and 30")
        
        if self.left_column_language not in ("english", "spanish"):
            raise ValueError("left_column_language must be 'english' or 'spanish'")
        
        if self.original_color and not self._is_valid_color(self.original_color):
            raise ValueError(f"Invalid original_color: {self.original_color}")
        
        if self.translation_color and not self._is_valid_color(self.translation_color):
            raise ValueError(f"Invalid translation_color: {self.translation_color}")
    
    @staticmethod
    def _is_valid_color(color: str) -> bool:
        """Check if color is valid hex or named color."""
        if color.startswith('#'):
            return len(color) in (4, 7) and all(c in '0123456789abcdefABCDEF' for c in color[1:])
        # Allow named colors
        return color.isalpha()
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            'layout_mode': self.layout_mode.value,
            'column_gap_percentage': self.column_gap_percentage,
            'left_column_language': self.left_column_language,
            'style_mode': self.style_mode.value,
            'original_color': self.original_color,
            'translation_color': self.translation_color,
            'use_br_separator': self.use_br_separator,
            'separator_class': self.separator_class,
            'translation_class': self.translation_class,
            'preserve_line_breaks': self.preserve_line_breaks,
            'element_type_formatting': self.element_type_formatting,
            'filter_captions': self.filter_captions,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BilingualConfig':
        """Create config from dictionary."""
        config_data = data.copy()
        
        # Convert string to enum
        if 'layout_mode' in config_data and isinstance(config_data['layout_mode'], str):
            config_data['layout_mode'] = LayoutMode.from_string(config_data['layout_mode'])
        
        if 'style_mode' in config_data and isinstance(config_data['style_mode'], str):
            style_value = config_data['style_mode'].lower()
            config_data['style_mode'] = StyleMode[style_value.upper()]
        
        return cls(**config_data)


# Default configuration
DEFAULT_CONFIG = BilingualConfig()


# Preset configurations for common use cases
PRESETS = {
    'default': BilingualConfig(
        layout_mode=LayoutMode.BELOW,
        style_mode=StyleMode.CLASS_BASED,
    ),
    
    'side_by_side': BilingualConfig(
        layout_mode=LayoutMode.SIDE_BY_SIDE,
        column_gap_percentage=10,
        left_column_language="english",
        style_mode=StyleMode.CLASS_BASED,
    ),
    
    'color_coded': BilingualConfig(
        layout_mode=LayoutMode.BELOW,
        style_mode=StyleMode.INLINE,
        original_color="#000000",
        translation_color="#555555",
    ),
    
    'spanish_first': BilingualConfig(
        layout_mode=LayoutMode.ABOVE,
        style_mode=StyleMode.CLASS_BASED,
    ),
    
    'spanish_only': BilingualConfig(
        layout_mode=LayoutMode.SPANISH_ONLY,
        style_mode=StyleMode.CLASS_BASED,
    ),
    
    'learner_mode': BilingualConfig(
        layout_mode=LayoutMode.SIDE_BY_SIDE,
        column_gap_percentage=15,
        left_column_language="spanish",  # Native language on left
        style_mode=StyleMode.INLINE,
        original_color="#000000",
        translation_color="#0066cc",  # Blue for learning language
    ),
}


def get_preset(name: str) -> BilingualConfig:
    """Get a preset configuration by name."""
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}. Available: {list(PRESETS.keys())}")
    return PRESETS[name]
