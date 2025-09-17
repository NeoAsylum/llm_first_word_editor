from typing import List
from pydantic import BaseModel, ConfigDict
from .word import Word
import html
from html.parser import HTMLParser

class Document(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _next_id: int = 0
    _header: List[Word] = []
    _content: List[Word] = []
    _footer: List[Word] = []

    def create_word(self, **kwargs) -> Word:
        if 'id' not in kwargs or kwargs['id'] is None:
            kwargs['id'] = self._next_id
            self._next_id += 1
        return Word(**kwargs)

    def to_html(self) -> str:
        html_parts = []
        if self._header:
            header_content = "".join(so.to_html() for so in self._header)
            html_parts.append(f"<header>{header_content}</header>")
        
        if self._content:
            main_content = "".join(so.to_html() for so in self._content)
            html_parts.append(f"<main>{main_content}</main>")

        if self._footer:
            footer_content = "".join(so.to_html() for so in self._footer)
            html_parts.append(f"<footer>{footer_content}</footer>")
            
        return "\n".join(html_parts)

    def find_in_body(self, text: str) -> List[dict]:
        results = []
        for so in self._content:
            # The .find(), .id attributes are not part of the Word interface.
            # This will fail if the Word is not a Word object.
            indices = so.find(text)
            if indices:
                results.append({
                    "id": so.id,
                    "indices": indices
                })
        return results

    def insert(self, so: Word, index: int):
        if index < 0 or index > len(self._content):
            raise IndexError("Index out of range.")
        self._content.insert(index, so)

    def delete(self, so_id: int):
        so_to_delete = None
        for so in self._content:
            # The .id attribute is not part of the Word interface.
            # This will fail if the Word is not a Word object.
            if so.id == so_id:
                so_to_delete = so
                break
        if so_to_delete:
            self._content.remove(so_to_delete)
        else:
            raise ValueError(f"Word with id {so_id} not found.")

    def switchBoldness(self, so_id: int):
        for so in self._header:
            if so.id == so_id:
                so.bold = not so.bold
                return
        for so in self._footer:
            if so.id == so_id:
                so.bold = not so.bold
                return
        for so in self._content:
            if so.id == so_id:
                so.bold = not so.bold
                return
        raise ValueError(f"Word with id {so_id} not found.")

    def switchItalic(self, so_id: int):
        for so in self._header:
            if so.id == so_id:
                so.italic = not so.italic
                return
        for so in self._footer:
            if so.id == so_id:
                so.italic = not so.italic
                return
        for so in self._content:
            if so.id == so_id:
                so.italic = not so.italic
                return
        raise ValueError(f"Word with id {so_id} not found.")

    def switchLowerscript(self, so_id: int):
        for so in self._header:
            if so.id == so_id:
                so.lowerscript = not so.lowerscript
                if so.lowerscript:
                    so.superscript = False
                return
        for so in self._footer:
            if so.id == so_id:
                so.lowerscript = not so.lowerscript
                if so.lowerscript:
                    so.superscript = False
                return
        for so in self._content:
            if so.id == so_id:
                so.lowerscript = not so.lowerscript
                if so.lowerscript:
                    so.superscript = False
                return
        raise ValueError(f"Word with id {so_id} not found.")

    def switchSuperscript(self, so_id: int):
        for so in self._header:
            if so.id == so_id:
                so.superscript = not so.superscript
                if so.superscript:
                    so.lowerscript = False
                return
        for so in self._footer:
            if so.id == so_id:
                so.superscript = not so.superscript
                if so.superscript:
                    so.lowerscript = False
                return
        for so in self._content:
            if so.id == so_id:
                so.superscript = not so.superscript
                if so.superscript:
                    so.lowerscript = False
                return
        raise ValueError(f"Word with id {so_id} not found.")

    def get_content(self) -> List[Word]:
        return self._content

    def get_header(self) -> List[Word]:
        return self._header

    def set_header(self, header: List[Word]):
        self._header = header

    def get_footer(self) -> List[Word]:
        return self._footer

    def set_footer(self, footer: List[Word]):
        self._footer = footer

    def get_next_id(self) -> int:
        return self._next_id
