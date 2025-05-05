#Steps to deploy the project

STEP 1:
Setup Overview:
Python Libraries:
•	Selenium for web scraping.
•	webdriver-manager to automatically handle the ChromeDriver.
•	fake_useragent for randomizing user agents.
•	mysql-connector-python for MySQL connectivity.
•	TextBlob for basic sentiment analysis of the reviews.
Database Setup:
•	Using XAMPP MySQL.
•	A MySQL database to store the scraped reviews.

STEP 2:
Requirements: 
The requirements.txt file that includes all the necessary libraries.

STEP 3:
MySQL Configuration:
The config.py contains the configuration for connecting to the MySQL database. You can update this with your XAMPP MySQL credentials

STEP 4:
Database Connection:
The databsse.py handles the database connection.

STEP 5:
Main Scraping Script:
The scraper.py is the core script that scrapes Amazon Iphone reviews for the given link , stores them in the MySQL database, and also performs basic sentiment analysis.

STEP 6:
Sentiment Analysis:
Each review’s sentiment (positive, neutral, or negative) is classified using TextBlob and stored in the database.

STEP 7:
MySQL Database Setup (XAMPP):
1.	Open XAMPP and start Apache and MySQL.
2.	Open phpMyAdmin at http://localhost/phpmyadmin/.
3.	Create a new database, say amazon_reviews.
4.	Create a table reviews in the amazon_reviews database
