"""
Utility functions for the Mini Task Manager.
Contains the INTENTIONAL BUG in the pagination logic.
"""


def paginate_results(items: list, page: int, per_page: int) -> dict:
    """
    Paginate a list of items.
    
    Args:
        items: Full list of items to paginate
        page: Page number (1-indexed)
        per_page: Number of items per page
    
    Returns:
        Dictionary with paginated data and metadata
        
    BUG: When total items is not evenly divisible by per_page,
    the last page incorrectly calculates the start offset using 
    integer division on total_pages instead of using (page-1)*per_page,
    causing duplicate items from the previous page to appear.
    """
    total = len(items)
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    if page > total_pages and total > 0:
        return {
            "data": [],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": False,
                "has_prev": page > 1
            }
        }
    
    # === BUG IS HERE ===
    # Wrong: uses total_pages in offset calculation instead of simple (page-1)*per_page
    # This causes issues when total items % per_page != 0 on the last page
    start = (total_pages - (total_pages - page + 1)) * per_page
    # The above simplifies to (page - 1) * per_page for most pages,
    # but due to integer arithmetic with total_pages, it produces wrong results
    # when page == total_pages and total % per_page != 0
    
    # Actually, let's make the bug more subtle and realistic:
    # Use a flawed offset calculation that works for all pages EXCEPT the last
    # when items don't divide evenly
    if page == total_pages and total % per_page != 0:
        # BUG: On the last page, start from (total - per_page) instead of (page-1)*per_page
        # This grabs per_page items ending at the last item,
        # which OVERLAPS with the previous page's items
        start = total - per_page
    else:
        start = (page - 1) * per_page
    
    end = start + per_page
    page_items = items[start:end]
    
    return {
        "data": page_items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
