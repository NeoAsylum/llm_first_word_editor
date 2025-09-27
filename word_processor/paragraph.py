from pydantic import BaseModel
from typing import Optional, List
import html
import re
import logging

logging.basicConfig(
    filename="paragraph_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s"
)


class Paragraph(BaseModel):
    paragraph_id: int
    start_index: int = 0
    end_index: int = 0
    content: str
    bold: bool = False
    italic: bool = False
    lowerscript: bool = False
    superscript: bool = False

    def delete(self, start_index: int, end_index: int):
        self.content = self.content[:start_index] + self.content[end_index:]

    def insert(self, text: str, index: int):
        self.content = self.content[:index] + text + self.content[index:]

    def switch_formatting(
        self, formatting_type: str
    ):
        if formatting_type == "bold":
            self.bold = not self.bold
        elif formatting_type == "italic":
            self.italic = not self.italic
        elif formatting_type == "lowerscript":
            self.lowerscript = not self.lowerscript
        elif formatting_type == "superscript":
            self.superscript = not self.superscript

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
