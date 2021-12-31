from file_handler import *

ec2_client=boto3.client("ec2")

def create_volume_details(data):
    try:
        if not "resource" in data:
            data["resource"] = {}
            data["resource"]["aws_ebs_volume"] = {}
    except:
        logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    try:
        terraform_ebs_import_statements=["terraform init\n"]
        for volume_details in ec2_client.get_paginator('describe_volumes').paginate().build_full_result()['Volumes']:
            ebs_volume_data={}
            ebs_volume_data['availability_zone']=volume_details['AvailabilityZone']
            ebs_volume_data['size']=volume_details['Size']
            if "Iops" in volume_details:
                ebs_volume_data['iops']=volume_details['Iops']
            ebs_volume_data['type']=volume_details['VolumeType']
            if "KmsKeyId" in volume_details:
                ebs_volume_data['kms_key_id']=volume_details['KmsKeyId']
            if "Tags" in volume_details:
                volume_tags={}
                for tag in volume_details['Tags']:
                    volume_tags[tag['Key']]=tag['Value']
                ebs_volume_data['tags']=volume_tags
            if "Throughput" in volume_details:
                ebs_volume_data['throughput']=volume_details['Throughput']
            data["resource"]["aws_ebs_volume"][volume_details['VolumeId']]=ebs_volume_data
            terraform_ebs_import_statements.append("terraform import aws_ebs_volume."+volume_details['VolumeId']+" "+volume_details['VolumeId']+"\n")
        return terraform_ebs_import_statements,data
    except:
        logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))

if __name__ == "__main__":
    try:
        file_data=get_file_data(destination_path+"/ebs.tf.json")
        logging.warning('Before processing')
        terraform_ec2_import_statements,data=create_volume_details(file_data)
        logging.warning('Completed processing')
        put_file_data(destination_path+"/ebs.tf.json",data)
        if platform == "win32":
            with open(destination_path+'/ebs_import.cmd','w') as out:
                out.writelines(terraform_ec2_import_statements)
        else:
            with open(destination_path+'/ebs_import.sh','w') as out:
                out.writelines(terraform_ec2_import_statements)
    except:
        logging.error("Exception occoured {} main".format(sys.exc_info()[1]))