from file_handler import *

vpc_client=boto3.client("ec2")
def create_vpc_details(data):
    try:
        if not "resource" in data:
            data["resource"] = {}
            data["resource"]["aws_vpc"] = {}
    except:
        logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    for vpc in vpc_client.get_paginator('describe_vpcs').paginate().build_full_result()['Vpcs']:
        try:
            vpc_details={}
            vpc_details['cidr_block']=vpc['CidrBlock']
            if "Tags" in vpc:
                instance_tags={}
                for tag in vpc['Tags']:
                    instance_tags[tag['Key']]=tag['Value']
                vpc_details['tags']=instance_tags
            data["resource"]["aws_vpc"][vpc['VpcId']]=vpc_details
        except:
            logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
        return data

data=get_file_data("../terraform/vpc.tf.json")
updated_data=create_vpc_details(data)
put_file_data("../terraform/vpc.tf.json",updated_data)