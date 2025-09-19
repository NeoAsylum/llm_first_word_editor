from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import uvicorn
from typing import List, Union, Annotated

import os

from word_processor.document import Document
from word_processor.paragraph import Paragraph
from word_processor.enums import FormattingType

app = FastAPI()

# Global document instance
# Initializing with default values, then setting content using methods
doc = Document()

doc.insert(doc.create_word(content="This is a "), 0)
doc.insert(doc.create_word(content="sample", bold=True), 1)
doc.insert(doc.create_word(content=" document."), 2)

# --- Request Models ---


class DocumentRequest(BaseModel):
    content: List[Paragraph]


class FindRequest(BaseModel):
    search_term: str


class InsertStringRequest(BaseModel):
    so: Paragraph
    index: int


class SaveRequest(BaseModel):
    filename: str


class LoadRequest(BaseModel):
    filename: str


# --- Response Models ---
class FindResult(BaseModel):
    paragraphId: int
    indexInParagraph: List[int]


class MessageResponse(BaseModel):
    message: str


# --- Static files ---

script_dir = os.path.dirname(os.path.abspath(__file__))
index_html_path = os.path.join(
    script_dir, "word_processor/index.html"
)  # this is the correct file path. dont edit.


@app.get("/")
def read_root():
    print("Tool call: read_root")
    return FileResponse(index_html_path)


# --- Document level endpoints ---


@app.get("/document", response_model=List[Paragraph])
def get_document():
    print("Tool call: get_document")
    return doc.get_content()


@app.get("/document/html", response_model=str)
def get_document_html():
    print("Tool call: get_document_html")
    return doc.to_html()


@app.post("/document/find_in_body", response_model=List[FindResult])
def find_in_body(req: FindRequest):
    print(f"Tool call: find_in_body with search_term='{req.search_term}'")
    return doc.find_in_body(req.search_term)


@app.post("/document/insert_string", response_model=MessageResponse)
def insert_object(req: InsertStringRequest) -> MessageResponse:
    print(
        f"Tool call: insert_object at index {req.index} with content='{req.so.content}'"
    )
    try:
        new_so = doc.create_word(**req.so.model_dump(exclude_unset=True))
        doc.insert(new_so, req.index)
        return MessageResponse(message="Object inserted.")
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/document/delete_paragraph/{paragraph_index}", response_model=MessageResponse)
def delete_object(paragraph_index: int):
    print(f"Tool call: delete_object with index={paragraph_index}")
    try:
        doc.delete(paragraph_index)
        return MessageResponse(message=f"Object at index {paragraph_index} deleted.")
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/format/switch/{paragraph_index}/{formatting_type}", response_model=MessageResponse)
def switch_formatting(
    paragraph_index: int,
    formatting_type: FormattingType
):
    print(f"Tool call: switch_formatting for index={paragraph_index}, type={formatting_type.value}")
    try:
        doc.switch_formatting(paragraph_index, formatting_type)
        return MessageResponse(message=f"Formatting {formatting_type.value} switched for object at index {paragraph_index}.")
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))


SAVES_DIR = "saves"


@app.post("/document/save", response_model=MessageResponse)
def save_document(req: SaveRequest):
    print(f"Tool call: save_document with filename='{req.filename}'")
    try:
        doc.save(req.filename, SAVES_DIR)
        return MessageResponse(message=f"Document saved to {req.filename}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/document/load", response_model=MessageResponse)
def load_document(req: LoadRequest):
    print(f"Tool call: load_document with filename='{req.filename}'")
    try:
        doc.load(req.filename, SAVES_DIR)
        return MessageResponse(message=f"Document loaded from {req.filename}.")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
