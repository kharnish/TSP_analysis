# TSP Fund Analysis

A little script to help determine the best way to invest your TSP funds or just keep track of your investments.


### Getting Started
If you've never used Python before, start by downloading [Miniconda](https://docs.conda.io/en/latest/miniconda.html) and [PyCharm](https://www.jetbrains.com/pycharm/download/#section=windows). They also have a good tutorial [here](https://www.jetbrains.com/help/pycharm/quick-start-guide.html#create) on cloning this repo and setting it up as a project.

Before you run the code:
* Input your contribution history into `src\main\resources\contributions.csv`. 
  * See `contributions_example.csv` for help formatting your own contribution information, including interfund transfers. 
* Update `share_prices.csv` from the [TSP website](https://www.tsp.gov/fund-performance/share-price-history/). 


### Automatically Import Contributions and Fund Performance
In the top level of the repository, make a file to store your private log-in information for TSP. 
The file should include your username and password, along with the answer to your multi-factor authentication security question.

    TSP_USER=username
    TSP_PASS=passwork
    TSP_MFA=mfa answer


### Happy investing!

*I am not an expert and this is just a tool; use at your own discretion.*