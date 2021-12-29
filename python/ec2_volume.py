from common import *

ec2_client=boto3.client("ec2")

def describe_volume():
    data={}
    for volume_details in ec2_client.get_paginator('describe_instances').paginate().build_full_result()['Reservations']:
        data['encrypted']=volume_details['Encrypted']
        data['kms_key_id']=volume_details['KmsKeyId']
        data['volume_size']=volume_details['Size']
        data['volume_type']=volume_details['VolumeType']
    return data