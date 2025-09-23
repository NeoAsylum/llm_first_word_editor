from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn
from typing import List
import os

from word_processor.document import Document
from word_processor.paragraph import Paragraph
from word_processor.enums import FormattingType, MarginType

app = FastAPI()

# Global document instance
# Initializing with default values, then setting content using methods
doc = Document()
load_dotenv()
SAVES_DIR = os.getenv("SAVES_DIR")

doc.insert("This is a ", 0, 0)
doc.insert("sample ", 0, 11)
doc.insert("document. \n And i am trying out some stuff right here. ", 0, 18)
doc.switch_formatting(0, 10, 7, FormattingType.BOLD)

# --- Request Models ---

class DocumentRequest(BaseModel):
    content: List[Paragraph]


class FindRequest(BaseModel):
    search_term: str


class InsertStringRequest(BaseModel):
    text: str
    paragraph_index: int
    string_index: int


class SaveRequest(BaseModel):
    filename: str


class LoadRequest(BaseModel):
    filename: str


class SwitchFormattingRequest(BaseModel):
    paragraph_index: int
    index: int
    length: int
    formatting_type: FormattingType

class SetMarginRequest(BaseModel):
    margin_type: MarginType
    value_mm: int

class DeleteRequest(BaseModel):
    paragraph_index: int
    string_index: int
    length: int


# --- Response Models ---
class FindResult(BaseModel):
    length: int
    locations: List[tuple[int, int]]


class MessageResponse(BaseModel):
    message: str


# --- Static files ---

script_dir = os.path.dirname(os.path.abspath(__file__))
index_html_path = os.path.join(
    script_dir,
    "word_processor/index.html",  # this is the correct file path. dont edit.
)


@app.get("/")
def read_root():
    print("Tool call: read_root")
    return FileResponse(index_html_path)


# --- Document level endpoints ---


@app.get("/document", response_model=List[Paragraph])
def get_document():
    print("Tool call: get_document")
    return doc.get_content()


@app.get("/document/html", response_class=HTMLResponse)
def get_document_html():
    print("Tool call: get_document_html")
    return doc.to_html()


@app.post("/document/find_in_body", response_model=FindResult)
def find_in_body(req: FindRequest):
    print(f"Tool call: find_in_body with search_term='{req.search_term}'")
    return doc.find_in_body(req.search_term)


@app.post("/document/insert_string", response_model=MessageResponse)
def insert_object(req: InsertStringRequest) -> MessageResponse:
    try:
        doc.insert(req.text, req.paragraph_index, req.string_index)
        return MessageResponse(
            message=f"Text inserted at paragraph {req.paragraph_index}, index {req.string_index}."
        )
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))



@app.post("/document/delete_substring", response_model=MessageResponse)
def delete_substring(req: DeleteRequest):
    try:
        doc.delete(req.paragraph_index, req.string_index, req.length)
        return MessageResponse(message="Substring deleted.")
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/format/switch", response_model=MessageResponse)
def switch_formatting(req: SwitchFormattingRequest):
    print(
        f"Tool call: switch_formatting for paragraph_index={req.paragraph_index}, index={req.index}, length={req.length}, type={req.formatting_type.value}"
    )
    try:
        doc.switch_formatting(
            req.paragraph_index, req.index, req.length, req.formatting_type
        )
        return MessageResponse(
            message=f"Formatting {req.formatting_type.value} switched for object at index {req.paragraph_index}."
        )
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))


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

@app.post("/document/set_margin", response_model=MessageResponse)
def set_margin(req: SetMarginRequest):
    try:
        doc.set_margin(req.margin_type, req.value_mm)
        return MessageResponse(message=f"Margin {req.margin_type.value} set to {req.value_mm}mm.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
