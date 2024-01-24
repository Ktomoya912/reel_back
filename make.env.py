import re

raw_aws_access_key_id = input()
raw_aws_secret_access_key = input()
raw_aws_session_token = input()

aws_access_key_id = re.sub(r"aws_access_key_id=", "", raw_aws_access_key_id)
aws_secret_access_key = re.sub(r"aws_secret_access_key=", "", raw_aws_secret_access_key)
aws_session_token = re.sub(r"aws_session_token=", "", raw_aws_session_token)

result = f"""
-e aws_access_key_id="{aws_access_key_id}" \\
-e aws_secret_access_key="{aws_secret_access_key}" \\
-e aws_session_token="{aws_session_token}" \\
"""
print(result)
