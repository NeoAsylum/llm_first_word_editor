from typing import List
from pydantic import BaseModel
from .word import Word
import html
from html.parser import HTMLParser

class Document(BaseModel):
    _next_id: int = 0
    _header: Word
    _content: List[Word] = []
    _footer: Word

    def create_word(self, **kwargs) -> Word:
        if 'id' not in kwargs or kwargs['id'] is None:
            kwargs['id'] = self._next_id
            self._next_id += 1
        return Word(**kwargs)

    def to_html(self) -> str:
        html_parts = []
        if self._header and self._header.content:
            html_parts.append(f"<header>{self._header.to_html()}</header>")
        
        if self._content:
            main_content = "".join(so.to_html() for so in self._content)
            html_parts.append(f"<main>{main_content}</main>")

        if self._footer and self._footer.content:
            html_parts.append(f"<footer>{self._footer.to_html()}</footer>")
            
        return "\n".join(html_parts)

    def find_in_body(self, text: str) -> List[dict]:
        results = []
        for so in self._content:
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
            if so.id == so_id:
                so_to_delete = so
                break
        if so_to_delete:
            self._content.remove(so_to_delete)
        else:
            raise ValueError(f"Word with id {so_id} not found.")

    def switchBoldness(self, so_id: int):
        if self._header.id == so_id:
            self._header.bold = not self._header.bold
            return
        if self._footer.id == so_id:
            self._footer.bold = not self._footer.bold
            return
        for so in self._content:
            if so.id == so_id:
                so.bold = not so.bold
                return
        raise ValueError(f"Word with id {so_id} not found.")

    def switchItalic(self, so_id: int):
        if self._header.id == so_id:
            self._header.italic = not self._header.italic
            return
        if self._footer.id == so_id:
            self._footer.italic = not self._footer.italic
            return
        for so in self._content:
            if so.id == so_id:
                so.italic = not so.italic
                return
        raise ValueError(f"Word with id {so_id} not found.")

    def get_content(self) -> List[Word]:
        return self._content

    def get_header(self) -> Word:
        return self._header

    def set_header(self, header: Word):
        self._header = header

    def get_footer(self) -> Word:
        return self._footer

    def set_footer(self, footer: Word):
        self._footer = footer

    def get_next_id(self) -> int:
        return self._next_id
