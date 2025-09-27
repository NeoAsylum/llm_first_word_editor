from enum import Enum

class FormattingType(Enum):
    BOLD = "bold"
    ITALIC = "italic"
    LOWERSCRIPT = "lowerscript"
    SUPERSCRIPT = "superscript"
    TITLE = "title"
    HEADING = "heading"
    SUBHEADING = "subheading"
    BODY = "body"

class MarginType(Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
