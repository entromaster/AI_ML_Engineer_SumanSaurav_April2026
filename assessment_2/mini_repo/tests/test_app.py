"""
Tests for the Mini Task Manager API.
Includes tests that expose the pagination bug.
"""

import os
import sys
import json
import sqlite3
import pytest

# Add mini_repo to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from models import init_db, get_db
from utils import paginate_results


@pytest.fixture
def client():
    """Create a test client."""
    app.config["TESTING"] = True
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_tasks.db")
    
    # Clean up any existing test db
    if os.path.exists(db_path):
        os.remove(db_path)
    
    init_db(db_path)
    
    # Monkey-patch the DATABASE path
    import app as app_module
    original_db = app_module.DATABASE
    app_module.DATABASE = db_path
    
    with app.test_client() as client:
        yield client
    
    # Cleanup
    app_module.DATABASE = original_db
    if os.path.exists(db_path):
        os.remove(db_path)


class TestPaginationUnit:
    """Unit tests for the pagination utility function."""
    
    def test_basic_pagination(self):
        """Test basic pagination with evenly divisible items."""
        items = list(range(1, 21))  # 20 items
        result = paginate_results(items, page=1, per_page=10)
        assert len(result["data"]) == 10
        assert result["data"] == list(range(1, 11))
        assert result["pagination"]["total_pages"] == 2
    
    def test_second_page(self):
        """Test second page returns correct items."""
        items = list(range(1, 21))  # 20 items
        result = paginate_results(items, page=2, per_page=10)
        assert len(result["data"]) == 10
        assert result["data"] == list(range(11, 21))
    
    def test_last_page_even_division(self):
        """Test last page when items divide evenly."""
        items = list(range(1, 31))  # 30 items, 3 pages of 10
        result = paginate_results(items, page=3, per_page=10)
        assert len(result["data"]) == 10
        assert result["data"] == list(range(21, 31))
    
    def test_last_page_uneven_division(self):
        """
        Test last page when items DON'T divide evenly.
        THIS TEST EXPOSES THE BUG.
        With 30 items and per_page=7:
        - Page 1: items 1-7
        - Page 2: items 8-14
        - Page 3: items 15-21
        - Page 4: items 22-28
        - Page 5 (last): should be items 29-30 (2 items)
        """
        items = list(range(1, 31))  # 30 items
        
        # Get page 4 and page 5
        page4 = paginate_results(items, page=4, per_page=7)
        page5 = paginate_results(items, page=5, per_page=7)
        
        # Page 4 should have items 22-28
        assert page4["data"] == list(range(22, 29)), f"Page 4 wrong: {page4['data']}"
        
        # Page 5 (last page) should only have items 29-30
        assert len(page5["data"]) == 2, f"Expected 2 items on last page, got {len(page5['data'])}"
        assert page5["data"] == [29, 30], f"Last page wrong: {page5['data']}"
    
    def test_no_duplicate_items_across_pages(self):
        """
        Verify that no item appears on multiple pages.
        THIS TEST ALSO EXPOSES THE BUG.
        """
        items = list(range(1, 26))  # 25 items, per_page=7 → 4 pages
        all_page_items = []
        
        total_pages = (25 + 7 - 1) // 7  # = 4 pages
        
        for page_num in range(1, total_pages + 1):
            result = paginate_results(items, page=page_num, per_page=7)
            all_page_items.extend(result["data"])
        
        # Check for duplicates
        assert len(all_page_items) == len(set(all_page_items)), \
            f"Duplicate items found! Total: {len(all_page_items)}, Unique: {len(set(all_page_items))}"
        
        # All items should be present
        assert sorted(all_page_items) == items, "Not all items are present across pages"
    
    def test_page_beyond_total(self):
        """Test requesting a page beyond total pages."""
        items = list(range(1, 11))
        result = paginate_results(items, page=5, per_page=10)
        assert result["data"] == []
    
    def test_single_item_last_page(self):
        """Test last page with exactly one item."""
        items = list(range(1, 12))  # 11 items, per_page=5 → 3 pages
        result = paginate_results(items, page=3, per_page=5)
        assert result["data"] == [11], f"Expected [11], got {result['data']}"


class TestAPIEndpoints:
    """Integration tests for the API endpoints."""
    
    def test_list_tasks(self, client):
        """Test listing tasks returns data."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert "pagination" in data
    
    def test_get_single_task(self, client):
        """Test getting a single task."""
        response = client.get("/api/tasks/1")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == 1
    
    def test_task_not_found(self, client):
        """Test 404 for non-existent task."""
        response = client.get("/api/tasks/999")
        assert response.status_code == 404
