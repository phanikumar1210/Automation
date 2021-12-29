from sys import platform
from file_handler import *

ec2_client=boto3.client("ec2")
def create_instance_details(data):
    try:
        if not "resource" in data:
            data["resource"] = {}
            data["resource"]["aws_instance"] = {}
    except:
        logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    try:
        terraform_ec2_import_statements=["terraform init\n"]
        for all_instance_details in ec2_client.get_paginator('describe_instances').paginate().build_full_result()['Reservations']:
            instance_details=all_instance_details['Instances'][0]
            details={}
            details['ami']=instance_details['ImageId']
            details['instance_type']=instance_details['InstanceType']
            details['subnet_id']=instance_details['SubnetId']
            security_groups=[]
            for securitygroups in instance_details['SecurityGroups']:
                security_groups.append(securitygroups['GroupId'])
            details['vpc_security_group_ids']=security_groups
            if 'KeyName' in instance_details:
                details['key_name'] = instance_details['KeyName']
            if "Tags" in instance_details:
                instance_tags={}
                for tag in instance_details['Tags']:
                    instance_tags[tag['Key']]=tag['Value']
                details['tags']=instance_tags
            if "IamInstanceProfile" in instance_details:
                details['iam_instance_profile']=(instance_details['IamInstanceProfile']['Arn']).split("/")[1]
            data["resource"]["aws_instance"][instance_details['InstanceId']]=details
            terraform_ec2_import_statements.append("terraform import aws_instance."+instance_details['InstanceId']+" "+instance_details['InstanceId']+"\n")
        return terraform_ec2_import_statements,data
    except:
        logging.error("Exception occoured {} processing data".format(sys.exc_info()[1]))

if __name__ == "__main__":
    try:
        terraform_ec2_import_statements,data=create_instance_details(get_file_data(destination_path+"/ec2.tf.json"))
        put_file_data(destination_path+"/ec2.tf.json",data)
        if platform == "win32":
            with open(destination_path+'/ec2_import.cmd','w') as out:
                out.writelines(terraform_ec2_import_statements)
        else:
            with open(destination_path+'/ec2_import.sh','w') as out:
                out.writelines(terraform_ec2_import_statements)
    except:
        logging.error("Exception occoured {} main".format(sys.exc_info()[1]))