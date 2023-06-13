#!  /usr/bin/env Rscript

repo_URL = "https://stat.ethz.ch/CRAN/"

repo = getOption("repos") 
repo["CRAN"] = repo_URL
options(repos=repo)

# remotes::install_version is used by this script
install.packages('remotes')

robust_install_version <- function (...) 
{
    tryCatch(remotes::install_version(...), error = function(e) {
        kwargs <- list(...)
        no.version <- kwargs[names(kwargs) != "version"]
        do.call(remotes::install_version, no.version)
    })
}

# Install Stan toolchain first
robust_install_version('rstan', version='2.21.8', repos=c('https://mc-stan.org/r-packages/', getOption('repos')))
robust_install_version('cmdstanr', version='0.5.3', repos=c('https://mc-stan.org/r-packages/', getOption('repos')))

cpp_opt <- list(
  "CXX" = "g++",
  "TBB_CXX_TYPE" = "gcc"
  )
cmdstanr::install_cmdstan(cores=parallel::detectCores(), cpp_options=cpp_opt)

# Install all other packages
robust_install_version('GGally', version='2.1.2')
robust_install_version('MetBrewer', version='0.2.0')
robust_install_version('assertthat', version='0.2.1')
robust_install_version('bookdown', version='0.33')
robust_install_version('brms', version='2.19.0')
robust_install_version('dplyr', version='1.1.0')
robust_install_version('effsize', version='0.8.1')
robust_install_version('emmeans', version='1.8.5')
robust_install_version('ggplot2', version='3.4.1')
robust_install_version('knitr', version='1.42')
robust_install_version('marginaleffects', version='0.11.0')
robust_install_version('posterior', version='1.4.1')
robust_install_version('readr', version='2.1.4')
remotes::install_github('rmcelreath/rethinking@2acf2fd7b01718cf66a8352c52d001886c7d3c4c') # package rethinking
robust_install_version('rmarkdown', version='2.20')
robust_install_version('scales', version='1.2.1')
robust_install_version('seqinr', version='4.2-23')
robust_install_version('stringr', version='1.5.0')
robust_install_version('tidyr', version='1.3.0')

# Install TinyTeX and PDFcrop to knit Rmd files to PDF
robust_install_version('tinytex', version='0.44')
tinytex::install_tinytex()
tinytex::tlmgr_install('pdfcrop')


# Log packages that should have been installed, and check whether they are actually available
requirements <- structure(list(package = c("GGally", "MetBrewer", "assertthat", 
"bookdown", "brms", "cmdstanr", "dplyr", "effsize", "emmeans", 
"ggplot2", "knitr", "marginaleffects", "posterior", "readr", 
"rethinking", "rmarkdown", "rstan", "scales", "seqinr", "stringr", 
"tidyr", "tinytex"), version = c("2.1.2", "0.2.0", "0.2.1", "0.33", 
"2.19.0", "0.5.3", "1.1.0", "0.8.1", "1.8.5", "3.4.1", "1.42", 
"0.11.0", "1.4.1", "2.1.4", "2.13", "2.20", "2.21.8", "1.2.1", 
"4.2-23", "1.5.0", "1.3.0", "0.44")), class = "data.frame", row.names = c(NA, 
-22L))
check_installed_packages <- function (requirements) 
{
    session <- devtools::session_info(pkgs = "installed")
    installed <- data.frame(package = session$packages$package, 
        version = session$packages$ondiskversion)
    not_installed <- setdiff(requirements$package, installed$package)
    if (length(not_installed) > 0) 
        stop(paste("The following required packages couldn't be installed:", 
            paste0(not_installed, collapse = " ")))
}
check_installed_packages(requirements)        
