from pydantic import BaseModel
from typing import Optional, List
import html
import re
import logging

logging.basicConfig(
    filename="paragraph_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s"
)


class Paragraph(BaseModel):
    content: str
    bold: bool = False
    italic: bool = False
    lowerscript: bool = False
    superscript: bool = False

    def delete(self, index: int, length: int):
        self.content = self.content.replace(self.content[index : index + length], "")

    def insert(self, text: str, index: int):
        self.content = self.content[:index] + text + self.content[index:]

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
        logging.info(f"Processing content: {self.content}")
        text = html.escape(self.content)
        text = re.sub(r"\n+", "<br>", text)
        if self.bold:
            text = f"<b>{text}</b>"
        if self.italic:
            text = f"<i>{text}</i>"
        if self.lowerscript:
            text = f"<sub>{text}</sub>"
        if self.superscript:
            text = f"<sup>{text}</sup>"
        return text

    def can_merge_with(self, other: "Paragraph") -> bool:
        return (
            self.bold == other.bold
            and self.italic == other.italic
            and self.lowerscript == other.lowerscript
            and self.superscript == other.superscript
        )

    def merge(self, other: "Paragraph"):
        self.content += other.content
