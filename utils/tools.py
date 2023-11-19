from django.core.exceptions import ValidationError



def none_numeric_value(value):
    try:
        is_numeric = type(int(value)) is int
    except Exception:
        return True
    if is_numeric :
            raise ValidationError("مقدار این فیلد نمی‌تواند عددی می‌باشد", params={"value": value})
    

def password_validation(password, username):
    nums = [str(num) for num in range(0, 10)]
    list_control = []
    chars = {'.', '-', '_', '@'}
    username_letters = set(username.lower()) - chars
    password_letters = set(password.lower()) - chars
    for char in password:
        if char in nums:
            list_control.append('n')
        else:
            list_control.append('l')
    # checking password combination
    if 'n' not in list_control or 'l' not in list_control:
        return 'combine_err'
    # checking password similarity to username
    elif username_letters.union(password_letters) == username_letters:
        return 'similar_err'
    else:
        return 'not_err'
