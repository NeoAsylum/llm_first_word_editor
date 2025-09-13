from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn


app = FastAPI()

# In-memory storage for the document
document_content = "This is a sample document."

class TextApiLogic:
    def __init__(self, content):
        self.content = content

    def find_occurrences_logic(self, search_term):
        occurrences = []
        start_index = 0
        while True:
            pos = self.content.find(search_term, start_index)
            if pos == -1:
                break
            
            end_pos = pos + len(search_term)
            occurrences.append((pos, end_pos))
            start_index = end_pos
        
        return occurrences

    def insert_text(self, pos, text):
        if pos < 0 or pos > len(self.content):
            raise ValueError("Invalid character position.")
        self.content = self.content[:pos] + text + self.content[pos:]

    def delete_text(self, start, end):
        if start < 0 or end > len(self.content) or start > end:
            raise ValueError("Invalid character range.")
        self.content = self.content[:start] + self.content[end:]

    def make_bold_at(self, start, end):
        if start < 0 or end > len(self.content) or start > end:
            raise ValueError("Invalid character range.")
        self.content = self.content[:start] + f'<b>{self.content[start:end]}</b>' + self.content[end:]

    def make_italic_at(self, start, end):
        if start < 0 or end > len(self.content) or start > end:
            raise ValueError("Invalid character range.")
        self.content = self.content[:start] + f'<i>{self.content[start:end]}</i>' + self.content[end:]


class DocumentRequest(BaseModel):
    content: str

class FindRequest(BaseModel):
    search_term: str

class InsertRequest(BaseModel):
    pos: int
    text: str

class DeleteRequest(BaseModel):
    start: int
    end: int

class FormatRequest(BaseModel):
    start: int
    end: int

@app.get("/")
def read_root():
    return FileResponse('index.html')

@app.get("/document")
def get_document():
    return {"content": document_content}

@app.put("/document")
def update_document(doc: DocumentRequest):
    global document_content
    document_content = doc.content
    return {"message": "Document updated successfully."}

@app.post("/find")
def find_text(req: FindRequest):
    logic = TextApiLogic(document_content)
    occurrences = logic.find_occurrences_logic(req.search_term)
    return {"occurrences": occurrences}

@app.post("/insert")
def insert_text(req: InsertRequest):
    global document_content
    logic = TextApiLogic(document_content)
    try:
        logic.insert_text(req.pos, req.text)
        document_content = logic.content
        return {"content": document_content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/delete")
def delete_text(req: DeleteRequest):
    global document_content
    logic = TextApiLogic(document_content)
    try:
        logic.delete_text(req.start, req.end)
        document_content = logic.content
        return {"content": document_content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/format/bold")
def format_bold(req: FormatRequest):
    global document_content
    logic = TextApiLogic(document_content)
    try:
        logic.make_bold_at(req.start, req.end)
        document_content = logic.content
        return {"content": document_content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/format/italic")
def format_italic(req: FormatRequest):
    global document_content
    logic = TextApiLogic(document_content)
    try:
        logic.make_italic_at(req.start, req.end)
        document_content = logic.content
        return {"content": document_content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/insert")
def insert_text(req: InsertRequest):
    logic = TextApiLogic(req.content)
    try:
        logic.insert_text(req.pos, req.text)
        return {"content": logic.content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/delete")
def delete_text(req: DeleteRequest):
    logic = TextApiLogic(req.content)
    try:
        logic.delete_text(req.start, req.end)
        return {"content": logic.content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/format/bold")
def format_bold(req: FormatRequest):
    logic = TextApiLogic(req.content)
    try:
        logic.make_bold_at(req.start, req.end)
        return {"content": logic.content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/format/italic")
def format_italic(req: FormatRequest):
    logic = TextApiLogic(req.content)
    try:
        logic.make_italic_at(req.start, req.end)
        return {"content": logic.content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8001)
