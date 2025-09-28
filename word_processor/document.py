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
    next_paragraph_id: int = 1
    _content: List[Paragraph] = []
    _content.append(Paragraph(content="", paragraph_id=0))

    def _get_paragraph_by_id(self, paragraph_id: int) -> tuple[int, Paragraph]:
        for i, p in enumerate(self._content):
            if p.paragraph_id == paragraph_id:
                return i, p
        raise ValueError(f"Paragraph with id {paragraph_id} not found")

    def create_paragraph(self, **kwargs) -> Paragraph:
        par = Paragraph(paragraph_id=self.next_paragraph_id, **kwargs)
        self.next_paragraph_id += 1
        return par

    def get_text_only(self) -> str:
        result: str
        result = "".join(so.content for so in self._content)
        return result

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
        html_parts.append("<style>h1, h2, h3, p { display: inline; }</style>")

        if self._content:
            main_content = "".join(so.to_html() for so in self._content)
            style = f"padding-top: {self.margin_top}cm; padding-bottom: {self.margin_bottom}cm; padding-left: {self.margin_left}cm; padding-right: {self.margin_right}cm;"
            html_parts.append(f'<main style="{style}">{main_content}</main>')

        return "\n".join(html_parts)

    def insert_at_index(self, text: str, index: int):
        """Inserts text at a specific index in the document."""
        if not self._content:
            self._content.append(Paragraph(content="", paragraph_id=0))

        target_paragraph = None
        for p in self._content:
            # The '+1' allows insertion at the very end of a paragraph's content
            if p.start_index <= index <= p.end_index + 1:
                target_paragraph = p
                break

        if target_paragraph is None:
            # If index is out of bounds, default to the last paragraph
            if self._content:
                target_paragraph = self._content[-1]
                # And insert at the end of it.
                index = target_paragraph.end_index + 1
            else:
                # This case should ideally not be reached if the content is always initialized
                raise IndexError("Cannot insert into a document with no paragraphs.")

        # Calculate the insertion index relative to the paragraph's content
        insertion_point = index - target_paragraph.start_index

        # Perform the insertion on the paragraph
        target_paragraph.insert(text, insertion_point)

        # Consolidate and re-index the document
        self.join_paragraphs()
        self.recalculate_start_and_end()

    def find_in_body(
        self, text: str, start_index: int = 0, end_index: int = -1
    ) -> List[tuple[int, int]]:
        if not text:
            return []

        full_text = self.get_text_only()

        if end_index == -1:
            end_index = len(full_text)

        locations = []
        current_pos = start_index
        while current_pos < end_index:
            found_pos = full_text.find(text, current_pos, end_index)
            if found_pos == -1:
                break
            locations.append((found_pos, found_pos + len(text) - 1))
            current_pos = found_pos + 1

        return locations

    def delete(self, start_index: int, end_index: int):
        if start_index > end_index:
            return

        start_p = None
        end_p = None
        start_p_index = -1
        end_p_index = -1

        for i, p in enumerate(self._content):
            if p.start_index <= start_index <= p.end_index + 1:
                start_p = p
                start_p_index = i
            if p.start_index <= end_index <= p.end_index + 1:
                end_p = p
                end_p_index = i

        if start_p is None:
            return

        if end_p is None:
            end_p_index = len(self._content) - 1
            end_p = self._content[end_p_index]

        relative_start = start_index - start_p.start_index
        relative_end = end_index - end_p.start_index

        if start_p is end_p:
            start_p.content = (
                start_p.content[:relative_start] + start_p.content[relative_end + 1 :]
            )
        else:
            start_p.content = start_p.content[:relative_start]
            end_p.content = end_p.content[relative_end + 1 :]

            if start_p_index + 1 < end_p_index:
                del self._content[start_p_index + 1 : end_p_index]

        self.join_paragraphs()
        self.recalculate_start_and_end()

    def switch_formatting(
        self, start_index: int, end_index: int, formatting_type: FormattingType
    ):
        copy_content = self._content.copy()
        for p in copy_content:
            if (
                p.start_index <= start_index <= p.end_index
                or p.end_index >= end_index >= p.start_index
            ):
                self.switch_style_within_paragraph(
                    p,
                    max(start_index, p.start_index),
                    min(end_index, p.end_index),
                    formatting_type,
                )
        self.join_paragraphs()
        self.recalculate_start_and_end()

    def switch_style_within_paragraph(
        self, p, start_index: int, end_index: int, formatting_type: FormattingType
    ):
        index = self._content.index(p)
        p_start = self.create_paragraph(
            content=p.content[: max(start_index - p.start_index, 0)],
            bold=p.bold,
            italic=p.italic,
            lowerscript=p.lowerscript,
            superscript=p.superscript,
            hierarchy=p.hierarchy,
        )
        if p_start.content != "":
            index += 1
            self._content.insert(index, p_start)
        p_end = self.create_paragraph(
            content=p.content[len(p.content) - max(p.end_index - end_index, 0) :],
            bold=p.bold,
            italic=p.italic,
            lowerscript=p.lowerscript,
            superscript=p.superscript,
            hierarchy=p.hierarchy,
        )
        if p_end.content != "":
            self._content.insert(index + 1, p_end)
        p.content = p.content[
            max(start_index - p.start_index, 0) : len(p.content)
            - max(p.end_index - end_index, 0)
        ]
        p.switch_formatting(formatting_type.value)

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
        self.recalculate_start_and_end()

    def recalculate_start_and_end(self):
        start_index: int = 0
        for so in self._content:
            so.start_index = start_index
            so.end_index = so.start_index + len(so.content) - 1
            start_index += len(so.content)

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
