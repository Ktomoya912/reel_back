import re

raw_aws_access_key_id = input()
raw_aws_secret_access_key = input()
raw_aws_session_token = input()

aws_access_key_id = re.sub(r"aws_access_key_id=", "", raw_aws_access_key_id)
aws_secret_access_key = re.sub(r"aws_secret_access_key=", "", raw_aws_secret_access_key)
aws_session_token = re.sub(r"aws_session_token=", "", raw_aws_session_token)

result = f"""
-e AWS_ACCESS_KEY_ID="{aws_access_key_id}" \\
 -e AWS_SECRET_ACCESS_KEY="{aws_secret_access_key}" \\
 -e AWS_SESSION_TOKEN="{aws_session_token}" \\
"""
print(result)
