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
from plotly.offline import plot

class ImportView(View):
    template_name = "logremoval/import2.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request,*args, **kwargs):
        csv_file = request.FILES["myfile"]
        data = pd.read_csv(csv_file)
        n_inflow = data.count()["inflow"]
        n_outflow = data.count()["outflow"]
        n_paired = data[["inflow", "outflow"]].dropna().count()["inflow"]
        inflow = data["inflow"].dropna()
        outflow = data["outflow"].dropna()


        Xin = np.ones_like(inflow)
        Xout = np.ones_like(outflow)
        nb_inflow = sm.NegativeBinomial(inflow, Xin).fit()
        nb_outflow = sm.NegativeBinomial(outflow, Xout).fit()
        inflow = simulate_negbin(nb_inflow)
        outflow = simulate_negbin(nb_outflow)
        df = pd.DataFrame({"inflow": inflow+1, "outflow": outflow+1})
        df["LRV"] =np.log10((df["inflow"])/df["outflow"])
        quantiles = df.quantile([.1, .5, .9])
        lrvplot = px.histogram(df, "LRV")
        inplot = px.histogram(df, "inflow")
        outplot = px.histogram(df, "outflow")

        return render(request, self.template_name, {"table": quantiles,
        "lrvplot": plot(lrvplot, output_type='div'),
        "inplot": plot(inplot, output_type='div'),
        "outplot": plot(outplot, output_type='div'),
        "n_inflow": n_inflow,
        "n_outflow": n_outflow,
        "n_paired": n_paired,
        "P10": quantiles["LRV"].iloc[0]. round(2),
        "P50": quantiles["LRV"].iloc[1]. round(2),
        "P90": quantiles["LRV"].iloc[2]. round(2)})

def simulate_negbin(model):
    mu = np.exp(model.params[0])
    p = 1/(1+np.exp(model.params[0])*model.params[1])
    n = np.exp(model.params[0])*p/(1-p)

    

    return np.random.negative_binomial(n, p, 10000)
        