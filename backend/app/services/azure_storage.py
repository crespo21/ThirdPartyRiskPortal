import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import (BlobSasPermissions, BlobServiceClient,
                                generate_blob_sas)

from ..config import settings

logger = logging.getLogger(__name__)

class AzureStorageService:
    """Azure Blob Storage service for secure file uploads with SAS tokens"""
    
    def __init__(self):
        self.connection_string = settings.azure_storage_connection_string
        self.account_name = settings.azure_storage_account_name
        self.account_key = settings.azure_storage_account_key
        self.container_name = settings.azure_storage_container_name
        
        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        elif self.account_name and self.account_key:
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{self.account_name}.blob.core.windows.net",
                credential=self.account_key
            )
        else:
            # Use managed identity in production
            credential = DefaultAzureCredential()
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{self.account_name}.blob.core.windows.net",
                credential=credential
            )
        
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
    
    def generate_sas_token(self, blob_name: str, permission: str = "write", expiry_hours: int = 1) -> str:
        """
        Generate a Shared Access Signature (SAS) token for secure file access
        
        Args:
            blob_name: Name of the blob
            permission: Permission level ('read', 'write', 'delete')
            expiry_hours: Token expiry time in hours
            
        Returns:
            SAS token string
        """
        try:
            # Define permissions based on operation
            if permission == "read":
                permissions = BlobSasPermissions(read=True)
            elif permission == "write":
                permissions = BlobSasPermissions(write=True, create=True)
            elif permission == "delete":
                permissions = BlobSasPermissions(delete=True)
            else:
                permissions = BlobSasPermissions(read=True, write=True, create=True)
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=permissions,
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours),
                protocol="https"  # Force HTTPS for security
            )
            
            logger.info(f"Generated SAS token for blob: {blob_name}")
            return sas_token
            
        except Exception as e:
            logger.error(f"Failed to generate SAS token: {e}")
            raise
    
    def get_upload_url(self, file_name: str, content_type: str) -> Dict[str, Any]:
        """
        Get a secure upload URL with SAS token for file upload
        
        Args:
            file_name: Original file name
            content_type: MIME type of the file
            
        Returns:
            Dictionary containing upload URL and metadata
        """
        try:
            # Generate unique blob name
            file_extension = os.path.splitext(file_name)[1]
            blob_name = f"{uuid.uuid4()}{file_extension}"
            
            # Generate SAS token for upload
            sas_token = self.generate_sas_token(blob_name, "write", expiry_hours=1)
            
            # Construct upload URL
            upload_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
            
            return {
                "upload_url": upload_url,
                "blob_name": blob_name,
                "original_name": file_name,
                "content_type": content_type,
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate upload URL: {e}")
            raise
    
    def get_download_url(self, blob_name: str, expiry_hours: int = 24) -> str:
        """
        Get a secure download URL with SAS token
        
        Args:
            blob_name: Name of the blob to download
            expiry_hours: Token expiry time in hours
            
        Returns:
            Download URL with SAS token
        """
        try:
            sas_token = self.generate_sas_token(blob_name, "read", expiry_hours)
            download_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
            
            logger.info(f"Generated download URL for blob: {blob_name}")
            return download_url
            
        except Exception as e:
            logger.error(f"Failed to generate download URL: {e}")
            raise
    
    def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob from storage
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            
            logger.info(f"Deleted blob: {blob_name}")
            return True
            
        except AzureError as e:
            logger.error(f"Failed to delete blob {blob_name}: {e}")
            return False
    
    def blob_exists(self, blob_name: str) -> bool:
        """
        Check if a blob exists
        
        Args:
            blob_name: Name of the blob to check
            
        Returns:
            True if blob exists, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            return blob_client.exists()
        except Exception as e:
            logger.error(f"Failed to check blob existence: {e}")
            return False
    
    def get_blob_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """
        Get blob metadata
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            Dictionary containing blob metadata
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            properties = blob_client.get_blob_properties()
            
            return {
                "name": blob_name,
                "size": properties.size,
                "content_type": properties.content_settings.content_type,
                "created": properties.creation_time,
                "last_modified": properties.last_modified,
                "etag": properties.etag
            }
            
        except Exception as e:
            logger.error(f"Failed to get blob metadata: {e}")
            return None

# Global instance
azure_storage_service = AzureStorageService() 