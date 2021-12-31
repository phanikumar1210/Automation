from file_handler import *

vpc_client=boto3.client("ec2")
def create_vpc_subnet_details(data):
    try:
        if not "resource" in data:
            data["resource"] = {}
            data["resource"]["aws_subnet"] = {}
    except:
        logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    terraform_vpc_subnets_import_statements=["terraform init\n"]
    for subnet in vpc_client.get_paginator('describe_subnets').paginate().build_full_result()['Subnets']:
        try:
            vpc_subnet_details={}
            # print("===============================")
            # # print(subnet)
            # print("===============================")
            vpc_subnet_details['vpc_id']=subnet['VpcId']
            vpc_subnet_details['availability_zone']=subnet['AvailabilityZone']
            # vpc_subnet_details['availability_zone_id']=subnet['AvailabilityZoneId']
            vpc_subnet_details['cidr_block']=subnet['CidrBlock'] 
            vpc_subnet_details['map_public_ip_on_launch']=subnet['MapPublicIpOnLaunch'] 
            if "Tags" in subnet:
                instance_tags={}
                for tag in subnet['Tags']:
                    instance_tags[tag['Key']]=tag['Value']
                vpc_subnet_details['tags']=instance_tags
            data["resource"]["aws_subnet"][subnet['SubnetId']]=vpc_subnet_details
            terraform_vpc_subnets_import_statements.append("terraform import aws_subnet."+subnet['SubnetId']+" "+subnet['SubnetId']+"\n")
        except:
            logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    return terraform_vpc_subnets_import_statements,data
if __name__ == "__main__":
    try:
        terraform_vpc_subnets_import_statements,data=create_vpc_subnet_details(get_file_data(destination_path+"/vpc_subnets.tf.json"))
        put_file_data(destination_path+"/vpc_subnets.tf.json",data)
        if platform == "win32":
            with open(destination_path+'/vpc_subnets_import.cmd','w') as out:
                out.writelines(terraform_vpc_subnets_import_statements)
        else:
            with open(destination_path+'/vpc_subnets_import.sh','w') as out:
                out.writelines(terraform_vpc_subnets_import_statements)
    except:
        logging.error("Exception occoured {} main".format(sys.exc_info()[1]))