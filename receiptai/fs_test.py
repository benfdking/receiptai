import base64
import os
import tempfile
import unittest

from fs import LocalFileSystem


class TestLocalFileSystem(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.fs = LocalFileSystem(self.temp_dir)

        # Test data for different MIME types
        self.pdf_data = b'%PDF-1.0 Test PDF'
        self.jpeg_data = b'\xff\xd8\xff Test JPEG'
        self.png_data = b'\x89PNG\r\n\x1a\n Test PNG'
        self.json_data = b'{"test": "data"}'
        self.html_data = b'<!DOCTYPE html><html></html>'

    def tearDown(self):
        # Clean up temporary directory
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_save_file_bytes(self):
        # Test saving binary data
        path = self.fs.save_file('test_pdf', 'application/pdf', self.pdf_data)
        self.assertTrue(os.path.exists(path))
        with open(path, 'rb') as f:
            content = f.read()
        self.assertEqual(content, self.pdf_data)

    def test_save_file_base64(self):
        # Test saving base64 encoded string
        encoded_data = base64.b64encode(self.jpeg_data).decode('utf-8')
        path = self.fs.save_file('test_jpeg', 'image/jpeg', encoded_data)
        self.assertTrue(os.path.exists(path))
        with open(path, 'rb') as f:
            content = f.read()
        self.assertEqual(content, self.jpeg_data)

    def test_retrieve_file(self):
        # Save and then retrieve a file
        test_path = os.path.join(self.temp_dir, 'test_file.txt')
        test_content = b'Test content'
        with open(test_path, 'wb') as f:
            f.write(test_content)

        retrieved_content = self.fs.retrieve_file('test_file.txt')
        self.assertEqual(retrieved_content, test_content)

    def test_retrieve_nonexistent_file(self):
        # Test retrieving a file that doesn't exist
        with self.assertRaises(FileNotFoundError):
            self.fs.retrieve_file('nonexistent_file.txt')

    def test_path_traversal_prevention(self):
        # Test that path traversal attacks are prevented
        with self.assertRaises(ValueError):
            self.fs._get_full_path('../../../../../etc/passwd')

    def test_mime_type_validation(self):
        # Test that MIME types are validated
        pdf_valid = self.fs._validate_mime_type(self.pdf_data, 'application/pdf')
        self.assertTrue(pdf_valid)

        # Test with invalid data for MIME type
        pdf_invalid = self.fs._validate_mime_type(b'invalid data', 'application/pdf')
        self.assertFalse(pdf_invalid)

    def test_file_extension_mapping(self):
        # Test file extensions are correctly applied based on MIME type
        path = self.fs.save_file('test_json', 'application/json', self.json_data)
        self.assertTrue(path.endswith('.json'))

        path = self.fs.save_file('test_png', 'image/png', self.png_data)
        self.assertTrue(path.endswith('.png'))

if __name__ == '__main__':
    unittest.main()
