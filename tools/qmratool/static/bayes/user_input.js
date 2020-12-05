document.addEventListener("DOMContentLoaded", function()
{
    document.querySelector("#exampleFormControlTextarea1").value=data
    document.querySelector(`#form` ).onsubmit =() => {
    data_new = document.querySelector("#exampleFormControlTextarea1").value
    console.log(data_new)
    
    var b = data_new.split(',').map(function(item) {
        return parseFloat(item, 10);
    });
    console.log(b)
    min = parseFloat(document.querySelector("#user_min").value)
    max = parseFloat(document.querySelector("#user_max").value)
    mean = parseFloat(document.querySelector("#user_mean").value)
    sd = parseFloat(document.querySelector("#user_sd").value)
    console.log(mean)
    
   var params = {
        mu: {type: "real"},
        sigma: {type: "real", lower: 0}};
      
    var log_post = function(state, b) {
        var log_post = 0;
        // Priors
        log_post += ld.norm(state.mu, mean, sd);
        log_post += ld.unif(state.sigma, min, max);
        //log_post += ld.lnorm(state.sigma, .7, 1);
        
        // Likelihood
        for(var i = 0; i < b.length; i++) {
          log_post += ld.norm(b[i], state.mu, state.sigma);
        }
        return log_post;
      };
      
      // Initializing the sampler and generate a sample of size 1000
      var sampler =  new mcmc.AmwgSampler(params, log_post, b);
      sampler.burn(500);
      var samples = sampler.sample(40000);
      
   
     var trace = {
            x: samples.mu,
            type: 'histogram',
            marker: {
               color: '#007c9f',
            }
            };
        
            var layout={title:
              {text: "Posterior distribution of the mean (µ)"}}

        var d = [trace];
        Plotly.newPlot('text_output_div', d, layout);
 
        var trace2 = {
          x: samples.sigma,
          type: 'histogram',
          marker: {
               color: '#007c9f',
            }
      };

      var layout2={title:
                  {text: "Posterior distribution of sigma"}}
      var d2 = [trace2];
      Plotly.newPlot('sd_output_div', d2, layout2);


      return false;
    }
})