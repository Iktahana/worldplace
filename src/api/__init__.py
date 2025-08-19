"""
API Settings
"""
import os

__DEFAULT_ALLOWED_COLORS__ = [
    "#000000", "#ffffff", "#0000ff", "#ff0000", "#00ff00", "#ffff00", "#ff00ff", "#800080", "#808000", "#808080",
    "#c0c0c0", "#800000", "#ff00ff", "#00ffff", "#808080", "#c0c0c0", "#800080", "#ff0000", "#00ff00", "#ffff00",
    "#000000", "#ffffff", "#0000ff", "#ff0000", "#00ff00", "#ffff00", "#ff00ff", "#800080", "#808000", "#808080",
]

__BLOCKS_IN_RANGE_MAXIMUM__ = int(os.environ.get("API_BLOCKS_IN_RANGE_MAXIMUM", "1000000"))
__ALLOWED_COLORS__ = os.environ.get(
    "API_ALLOWED_COLORS",
    ",".join(__DEFAULT_ALLOWED_COLORS__)).replace(" ", "").strip(",")
