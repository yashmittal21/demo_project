import json
import os

import boto3
from botocore.exceptions import ClientError
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import Data

# from django.core.mail import send_mail
# from django.conf import settings

aws_region = 'us-east-1'
endpoint_url = "http://localhost.localstack.cloud:4566"
# for interacting with s3
s3_client = boto3.client("s3", endpoint_url=endpoint_url, region_name=aws_region, aws_access_key_id='test',
                         aws_secret_access_key='test')
s3_resource = boto3.resource("s3", region_name=aws_region, endpoint_url=endpoint_url)
bucket_name = "test-bucket"


def create_bucket(bucket_name):
    """
    Creates a S3 bucket.
    """
    try:
        response = s3_client.create_bucket(
            Bucket=bucket_name)
    except ClientError:
        print('Could not create S3 bucket locally.')
        raise
    else:
        response


def list_buckets():
    """
    List S3 buckets.
    """
    try:

        response = s3_resource.buckets.all()
    except ClientError:
        print('Could not list S3 bucket from LocalStack.')
        raise
    else:
        return response


def upload_file(file_name, bucket, object_name=None):
    """
    Upload a file to a S3 bucket.
    """
    try:
        if object_name is None:
            object_name = os.path.basename(file_name)
        response = s3_client.upload_file(
            file_name, bucket, object_name)
    except ClientError:
        print('Could not upload file to S3 bucket.')
        raise
    else:
        return response


def download_file(file_name, bucket, object_name):
    """
    Download a file from a S3 bucket.
    """
    try:
        response = s3_resource.Bucket(bucket).download_file(object_name, file_name)
    except ClientError:
        print('Could not download file to S3 bucket.')
        raise
    else:
        return response


def home(request):
    if request.user.is_authenticated:
        if Data.objects.filter(user=request.user).exists():
            all_data = Data.objects.filter(user=request.user)
        else:
            all_data = []
        file_list = []
        # print(all_data)
        for data in all_data:
            temp = []
            temp.append(data.id)
            temp.append(data.name)
            # print(data.data)
            for val in data.data:
                # print(key)
                temp.append(val)
            file_list.append(temp)
        return render(request, 'home.html', {'file_list': file_list})
    return redirect('login')


def post_data(request):
    file = json.loads(request.POST['data'])  ##this convert json string into python data structure
    upload_on_s3(file)
    file_data = file["file_data"]
    file_name = file["file_name"]
    Data.objects.create(data=file_data, name=file_name, user=request.user)
    return JsonResponse({"message": "ok"})


def show(request, id):
    if not request.user.is_authenticated:
        redirect('login')
    data = Data.objects.get(id=id)
    file = {}
    file[data.name] = data.data

    return render(request, 'show.html', {
        'file': file, "id": id
    })


def data_analysis(request):
    if request.method == 'POST':
        id = request.POST.get("id")
        data = Data.objects.get(id=id)
        value = []
        for key in data.data:
            value.append(key['domain_rating'])
        value.sort()
        # print(value)
        sum = 0
        for val in value:
            sum += int(val)
        # print(sum)
        n = len(value)
        if n != 0:
            mean = sum / n
            print(mean)
            median = value[int(n / 2)]
            if n % 2 == 0:
                median = (value[int(n / 2)] + value[int(n / 2) - 1]) / 2
            mx = value[n - 1]
            return render(request, 'data_analysis.html', {
                'mean': mean,
                'median': median,
                'max': mx
            })


def upload_on_s3(file):
    s3 = create_bucket(bucket_name)
    file_name = '/Users/yash.mittal/Downloads/' + file["file_name"] + '.csv'
    object_name = file["file_name"] + '.csv'
    upload_file(file_name, bucket_name, object_name)


def download(request):
    if request.method == 'POST':
        id = request.POST.get("id")
        file = Data.objects.get(id=id)
        file_name = '/Users/yash.mittal/Downloads/' + file.name + '.csv'
        object_name = file.name + '.csv'
        s3 = download_file(file_name, bucket_name, object_name)
        print(s3)
        print("file downloaded")
        return redirect('/')


def send_email(request):
    if request.method == 'POST':
        title = request.POST['title']
        email = request.POST['email']
        message = request.POST['message']
        print(title)
        print(email)
        print(message)
        #   send_mail(
        # "Subject here",
        # "Here is the message.",
        # settings.EMAIL_HOST_USER,
        # ["yashmittal391@gmail.com"],
        # fail_silently=False,
        # )
        return redirect('/')
