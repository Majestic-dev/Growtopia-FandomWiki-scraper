# Growtopia-FandomWiki-scraper
Growtopia Fandom Wiki Scraper written in python using [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) for web-scraping and [growtopia.py](https://github.com/kaJob-dev/growtopia.py) to decode items.dat

# Installation

## Requirements

- [Python 3.11 or higher](https://www.python.org/downloads/)

## Guide

```bash
git clone https://github.com/Majestic-dev/Growtopia-FandomWiki-scraper.git # Clone the repository

python -m venv venv # I recommend creating a virtual environment for this, but this is not required

pip install -r requirements.txt # Install requirements.txt
```

### Usage

After you've done everything above, move the items.dat file you want to decode to the workspace, specify it on line 6 in [ItemSearch.py](ItemSearch.py) if you want to search for individual items or [WikiParser.py](WikiParser.py) if you want to scrape the whole wiki. Run the file, everything else will be handled by the code.

# Contributing 
All contributions are welcome! If you'd like to contribute, please make a pull request.

Please make sure that your code is formatted correctly before making a new pull request. This project is formatted using [black](https://black.readthedocs.io/en/stable/) and [isort](https://pycqa.github.io/isort/) to sort imports. Read through open and closed pull requests and ensure that no one else has already made a similar pull request. 

# License
This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details


