from ..common import *

iam_client=boto3.client("iam")
def create_iam_user_details(data):
    try:
        