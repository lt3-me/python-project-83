### Hexlet tests and linter status:
[![Actions Status](https://github.com/lt3-me/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/lt3-me/python-project-83/actions)
[![Github Actions Status](https://github.com/lt3-me/python-project-83/workflows/Python%20CI/badge.svg)](https://github.com/lt3-me/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/47535995af52be66b998/maintainability)](https://codeclimate.com/github/lt3-me/python-project-83/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/47535995af52be66b998/test_coverage)](https://codeclimate.com/github/lt3-me/python-project-83/test_coverage)

## Page Analyzer

Page Analyzer is a web application based on the Flask framework.

https://hexlet-code-x1te.onrender.com/

### Description

Page Analyzer is a website that analyzes specified pages for SEO suitability similar to PageSpeed Insights.

To access the project, please visit [Page Analyzer](https://hexlet-code-x1te.onrender.com/).

### How to Use

* On the main page of Page Analyzer, click on the input field.
* Type or paste the URL of the webpage you want to analyze.
* Once you've entered the URL, you can either press the "Enter" key or click on the "ПРОВЕРИТЬ" (CHECK) button to initiate the analysis process.
* If your URL is valid and doesn't exceed 255 characters, you'll be able to run checks on it.
* The checks will return the response code from trying to access the website, as well as h1, title, and description if available.

### Navigation

* Click on "Сайты" (Sites) in the navigation panel to open the table of all pages added for analysis.
* The table displays the time and results of the last check for each page.

### Quick Setup and Start on a Local Server Guide

* Download this repository contents to your local machine.
* Create file named ".env" in your project directory. Add `export DATABASE_URL=...` and `export SECRET_KEY=...` lines to this file, so you can set your environment variables.
> :warning: DATABASE_URL is URL of your local database that will be used to store data. If you don't have an empty database, create one using PostgreSQL. Please, don't create any tables in this database manually before the next step.
* Use command `make build` to install and create required tables in your database.
> Alternatively, you can just directly start the "build.sh" script.
* Use command `make start` to start Page Analyzer locally.
> If you want to use any port other than 8000, you can change the variable in the Makefile.

Feel free to explore and analyze webpages effectively using Page Analyzer!