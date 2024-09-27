from venv import logger
from django.core.mail import BadHeaderError, send_mail
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
# from apps.classes.models import Classes
from apps.accounts.models import User
# from apps.groups.models import Groups
from django.conf import settings
from django.utils.html import strip_tags
from django.shortcuts import render
from rest_framework.decorators import api_view
from .utils import custom_success_response

EMAIL_HOST_USER = settings.EMAIL_HOST_USER

def inviteFunction(data):
    try:
        class_type = ""
        class_teacher = ""
        member_obj = User.objects.filter(profile_id=data['data']['profile_id']).last()
        class_obj = ""
        if 'class_id' in data['data']:
            class_type = "class"
            class_obj = Classes.objects.filter(id=data['data']['class_id']).last()
            if class_obj:
                class_teacher = class_obj.class_owner.name  
        else:
            class_type = "group"
            class_obj = Groups.objects.filter(id=data['data']['group_id']).last()
            if class_obj:
                class_teacher = class_obj.group_owner.name
            else:
                raise ValidationError({"message": ["Group does not exist"]})
        
        class_name = class_obj.name
        class_code = class_obj.code
        send_email_to = member_obj.email
        subject = "Welcome to a new " + class_type
        email_type = 'member'
        student = member_obj.first_name

        if class_type == 'class' and member_obj.user_subtype in settings.STUDENT_TYPE:
            profile_id_list = class_obj.class_members.all().values_list('member_users__id', flat=True)
            send_email_to = User.objects.filter(profile_id__in=profile_id_list, user_subtype__in=settings.TEACHER_TYPE).values_list('email', flat=True)
            subject = "New Student in " + class_type
            email_type = 'faculty'

        if class_type == 'group':
            profile_id_list = class_obj.group_owner.id
            send_email_to = User.objects.filter(profile_id=profile_id_list).values_list('email', flat=True)

        email_html_message = render_to_string(
            'Invite/invite.html', {'class_name': class_name, 'class_code': class_code, 'class_teacher': class_teacher, 'type': class_type, 'email_type': email_type, 'student': student})
        email_plaintext_message = strip_tags(email_html_message)

        result = send_mail(subject, email_plaintext_message, EMAIL_HOST_USER,
            list(send_email_to), html_message=email_html_message)
        
        return custom_success_response({'message': 'Email Sent successfully'})
    
    except Exception as e:
        # Handle or log the exception as necessary
        print(f'Error: {e}')


def welcome(request):
    email_html_message = render_to_string(
        'email/welcome.html', {'data': 'any dynamic data'})
    email_plaintext_message = strip_tags(email_html_message)

    result = send_mail("Test Email", email_plaintext_message, EMAIL_HOST_USER, [
        request.GET['email'], EMAIL_HOST_USER], html_message=email_html_message)
    return custom_success_response({'message': 'Email Sent successfully'})