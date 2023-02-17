def sanitize_input(input):
    input_lower = input.lower()
    input_list = input_lower.split()
    result_list = []
    for element in input_list:
        element.strip()
        if "'" in element:
            print(element)
            index = element.index("'")
            element = element[:index] + "'" + element[index:]
        result_list.append(element)
    input_sanitized = " ".join(result_list)
    return input_sanitized
def title_input(input):
    input_title = input.title()
    return input_title
