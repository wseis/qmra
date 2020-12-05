//A small demo of https://github.com/rasmusab/bayes.js running a standard Normal model. Just click "start sampling" to eh... start sampling...

// Feel free to change this model and/or data and see what happens! :) What distributions are available can be found here: https://github.com/rasmusab/bayes.js/blob/master/distributions.js

// Setting up the data, parameter definitions and the defining the log posterior
// The heights of the last ten American presidents in cm, from Kennedy to Obama 
//var data = [183, 192, 182, 183, 177, 185, 188, 188, 182, 185];



var data = [183, 192, 182, 183, 177, 185, 188, 188, 182, 185];

//var data = [183];
var params = {
  mu: {type: "real"},
  sigma: {type: "real", lower: 0}};

var log_post = function(state, data) {
  var log_post = 0;
  // Priors
  log_post += ld.norm(state.mu, 100, 100);
  log_post += ld.unif(state.sigma, 0, 100);
  //log_post += ld.lnorm(state.sigma, .7, 1);
  
  // Likelihood
  for(var i = 0; i < data.length; i++) {
    log_post += ld.norm(data[i], state.mu, state.sigma);
  }
  return log_post;
};

// Initializing the sampler and generate a sample of size 1000
var sampler =  new mcmc.AmwgSampler(params, log_post, data);
sampler.burn(500);
var samples = sampler.sample(1);

//// Below is just the code to run the sampler and
//// to plot the samples. It's somewhat of a hack...
////////////////////////////////////////////////////

// Setting up the plots
var plot_margins =  {l: 40, r: 10, b: 40, t: 40, pad: 4}

var param_names = Object.keys(params);
var params_to_plot = Object.keys(params);

for(var i = 0; i < params_to_plot.length; i++) {
  var param = params_to_plot[i];
 $("div#mcmc_plots_div").append('<div>' +
    '<div id = "' + param + "_trace_div" + 
    '" style="width:350px;height:250px;display: inline-block;"></div>' +
    '<div id = "' +  param + "_hist_div" + 
    '" style="width:350px;height:250px;display: inline-block;"></div>' +
    '</div>')
  Plotly.plot( $("div#" + param + "_trace_div")[0], [{y: samples[param] }], 
            {margin: plot_margins, title: "Traceplot of " + param});
  Plotly.plot( $("div#" +  param + "_hist_div")[0], [{x: samples[param], type: 'histogram' }], 
            {margin: plot_margins, title: "Posterior of " + param });
}

var update_trace_plots = function() {
  for(var i = 0; i < params_to_plot.length; i++) {
    var param = params_to_plot[i]
    Plotly.restyle($("div#" + param + "_trace_div")[0], {y: [samples[param]],marker: {
      color: '#007c9f',
   }
  })
  }
}

var update_histograms = function() {
  for(var i = 0; i < params_to_plot.length; i++) {
    var param = params_to_plot[i]
    Plotly.restyle($("div#" + param + "_hist_div")[0], 
                   {x: [samples[param]], marker: {
                    color: '#007c9f',
                 },xbins: {}})
  }
}

// Below are the functions that enables starting and stopping the 
// sampling using the buttons

var clear_samples = function() {
  samples = sampler.sample(1)
  update_trace_plots();
  update_histograms();
}

var sample_loop_timeout_id;
var sample_loop = function() {
  var n_samples = Math.min(250, Math.ceil(samples[param_names[0]].length / 10) );
  var more_samples = sampler.sample(n_samples);
  for(var i = 0; i < param_names.length; i++) {
    var param = param_names[i]
    Array.prototype.push.apply(samples[param], more_samples[param])
  }
  update_trace_plots();
  sample_loop_timeout_id = setTimeout(sample_loop, 1)
}

var stop_sample_loop = function() {
  clearTimeout(sample_loop_timeout_id)
  update_trace_plots();
  update_histograms();
}

clear_samples()
