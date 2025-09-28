from pydantic import BaseModel, field_serializer
from typing import Optional, List
import html
import re
import logging
from word_processor.enums import FormattingType

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
    hierarchy: FormattingType = FormattingType.BODY

    @field_serializer('hierarchy')
    def serialize_hierarchy(self, hierarchy: FormattingType, _info):
        return hierarchy.value

    def delete(self, start_index: int, end_index: int):
        self.content = self.content[:start_index] + self.content[end_index:]

    def insert(self, text: str, index: int):
        self.content = self.content[:index] + text + self.content[index:]

    def switch_formatting(self, formatting_type: FormattingType):
        if formatting_type == FormattingType.BOLD.value:
            self.bold = not self.bold
        elif formatting_type == FormattingType.ITALIC.value:
            self.italic = not self.italic
        elif formatting_type == FormattingType.LOWERSCRIPT.value:
            self.lowerscript = not self.lowerscript
        elif formatting_type == FormattingType.SUPERSCRIPT.value:
            self.superscript = not self.superscript
        else:
            self.hierarchy = FormattingType(formatting_type)

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

        if self.hierarchy == FormattingType.TITLE:
            text = f"<h1>{text}</h1>"
        elif self.hierarchy == FormattingType.HEADING:
            text = f"<h2>{text}</h2>"
        elif self.hierarchy == FormattingType.SUBHEADING:
            text = f"<h3>{text}</h3>"
        return text

    def can_merge_with(self, other: "Paragraph") -> bool:
        return (
            self.bold == other.bold
            and self.italic == other.italic
            and self.lowerscript == other.lowerscript
            and self.superscript == other.superscript
            and self.hierarchy == other.hierarchy
        )

    def merge(self, other: "Paragraph"):
        self.content += other.content