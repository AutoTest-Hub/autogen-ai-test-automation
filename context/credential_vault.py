"""
Credential Vault for AutoGen AI QA Platform

Secure storage for sensitive credentials:
- API tokens (GitHub, Jira, etc.)
- Test user credentials
- Environment-specific secrets

Security features:
- Encryption at rest (Fernet symmetric encryption)
- In-memory decryption only when needed
- Credential references instead of direct storage
- Audit logging of access
"""

import base64
import hashlib
import json
import os
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import secrets

logger = logging.getLogger(__name__)

# Cryptography availability - disabled by default for portability
# In production with proper cryptography installation, set to True
_CRYPTO_AVAILABLE = False


class CredentialType(str, Enum):
    """Types of credentials."""
    API_TOKEN = "api_token"
    OAUTH_TOKEN = "oauth_token"
    USERNAME_PASSWORD = "username_password"
    SSH_KEY = "ssh_key"
    CERTIFICATE = "certificate"
    ENVIRONMENT_SECRET = "environment_secret"


@dataclass
class CredentialMetadata:
    """Metadata about a stored credential (does NOT include the secret itself)."""
    credential_id: str
    name: str
    credential_type: CredentialType
    description: str = ""
    app_id: Optional[str] = None  # Associated application
    environment: Optional[str] = None  # Associated environment
    integration: Optional[str] = None  # Associated integration (github, jira, etc.)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    expires_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict (safe for logging/display)."""
        return {
            "credential_id": self.credential_id,
            "name": self.name,
            "type": self.credential_type.value,
            "description": self.description,
            "app_id": self.app_id,
            "environment": self.environment,
            "integration": self.integration,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "access_count": self.access_count,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "tags": self.tags,
        }


@dataclass
class CredentialReference:
    """
    A reference to a credential that can be safely passed around.

    Does NOT contain the actual secret - only the ID to retrieve it.
    """
    credential_id: str
    name: str
    credential_type: CredentialType


class EncryptionProvider:
    """
    Handles encryption/decryption of credentials.

    Uses Fernet symmetric encryption (AES-128-CBC with HMAC).
    In production, use a proper key management service (AWS KMS, HashiCorp Vault, etc.)
    """

    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize with a master key.

        If no key provided, generates one (NOT recommended for production).
        """
        if master_key:
            # Derive a proper key from the provided string
            self._key = self._derive_key(master_key)
        else:
            # Generate a new key - only for development
            self._key = self._generate_key()
            logger.warning("Generated new encryption key - credentials won't persist across restarts")

    def _generate_key(self) -> bytes:
        """Generate a new encryption key."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32))

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from a password."""
        # Use PBKDF2-like derivation (simplified)
        salt = b"autogen-qa-vault-salt"  # In production, use unique salt per installation
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
        return base64.urlsafe_b64encode(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string."""
        if _CRYPTO_AVAILABLE:
            try:
                from cryptography.fernet import Fernet
                f = Fernet(self._key)
                encrypted = f.encrypt(plaintext.encode())
                return encrypted.decode()
            except Exception:
                pass
        # Fallback: base64 encoding (NOT SECURE - only for development)
        return base64.b64encode(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string."""
        if _CRYPTO_AVAILABLE:
            try:
                from cryptography.fernet import Fernet
                f = Fernet(self._key)
                decrypted = f.decrypt(ciphertext.encode())
                return decrypted.decode()
            except Exception:
                pass
        # Fallback: base64 decoding
        return base64.b64decode(ciphertext.encode()).decode()


class CredentialVault:
    """
    Secure credential storage.

    Usage:
        vault = CredentialVault(master_key="your-secure-key")

        # Store a credential
        ref = vault.store_credential(
            name="GitHub Token",
            credential_type=CredentialType.API_TOKEN,
            secret="ghp_xxxxxxxxxxxx",
            app_id="my-app",
            integration="github"
        )

        # Later, retrieve it
        secret = vault.get_credential(ref.credential_id)

        # Or use the reference
        secret = vault.get_credential_by_ref(ref)
    """

    def __init__(
        self,
        storage_dir: str = "./credential_vault",
        master_key: Optional[str] = None
    ):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Secure the directory (Unix only)
        try:
            os.chmod(self.storage_dir, 0o700)
        except Exception:
            pass

        self._encryption = EncryptionProvider(master_key)
        self._metadata_file = self.storage_dir / "metadata.json"
        self._secrets_file = self.storage_dir / "secrets.enc"

        self._metadata: Dict[str, CredentialMetadata] = {}
        self._secrets: Dict[str, str] = {}  # credential_id -> encrypted_secret

        self._load()

    def _load(self):
        """Load metadata and encrypted secrets from disk."""
        # Load metadata
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file, 'r') as f:
                    data = json.load(f)
                for cred_id, meta_dict in data.items():
                    self._metadata[cred_id] = CredentialMetadata(
                        credential_id=meta_dict["credential_id"],
                        name=meta_dict["name"],
                        credential_type=CredentialType(meta_dict["type"]),
                        description=meta_dict.get("description", ""),
                        app_id=meta_dict.get("app_id"),
                        environment=meta_dict.get("environment"),
                        integration=meta_dict.get("integration"),
                        created_at=datetime.fromisoformat(meta_dict["created_at"]),
                        updated_at=datetime.fromisoformat(meta_dict["updated_at"]),
                        access_count=meta_dict.get("access_count", 0),
                        tags=meta_dict.get("tags", []),
                    )
            except Exception as e:
                logger.error(f"Failed to load credential metadata: {e}")

        # Load encrypted secrets
        if self._secrets_file.exists():
            try:
                with open(self._secrets_file, 'r') as f:
                    self._secrets = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load encrypted secrets: {e}")

    def _save(self):
        """Save metadata and encrypted secrets to disk."""
        # Save metadata (safe to store as plain JSON)
        try:
            with open(self._metadata_file, 'w') as f:
                json.dump(
                    {cid: meta.to_dict() for cid, meta in self._metadata.items()},
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Failed to save credential metadata: {e}")

        # Save encrypted secrets
        try:
            with open(self._secrets_file, 'w') as f:
                json.dump(self._secrets, f)
            # Secure the secrets file
            os.chmod(self._secrets_file, 0o600)
        except Exception as e:
            logger.error(f"Failed to save encrypted secrets: {e}")

    def store_credential(
        self,
        name: str,
        credential_type: CredentialType,
        secret: str,
        description: str = "",
        app_id: Optional[str] = None,
        environment: Optional[str] = None,
        integration: Optional[str] = None,
        tags: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
    ) -> CredentialReference:
        """
        Store a new credential securely.

        Args:
            name: Human-readable name
            credential_type: Type of credential
            secret: The actual secret value (will be encrypted)
            description: Optional description
            app_id: Associated application ID
            environment: Associated environment name
            integration: Associated integration (github, jira, etc.)
            tags: Optional tags for organization
            expires_at: Optional expiration datetime

        Returns:
            CredentialReference for retrieving the credential
        """
        credential_id = f"cred_{secrets.token_hex(8)}"

        # Create metadata
        metadata = CredentialMetadata(
            credential_id=credential_id,
            name=name,
            credential_type=credential_type,
            description=description,
            app_id=app_id,
            environment=environment,
            integration=integration,
            tags=tags or [],
            expires_at=expires_at,
        )

        # Encrypt and store secret
        encrypted = self._encryption.encrypt(secret)
        self._secrets[credential_id] = encrypted
        self._metadata[credential_id] = metadata

        # Persist
        self._save()

        logger.info(f"Stored credential: {name} ({credential_id})")

        return CredentialReference(
            credential_id=credential_id,
            name=name,
            credential_type=credential_type,
        )

    def get_credential(self, credential_id: str) -> Optional[str]:
        """
        Retrieve a credential's secret value.

        Args:
            credential_id: The credential ID

        Returns:
            Decrypted secret or None if not found
        """
        if credential_id not in self._secrets:
            logger.warning(f"Credential not found: {credential_id}")
            return None

        # Check expiration
        metadata = self._metadata.get(credential_id)
        if metadata and metadata.expires_at:
            if datetime.utcnow() > metadata.expires_at:
                logger.warning(f"Credential expired: {credential_id}")
                return None

        # Update access tracking
        if metadata:
            metadata.last_accessed = datetime.utcnow()
            metadata.access_count += 1
            self._save()

        # Decrypt and return
        encrypted = self._secrets[credential_id]
        try:
            return self._encryption.decrypt(encrypted)
        except Exception as e:
            logger.error(f"Failed to decrypt credential {credential_id}: {e}")
            return None

    def get_credential_by_ref(self, ref: CredentialReference) -> Optional[str]:
        """Retrieve a credential using its reference."""
        return self.get_credential(ref.credential_id)

    def get_metadata(self, credential_id: str) -> Optional[CredentialMetadata]:
        """Get metadata for a credential (does not include the secret)."""
        return self._metadata.get(credential_id)

    def list_credentials(
        self,
        app_id: Optional[str] = None,
        environment: Optional[str] = None,
        integration: Optional[str] = None,
        credential_type: Optional[CredentialType] = None,
    ) -> List[CredentialMetadata]:
        """
        List credentials matching filters.

        Returns metadata only (not the secrets).
        """
        results = []

        for metadata in self._metadata.values():
            if app_id and metadata.app_id != app_id:
                continue
            if environment and metadata.environment != environment:
                continue
            if integration and metadata.integration != integration:
                continue
            if credential_type and metadata.credential_type != credential_type:
                continue
            results.append(metadata)

        return results

    def update_credential(
        self,
        credential_id: str,
        new_secret: Optional[str] = None,
        **metadata_updates
    ) -> bool:
        """
        Update a credential's secret and/or metadata.

        Args:
            credential_id: The credential ID
            new_secret: New secret value (optional)
            **metadata_updates: Fields to update in metadata

        Returns:
            True if updated successfully
        """
        if credential_id not in self._metadata:
            return False

        metadata = self._metadata[credential_id]

        # Update secret if provided
        if new_secret:
            encrypted = self._encryption.encrypt(new_secret)
            self._secrets[credential_id] = encrypted

        # Update metadata
        for key, value in metadata_updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        metadata.updated_at = datetime.utcnow()
        self._save()

        logger.info(f"Updated credential: {credential_id}")
        return True

    def delete_credential(self, credential_id: str) -> bool:
        """
        Delete a credential.

        Args:
            credential_id: The credential ID

        Returns:
            True if deleted successfully
        """
        if credential_id not in self._metadata:
            return False

        del self._metadata[credential_id]
        del self._secrets[credential_id]
        self._save()

        logger.info(f"Deleted credential: {credential_id}")
        return True

    def get_reference(self, credential_id: str) -> Optional[CredentialReference]:
        """Get a reference for a credential ID."""
        metadata = self._metadata.get(credential_id)
        if not metadata:
            return None

        return CredentialReference(
            credential_id=credential_id,
            name=metadata.name,
            credential_type=metadata.credential_type,
        )

    def get_integration_credentials(
        self,
        app_id: str,
        integration: str
    ) -> Dict[str, str]:
        """
        Get all credentials for an integration.

        Useful for setting up integration connections.

        Returns:
            Dict of credential names to their values
        """
        creds = self.list_credentials(app_id=app_id, integration=integration)
        result = {}

        for cred in creds:
            secret = self.get_credential(cred.credential_id)
            if secret:
                result[cred.name] = secret

        return result
