from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
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

doc.insert_at_index("This is a sample document. \n And i am trying out some stuff right here. ", 0)
doc.switch_formatting(start_index=10, end_index=17, formatting_type=FormattingType.BOLD)

# --- Request Models ---


class DocumentRequest(BaseModel):
    content: List[Paragraph]


class FindResult(BaseModel):
    locations: List[tuple[int, int]]


class FindRequest(BaseModel):
    search_term: str
    start_index: int = 0
    end_index: int = -1


class InsertStringRequest(BaseModel):
    text: str
    index: int


class SaveRequest(BaseModel):
    filename: str


class LoadRequest(BaseModel):
    filename: str


class SwitchFormattingRequest(BaseModel):
    start_index: int
    end_index: int
    formatting_type: FormattingType


class SetMarginRequest(BaseModel):
    margin_type: MarginType
    value_mm: int


class DeleteRequest(BaseModel):
    start_index: int
    end_index: int


# --- Response Models ---



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
def find_in_body(req: FindRequest) -> FindResult:
    print(f"Tool call: find_in_body with search_term='{req.search_term}'")
    locations = doc.find_in_body(req.search_term, req.start_index, req.end_index)
    return FindResult(locations=locations)


@app.post("/document/insert_string", response_model=MessageResponse)
def insert_object(req: InsertStringRequest) -> MessageResponse:
    try:
        doc.insert_at_index(req.text, req.index)
        return MessageResponse(
            message=f"Text inserted at index {req.index}."
        )
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/document/text_only", response_class=PlainTextResponse)
def get_text_only() -> str:
    try:
        return doc.get_text_only()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/document/delete_substring", response_model=MessageResponse)
def delete_substring(req: DeleteRequest):
    try:
        doc.delete(req.start_index, req.end_index)
        return MessageResponse(message="Substring deleted.")
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/format/switch", response_model=MessageResponse)
def switch_formatting(req: SwitchFormattingRequest):
    print(
        f"Tool call: switch_formatting for start_index={req.start_index}, end_index={req.end_index}, type={req.formatting_type.value}"
    )
    try:
        doc.switch_formatting(
            req.start_index, req.end_index, req.formatting_type
        )
        return MessageResponse(
            message=f"Formatting {req.formatting_type.value} switched for selection from index {req.start_index} to {req.end_index}."
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
        return MessageResponse(
            message=f"Margin {req.margin_type.value} set to {req.value_mm}mm."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)