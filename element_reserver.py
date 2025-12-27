"""
Element Reserver - Preserve complex elements during alignment.

This module provides a system to extract complex nested elements (SVG, MathML,
code blocks, etc.) before text alignment and restore them afterward, preventing
corruption during HTML manipulation.
"""

import re
from bs4 import BeautifulSoup, NavigableString


class ElementReserver:
    """
    Preserve complex elements during text alignment.
    
    Usage:
        reserver = ElementReserver()
        cleaned_html = reserver.extract_and_mark(original_html)
        # ... perform alignment on cleaned_html ...
        final_html = reserver.restore(aligned_html)
    """
    
    # Elements that should be preserved as-is during alignment
    RESERVED_TAGS = {
        'svg', 'math', 'code', 'pre', 'script', 'style',
        'canvas', 'object', 'embed', 'iframe', 'video', 'audio'
    }
    
    # Placeholder format: unique and unlikely to appear in natural text
    PLACEHOLDER_FORMAT = "___RESERVED_ELEMENT_{:05d}___"
    
    def __init__(self):
        self.reserved_elements = []
        self.placeholder_pattern = re.compile(r'___RESERVED_ELEMENT_(\d{5})___')
    
    def extract_and_mark(self, soup_element):
        """
        Extract reserved elements and replace with placeholders.
        
        Args:
            soup_element: BeautifulSoup element to process
            
        Returns:
            Modified soup_element with placeholders
        """
        if isinstance(soup_element, NavigableString):
            return soup_element
        
        # Find all reserved elements in depth-first order
        reserved_elems = []
        for tag_name in self.RESERVED_TAGS:
            reserved_elems.extend(soup_element.find_all(tag_name))
        
        # Replace each with a placeholder
        for elem in reserved_elems:
            idx = len(self.reserved_elements)
            placeholder_text = self.PLACEHOLDER_FORMAT.format(idx)
            
            # Store the original HTML
            self.reserved_elements.append(str(elem))
            
            # Replace element with placeholder text
            placeholder_tag = soup_element.new_tag('span')
            placeholder_tag.string = placeholder_text
            placeholder_tag['class'] = 'reserved-placeholder'
            
            elem.replace_with(placeholder_tag)
        
        return soup_element
    
    def restore(self, html_or_soup):
        """
        Restore reserved elements from placeholders.
        
        Args:
            html_or_soup: HTML string or BeautifulSoup object containing placeholders
            
        Returns:
            HTML string or BeautifulSoup with reserved elements restored
        """
        if isinstance(html_or_soup, BeautifulSoup):
            return self._restore_soup(html_or_soup)
        else:
            return self._restore_string(str(html_or_soup))
    
    def _restore_soup(self, soup):
        """Restore placeholders in a BeautifulSoup object."""
        # Find all placeholder spans
        placeholders = soup.find_all('span', class_='reserved-placeholder')
        
        for placeholder in placeholders:
            text = placeholder.get_text()
            match = self.placeholder_pattern.match(text)
            
            if match:
                idx = int(match.group(1))
                if 0 <= idx < len(self.reserved_elements):
                    # Parse the reserved HTML
                    reserved_html = self.reserved_elements[idx]
                    reserved_elem = BeautifulSoup(reserved_html, 'html.parser')
                    
                    # Replace placeholder with original element
                    if reserved_elem.contents:
                        placeholder.replace_with(reserved_elem.contents[0])
        
        return soup
    
    def _restore_string(self, html_text):
        """Restore placeholders in an HTML string."""
        def replace_placeholder(match):
            idx = int(match.group(1))
            if 0 <= idx < len(self.reserved_elements):
                return self.reserved_elements[idx]
            return match.group(0)
        
        # Replace all placeholder patterns with original HTML
        restored = self.placeholder_pattern.sub(replace_placeholder, html_text)
        
        # Clean up any remaining placeholder span tags
        restored = re.sub(r'<span class=["\']reserved-placeholder["\']>(.*?)</span>', 
                         replace_placeholder, restored)
        
        return restored
    
    def clear(self):
        """Clear all reserved elements (use when processing a new document)."""
        self.reserved_elements.clear()


def should_reserve_element(elem):
    """
    Determine if an element should be reserved during alignment.
    
    Args:
        elem: BeautifulSoup element to check
        
    Returns:
        bool: True if element should be reserved
    """
    if not elem.name:
        return False
    
    return elem.name in ElementReserver.RESERVED_TAGS
