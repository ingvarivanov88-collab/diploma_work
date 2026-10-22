from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .tasks import do_import


@staff_member_required
def import_products_view(request):
    if request.method == 'POST':
        file_path = request.POST.get('file_path')
        if file_path:
            do_import.delay(file_path)
            return render(request, 'import_success.html', {'file_path': file_path})
    return render(request, 'import_form.html')