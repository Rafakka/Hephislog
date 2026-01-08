
def to_html(input_value, input_type):
    if input_type == "html":
        return input_value

    if input_type == "url":
        return fetch_url_as_html(input_type)
    
    if input_type == "text":
        return wrap_text_as_html(input_value)

    return None

