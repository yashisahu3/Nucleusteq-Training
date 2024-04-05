import json

data="""{
    "name": "Python Training",
    "date": "April 19, 2024",
    "completed": true,
    "instructor": {
     "name": "XYZ",
     "website": "http://pqr.com/"
    },
    "participants": [
      {
        "name": "Participant 1",
        "email": "email1@example.com"
      },
      {
        "name": "Participant 2",
        "email": "email2@example.com"
      }
    ]
  }"""

training_data=json.loads(data)
print(training_data)

#Accessing string value
name=training_data["name"]

#Accessing date
date=training_data["date"]

#Accessing Boolean value
completed=training_data["completed"]

#Accessing dictionary
instructor_name=training_data["instructor"]["name"]
instructor_website=training_data["instructor"]["website"]

#Accessing list
participants=training_data["participants"]
partcipants_names=[participant["name"] for participant in participants]
participants_emails=[participant["email"] for participant in participants] 

print("Name:",name)
print("Date:",date)
print("Completed:",completed)
print("Instructor name:",instructor_name)
print("Instructor Website",instructor_website)
print("Participants:",participants)
print("Partcipants-Names",partcipants_names)
print("Partricicpants-Emails",participants_emails)



