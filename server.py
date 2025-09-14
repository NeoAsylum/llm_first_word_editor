from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from typing import List

import os

from word_processor.document import documentObject
from word_processor.word import stringObject

app = FastAPI()

# Global document instance
# Initializing with default values, then setting content using methods
doc = documentObject(
    _header=stringObject(id=0, content=""), # Temporary header
    _footer=stringObject(id=1, content=""), # Temporary footer
    _next_id=2 # Starting ID for content
)
doc.set_header(doc.create_string_object(content="My Header"))
doc.set_footer(doc.create_string_object(content="Page 1"))

doc.insert(doc.create_string_object(content="This is a "), 0)
doc.insert(doc.create_string_object(content="sample", bold=True), 1)
doc.insert(doc.create_string_object(content=" document."), 2)


# --- Request Models ---

class DocumentRequest(BaseModel):
    content: List[stringObject]

class HeaderRequest(BaseModel):
    header: stringObject

class FooterRequest(BaseModel):
    footer: stringObject

class FindRequest(BaseModel):
    search_term: str

class InsertObjectRequest(BaseModel):
    so: stringObject
    index: int

# --- Static files ---

script_dir = os.path.dirname(os.path.abspath(__file__))
index_html_path = os.path.join(script_dir, "word_processor/index.html") # this is the correct file path. dont edit.

@app.get("/")
def read_root():
    print("Tool call: read_root")
    return FileResponse(index_html_path)

# --- Document level endpoints ---

@app.get("/document", response_model=List[stringObject])
def get_document():
    print("Tool call: get_document")
    return doc.get_content()

@app.put("/document")
def update_document(req: DocumentRequest):
    print("Tool call: update_document")
    # This endpoint is removed as per user's request.
    # This is a placeholder to avoid syntax error.
    # The user wants to update the document using insert/delete.
    return {"message": "This endpoint is removed. Use insert/delete for updates."}


@app.get("/header", response_model=stringObject)
def get_header():
    print("Tool call: get_header")
    return doc.get_header()

@app.put("/header")
def update_header(req: HeaderRequest):
    print("Tool call: update_header")
    doc.set_header(req.header)
    return {"message": "Header updated successfully."}

@app.get("/footer", response_model=stringObject)
def get_footer():
    print("Tool call: get_footer")
    return doc.get_footer()

@app.put("/footer")
def update_footer(req: FooterRequest):
    print("Tool call: update_footer")
    doc.set_footer(req.footer)
    return {"message": "Footer updated successfully."}

# --- Object-based logic endpoints ---

@app.post("/document/find_in_body")
def find_in_body(req: FindRequest):
    print(f"Tool call: find_in_body with search_term='{req.search_term}'")
    return doc.find_in_body(req.search_term)

@app.post("/document/insert_object")
def insert_object(req: InsertObjectRequest):
    print(f"Tool call: insert_object at index {req.index} with content='{req.so.content}'")
    try:
        # The stringObject from the request might not have an ID.
        # The create_string_object method will assign a new ID if it's missing.
        new_so = doc.create_string_object(**req.so.dict(exclude_unset=True))
        doc.insert(new_so, req.index)
        return {"message": "Object inserted."}
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/document/delete_object/{so_id}")
def delete_object(so_id: int):
    print(f"Tool call: delete_object with id={so_id}")
    try:
        doc.delete(so_id)
        return {"message": f"Object with id {so_id} deleted."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/format/bold/{so_id}")
def switch_boldness(so_id: int):
    print(f"Tool call: switch_boldness for id={so_id}")
    try:
        doc.switchBoldness(so_id)
        return {"message": f"Boldness switched for object with id {so_id}."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/format/italic/{so_id}")
def switch_italic(so_id: int):
    print(f"Tool call: switch_italic for id={so_id}")
    try:
        doc.switchItalic(so_id)
        return {"message": f"Italic switched for object with id {so_id}."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
