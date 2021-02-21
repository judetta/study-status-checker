#!/usr/bin/python3

import os
import cgi
import requests
import json

# ids of Trello lists and credits custom field
courses_in_progress_list_id = '5f05c6d175bfc506e1166f54'
waiting_for_credits_list_id = '5f3fbe38e514972615f51799'
finished_courses_list_id = '5f05c6d5ba81e62525d73f35'
credits_custom_field_id = '5f47a51f0550bc043fdfe114'

# check the form actions
selection = ""
method = os.environ.get('REQUEST_METHOD', '')
if method == 'POST':
    form = cgi.FieldStorage()
    if "i" in form:
        selection = "i"
    elif "w" in form:
        selection = "w"
    elif "f" in form:
        selection = "f"


# get the apikey and token from files
try:
    apikeyfile = open('../data/apikey.txt')
    apikey = apikeyfile.read()
except Exception as e:
    print(f"Error reading api key from file: {e}")
finally:
    apikeyfile.close()

try:
    apitokenfile = open('../data/apitoken.txt')
    apitoken = apitokenfile.read()
except Exception as e:
    print(f"Error reading api token from file: {e}")
finally:
    apitokenfile.close()


# get cards in list by list id and format response as json
def api_request(list_id):
    response = requests.get(
        'https://api.trello.com/1/lists/'+list_id
        +'/cards?fields=name&customFieldItems=true&key='
        +apikey+'&token='+apitoken
        )
    if response.status_code != 200:
        response_error = response.status_code
        return response_error
    else:
        json_response = response.json()
        return json_response


# create a dictionary with course names as keys and credits as values
def course_parser(json_response):
    courses = dict()
    for card in json_response:
        name = (card['name'])
        for custom_field_item in card['customFieldItems']:
            if custom_field_item['idCustomField'] == credits_custom_field_id:
                value = custom_field_item.get('value')
                course_credits = value.get('number')
                courses.update({name: course_credits})
            else:
                continue
    return courses


# calculate the sum of course credits in a list
def course_credits_sum(courses):
    sum = 0
    for x in courses.values():
        sum += int(x)
    return sum


# print out information of courses, except if request was not successful
def course_info_printer():
    try:
        response = api_request(list_id)
        courses = course_parser(response)
        credits_sum = course_credits_sum(courses)
        for k, v in courses.items():
            print(f'{k}, {v} credits<br>')
        print(f'<strong>Total amount of credits: {credits_sum} </strong>')
    except TypeError:
        print(f'API request was not successful, error code {response}')


print("Content-type: text/html;charset=utf-8")
print("")
print('<html>')
print('<head>')
print('<title>Study status checker</title>')
print('</head>')
print('<body style="background-color:#f2f2f2; font-family:Verdana, sans serif; padding:2%">')
print('<h2>Study status checker</h2>')
print("""<p>With this tool you can check which courses Jutta is currently working on,<br>
which courses she has lately finished but which are waiting for credits still,<br>
and which courses she has officially finished and got credits for.</p>""")
print('<form action="" method="post">')
print('<input type="submit" name="i" value="Show courses in progress">')
print('<input type="submit" name="w" value="Show courses waiting for credits">')
print('<input type="submit" name="f" value="Show finished courses">')
print('</form>')
print('<p>')
if selection == 'i':
    print('<strong>Courses in progress:</strong><br>')
    list_id = courses_in_progress_list_id
    course_info_printer()
elif selection == 'w':
    print('<strong>Courses waiting for credits:</strong><br>')
    list_id = waiting_for_credits_list_id
    course_info_printer()
elif selection == 'f':
    print('<strong>Courses finished:</strong><br>')
    list_id = finished_courses_list_id
    course_info_printer()
else:
    print('Click a button above')
print('</p>')
print('</body>')
print('</html>')
