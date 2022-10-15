from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
# some_app/views.py
from django.views.generic import View
import pandas as pd
#import os
import numpy as np
import statsmodels.api as sm
import plotly.express as px

class ImportView(View):
    template_name = "logremoval/import.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request,*args, **kwargs):
        csv_file = request.FILES["myfile"]
        data = pd.read_csv(csv_file)

        Xin = np.ones_like(data["inflow"])
        Xout = np.ones_like(data["inflow"])
        nb_inflow = sm.NegativeBinomial(data["inflow"], Xin).fit()
        nb_outflow = sm.NegativeBinomial(data["outflow"], Xout).fit()
        inflow = simulate_negbin(nb_inflow)
        outflow = simulate_negbin(nb_outflow)
        df = pd.DataFrame({"inflow": inflow+1, "outflow": outflow+1})
        df["LRV"] =np.log10((df["inflow"])/df["outflow"])
        quantiles = df.quantile([.1, .5, .9]).to_html()
        print(quantiles)

        return render(request, self.template_name, {"table": quantiles})

def simulate_negbin(model):
    mu = np.exp(model.params[0])
    p = 1/(1+np.exp(model.params[0])*model.params[1])
    n = np.exp(model.params[0])*p/(1-p)

    

    return np.random.negative_binomial(n, p, 10000)
        