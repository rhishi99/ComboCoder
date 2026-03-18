import unittest
import os
import tempfile
import shutil
from pathlib import Path
from freeagentdev.core.file_ops import FileOperations


class TestFileOperations(unittest.TestCase):
    """
    Unit tests for the FileOperations class.
    
    These tests verify the correct behavior of file creation operations,
    including success cases and various error conditions.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp(prefix="freeagentdev_test_")
        self.file_ops = FileOperations()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.test_dir)
    
    def test_create_file(self):
        """Test case for successful file creation."""
        # Arrange
        filename = os.path.join(self.test_dir, "hello_test.txt")
        content = "Testing FreeAgentDev"
        
        # Act
        self.file_ops.create_file(filename, content)
        
        # Assert
        file_path = Path(filename)
        self.assertTrue(file_path.exists(), f"File {filename} should exist")
        self.assertTrue(file_path.is_file(), f"{filename} should be a file")
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        self.assertEqual(file_content, content, "File content should match the provided content")
    
    def test_create_file_permission_error(self):
        """Test case for permission error during file creation."""
        # Arrange
        # Use a path that likely doesn't exist and is not writable
        # On Unix-like systems, /root is typically not writable by regular users
        # On Windows, C:\Windows\System32 might not be writable
        if os.name == 'nt':  # Windows
            protected_path = "C:\\Windows\\System32\\test_file.txt"
        else:  # Unix-like
            protected_path = "/root/test_file.txt"
        
        content = "Test content"
        
        # Act & Assert
        with self.assertRaises(OSError, msg="Should raise OSError for permission denied"):
            self.file_ops.create_file(protected_path, content)
    
    def test_create_file_existing_file(self):
        """Test case for creating a file that already exists (should overwrite)."""
        # Arrange
        filename = os.path.join(self.test_dir, "existing_file.txt")
        initial_content = "Initial content"
        new_content = "Updated content"
        
        # Create the file first
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # Verify the file exists and has the initial content
        file_path = Path(filename)
        self.assertTrue(file_path.exists())
        with open(file_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), initial_content)
        
        # Act: Create the file again with new content
        self.file_ops.create_file(filename, new_content)
        
        # Assert: The file should be overwritten with the new content
        self.assertTrue(file_path.exists(), f"File {filename} should still exist")
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        self.assertEqual(file_content, new_content, "Existing file should be overwritten with new content")
    
    def test_create_file_in_nested_directory(self):
        """Test creating a file in a nested directory that doesn't exist (should create directories)."""
        # Arrange
        filename = os.path.join(self.test_dir, "nested", "dir", "deep_file.txt")
        content = "Deeply nested content"
        
        # Act
        self.file_ops.create_file(filename, content)
        
        # Assert
        file_path = Path(filename)
        self.assertTrue(file_path.exists(), f"File {filename} should exist")
        self.assertTrue(file_path.parent.exists(), f"Parent directory {file_path.parent} should exist")
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        self.assertEqual(file_content, content, "File content should match")
    
    def test_create_file_with_empty_content(self):
        """Test creating a file with empty content."""
        # Arrange
        filename = os.path.join(self.test_dir, "empty.txt")
        content = ""
        
        # Act
        self.file_ops.create_file(filename, content)
        
        # Assert
        file_path = Path(filename)
        self.assertTrue(file_path.exists(), f"File {filename} should exist")
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        self.assertEqual(file_content, content, "File content should be empty")
    
    def test_create_file_with_none_filename(self):
        """Test creating a file with None filename (should raise TypeError)."""
        # Arrange
        content = "Test content"
        
        # Act & Assert
        with self.assertRaises(TypeError, msg="Should raise TypeError for None filename"):
            self.file_ops.create_file(None, content)
    
    def test_create_file_with_none_content(self):
        """Test creating a file with None content (should raise TypeError)."""
        # Arrange
        filename = os.path.join(self.test_dir, "test.txt")
        
        # Act & Assert
        with self.assertRaises(TypeError, msg="Should raise TypeError for None content"):
            self.file_ops.create_file(filename, None)
    
    def test_create_file_with_non_string_filename(self):
        """Test creating a file with non-string filename (should raise TypeError)."""
        # Arrange
        filename = 123
        content = "Test content"
        
        # Act & Assert
        with self.assertRaises(TypeError, msg="Should raise TypeError for non-string filename"):
            self.file_ops.create_file(filename, content)
    
    def test_create_file_with_non_string_content(self):
        """Test creating a file with non-string content (should raise TypeError)."""
        # Arrange
        filename = os.path.join(self.test_dir, "test.txt")
        content = 123
        
        # Act & Assert
        with self.assertRaises(TypeError, msg="Should raise TypeError for non-string content"):
            self.file_ops.create_file(filename, content)


if __name__ == '__main__':
    unittest.main()
