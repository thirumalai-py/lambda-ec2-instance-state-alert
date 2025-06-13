import boto3
import os

sns = boto3.client('sns')
ec2 = boto3.resource('ec2')

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def get_instance_name(instance_id):
    """Fetch the 'Name' tag for a given EC2 instance"""
    try:
        instance = ec2.Instance(instance_id)
        for tag in instance.tags or []:
            if tag['Key'] == 'Name':
                return tag['Value']
    except Exception as e:
        print(f"Failed to get name for {instance_id}: {e}")
    return "Unnamed-Instance"

def lambda_handler(event, context):
    detail = event.get('detail', {})
    instance_id = detail.get('instance-id')
    state = detail.get('state')

    if not instance_id or not state:
        print("Missing instance ID or state in event.")
        return

    name = get_instance_name(instance_id)
    region = event.get('region', 'unknown')

    subject = f"[{state.upper()}] EC2: {name} ({instance_id})"
    message = (
        f"EC2 Instance State Change Detected:\n\n"
        f"Name: {name}\n"
        f"Instance ID: {instance_id}\n"
        f"New State: {state.upper()}\n"
        f"Region: {region}"
    )

    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"Notification sent: {subject}")
    except Exception as e:
        print(f"Failed to send SNS: {e}")
