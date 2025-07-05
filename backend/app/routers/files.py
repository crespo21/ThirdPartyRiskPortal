import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..database import get_db
from ..security import get_current_user
from ..services.azure_storage import azure_storage_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/files",
    tags=["files"]
)

# Error messages
DOCUMENT_NOT_FOUND = "Document not found"

@router.post("/upload-url", response_model=dict)
async def get_upload_url(
    file_name: str = Form(...),
    content_type: str = Form(...),
    company_id: int = Form(...),
    document_type: str = Form(...),
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a secure upload URL with SAS token for file upload
    """
    try:
        # Validate file type
        if content_type not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {content_type} not allowed. Allowed types: {settings.allowed_file_types}"
            )
        
        # Validate document type
        valid_document_types = ["CONTRACT", "ASSESSMENT", "COMPLIANCE", "FINANCIAL", "OTHER"]
        if document_type not in valid_document_types:
            raise HTTPException(
                status_code=400,
                detail=f"Document type {document_type} not valid. Valid types: {valid_document_types}"
            )
        
        # Get upload URL from Azure Storage
        upload_data = azure_storage_service.get_upload_url(file_name, content_type)
        
        # Store document metadata in database
        document = models.models.Document(
            file_name=upload_data["blob_name"],
            original_name=file_name,
            blob_name=upload_data["blob_name"],
            content_type=content_type,
            file_size=0,  # Will be updated after upload
            company_id=company_id,
            uploaded_by=current_user.id,
            document_type=document_type,
            status="PENDING"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Add document ID to upload data
        upload_data["document_id"] = document.id
        
        logger.info(f"Generated upload URL for document {document.id} - {file_name}")
        return upload_data
        
    except Exception as e:
        logger.error(f"Failed to generate upload URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")

@router.post("/confirm-upload/{document_id}")
async def confirm_upload(
    document_id: int,
    file_size: int = Form(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm file upload and update document metadata
    """
    try:
        document = db.query(models.Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail=DOCUMENT_NOT_FOUND)
        
        # Verify blob exists in Azure Storage
        if not azure_storage_service.blob_exists(document.blob_name):
            raise HTTPException(status_code=400, detail="File not found in storage")
        
        # Update document metadata
        document.file_size = file_size
        document.status = "ACTIVE"
        document.upload_date = datetime.utcnow()
        
        db.commit()
        db.refresh(document)
        
        logger.info(f"Confirmed upload for document {document_id}")
        return {"message": "Upload confirmed successfully", "document_id": document_id}
        
    except Exception as e:
        logger.error(f"Failed to confirm upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm upload")

@router.get("/download/{document_id}")
async def get_download_url(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a secure download URL for a document
    """
    try:
        document = db.query(models.Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail=DOCUMENT_NOT_FOUN)
        
        # Generate download URL with SAS token
        download_url = azure_storage_service.get_download_url(document.blob_name)
        
        logger.info(f"Generated download URL for document {document_id}")
        return {
            "download_url": download_url,
            "file_name": document.original_name,
            "content_type": document.content_type,
            "expires_in": "24 hours"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate download URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate download URL")

@router.get("/company/{company_id}", response_model=List[schemas.DocumentResponse])
async def get_company_documents(
    company_id: int,
    document_type: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all documents for a company
    """
    try:
        query = db.query(models.Document).filter(Document.company_id == company_id)
        
        if document_type:
            query = query.filter(Document.document_type == document_type)
        
        documents = query.all()
        
        logger.info(f"Retrieved {len(documents)} documents for company {company_id}")
        return documents
        
    except Exception as e:
        logger.error(f"Failed to retrieve company documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document (soft delete)
    """
    try:
        document = db.query(models.Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Soft delete - mark as deleted
        document.status = "DELETED"
        db.commit()
        
        logger.info(f"Soft deleted document {document_id}")
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@router.get("/{document_id}/metadata")
async def get_document_metadata(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get document metadata from Azure Storage
    """
    try:
        document = db.query(models.Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get metadata from Azure Storage
        metadata = azure_storage_service.get_blob_metadata(document.blob_name)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="Document metadata not found")
        
        logger.info(f"Retrieved metadata for document {document_id}")
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to retrieve document metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document metadata")

@router.post("/validate-file")
async def validate_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Validate file before upload
    """
    try:
        # Check file size
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size {file.size} exceeds maximum allowed size of {settings.max_file_size}"
            )
        
        # Check file type
        if file.content_type not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed. Allowed types: {settings.allowed_file_types}"
            )
        
        logger.info(f"File validation successful for {file.filename}")
        return {
            "valid": True,
            "file_name": file.filename,
            "content_type": file.content_type,
            "size": file.size
        }
        
    except Exception as e:
        logger.error(f"File validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e)) 