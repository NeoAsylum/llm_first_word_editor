import json
import os
from typing import List
from pydantic import BaseModel, ConfigDict
from .paragraph import Paragraph
from .enums import FormattingType

class Document(BaseModel):
    _content: List[Paragraph] = []

    def create_word(self, **kwargs) -> Paragraph:
        return Paragraph(**kwargs)

    def save(self, filename: str, saves_dir: str):
        os.makedirs(saves_dir, exist_ok=True)
        file_path = os.path.join(saves_dir, filename)
        with open(file_path, "w") as f:
            json.dump([word.model_dump() for word in self._content], f, indent=4)

    def load(self, filename: str, saves_dir: str):
        file_path = os.path.join(saves_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' not found in '{saves_dir}'")
        with open(file_path, "r") as f:
            loaded_content = json.load(f)
            self._content = [Paragraph(**item) for item in loaded_content]

    def to_html(self) -> str:
        html_parts = []
        
        if self._content:
            main_content = "".join(so.to_html() for so in self._content)
            html_parts.append(f"<main>{main_content}</main>")

            
        return "\n".join(html_parts)

    def find_in_body(self, text: str) -> List[dict[int, int]]:
        results = []
        for i, so in enumerate(self._content):
            indices = so.find(text)
            if indices:
                results.append({
                    "paragraphId": i,
                    "indexInParagraph": indices
                })
        return results

    def insert(self, so: Paragraph, index: int):
        if index < 0 or index > len(self._content):
            raise IndexError("Index out of range.")
        self._content.insert(index, so)

    def delete(self, paragraph_index: int):
        if paragraph_index < 0 or paragraph_index >= len(self._content):
            raise IndexError("Paragraph index out of range.")
        del self._content[paragraph_index]

    def switch_formatting(self, paragraph_index: int, formatting_type: FormattingType):
        if paragraph_index < 0 or paragraph_index >= len(self._content):
            raise IndexError("Paragraph index out of range.")
        
        so = self._content[paragraph_index]
        if formatting_type == FormattingType.BOLD:
            so.bold = not so.bold
        elif formatting_type == FormattingType.ITALIC:
            so.italic = not so.italic
        elif formatting_type == FormattingType.LOWERSCRIPT:
            so.lowerscript = not so.lowerscript
            if so.lowerscript:
                so.superscript = False
        elif formatting_type == FormattingType.SUPERSCRIPT:
            so.superscript = not so.superscript
            if so.superscript:
                so.lowerscript = False

    def get_content(self) -> List[Paragraph]:
        return self._content

