"""Color utilities and palettes."""

from typing import Dict, List, Optional, Tuple
import colorsys


class ColorManager:
    """Manages color assignment for different tracks/subjects.
    
    This class provides automatic color assignment from a curated
    palette of visually distinct colors, with support for custom
    color assignment and color manipulation utilities.
    """
    
    def __init__(self):
        """Initialize color manager with default palette."""
        # Curated palette of visually distinct colors
        self.default_palette = [
            "#FF6B6B",  # Red
            "#4ECDC4",  # Teal
            "#45B7D1",  # Sky blue
            "#96CEB4",  # Sage green
            "#FECA57",  # Yellow
            "#FF6B9D",  # Pink
            "#C44569",  # Rose
            "#786FA6",  # Purple
            "#FD79A8",  # Light pink
            "#A29BFE",  # Lavender
            "#74B9FF",  # Light blue
            "#55A3FF",  # Blue
            "#FDA7DF",  # Coral
            "#FDCB6E",  # Orange
            "#6C5CE7",  # Violet
            "#00B894",  # Mint
            "#E17055",  # Terra cotta
            "#00CEC9",  # Robin egg blue
            "#FF7675",  # Light red
            "#81ECEC",  # Light cyan
        ]
        
        # Color assignments
        self.assigned_colors: Dict[str, str] = {}
        self.color_index = 0
        
        # Named color schemes
        self.color_schemes = {
            "default": self.default_palette,
            "rainbow": self._generate_rainbow_palette(20),
            "monochrome": self._generate_monochrome_palette(20),
            "warm": self._generate_warm_palette(20),
            "cool": self._generate_cool_palette(20),
        }
        
        self.active_scheme = "default"
    
    def get_track_color(self, track_id: str) -> str:
        """Get a consistent color for a track ID.
        
        Args:
            track_id: Unique track identifier.
            
        Returns:
            Hex color string.
        """
        if track_id not in self.assigned_colors:
            palette = self.color_schemes[self.active_scheme]
            color = palette[self.color_index % len(palette)]
            self.assigned_colors[track_id] = color
            self.color_index += 1
        return self.assigned_colors[track_id]
    
    def set_track_color(self, track_id: str, color: str):
        """Manually set a color for a track.
        
        Args:
            track_id: Track identifier.
            color: Hex color string.
        """
        self.assigned_colors[track_id] = color
    
    def reset_assignments(self):
        """Clear all color assignments."""
        self.assigned_colors.clear()
        self.color_index = 0
    
    def set_color_scheme(self, scheme: str):
        """Set the active color scheme.
        
        Args:
            scheme: Scheme name ("default", "rainbow", etc.).
            
        Raises:
            ValueError: If scheme not found.
        """
        if scheme not in self.color_schemes:
            raise ValueError(
                f"Unknown color scheme '{scheme}'. "
                f"Available: {list(self.color_schemes.keys())}"
            )
        self.active_scheme = scheme
    
    def add_custom_scheme(self, name: str, colors: List[str]):
        """Add a custom color scheme.
        
        Args:
            name: Scheme name.
            colors: List of hex color strings.
        """
        self.color_schemes[name] = colors
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple (0-1 range).
        
        Args:
            hex_color: Hex color string (e.g., "#FF6B6B").
            
        Returns:
            Tuple of (r, g, b) in 0-1 range.
        """
        # Remove # if present
        hex_color = hex_color.lstrip("#")
        
        # Convert to RGB
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        return (r, g, b)
    
    @staticmethod
    def rgb_to_hex(r: float, g: float, b: float) -> str:
        """Convert RGB to hex color string.
        
        Args:
            r: Red component (0-1).
            g: Green component (0-1).
            b: Blue component (0-1).
            
        Returns:
            Hex color string.
        """
        r_int = int(r * 255)
        g_int = int(g * 255)
        b_int = int(b * 255)
        return f"#{r_int:02x}{g_int:02x}{b_int:02x}"
    
    @staticmethod
    def adjust_brightness(hex_color: str, factor: float) -> str:
        """Adjust color brightness.
        
        Args:
            hex_color: Input color.
            factor: Brightness factor (< 1 darker, > 1 brighter).
            
        Returns:
            Adjusted hex color.
        """
        r, g, b = ColorManager.hex_to_rgb(hex_color)
        
        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        # Adjust value (brightness)
        v = min(1.0, max(0.0, v * factor))
        
        # Convert back to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        
        return ColorManager.rgb_to_hex(r, g, b)
    
    @staticmethod
    def adjust_saturation(hex_color: str, factor: float) -> str:
        """Adjust color saturation.
        
        Args:
            hex_color: Input color.
            factor: Saturation factor (< 1 less saturated, > 1 more saturated).
            
        Returns:
            Adjusted hex color.
        """
        r, g, b = ColorManager.hex_to_rgb(hex_color)
        
        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        # Adjust saturation
        s = min(1.0, max(0.0, s * factor))
        
        # Convert back to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        
        return ColorManager.rgb_to_hex(r, g, b)
    
    def _generate_rainbow_palette(self, n_colors: int) -> List[str]:
        """Generate rainbow color palette.
        
        Args:
            n_colors: Number of colors to generate.
            
        Returns:
            List of hex colors.
        """
        colors = []
        for i in range(n_colors):
            hue = i / n_colors
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            colors.append(self.rgb_to_hex(*rgb))
        return colors
    
    def _generate_monochrome_palette(self, n_colors: int) -> List[str]:
        """Generate monochrome palette.
        
        Args:
            n_colors: Number of colors to generate.
            
        Returns:
            List of hex colors.
        """
        colors = []
        for i in range(n_colors):
            # Vary brightness from light to dark
            value = 0.3 + (0.6 * (i / (n_colors - 1)))
            rgb = (value, value, value)
            colors.append(self.rgb_to_hex(*rgb))
        return colors
    
    def _generate_warm_palette(self, n_colors: int) -> List[str]:
        """Generate warm color palette.
        
        Args:
            n_colors: Number of colors to generate.
            
        Returns:
            List of hex colors.
        """
        colors = []
        for i in range(n_colors):
            # Warm hues: red to yellow (0.0 to 0.16)
            hue = (i / n_colors) * 0.16
            # Vary saturation and value
            sat = 0.6 + (0.4 * ((i % 3) / 2))
            val = 0.7 + (0.3 * ((i % 5) / 4))
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            colors.append(self.rgb_to_hex(*rgb))
        return colors
    
    def _generate_cool_palette(self, n_colors: int) -> List[str]:
        """Generate cool color palette.
        
        Args:
            n_colors: Number of colors to generate.
            
        Returns:
            List of hex colors.
        """
        colors = []
        for i in range(n_colors):
            # Cool hues: cyan to blue to purple (0.5 to 0.75)
            hue = 0.5 + (i / n_colors) * 0.25
            # Vary saturation and value
            sat = 0.5 + (0.5 * ((i % 3) / 2))
            val = 0.6 + (0.4 * ((i % 5) / 4))
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            colors.append(self.rgb_to_hex(*rgb))
        return colors
    
    def get_keypoint_gradient(
        self,
        track_color: str,
        n_keypoints: int,
        gradient_type: str = "brightness"
    ) -> List[str]:
        """Generate gradient colors for keypoints.
        
        Args:
            track_color: Base track color.
            n_keypoints: Number of keypoints.
            gradient_type: "brightness", "saturation", or "hue".
            
        Returns:
            List of colors for each keypoint.
        """
        if n_keypoints == 1:
            return [track_color]
        
        colors = []
        
        if gradient_type == "brightness":
            # Vary from bright to slightly darker
            for i in range(n_keypoints):
                factor = 0.7 + (0.3 * (i / (n_keypoints - 1)))
                colors.append(self.adjust_brightness(track_color, factor))
                
        elif gradient_type == "saturation":
            # Vary saturation
            for i in range(n_keypoints):
                factor = 0.5 + (0.5 * (i / (n_keypoints - 1)))
                colors.append(self.adjust_saturation(track_color, factor))
                
        elif gradient_type == "hue":
            # Slight hue shift
            r, g, b = self.hex_to_rgb(track_color)
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            for i in range(n_keypoints):
                # Shift hue slightly
                h_shift = -0.05 + (0.1 * (i / (n_keypoints - 1)))
                new_h = (h + h_shift) % 1.0
                rgb = colorsys.hsv_to_rgb(new_h, s, v)
                colors.append(self.rgb_to_hex(*rgb))
        
        return colors