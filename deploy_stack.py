from __future__ import print_function
import json
import boto3
import time
import datetime
import string
import random
from pprint import pprint
from os import path
from jinja2 import Environment, FileSystemLoader

cfn_client = boto3.client('cloudformation')

def load_jinja_template(jinja_template_file, input_page):
    env = Environment(loader=FileSystemLoader(path.dirname(__file__)))
    env.filters['jsonify'] = json.dumps
    template = env.get_template(jinja_template_file)

    cfn_parameters = {
        'title': 'Jinja Example Page',
        'tags': ['jinja', 'python', 'migration'],
        'description': 'This is an example page created using Jinja2 with a JSON template.'
    }

    return json.loads(template.render(page=input_page))

def launch_cfn(stack_name, template_file, parameter_list):
    with open(template_file, 'r') as f:
        template_body = f.read()
    response = cfn_client.create_stack(StackName=stack_name, TemplateBody=template_body, Parameters=parameter_list, Capabilities=['CAPABILITY_IAM'])

    return response

def update_cfn(stack_name, template_file, parameter_list):
    with open(template_file, 'r') as f:
        template_body = f.read()
    response = cfn_client.update_stack(StackName=stack_name, TemplateBody=template_body, Parameters=parameter_list, Capabilities=['CAPABILITY_IAM'])

    return response

def delete_cfn(stack_name):
    response = cfn_client.delete_stack(StackName=stack_name)

    return response

def print_cfn_progress(stack_id):
    print("Stack Id: ", stack_id)
    stack_name = stack_id.split(':stack/')[1].split('/')[0]
    while True:
        stack_info = cfn_client.describe_stack_events(StackName=stack_id)
        stack_status = stack_info['StackEvents'][0]
        if 'LogicalResourceId' in stack_status and 'ResourceStatus' in stack_status:
            print("*"*60)
            print("Resource: " + stack_status['LogicalResourceId'] + " " + stack_status['ResourceStatus'])
            if stack_status['LogicalResourceId'] == stack_name and (stack_status['ResourceStatus'] == 'CREATE_COMPLETE' or stack_status['ResourceStatus'] == 'UPDATE_COMPLETE' or stack_status['ResourceStatus'] == 'UPDATE_ROLLBACK_COMPLETE' or stack_status['ResourceStatus'] == 'DELETE_COMPLETE'):
                break
        if 'ResourceStatusReason' in stack_status:
            print(stack_status['ResourceStatusReason'])
        time.sleep(10)

stamp = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))

cfn_parameter_injection = {
    'app_name': 'two-tier-stack' + stamp,
    'front_tier_ami': 'ami-08f5d22d9fb87d8b9',
    'front_tier_instance_key': 'perall',
    'app_vpc': 'vpc-dc0f66b9',
    'public_subnet_1': 'subnet-0ba6ad0d8244138e2',
    'public_subnet_2': 'subnet-0137ebbaa4c54806c'
}

cfn_parameters = load_jinja_template('parameters.json.j2', cfn_parameter_injection)
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-')
stack_name = "two-tiered-stack"
## stack_name = "two-tiered-stack1" + st + stamp

## response = delete_cfn(stack_name)
## response = update_cfn(stack_name, 'app-stack-cfn.template', cfn_parameters)
response = launch_cfn(stack_name, 'app-stack-cfn.template', cfn_parameters)
stack_id = response['StackId']
# stack_id = "arn:aws:cloudformation:us-west-2:224915900166:stack/two-tiered-stack/582258c0-1d3c-11e9-9791-0630890b2eee"
print_cfn_progress(stack_id)

##{u'StackId': 'arn:aws:cloudformation:us-west-2:224915900166:stack/two-tiered-stack/6e6c3150-1d0f-11e9-b972-028e0c7104f2', 'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': '6e657af1-1d0f-11e9-bf68-05948caddf8c', 'HTTPHeaders': {'x-amzn-requestid': '6e657af1-1d0f-11e9-bf68-05948caddf8c', 'date': 'Sun, 20 Jan
##2019 23:59:32 GMT', 'content-length': '386', 'content-type': 'text/xml'}}}