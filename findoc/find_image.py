def find_image(text: str) -> int:
    """Function to find if pdf has image only page.
    
       text: text version of pdf document

       return: 1 if image was found, 0 otherwise
    """
    
    list_of_pages = text.split('\x0c')[:-1]
    page_number = 0
    found_image = 0
    while page_number < len(list_of_pages):
        if list_of_pages[page_number] == '':
            found_image = 1
            break
        page_number += 1
    return found_image
