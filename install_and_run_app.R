################################################################################
### Improve Reproducibility ("environment.yml") and Automate Django Server Startup
### *** Note: Works Only on Windows! ***
################################################################################

install.packages(c("fs", "reticulate"), repos = "https://cloud.r-project.org")

reticulate::install_miniconda()

pkgs <- list(conda = c("django",
                       "django-crispy-forms",
                       "django-extensions",
                       "django-import-export",
                       "django-pandas",
                       "numpy",
                       "markdown2",
                       "pandas",
                       "plotly",
                       "python-decouple"
                       ),
             py = c("django-formtools")
             )

env_name <- "qmra"

reticulate::conda_install(envname = env_name,
                          packages = pkgs$conda)

reticulate::use_condaenv(condaenv = env_name, required = TRUE)

pyconfig <- reticulate::py_config()

reticulate::use_python(python = pyconfig$python, required = TRUE)

## on windows: (try this: https://github.com/rstudio/reticulate/issues/367#issuecomment-432920802)
if(.Platform$OS.type == "windows") {
  Sys.setenv(PATH = paste(PATH = pyconfig$pythonpath,
                          Sys.getenv()["PATH"], sep=";")
  )
}

reticulate::py_install(envname = env_name,
                       packages = pkgs$py,
                       pip = TRUE,
                       pip_install_ignored = TRUE)

conda_export <- function(condaenv, export_dir = getwd()) {
  stopifnot(dir.exists(export_dir))
  reticulate::use_miniconda(condaenv = condaenv, required = TRUE)
  pyconfig <- reticulate::py_config()

  ## on windows: (try this: https://github.com/rstudio/reticulate/issues/367#issuecomment-432920802)
  if(.Platform$OS.type == "windows") {
    Sys.setenv(PATH = paste(PATH = pyconfig$pythonpath,
                            Sys.getenv()["PATH"], sep=";")
    )
  }

cmds <- sprintf("conda activate %s && conda env export > %s",
          condaenv,
          file.path(export_dir, "environment.yml"))
shell(cmd = cmds)
}

## Export python dependencies in yml
conda_export("qmra", export_dir = "tools")

run_django_qmra <- function(cmd = "runserver",
                       condaenv = "qmra",
                       path_manage.py = "tools/manage.py") {


stopifnot(file.exists(path_manage.py))
path_manage.py <- normalizePath(fs::path_abs(path_manage.py))
reticulate::use_miniconda(condaenv = condaenv, required = TRUE)
pyconfig <- reticulate::py_config()

## on windows: (try this: https://github.com/rstudio/reticulate/issues/367#issuecomment-432920802)
if(.Platform$OS.type == "windows") {
  Sys.setenv(PATH = paste(PATH = pyconfig$pythonpath,
                          Sys.getenv()["PATH"], sep=";")
  )
}

cmds <- sprintf("conda activate %s && python %s %s",
                  condaenv,
                  path_manage.py,
                  cmd)

browseURL("http://127.0.0.1:8000", browser = NULL)
shell(cmd = cmds, shell = "cmd.exe")
}

## Opens default browser on windows and start webserver
run_django_qmra(condaenv = env_name)
