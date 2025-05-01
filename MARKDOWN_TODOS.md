# ClickUp Markdown Processor TODOs

## Issues and Improvements

- [x] Fix task descriptions showing raw HTML instead of formatted text
- [x] Fix HTML encoding/decoding issues in `clickup_safe_html` function
- [x] Improve HTML-to-markdown conversion in `format_description_for_display`
- [x] Handle nested lists properly in markdown conversion
- [x] Add proper handling for code blocks in responses

## GET_COMMENTS Endpoint Fixes

- [ ] Add detailed logging to `client.get_comments` method to track the exact structure of the API response
- [ ] Debug date parsing issues in GET_COMMENTS endpoint (error: "unsupported operand type(s) for /: 'str' and 'int'")
- [ ] Consider adding a special handling mode for the date field that avoids division operations
- [ ] Test the comments endpoint against the official ClickUp API documentation
- [ ] Implement proper error handling to gracefully degrade when date conversion fails

## Markdown-to-HTML Conversion Improvements

- [ ] Consider using a specialized HTML-to-markdown library instead of custom implementation
- [ ] Add support for additional markdown features like tables and checkboxes
- [ ] Improve handling of links in the markdown-to-HTML and HTML-to-markdown conversions
- [ ] Add tests for markdown processing to verify conversion works as expected
- [ ] Add option to include language specifier in code blocks

## HTML Entity Handling

- [ ] Create a comprehensive test suite for HTML entity handling
- [ ] Fix entity escaping/unescaping logic to handle common entities correctly
- [ ] Ensure proper handling of code examples that include HTML-like syntax

## General Improvements

- [ ] Add option to disable HTML conversion and use raw markdown
- [ ] Consider adding a preview mode for markdown content
- [ ] Document markdown features supported by the processor
- [ ] Add examples of markdown usage in the README

## Notes

- The `format_description_for_display` function has been significantly improved but needs further testing
- The HTML entity handling in `clickup_safe_html` has been fixed to avoid double encoding
- The GET_COMMENTS endpoint still has issues with date parsing that need resolution