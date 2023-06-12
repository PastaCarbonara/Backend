# pylint: skip-file

import re


value = (
    'File "D:\\Users\\User\\Documents\\school\\Munchie\\Backend\\app\\swipe_session_recipe_queue\\services\\swipe_session_recipe_queue.py", line 28, in get_and_progress_queue'
    '   for que in swipe_session_recipe_queue.queue'
)

value = str(value)
print(value)
value = re.sub(r'[^\w\s-]', '-', value.lower())
print(value)
value = re.sub(r"[-\s]+", "-", value).strip("-_")
print(value)
