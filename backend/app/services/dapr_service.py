import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from dapr.clients.grpc._request import (TransactionalStateOperation,
                                        TransactionOperationType)
from dapr.clients.grpc._response import GetStateResponse

from dapr import DaprClient

from ..config import settings

logger = logging.getLogger(__name__)

class DaprService:
    """Dapr service for distributed application runtime integration"""
    
    def __init__(self):
        self.dapr_client = DaprClient()
        self.http_port = settings.dapr_http_port
        self.grpc_port = settings.dapr_grpc_port
        self.enabled = settings.dapr_enabled
        
        if not self.enabled:
            logger.warning("Dapr is disabled in configuration")
    
    async def invoke_service(self, service_id: str, method: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke another service via Dapr
        
        Args:
            service_id: Target service ID
            method: HTTP method to invoke
            data: Request data
            
        Returns:
            Response from the service
        """
        if not self.enabled:
            logger.warning("Dapr service invocation skipped - Dapr is disabled")
            return {"error": "Dapr is disabled"}
        
        try:
            response = await self.dapr_client.invoke_method(
                service_id,
                method,
                data=json.dumps(data) if data else None
            )
            
            logger.info(f"Successfully invoked service {service_id} method {method}")
            return json.loads(response.data) if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to invoke service {service_id}: {e}")
            raise
    
    async def save_state(self, store_name: str, key: str, value: Any, etag: str = None) -> bool:
        """
        Save state to Dapr state store
        
        Args:
            store_name: Name of the state store
            key: State key
            value: State value
            etag: ETag for concurrency control
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.warning("Dapr state save skipped - Dapr is disabled")
            return False
        
        try:
            await self.dapr_client.save_state(
                store_name=store_name,
                key=key,
                value=json.dumps(value),
                etag=etag
            )
            
            logger.info(f"Successfully saved state to {store_name} with key {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state to {store_name}: {e}")
            return False
    
    async def get_state(self, store_name: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Get state from Dapr state store
        
        Args:
            store_name: Name of the state store
            key: State key
            
        Returns:
            State value or None if not found
        """
        if not self.enabled:
            logger.warning("Dapr state get skipped - Dapr is disabled")
            return None
        
        try:
            response: GetStateResponse = await self.dapr_client.get_state(
                store_name=store_name,
                key=key
            )
            
            if response.data:
                logger.info(f"Successfully retrieved state from {store_name} with key {key}")
                return json.loads(response.data)
            else:
                logger.info(f"No state found in {store_name} with key {key}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get state from {store_name}: {e}")
            return None
    
    async def delete_state(self, store_name: str, key: str, etag: str = None) -> bool:
        """
        Delete state from Dapr state store
        
        Args:
            store_name: Name of the state store
            key: State key
            etag: ETag for concurrency control
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.warning("Dapr state delete skipped - Dapr is disabled")
            return False
        
        try:
            await self.dapr_client.delete_state(
                store_name=store_name,
                key=key,
                etag=etag
            )
            
            logger.info(f"Successfully deleted state from {store_name} with key {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete state from {store_name}: {e}")
            return False
    
    async def publish_event(self, pubsub_name: str, topic: str, data: Dict[str, Any]) -> bool:
        """
        Publish event to Dapr pub/sub
        
        Args:
            pubsub_name: Name of the pub/sub component
            topic: Topic name
            data: Event data
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.warning("Dapr event publish skipped - Dapr is disabled")
            return False
        
        try:
            await self.dapr_client.publish_event(
                pubsub_name=pubsub_name,
                topic=topic,
                data=json.dumps(data),
                publish_metadata={"ttlInSeconds": "120"}
            )
            
            logger.info(f"Successfully published event to {pubsub_name}/{topic}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event to {pubsub_name}/{topic}: {e}")
            return False
    
    async def get_secret(self, store_name: str, key: str) -> Optional[str]:
        """
        Get secret from Dapr secret store
        
        Args:
            store_name: Name of the secret store
            key: Secret key
            
        Returns:
            Secret value or None if not found
        """
        if not self.enabled:
            logger.warning("Dapr secret get skipped - Dapr is disabled")
            return None
        
        try:
            response = await self.dapr_client.get_secret(
                store_name=store_name,
                key=key
            )
            
            if response.secret:
                logger.info(f"Successfully retrieved secret from {store_name} with key {key}")
                return response.secret.get(key)
            else:
                logger.warning(f"No secret found in {store_name} with key {key}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get secret from {store_name}: {e}")
            return None
    
    async def save_state_transaction(self, store_name: str, operations: List[Dict[str, Any]]) -> bool:
        """
        Execute a state transaction with multiple operations
        
        Args:
            store_name: Name of the state store
            operations: List of operations to execute
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.warning("Dapr state transaction skipped - Dapr is disabled")
            return False
        
        try:
            # Convert operations to Dapr format
            dapr_operations = []
            for op in operations:
                operation_type = op.get("operation")
                key = op.get("key")
                value = op.get("value")
                etag = op.get("etag")
                
                if operation_type == "upsert":
                    dapr_op = TransactionalStateOperation(
                        operation_type=TransactionOperationType.upsert,
                        key=key,
                        value=json.dumps(value),
                        etag=etag
                    )
                elif operation_type == "delete":
                    dapr_op = TransactionalStateOperation(
                        operation_type=TransactionOperationType.delete,
                        key=key,
                        etag=etag
                    )
                else:
                    logger.warning(f"Unknown operation type: {operation_type}")
                    continue
                
                dapr_operations.append(dapr_op)
            
            # Execute transaction
            await self.dapr_client.execute_state_transaction(
                store_name=store_name,
                operations=dapr_operations
            )
            
            logger.info(f"Successfully executed state transaction on {store_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute state transaction on {store_name}: {e}")
            return False

# Global instance
dapr_service = DaprService() 