# Take Home Assessment

Create a web app that allows users to submit data requests
Handle validation in the Backend with subclasses

## To run code

```
# From the top level directory
# Create a venv
python3 -m venv venv

# install requirements
pip3 install -r requirements.txt

# start server
uvicorn main:app --reload 

```

You can then navigate to 127.0.0.1 and test the form. Some examples would be

Submit with no date range and get an error
Submit without outcomes or data_source for TypeIReport