import datetime
import uuid

from django import urls
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, \
    HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse

from storage.forms import ObjectForm
from storage.models import Object


@login_required
def index(request):
    if request.method == 'GET':
        cursor = request.GET.get('cursor', datetime.datetime.now())
        context = {
            'total_count': Object.objects.filter(uploader=request.user).count(),
            'files': Object.objects.filter(uploader=request.user, modified_at__lt=cursor).order_by('-created_at'),
        }

        return render(request, 'index.html', context=context)


@login_required
def upload(request):
    """
    Upload an object to server.
    """
    if request.method == 'GET':
        form = ObjectForm()
    elif request.method == 'POST':
        form = ObjectForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES['file']
            uploaded_file.name = str(uuid.uuid4())

            # Make object and save
            obj = Object(file_obj=uploaded_file, name=request.POST['name'], uploader=request.user)
            try:
                with transaction.atomic():
                    obj.save()
                messages.add_message(request, level=messages.SUCCESS, message='성공적으로 업로드 되었습니다.')
                return redirect(urls.reverse('storage'))
            except IntegrityError:
                form.add_error('name', '파일 이름이 유효하지 않습니다. 다른 이름으로 다시 시도해주세요.')

        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

    context = {'form': form}

    return render(request, 'upload.html', context=context)


def show(request, name):
    """
    Get an object.
    """
    try:
        obj = Object.objects.get(name=name)

        # TODO: Block if safety check is not finished
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    return HttpResponse(obj.file_obj.read(), content_type=obj.content_type)


def show_from_media(request, name):
    """
    Migrated from media.
    """
    return redirect(reverse('storage-show', kwargs={'name': name}), permanent=True)


@login_required
def delete(request, name):
    """
    Delete an object.
    """
    if request.method == 'GET':
        try:
            obj = Object.objects.get(name=name)
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        if not obj.uploader == request.user:
            return HttpResponseForbidden()

        obj.delete()

        messages.add_message(request, level=messages.SUCCESS, message='성공적으로 삭제되었습니다.')
        return redirect(reverse('storage'))