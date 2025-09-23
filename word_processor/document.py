import json
import os
from typing import List
from pydantic import BaseModel, ConfigDict
from .paragraph import Paragraph
from .enums import FormattingType, MarginType


class Document(BaseModel):
    margin_left: float = 2.5
    margin_right: float = 2.5
    margin_top: float = 2.5
    margin_bottom: float = 2.5
    _content: List[Paragraph] = []
    _content.append(Paragraph(content=""))

    def create_paragraph(self, **kwargs) -> Paragraph:
        self.join_paragraphs()
        return Paragraph(**kwargs)

    def save(self, filename: str, saves_dir: str):
        os.makedirs(saves_dir, exist_ok=True)
        file_path = os.path.join(saves_dir, filename)
        with open(file_path, "w") as f:
            json.dump([word.model_dump() for word in self._content], f, indent=4)
        self.join_paragraphs()

    def load(self, filename: str, saves_dir: str):
        file_path = os.path.join(saves_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' not found in '{saves_dir}'")
        with open(file_path, "r") as f:
            loaded_content = json.load(f)
            self._content = [Paragraph(**item) for item in loaded_content]
        self.join_paragraphs()

    def to_html(self) -> str:
        html_parts = []

        if self._content:
            main_content = "".join(so.to_html() for so in self._content)
            style = f"padding-top: {self.margin_top}cm; padding-bottom: {self.margin_bottom}cm; padding-left: {self.margin_left}cm; padding-right: {self.margin_right}cm;"
            html_parts.append(f'<main style="{style}">{main_content}</main>')

        self.join_paragraphs()

        return "\n".join(html_parts)

    def insert(self, text: str, paragraph_index: int, string_index: int) -> str:
        if self._content.__len__() == 0:
            self._content.append(Paragraph(content=""))
        self._content[paragraph_index].insert(text, string_index)
        self.join_paragraphs()

    def find_in_body(self, text: str) -> dict:
        locations = []
        text_length = len(text)
        if not text:
            return {"length": 0, "locations": []}

        for i, so in enumerate(self._content):
            for index in so.find(text):
                locations.append((i, index))
        self.join_paragraphs()
        return {"length": text_length, "locations": locations}

    def delete(self, paragraph_index: int, string_index: int, length: int):
        if paragraph_index < 0 or paragraph_index >= len(self._content):
            raise IndexError("Paragraph index out of range.")
        self._content[paragraph_index].delete(string_index, length)
        self.join_paragraphs()

    def switch_formatting(
        self,
        paragraph_index: int,
        index: int,
        length: int,
        formatting_type: FormattingType,
    ):
        if paragraph_index < 0 or paragraph_index >= len(self._content):
            raise IndexError("Paragraph index out of range.")

        original_paragraph = self._content[paragraph_index]
        original_content = original_paragraph.content

        if (
            index < 0
            or index > len(original_content)
            or (index + length) > len(original_content)
        ):
            raise IndexError("Index or length out of range for the paragraph content.")

        # 1. Split the content
        before_content = original_content[:index]
        selected_content = original_content[index : index + length]
        after_content = original_content[index + length :]

        new_paragraphs = []

        # 2. Create the "before" paragraph if it has content
        if before_content:
            before_paragraph = original_paragraph.model_copy()
            before_paragraph.content = before_content
            new_paragraphs.append(before_paragraph)

        # 3. Create the "selected" paragraph with new formatting
        if selected_content:
            selected_paragraph = original_paragraph.model_copy()
            selected_paragraph.content = selected_content

            # Toggle the formatting
            if formatting_type == FormattingType.BOLD:
                selected_paragraph.bold = not selected_paragraph.bold
            elif formatting_type == FormattingType.ITALIC:
                selected_paragraph.italic = not selected_paragraph.italic
            elif formatting_type == FormattingType.LOWERSCRIPT:
                selected_paragraph.lowerscript = not selected_paragraph.lowerscript
                if selected_paragraph.lowerscript:
                    selected_paragraph.superscript = False
            elif formatting_type == FormattingType.SUPERSCRIPT:
                selected_paragraph.superscript = not selected_paragraph.superscript
                if selected_paragraph.superscript:
                    selected_paragraph.lowerscript = False

            new_paragraphs.append(selected_paragraph)

        # 4. Create the "after" paragraph if it has content
        if after_content:
            after_paragraph = original_paragraph.model_copy()
            after_paragraph.content = after_content
            new_paragraphs.append(after_paragraph)

        # 5. Replace the original paragraph with the new paragraphs
        self._content[paragraph_index : paragraph_index + 1] = new_paragraphs

        self.join_paragraphs()

    def get_content(self) -> List[Paragraph]:
        return self._content

    def join_paragraphs(self):
        if not self._content:
            return

        i = len(self._content) - 1
        while i > 0:
            current_paragraph = self._content[i]
            previous_paragraph = self._content[i - 1]

            if previous_paragraph.can_merge_with(current_paragraph):
                previous_paragraph.merge(current_paragraph)
                del self._content[i]

            i -= 1

    def set_margin(self, margin_type: MarginType, value_mm: int):
        value_cm = value_mm / 10.0
        if margin_type == MarginType.LEFT:
            self.margin_left = value_cm
        elif margin_type == MarginType.RIGHT:
            self.margin_right = value_cm
        elif margin_type == MarginType.TOP:
            self.margin_top = value_cm
        elif margin_type == MarginType.BOTTOM:
            self.margin_bottom = value_cm
