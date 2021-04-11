Welcome to QMRA's documentation!
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

QMRA is a Django project which experiments with deploying state of the art techniques 
for Quantitative Microbial Risk Assessment (QMRA). 

The implemented simulations rely on a freely available `database <https://kwb-r.github.io/qmra.db/>`_, which was developed within the research project `Aquanes <https://cordis.europa.eu/project/id/689450>`_.

The tool allows to estimate the risk of infection for three reference pathogen (Rotavirus, *Campylobacer jejuni*, and *Cryptosporidium parvum*) for mutliple source waters and treatment scenarios.

Basic functionality
###################

The tool provides the user with a graphical user interface, which allows the configuration of the most important model input variables
for a Quantitative Microbial Risk Assessment (QMRA) in the field of water supply and water reuse systems. 
Based on the user's configuration, the tool runs a Monte Carlo Simulation (MCS) to simulate the range of potential risk outcomes.

The model inputs, which can be configured by the user inlcude:

#. the source water quality
#. the implemented water treatment
#. the exposure based on the intended use (drinking, irrigation etc.)

The simulated risk is expressed and visualized both in term of annual risk of infection and disability adjusted life years (DALYs).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
