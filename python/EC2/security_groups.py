from file_handler import *

ec2_client=boto3.client("ec2")

def create_security_group_details(data):
    try:
        if not "resource" in data:
            data["resource"] = {}
            data["resource"]["aws_security_group"] = {}
    except:
        logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    try:
        terraform_ec2_sg_import_statements=["terraform init\n"]
        for all_security_group_details in ec2_client.get_paginator('describe_security_groups').paginate().build_full_result()['SecurityGroups']:
            details={}
            print(all_security_group_details)
            details['name']=all_security_group_details['GroupName']
            if "Description" in all_security_group_details:
                details['description']=all_security_group_details['Description']
            details['vpc_id']=all_security_group_details['VpcId']
            if "IpPermissions" in all_security_group_details:
                all_ingress=[]
                for ingress in all_security_group_details['IpPermissions']:
                    ingress_data={}
                    if "FromPort" in ingress:
                        ingress_data['from_port']=ingress['FromPort']
                    else:
                        ingress_data['from_port']=0
                    if "ToPort" in ingress:
                        ingress_data['to_port']=ingress['ToPort']
                    else:
                        ingress_data['to_port']=0
                    if "IpProtocol" in ingress:
                        ingress_data['protocol']=ingress['IpProtocol']
                    if len(ingress['IpRanges']) > 0:
                        ingress_data['cidr_blocks']=[ingress['IpRanges'][0]['CidrIp']]
                        if "Description" in ingress['IpRanges'][0]:
                            ingress_data['description']=ingress['IpRanges'][0]['Description']
                        else:
                            ingress_data['description']=""
                    else:
                        ingress_data['cidr_blocks']=[]
                    if len(ingress['Ipv6Ranges']) > 0:
                        ingress_data['ipv6_cidr_blocks']=[ingress['Ipv6Ranges'][0]['CidrIpv6']]
                        if "Description" in ingress['Ipv6Ranges'][0]:
                            ingress_data['description']=ingress['Ipv6Ranges'][0]['Description']
                        else:
                            ingress_data['description']=""
                    else:
                        ingress_data['ipv6_cidr_blocks']=[]
                    if len(ingress['PrefixListIds']) > 0:
                        ingress_data['prefix_list_ids']=[ingress['PrefixListIds'][0]['PrefixListId']]
                        if "Description" in ingress['PrefixListIds'][0]:
                            ingress_data['description']=ingress['PrefixListIds'][0]['Description']
                        else:
                            ingress_data['description']=""
                    else:
                        ingress_data['prefix_list_ids']=[]
                    if len(ingress['UserIdGroupPairs']) > 0:
                        ingress_data['security_groups']=[ingress['UserIdGroupPairs'][0]['GroupId']]
                        if "Description" in ingress['UserIdGroupPairs'][0]:
                            ingress_data['description']=ingress['UserIdGroupPairs'][0]['Description']
                        else:
                            ingress_data['description']=""
                    else:
                        ingress_data['security_groups']=[]
                    ingress_data['self']= False
                    all_ingress.append(ingress_data)
                details['ingress']=all_ingress
                all_egress=[]
                for egress in all_security_group_details['IpPermissions']:
                    egress_data={}
                    if "FromPort" in egress:
                        egress_data['from_port']=egress['FromPort']
                    else:
                        egress_data['from_port']=0
                    if "ToPort" in egress:
                        egress_data['to_port']=egress['ToPort']
                    else:
                        egress_data['to_port']=0
                    if "IpProtocol" in egress:
                        egress_data['protocol']=egress['IpProtocol']
                    if len(egress['IpRanges']) > 0:
                        egress_data['cidr_blocks']=[egress['IpRanges'][0]['CidrIp']]
                        if "Description" in egress['IpRanges'][0]:
                            egress_data['description']=egress['IpRanges'][0]['Description']
                        else:
                            egress_data['description']=""
                    else:
                        egress_data['cidr_blocks']=[]
                    if len(egress['Ipv6Ranges']) > 0:
                        egress_data['ipv6_cidr_blocks']=[egress['Ipv6Ranges'][0]['CidrIpv6']]
                        if "Description" in egress['Ipv6Ranges'][0]:
                            egress_data['description']=egress['Ipv6Ranges'][0]['Description']
                        else:
                            egress_data['description']=""
                    else:
                        egress_data['ipv6_cidr_blocks']=[]
                    if len(egress['PrefixListIds']) > 0:
                        egress_data['prefix_list_ids']=[egress['PrefixListIds'][0]['PrefixListId']]
                        if "Description" in egress['PrefixListIds'][0]:
                            egress_data['description']=egress['PrefixListIds'][0]['Description']
                        else:
                            egress_data['description']=""
                    else:
                        egress_data['prefix_list_ids']=[]
                    if len(egress['UserIdGroupPairs']) > 0:
                        egress_data['security_groups']=[egress['UserIdGroupPairs'][0]['GroupId']]
                        if "Description" in egress['UserIdGroupPairs'][0]:
                            egress_data['description']=egress['UserIdGroupPairs'][0]['Description']
                        else:
                            egress_data['description']=""
                    else:
                        egress_data['security_groups']=[]
                    egress_data['self']= False
                    all_egress.append(egress_data)
                details['egress']=all_egress
            if "Tags" in all_security_group_details:
                instance_tags={}
                for tag in all_security_group_details['Tags']:
                    instance_tags[tag['Key']]=tag['Value']
            data["resource"]["aws_security_group"][all_security_group_details['GroupId']]=details
            terraform_ec2_sg_import_statements.append("terraform import aws_security_group."+all_security_group_details['GroupId']+" "+all_security_group_details['GroupId']+"\n")
        return terraform_ec2_sg_import_statements,data
    except:
        logging.error("Exception occoured {} processing data".format(sys.exc_info()[1]))

if __name__ == "__main__":
    try:
        terraform_ec2_sg_import_statements,data=create_security_group_details(get_file_data(destination_path+"/ec2_sg.tf.json"))
        put_file_data(destination_path+"/ec2_sg.tf.json",data)
        if platform == "win32":
            with open(destination_path+'/ec2__sg_import.cmd','w') as out:
                out.writelines(terraform_ec2_sg_import_statements)
        else:
            with open(destination_path+'/ec2_sg_import.sh','w') as out:
                out.writelines(terraform_ec2_sg_import_statements)
    except:
        logging.error("Exception occoured {} main".format(sys.exc_info()[1]))