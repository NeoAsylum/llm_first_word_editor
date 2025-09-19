from pydantic import BaseModel
from typing import Optional, List
import html

class Paragraph(BaseModel):
    content: str
    bold: bool = False
    italic: bool = False
    lowerscript: bool = False
    superscript: bool = False

    def find(self, text: str) -> List[int]:
        if not text:
            return []
        
        indices = []
        start_index = 0
        while True:
            pos = self.content.find(text, start_index)
            if pos == -1:
                break
            indices.append(pos)
            start_index = pos + 1
        return indices

    def to_html(self) -> str:
        text = html.escape(self.content)
        if self.bold:
            text = f"<b>{text}</b>"
        if self.italic:
            text = f"<i>{text}</i>"
        if self.lowerscript:
            text = f"<sub>{text}</sub>"
        if self.superscript:
            text = f"<sup>{text}</sup>"
        return text
