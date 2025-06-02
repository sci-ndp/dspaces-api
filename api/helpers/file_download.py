"""
Utility functions for downloading files from URLs.
"""

import logging
import os
import tempfile
import urllib.parse
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def download_csv_from_url(
    url: str, 
    custom_filename: Optional[str] = None,
    download_dir: Optional[str] = None,
    timeout: int = 300,
    chunk_size: int = 8192
) -> str:
    """
    Download a CSV file from a URL to a local temporary or specified directory.
    
    Args:
        url: The URL to download the CSV file from
        custom_filename: Optional custom filename for the downloaded file
        download_dir: Optional directory to download to (uses temp directory if None)
        timeout: Request timeout in seconds (default: 300)
        chunk_size: Chunk size for streaming download (default: 8192)
        
    Returns:
        str: Path to the downloaded file
        
    Raises:
        ValueError: If URL is invalid or file is not accessible
        requests.RequestException: If download fails
        IOError: If file cannot be written to disk
    """
    
    # Validate URL
    parsed_url = urllib.parse.urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"Invalid URL provided: {url}")
    
    logger.info(f"Starting download from URL: {url}")
    
    try:
        # Send HEAD request first to check if file exists and get metadata
        head_response = requests.head(url, timeout=30, allow_redirects=True)
        head_response.raise_for_status()
        
        # Check content type if available
        content_type = head_response.headers.get('content-type', '').lower()
        if content_type and 'text/csv' not in content_type and 'application/csv' not in content_type and 'text/plain' not in content_type:
            logger.warning(f"Content-Type '{content_type}' may not be CSV. Proceeding anyway.")
        
        # Get file size if available for progress tracking
        content_length = head_response.headers.get('content-length')
        file_size = int(content_length) if content_length else None
        
        # Determine filename
        if custom_filename:
            filename = custom_filename
        else:
            # Try to get filename from URL or Content-Disposition header
            content_disposition = head_response.headers.get('content-disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"\'')
            else:
                # Extract from URL path
                url_path = urllib.parse.urlparse(url).path
                filename = os.path.basename(url_path) or 'downloaded_data.csv'
        
        # Ensure filename has .csv extension
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
        
        # Determine download directory
        if download_dir:
            download_path = Path(download_dir)
            download_path.mkdir(parents=True, exist_ok=True)
        else:
            download_path = Path(tempfile.gettempdir())
        
        file_path = download_path / filename
        
        logger.info(f"Downloading to: {file_path}")
        if file_size:
            logger.info(f"File size: {file_size:,} bytes")
        
        # Download the file with streaming
        with requests.get(url, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress for large files
                        if file_size and downloaded % (chunk_size * 100) == 0:
                            progress = (downloaded / file_size) * 100
                            logger.info(f"Download progress: {progress:.1f}% ({downloaded:,}/{file_size:,} bytes)")
        
        # Verify file was created and has content
        if not file_path.exists():
            raise IOError(f"Downloaded file was not created: {file_path}")
        
        actual_size = file_path.stat().st_size
        if actual_size == 0:
            raise IOError(f"Downloaded file is empty: {file_path}")
        
        logger.info(f"Successfully downloaded {actual_size:,} bytes to {file_path}")
        return str(file_path)
        
    except requests.exceptions.Timeout:
        raise ValueError(f"Download timeout after {timeout} seconds for URL: {url}")
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Could not connect to URL: {url}")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error {e.response.status_code} when accessing URL: {url}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Request failed for URL {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error downloading from URL {url}: {str(e)}")
        raise


def cleanup_downloaded_file(file_path: str) -> None:
    """
    Clean up a downloaded file.
    
    Args:
        file_path: Path to the file to remove
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up downloaded file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up file {file_path}: {str(e)}")


def validate_csv_file(file_path: str, max_sample_lines: int = 10) -> dict:
    """
    Validate that a downloaded file appears to be a valid CSV.
    
    Args:
        file_path: Path to the file to validate
        max_sample_lines: Number of lines to sample for validation
        
    Returns:
        dict: Validation results with 'is_valid', 'error', and 'sample_lines'
        
    Raises:
        IOError: If file cannot be read
    """
    try:
        import csv
        
        sample_lines = []
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first few lines
            for i, line in enumerate(f):
                if i >= max_sample_lines:
                    break
                sample_lines.append(line.strip())
        
        if not sample_lines:
            return {
                'is_valid': False,
                'error': 'File is empty',
                'sample_lines': []
            }
        
        # Try to parse first line as CSV
        try:
            first_line = sample_lines[0]
            csv_reader = csv.reader([first_line])
            columns = next(csv_reader)
            
            if len(columns) < 1:
                return {
                    'is_valid': False,
                    'error': 'No columns detected in first line',
                    'sample_lines': sample_lines
                }
            
            # Basic validation: check if we can parse multiple lines
            if len(sample_lines) > 1:
                try:
                    csv_reader = csv.reader(sample_lines[:3])  # Check first 3 lines
                    rows = list(csv_reader)
                    if len(rows) < 2:
                        return {
                            'is_valid': False,
                            'error': 'Could not parse multiple CSV rows',
                            'sample_lines': sample_lines
                        }
                except Exception as e:
                    return {
                        'is_valid': False,
                        'error': f'CSV parsing error: {str(e)}',
                        'sample_lines': sample_lines
                    }
            
            return {
                'is_valid': True,
                'error': None,
                'sample_lines': sample_lines,
                'estimated_columns': len(columns)
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': f'CSV validation error: {str(e)}',
                'sample_lines': sample_lines
            }
            
    except UnicodeDecodeError:
        return {
            'is_valid': False,
            'error': 'File encoding is not UTF-8 compatible',
            'sample_lines': []
        }
    except Exception as e:
        raise IOError(f"Could not validate CSV file {file_path}: {str(e)}")


# Utility function to dynamically generate ingestion paths
def get_dynamic_ingestion_path(dataset_name):
    # Replace this logic with actual dynamic path generation
    return f"/dynamic/path/{dataset_name}.csv"
