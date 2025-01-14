def validate_email(email):
    import re
    email_re = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_re, email) is not None


def validate_password(password):
    # Password must be at least 8 characters long and include letters and numbers
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True
