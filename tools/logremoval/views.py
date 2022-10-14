from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
# some_app/views.py
from django.views.generic import View
import pandas as pd

class ImportView(View):
    template_name = "logremoval/import.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request,*args, **kwargs):
        csv_file = request.FILES["myfile"]
        file_data = pd.read_csv(csv_file).to_html()
        return render(request, self.template_name, {'data': file_data})