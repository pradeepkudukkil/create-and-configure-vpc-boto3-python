import boto3

session = boto3.session.Session(profile_name="full")
ec2_res = session.resource(service_name="ec2",region_name="us-east-1")
ec2_cli = session.client(service_name="ec2",region_name="us-east-1")

# create VPC with Tag
vpc = ec2_res.create_vpc(CidrBlock='172.16.0.0/16')
vpc.create_tags(Tags=[{"Key": "Name", "Value": "MY_VPC"}])
vpc.wait_until_available()

# enable public dns hostname.
ec2_cli.modify_vpc_attribute( VpcId = vpc.id , EnableDnsSupport = { 'Value': True } )
ec2_cli.modify_vpc_attribute( VpcId = vpc.id , EnableDnsHostnames = { 'Value': True } )

# create an internet gateway and attach it to VPC
internetgateway = ec2_res.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=internetgateway.id)

# create a route table and a public route
routetable = vpc.create_route_table()
route = routetable.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internetgateway.id)

# create subnet with tag and associate it with public route table
subnet = ec2_res.create_subnet(CidrBlock='172.16.2.0/24', VpcId=vpc.id)
routetable.associate_with_subnet(SubnetId=subnet.id)

subnet = ec2_res.Subnet(subnet.id)
pub_subnet=subnet.id
subnet.create_tags(
    Tags=[
        {
            'Key': 'Name',
            'Value': 'Public Subnet'
        },
    ]
)

# create a route table and a private route
routetable = vpc.create_route_table()

# create subnet with tag and associate it with private route table
subnet = ec2_res.create_subnet(CidrBlock='172.16.1.0/24', VpcId=vpc.id)
routetable.associate_with_subnet(SubnetId=subnet.id)
pri_subnet=subnet.id

subnet = ec2_res.Subnet(subnet.id)
subnet.create_tags(
    Tags=[
        {
            'Key': 'Name',
            'Value': 'Private Subnet'
        },
    ]
)

# Print values
print("Region Name: us-east-1\n\n"+"VPC ID(CIDR block-172.16.0.0/16): "+ vpc.id +"\nPublic subnet(CIDR block-172.16.2.0/24): "+pub_subnet+"\nPrivate subnet(CIDR block-172.16.1.0/24): "+pri_subnet+"\nInternetGateway ID: "+ internetgateway.id)
