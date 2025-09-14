from typing import List
from pydantic import BaseModel
from .word import stringObject
import html
from html.parser import HTMLParser

class documentObject(BaseModel):
    _next_id: int = 0
    _header: stringObject
    _content: List[stringObject] = []
    _footer: stringObject

    def create_string_object(self, **kwargs) -> stringObject:
        if 'id' not in kwargs or kwargs['id'] is None:
            kwargs['id'] = self._next_id
            self._next_id += 1
        return stringObject(**kwargs)

    def to_html(self) -> str:
        def string_obj_to_html(so: stringObject) -> str:
            text = so.content
            text = html.escape(text)
            if so.bold:
                text = f"<b>{text}</b>"
            if so.italic:
                text = f"<i>{text}</i>"
            return text

        html_parts = []
        if self._header and self._header.content:
            html_parts.append(f"<header>{string_obj_to_html(self._header)}</header>")
        
        if self._content:
            main_content = "".join(string_obj_to_html(so) for so in self._content)
            html_parts.append(f"<main>{main_content}</main>")

        if self._footer and self._footer.content:
            html_parts.append(f"<footer>{string_obj_to_html(self._footer)}</footer>")
            
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

    def insert(self, so: stringObject, index: int):
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
            raise ValueError(f"stringObject with id {so_id} not found.")

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
        raise ValueError(f"stringObject with id {so_id} not found.")

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
        raise ValueError(f"stringObject with id {so_id} not found.")

    def get_content(self) -> List[stringObject]:
        return self._content

    def get_header(self) -> stringObject:
        return self._header

    def set_header(self, header: stringObject):
        self._header = header

    def get_footer(self) -> stringObject:
        return self._footer

    def set_footer(self, footer: stringObject):
        self._footer = footer

    def get_next_id(self) -> int:
        return self._next_id