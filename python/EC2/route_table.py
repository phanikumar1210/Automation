from file_handler import *

ec2_client=boto3.client("ec2")
def create_instance_details(data):
    try:
        if not "resource" in data:
            data["resource"] = {}
            data["resource"]["aws_route_table"] = {}
    except:
        logging.error("Exception occoured while validating json data {} ".format(sys.exc_info()[1]))
    try:
        terraform_vpc_route_import_statements=["terraform init\n"]
        for routes in ec2_client.get_paginator('describe_route_tables').paginate().build_full_result()['RouteTables']:
            route_table_data={}
            route_table_data['vpc_id']=routes['VpcId']
            route_paths=[]
            data['resource']['aws_route_table_association'] = {}
            for associations in routes['Associations']:
                association_data={}
                if 'SubnetId' in associations:
                    association_data['subnet_id']=associations['SubnetId']
                    terraform_vpc_route_import_statements.append("terraform import aws_route_table_association."+associations['RouteTableAssociationId']+" "+associations['SubnetId']+"/"+associations['RouteTableId']+"\n")
                if 'GatewayId' in associations:
                    association_data['gateway_id']=associations['GatewayId']
                    terraform_vpc_route_import_statements.append("terraform import aws_route_table_association."+associations['RouteTableAssociationId']+" "+associations['GatewayId']+"/"+associations['RouteTableId']+"\n")
                if ('GatewayId' in associations) or ('SubnetId' in associations):
                    association_data['route_table_id']=associations['RouteTableId']
                    data['resource']['aws_route_table_association'][associations['RouteTableAssociationId']]=association_data
            if 'PropagatingVgws' in routes:
                propogation_gateways = []
                for propogation_gateway in routes['PropagatingVgws']:
                    propogation_gateways.append(propogation_gateway['GatewayId'])
                route_table_data['propagating_vgws'] = propogation_gateways
            for route_table_records in routes['Routes']:
                if 'GatewayId' in route_table_records  and route_table_records['GatewayId'] == 'local':
                    continue
                else:
                    route_path_data={
                        "nat_gateway_id": "",
                        "vpc_peering_connection_id": "",
                        "vpc_endpoint_id": "",
                        "transit_gateway_id": "",
                        "carrier_gateway_id": "",
                        "destination_prefix_list_id": "",
                        "egress_only_gateway_id": "",
                        "gateway_id": "",
                        "ipv6_cidr_block": "",
                        "local_gateway_id": "",
                        "network_interface_id": "",
                        "instance_id":  "",
                        "cidr_block": ""
                    }
                    if 'GatewayId' in route_table_records:
                        if route_table_records['GatewayId'] != 'local':
                            if 'DestinationCidrBlock' in route_table_records:
                                route_path_data['cidr_block']=route_table_records['DestinationCidrBlock']
                            if route_table_records['GatewayId'].startswith('vpce'):
                                route_path_data['vpc_endpoint_id']=route_table_records['GatewayId']
                            else:
                                route_path_data['gateway_id']=route_table_records['GatewayId']
                    elif 'VpcPeeringConnectionId' in route_table_records:
                        route_path_data['vpc_peering_connection_id']=route_table_records['VpcPeeringConnectionId']
                    elif 'NatGatewayId' in route_table_records:
                        route_path_data['nat_gateway_id']=route_table_records['NatGatewayId']
                    elif 'TransitGatewayId' in route_table_records:
                        route_path_data['transit_gateway_id']=route_table_records['TransitGatewayId']
                    elif 'InstanceId' in route_table_records:
                        route_path_data['instance_id']=route_table_records['InstanceId']
                    elif 'NetworkInterfaceId' in route_table_records:
                        route_path_data['network_interface_id']=route_table_records['NetworkInterfaceId']
                    if 'DestinationCidrBlock' in route_table_records:
                        route_path_data['cidr_block']=route_table_records['DestinationCidrBlock']
                    elif 'DestinationPrefixListId' in route_table_records:
                        route_path_data['destination_prefix_list_id']=route_table_records['DestinationPrefixListId']
                    elif 'DestinationIpv6CidrBlock' in route_table_records:
                        route_path_data['ipv6_cidr_block']=route_table_records['DestinationIpv6CidrBlock']
                    route_paths.append(route_path_data)
                route_table_data['route']=route_paths
            if "Tags" in routes:
                route_table_tags={}
                for tag in routes['Tags']:
                    route_table_tags[tag['Key']]=tag['Value']
                route_table_data['tags']=route_table_tags
            data["resource"]["aws_route_table"][routes['RouteTableId']]=route_table_data
            terraform_vpc_route_import_statements.append("terraform import aws_route_table."+routes['RouteTableId']+" "+routes['RouteTableId']+"\n")
        return terraform_vpc_route_import_statements,data
    except:
        logging.error("Exception occoured {} processing data".format(sys.exc_info()[1]))

if __name__ == "__main__":
    try:
        terraform_vpc_route_import_statements,data=create_instance_details(get_file_data(destination_path+"/vpc_route.tf.json"))
        put_file_data(destination_path+"/vpc_route.tf.json",data)
        if platform == "win32":
            with open(destination_path+'/vpc_route_import.cmd','w') as out:
                out.writelines(terraform_vpc_route_import_statements)
        else:
            with open(destination_path+'/vpc_route_import.sh','w') as out:
                out.writelines(terraform_vpc_route_import_statements)
    except:
        logging.error("Exception occoured {} main".format(sys.exc_info()[1]))