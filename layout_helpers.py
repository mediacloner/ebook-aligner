"""
Layout helper functions for different bilingual EPUB presentation modes.

This module provides HTML generation functions for various layout modes
inspired by the Ebook-Translator-Calibre-Plugin analysis.
"""

from bs4 import BeautifulSoup


def create_comparison_table(soup, en_node, es_content, config):
    """
    Creates a side-by-side table layout for parallel reading.
    
    Args:
        soup: BeautifulSoup object for creating new tags
        en_node: The original English BeautifulSoup node
        es_content: Spanish content (can be text or parsed HTML)
        config: BilingualConfig object with layout settings
        
    Returns:
        BeautifulSoup table element ready to insert
    """
    bilingual_config = config.get('bilingual')
    
    # Create table structure
    table = soup.new_tag('table')
    table['width'] = '100%'
    table['style'] = 'border-collapse: collapse; margin-bottom: 1em;'
    
    tr = soup.new_tag('tr')
    td_left = soup.new_tag('td')
    td_left['style'] = 'vertical-align: top; padding-right: 0.5em;'
    
    td_gap = soup.new_tag('td')
    td_right = soup.new_tag('td')
    td_right['style'] = 'vertical-align: top; padding-left: 0.5em;'
    
    # Set column widths based on gap percentage
    gap_pct = bilingual_config.column_gap_percentage
    side_width = (100 - gap_pct) / 2
    
    td_left.set('width', f'{side_width}%')
    td_gap.set('width', f'{gap_pct}%')
    td_right.set('width', f'{side_width}%')
    
    # Clone English node for left/right placement
    import copy
    en_clone = copy.copy(en_node)
    
    # Remove bottom margin from English to prevent double spacing
    en_style = en_clone.get('style', '')
    if en_style:
        en_style += ';'
    en_clone['style'] = en_style + ' margin-bottom: 0;'
    
    # Create Spanish node
    es_node = soup.new_tag(en_node.name)
    es_node.attrs = en_node.attrs.copy()
    if 'id' in es_node.attrs:
        del es_node.attrs['id']
    
    # Add styling based on configuration
    apply_styling(es_node, config, is_translation=True)
    
    # Parse and add Spanish content
    if isinstance(es_content, str):
        es_parsed = BeautifulSoup(es_content, 'html.parser')
        es_node.append(es_parsed)
    else:
        es_node.append(es_content)
    
    # Place content in correct columns based on left_column_language
    if bilingual_config.left_column_language == 'english':
        td_left.append(en_clone)
        td_right.append(es_node)
    else:  # Spanish on left
        td_left.append(es_node)
        td_right.append(en_clone)
    
    # Assemble table
    tr.append(td_left)
    tr.append(td_gap)
    tr.append(td_right)
    table.append(tr)
    
    return table


def apply_styling(node, config, is_translation=False):
    """
    Applies styling to a node based on configuration mode.
    
    Args:
        node: BeautifulSoup node to style
        config: Configuration dict with 'bilingual' key
        is_translation: Whether this is the translation (Spanish) node
    """
    bilingual_config = config.get('bilingual')
    if not bilingual_config:
        return
    
    from bilingual_config import StyleMode
    
    # Determine which color to use
    if is_translation:
        color = bilingual_config.translation_color
        css_class = bilingual_config.translation_class
    else:
        color = bilingual_config.original_color
        css_class = None  # Original doesn't get special class
    
    # Apply styling based on mode
    # ALWAYS apply color if explicitly set in config, regardless of mode
    # (Users expect the color they picked to work)
    if color:
        current_style = node.get('style', '')
        if current_style and not current_style.endswith(';'):
            current_style += ';'
        node['style'] = f"{current_style} color: {color} !important;"

    # Apply class if needed
    if bilingual_config.style_mode == StyleMode.CLASS_BASED or bilingual_config.style_mode == StyleMode.HYBRID:
        if is_translation and css_class:
            current_classes = node.get('class', [])
            if isinstance(current_classes, str):
                current_classes = [current_classes]
            if css_class not in current_classes:
                current_classes.append(css_class)
            node['class'] = current_classes


def inject_layout_mode(soup, en_node, es_content, config):
    """
    Main entry point for layout-mode-aware injection.
    
    This function routes to the appropriate layout strategy based on configuration.
    
    Args:
        soup: BeautifulSoup object
        en_node: Original English node
        es_content: Spanish translation content (string or HTML)
        config: Configuration dict with 'bilingual' key
        
    Returns:
        The modified/inserted node(s) or None
    """
    bilingual_config = config.get('bilingual')
    if not bilingual_config:
        # Fallback to default behavior
        return None
    
    from bilingual_config import LayoutMode
    
    mode = bilingual_config.layout_mode
    
    # Check if element-type-specific formatting is enabled
    if bilingual_config.element_type_formatting:
        return inject_type_aware(soup, en_node, es_content, config, mode)
    
    # Standard layout mode routing
    if mode == LayoutMode.SPANISH_ONLY:
        return inject_spanish_only(soup, en_node, es_content, config)
    elif mode == LayoutMode.ABOVE:
        return inject_above(soup, en_node, es_content, config)
    elif mode == LayoutMode.SIDE_BY_SIDE:
        return inject_side_by_side(soup, en_node, es_content, config)
    else:  # LayoutMode.BELOW (default)
        return inject_below(soup, en_node, es_content, config)


def inject_type_aware(soup, en_node, es_content, config, layout_mode):
    """
    Apply element-type-specific formatting strategies.
    
    Different element types benefit from different bilingual presentation:
    - Inline elements (em, strong, code): Stay inline with space separator
    - List/Table elements (li, td, th): Vertical stacking with <br>
    - Block elements: Standard layout mode behavior
    """
    INLINE_TAGS = {'em', 'strong', 'a', 'span', 'code', 'kbd', 'abbr', 'cite', 'q'}
    LIST_TABLE_TAGS = {'li', 'dt', 'dd', 'td', 'th', 'caption'}
    
    elem_name = en_node.name if en_node.name else 'div'
    
    # Inline elements: append with space separator
    if elem_name.lower() in INLINE_TAGS:
        return inject_inline_with_space(soup, en_node, es_content, config)
    
    # List/Table elements: use <br> for clean stacking
    elif elem_name.lower() in LIST_TABLE_TAGS:
        return inject_with_br_separator(soup, en_node, es_content, config)
    
    # Block elements: use configured layout mode
    else:
        # Use standard layout mode injection
        from bilingual_config import LayoutMode
        if layout_mode == LayoutMode.SPANISH_ONLY:
            return inject_spanish_only(soup, en_node, es_content, config)
        elif layout_mode == LayoutMode.ABOVE:
            return inject_above(soup, en_node, es_content, config)
        elif layout_mode == LayoutMode.SIDE_BY_SIDE:
            return inject_side_by_side(soup, en_node, es_content, config)
        else:
            return inject_below(soup, en_node, es_content, config)


def inject_inline_with_space(soup, en_node, es_content, config):
    """Inject Spanish inline with space separator (for em, strong, code, etc.)."""
    # Create a span for the Spanish content
    es_span = soup.new_tag('span')
    apply_styling(es_span, config, is_translation=True)
    
    # Parse and add content
    if isinstance(es_content, str):
        es_parsed = BeautifulSoup(es_content, 'html.parser')
        es_span.append(es_parsed)
    else:
        es_span.append(es_content)
    
    # Insert space and Spanish span after English
    space = soup.new_string(' ')
    en_node.insert_after(space)
    space.insert_after(es_span)
    
    return es_span


def inject_with_br_separator(soup, en_node, es_content, config):
    """Inject Spanish with <br> separator (for li, td, th, etc.)."""
    # Create line break
    br = soup.new_tag('br')
    
    # Create Spanish span
    es_span = soup.new_tag('span')
    apply_styling(es_span, config, is_translation=True)
    
    # Parse and add content
    if isinstance(es_content, str):
        es_parsed = BeautifulSoup(es_content, 'html.parser')
        es_span.append(es_parsed)
    else:
        es_span.append(es_content)
    
    # Append <br> and Spanish to the English node directly
    en_node.append(br)
    en_node.append(es_span)
    
    return es_span



def inject_spanish_only(soup, en_node, es_content, config):
    """Replace English with Spanish translation."""
    # Clear English node content
    en_node.clear()
    
    # Parse and insert Spanish content
    if isinstance(es_content, str):
        es_parsed = BeautifulSoup(es_content, 'html.parser')
        en_node.append(es_parsed)
    else:
        en_node.append(es_content)
    
    # Apply styling
    apply_styling(en_node, config, is_translation=True)
    
    return en_node


def inject_above(soup, en_node, es_content, config):
    """Insert Spanish translation above English original."""
    # Create Spanish node
    es_node = soup.new_tag(en_node.name)
    es_node.attrs = en_node.attrs.copy()
    if 'id' in es_node.attrs:
        del es_node.attrs['id']
    
    # Parse and add Spanish content
    if isinstance(es_content, str):
        es_parsed = BeautifulSoup(es_content, 'html.parser')
        es_node.append(es_parsed)
    else:
        es_node.append(es_content)
    
    # Apply styling
    apply_styling(es_node, config, is_translation=True)
    
    # Adjust spacing
    es_style = es_node.get('style', '')
    if es_style and not es_style.endswith(';'):
        es_style += ';'
    es_node['style'] = es_style + ' margin-bottom: 0;'
    
    en_style = en_node.get('style', '')
    if en_style and not en_style.endswith(';'):
        en_style += ';'
    en_node['style'] = en_style + ' margin-top: 0;'
    
    # Insert Spanish before English
    en_node.insert_before(es_node)
    
    return es_node


def inject_below(soup, en_node, es_content, config):
    """Insert Spanish translation below English original (default behavior)."""
    bilingual_config = config.get('bilingual')
    
    # Create Spanish node
    es_node = soup.new_tag(en_node.name)
    es_node.attrs = en_node.attrs.copy()
    if 'id' in es_node.attrs:
        del es_node.attrs['id']
    
    # For compatibility with existing code, wrap in span if using BR separator
    if bilingual_config and bilingual_config.use_br_separator:
        span = soup.new_tag('span')
        apply_styling(span, config, is_translation=True)
        
        if isinstance(es_content, str):
            es_parsed = BeautifulSoup(es_content, 'html.parser')
            span.append(es_parsed)
        else:
            span.append(es_content)
        
        es_node.append(span)
    else:
        # Direct content insertion
        if isinstance(es_content, str):
            es_parsed = BeautifulSoup(es_content, 'html.parser')
            es_node.append(es_parsed)
        else:
            es_node.append(es_content)
        
        apply_styling(es_node, config, is_translation=True)
    
    # Adjust spacing
    en_style = en_node.get('style', '')
    if en_style and not en_style.endswith(';'):
        en_style += ';'
    en_node['style'] = en_style + ' margin-bottom: 0;'
    
    es_style = es_node.get('style', '')
    if es_style and not es_style.endswith(';'):
        es_style += ';'
    es_node['style'] = es_style + ' margin-top: 0;'
    
    # Insert Spanish after English
    en_node.insert_after(es_node)
    
    return es_node


def inject_side_by_side(soup, en_node, es_content, config):
    """Create side-by-side table layout for parallel reading."""
    table = create_comparison_table(soup, en_node, es_content, config)
    
    # Replace the English node with the table
    en_node.replace_with(table)
    
    return table
