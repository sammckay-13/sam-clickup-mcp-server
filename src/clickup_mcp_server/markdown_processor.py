import logging
import markdown
from bs4 import BeautifulSoup
from typing import Optional

logger = logging.getLogger(__name__)

def process_markdown(text: Optional[str], convert_to_html: bool = True) -> Optional[str]:
    """
    Process markdown text to ensure it's properly formatted for ClickUp.
    
    Args:
        text: The markdown text to process
        convert_to_html: Whether to convert the markdown to HTML (default: True)
        
    Returns:
        Processed text ready for ClickUp display
    """
    if not text:
        return text
        
    try:
        # More robust check if the input text is already HTML
        is_html = False
        text_stripped = text.strip()
        if text_stripped.startswith('<') and ('</p>' in text or '</ol>' in text or '</ul>' in text or '</div>' in text or '</br>' in text or '</b>' in text or '</i>' in text or '</a>' in text or '</span>' in text):
            is_html = True
            
        if convert_to_html:
            if is_html:
                # The content is already HTML, just ensure it's ClickUp-compatible
                return clickup_safe_html(text)
            else:
                # Convert markdown to HTML
                html = markdown.markdown(
                    text,
                    extensions=[
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.tables',
                        'markdown.extensions.nl2br',
                        'markdown.extensions.sane_lists'
                    ]
                )
                
                # Clean up the HTML to ensure it's compatible with ClickUp's HTML subset
                soup = BeautifulSoup(html, 'html.parser')
                
                # Ensure heading tags are properly formatted for ClickUp
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    tag.name = 'h'
                    tag['class'] = f"h{tag.name[-1]}"
                
                # Ensure code blocks are properly formatted
                for tag in soup.find_all('pre'):
                    if tag.code:
                        code_content = tag.code.string if tag.code.string else ''.join(str(c) for c in tag.code.contents)
                        tag.clear()
                        tag['class'] = 'code'
                        tag.string = code_content
                
                # Return the cleaned HTML
                return str(soup)
        else:
            if is_html:
                # Convert HTML to markdown-style text for display
                soup = BeautifulSoup(text, 'html.parser')
                return soup.get_text(separator='\n')
            else:
                # Just clean up the markdown for better readability
                lines = text.split('\n')
                
                # Ensure headers have proper spacing
                for i in range(len(lines)):
                    if lines[i].startswith('#'):
                        # Count the number of # symbols
                        header_level = 0
                        while header_level < len(lines[i]) and lines[i][header_level] == '#':
                            header_level += 1
                        
                        # Ensure there's a space after the # symbols
                        if header_level < len(lines[i]) and lines[i][header_level] != ' ':
                            lines[i] = lines[i][:header_level] + ' ' + lines[i][header_level:]
                
                return '\n'.join(lines)
    except Exception as e:
        logger.error(f"Error processing markdown: {e}")
        return text  # Return the original text in case of errors
        
def clickup_safe_html(html: str) -> str:
    """
    Ensure HTML is compatible with ClickUp's supported HTML subset.
    
    Args:
        html: HTML content to make ClickUp-safe
        
    Returns:
        ClickUp-compatible HTML
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # ClickUp supports a limited set of HTML tags
        allowed_tags = [
            'a', 'b', 'i', 'u', 'strike', 'code', 'pre', 'h', 'blockquote',
            'ul', 'ol', 'li', 'p', 'div', 'em', 'strong', 'del', 'span', 'br'
        ]
        
        # Process all tags to ensure they're ClickUp-compatible
        for tag in soup.find_all():
            if tag.name not in allowed_tags:
                # Replace unsupported tags with an appropriate equivalent when possible
                if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # Convert to ClickUp's h tag with class
                    new_tag = soup.new_tag('h')
                    new_tag['class'] = f"h{tag.name[1]}"
                    new_tag.string = tag.get_text()
                    tag.replace_with(new_tag)
                else:
                    # Default to div for unknown tags
                    tag.name = 'div'
        
        # Clean the html to ensure it's properly formatted
        cleaned_html = str(soup)
        
        # No need to double-encode HTML entities
        # ClickUp handles standard HTML entities properly
        
        return cleaned_html
    except Exception as e:
        logger.error(f"Error converting to ClickUp-safe HTML: {e}")
        return html  # Return the original HTML in case of errors

def format_description_for_display(description: Optional[str]) -> Optional[str]:
    """
    Format a task description for display in a more readable form.
    
    Args:
        description: The task description (may contain HTML)
        
    Returns:
        Formatted description text for display
    """
    if not description:
        return description
        
    try:
        # Check if the description contains HTML tags
        contains_html = False
        html_tags = ['<h', '<p>', '<ul>', '<ol>', '<li>', '<pre>', '<code>', '<em>', '<strong>', '<b>', '<i>', '<a ', '<table>', '<tr>', '<td>', '<blockquote>']
        for tag in html_tags:
            if tag in description:
                contains_html = True
                break
                
        if not contains_html:
            # If description doesn't contain HTML, return as is
            return description
            
        # First, strip out any HTML entities to prevent double-encoding issues
        from html import unescape
        description = unescape(description)
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(description, 'html.parser')
        
        # Create a new document to add the processed elements to
        output = []
        
        # Process each element in the document structure
        for element in soup.children:
            if element.name == 'h':
                # Handle headers
                header_level = 1
                classes = element.get('class', [])
                
                # Extract header level from class name
                for class_name in classes:
                    if class_name.startswith('h') and len(class_name) > 1:
                        try:
                            header_level = int(class_name[1:])
                        except ValueError:
                            pass
                
                output.append(f"{'#' * header_level} {element.get_text().strip()}")
                
            elif element.name == 'p':
                # Handle paragraphs
                output.append(element.get_text().strip())
                
            elif element.name == 'ul' or element.name == 'ol':
                # Handle lists
                list_output = process_list_element(element)
                output.append(list_output)
                
            elif element.name == 'pre':
                # Handle code blocks
                code_text = element.get_text().strip()
                output.append(f"```\n{code_text}\n```")
                
            elif element.name == 'blockquote':
                # Handle blockquotes
                text = element.get_text().strip()
                lines = text.split('\n')
                quoted_lines = [f"> {line}" for line in lines]
                output.append('\n'.join(quoted_lines))
                
            elif isinstance(element, str) and element.strip():
                # Handle plain text
                output.append(element.strip())
        
        # Join everything with double newlines for proper markdown spacing
        return '\n\n'.join(output).strip()
    except Exception as e:
        logger.error(f"Error formatting description for display: {e}")
        return description  # Return the original description in case of errors

def process_list_element(list_element, indent_level=0):
    """
    Process a list element (ul/ol) and its children recursively.
    
    Args:
        list_element: The BeautifulSoup list element
        indent_level: Current indentation level for nested lists
        
    Returns:
        Formatted markdown list
    """
    result = []
    
    for i, item in enumerate(list_element.find_all('li', recursive=False)):
        prefix = "  " * indent_level + "- "
        if list_element.name == 'ol':  # If it's an ordered list
            prefix = f"  {indent_level * '  '}{i+1}. "
            
        # Get the text content, but handle nested lists properly
        item_content = []
        for child in item.children:
            if isinstance(child, str):
                item_content.append(child.strip())
            elif child.name == 'ul' or child.name == 'ol':
                # Recursive call for nested lists
                nested_list = process_list_element(child, indent_level + 1)
                item_content.append("\n" + nested_list)
            elif child.name:  # Any other HTML element
                item_content.append(child.get_text().strip())
                
        # Join this item's content
        item_text = ' '.join([c for c in item_content if c])
        result.append(f"{prefix}{item_text}")
        
    return '\n'.join(result)