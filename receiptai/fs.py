import os
import base64
import logging
from abc import ABC, abstractmethod
from typing import Union, Dict
from pydantic import BaseModel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttachmentResponse(BaseModel):
    filename: str
    mimeType: str
    data: Union[bytes, str]

class FileSystem(ABC):
    """
    Abstract base class for a file system.
    """
    @abstractmethod
    def save_file(self, filename: str, mimeType: str, data: Union[bytes, str]) -> str:
        """
        Saves the given content against the filename.
        Args:
            filename: The path to save the file to.
            mimeType: The MIME type of the data.
            data: The data to save.  Must be bytes or a string.
        Returns:
            The path to the saved file.
        """
        pass

    @abstractmethod
    def retrieve_file(self, filename: str) -> Union[bytes, str]:
        """
        Retrieves the content of the file at the specified path.
        Args:
            path: The path to the file to retrieve.
        Returns:
            The content of the file, either as bytes or a string.
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        pass



class LocalFileSystem(FileSystem):
    """
    A local file system implementation that checks MIME types before saving files.
    """
    MIME_SIGNATURES: Dict[str, bytes] = {
        'application/pdf': b'%PDF-',
        'image/jpeg': b'\xFF\xD8\xFF',
        'image/png': b'\x89PNG\r\n\x1A\n',
        'application/zip': b'PK\x03\x04',
        'application/x-gzip': b'\x1F\x8B\x08',
        'text/html': b'<!DOCTYPE',
        'application/json': b'{',
    }

    MIME_SIGNATURES_EXTENSIONS: Dict[str, str] = {
        'application/pdf': 'pdf',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'application/zip': 'zip',
        'application/x-gzip': 'gz',
        'text/html': 'html',
        'application/json': 'json',
    }

    def __init__(self, base_directory: str = '.'):
        """
        Initialize the local file system.

        Args:
            base_directory: The base directory for all file operations.
        """
        self.base_directory = os.path.abspath(base_directory)
        os.makedirs(self.base_directory, exist_ok=True)
        logger.info(f"LocalFileSystem initialized with base directory: {self.base_directory}")

    def _get_full_path(self, filename: str) -> str:
        """
        Get the full path for a filename.

        Args:
            filename: The relative filename.

        Returns:
            The full absolute path.
        """
        full_path = os.path.abspath(os.path.join(self.base_directory, filename))
        if not full_path.startswith(self.base_directory):
            raise ValueError(f"Path traversal attempt detected: {filename}")
        return full_path

    def _validate_mime_type(self, data: bytes, mime_type: str) -> bool:
        """
        Validate that the data matches the specified MIME type.

        Args:
            data: The binary data to validate.
            mime_type: The expected MIME type.

        Returns:
            True if valid, False otherwise.
        """
        if mime_type not in self.MIME_SIGNATURES:
            logger.warning(f"No signature defined for MIME type: {mime_type}")
            return True  # Can't check, assume it's valid

        signature = self.MIME_SIGNATURES[mime_type]
        if data.startswith(signature):
            logger.info(f"Data matches signature for MIME type: {mime_type}")
            return True

        logger.warning(f"Data does not match signature for MIME type: {mime_type}")
        return False

    def save_file(self, filename: str, mimeType: str, data: Union[bytes, str]) -> str:
        """
        Save data to a file with MIME type validation.

        Args:
            filename: The name of the file to save.
            mimeType: The MIME type of the data.
            data: The data to save, either as bytes or a string.

        Returns:
            The path to the saved file.
        """

        # Check MIME type against file extension
        if mimeType in self.MIME_SIGNATURES:
            if mimeType not in self.MIME_SIGNATURES_EXTENSIONS:
                logger.info(f"No file extension found for MIME type: {mimeType}")

        file_extension = self.MIME_SIGNATURES_EXTENSIONS[mimeType]

        full_path = self._get_full_path(f"{filename}.{file_extension}")
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Handle both string and binary data
        if isinstance(data, str):
            try:
                # Assume it's base64 encoded
                decoded_data = base64.b64decode(data)
                logger.info("Base64 decoding successful")
            except Exception as e:
                logger.error(f"Base64 decoding error: {e}")
                raise
        else:
            # It's already binary data
            decoded_data = data

        # Check MIME type
        if mimeType in self.MIME_SIGNATURES:
            if decoded_data.startswith(self.MIME_SIGNATURES[mimeType]):
                logger.info(f"Decoded data starts with expected signature for {mimeType}")
            else:
                logger.warning(f"Decoded data does NOT start with expected signature for {mimeType}")

        # Save the decoded data to a file
        try:
            with open(full_path, "wb") as f:
                f.write(decoded_data)
            logger.info(f"File saved to {full_path}")
            return full_path
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise

    def retrieve_file(self, filename: str) -> bytes:
        """
        Retrieve the content of a file.

        Args:
            filename: The name of the file to retrieve.

        Returns:
            The content of the file as bytes.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        full_path = self._get_full_path(filename)

        if not os.path.exists(full_path):
            logger.error(f"File not found: {full_path}")
            raise FileNotFoundError(f"File not found: {filename}")

        try:
            with open(full_path, "rb") as f:
                data = f.read()
            logger.info(f"File {filename} retrieved")
            return data
        except Exception as e:
            logger.error(f"Error retrieving file: {e}")
            raise
