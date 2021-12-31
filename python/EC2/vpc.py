from file_handler import *

ec2_client=boto3.client("ec2")
def create_vpc_details(data):
    try:
        if not "resource" in data:
            data["resource"] = {}
            data["resource"]["aws_vpc"] = {}
    except:
        logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    terraform_vpc_import_statements=["terraform init\n"]
    for vpc in ec2_client.get_paginator('describe_vpcs').paginate().build_full_result()['Vpcs']:
        try:
            vpc_details={}
            vpc_details['cidr_block']=vpc['CidrBlock']
            vpc_details['instance_tenancy']=vpc['InstanceTenancy']
            vpc_details['enable_dns_hostnames']=ec2_client.describe_vpc_attribute(Attribute='enableDnsHostnames',VpcId=vpc['VpcId'])['EnableDnsHostnames']['Value']
            vpc_details['enable_dns_support']=ec2_client.describe_vpc_attribute(Attribute='enableDnsSupport',VpcId=vpc['VpcId'])['EnableDnsSupport']['Value']
            if "Tags" in vpc:
                instance_tags={}
                for tag in vpc['Tags']:
                    instance_tags[tag['Key']]=tag['Value']
                vpc_details['tags']=instance_tags
            data["resource"]["aws_vpc"][vpc['VpcId']]=vpc_details
            terraform_vpc_import_statements.append("terraform import aws_vpc."+vpc['VpcId']+" "+vpc['VpcId']+"\n")
        except:
            logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    return terraform_vpc_import_statements,data
if __name__ == "__main__":
    try:
        terraform_vpc_import_statements,data=create_vpc_details(get_file_data(destination_path+"/vpc.tf.json"))
        put_file_data(destination_path+"/vpc.tf.json",data)
        if platform == "win32":
            with open(destination_path+'/vpc_import.cmd','w') as out:
                out.writelines(terraform_vpc_import_statements)
        else:
            with open(destination_path+'/vpc_import.sh','w') as out:
                out.writelines(terraform_vpc_import_statements)
    except:
        logging.error("Exception occoured {} main".format(sys.exc_info()[1]))