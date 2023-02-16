def sanitize_input(input):
    input_lower = input.lower()
    input_list = input_lower.split()
    for element in input_list:
        element.strip()
    input_sanitized = " ".join(input_list)
    return input_sanitized
def title_input(input):
    input_title = input.title()
    return input_title
