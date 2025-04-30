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
        if convert_to_html:
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
            'ul', 'ol', 'li', 'p', 'div', 'em', 'strong', 'del', 'span'
        ]
        
        for tag in soup.find_all():
            if tag.name not in allowed_tags:
                # Replace unsupported tags with a div
                tag.name = 'div'
        
        return str(soup)
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
        # Convert HTML to readable text
        soup = BeautifulSoup(description, 'html.parser')
        
        # Handle headers properly
        for h_tag in soup.find_all('h'):
            classes = h_tag.get('class', [])
            header_level = 1
            
            # Extract header level from class name
            for class_name in classes:
                if class_name.startswith('h') and len(class_name) > 1:
                    try:
                        header_level = int(class_name[1:])
                    except ValueError:
                        pass
            
            # Replace with markdown-style headers
            new_tag = soup.new_tag('p')
            new_tag.string = '#' * header_level + ' ' + h_tag.get_text()
            h_tag.replace_with(new_tag)
        
        # Handle other formatting
        for tag in soup.find_all('b'):
            tag.replace_with(f"**{tag.get_text()}**")
            
        for tag in soup.find_all('i'):
            tag.replace_with(f"*{tag.get_text()}*")
            
        for tag in soup.find_all('code'):
            tag.replace_with(f"`{tag.get_text()}`")
            
        for tag in soup.find_all('pre'):
            tag.replace_with(f"```\n{tag.get_text()}\n```")
            
        # Convert to text while preserving basic formatting
        text = soup.get_text(separator='\n')
        
        return text
    except Exception as e:
        logger.error(f"Error formatting description for display: {e}")
        return description  # Return the original description in case of errors