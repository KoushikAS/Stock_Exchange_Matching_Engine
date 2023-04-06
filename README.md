# erss-hwk3-ka266-rm358

# Scalability: Exchange Matching for ECE568 project
following the requirements of  https://sakai.duke.edu/access/content/attachment/f74215cd-4881-4c67-a401-0f9ed2057e60/Assignments/96b4b0b0-f808-4ba2-bd9d-5727116863b4/hw4.pdf

#Authors 
Koushik Annareddy Sreenath (ka266)
Ryan Mecca (rm358)

## Getting started
To run the application 

```
docker-compose up -d
```

## Testing

There are two type of testing functionality testing
Ensure the proxy server is running and then type the command
```
cd testing/
bash functionality-test.sh 

```

This will check for all the functionality testing and matches the output.
Note: Account creation output may differ if you run it multiple times. Please clear the database before running it


To Run Load testing run 

```
cd testing/
python3 loadtesting.py 

```
