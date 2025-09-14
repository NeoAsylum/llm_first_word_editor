from pydantic import BaseModel
from typing import Optional, List

class stringObject(BaseModel):
    id: Optional[int] = None
    content: str
    bold: bool = False
    italic: bool = False

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
