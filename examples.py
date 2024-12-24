examples = [
     {
         "input": "How many students got into  MAANG?",
         "query": "SELECT COUNT(*) FROM STUDENT WHERE COMPANY_PLACED IN ('Google','Facebook','Amazon','Amazon Dublin','Netflix','Apple');"
     },
     {
         "input": "Name the students with compensation greater than 30 LPA.",
         "query": "SELECT ROLL_NUMBER,STUDENT_NAME FROM STUDENT WHERE COMPENSATION_OFFERED>30;"
     },
     {
         "input":"What percentage of students are placed?",
         "query":"SELECT COUNT(*) *100.0 / (SELECT COUNT(*) FROM STUDENT) FROM STUDENT WHERE COMPANY_PLACED NOT LIKE '%Higher_Studies%';"
     },
     {
         "input":"What percentage of students are going for Higher Studies?",
         "query":"SELECT COUNT(*) *100.0 / (SELECT COUNT(*) FROM STUDENT) FROM STUDENT WHERE COMPANY_PLACED LIKE '%Higher_Studies%'"
     },
     { 
         "input": "What is the average compensation offered to students?",
         "query": "SELECT AVG(COMPENSATION_OFFERED) FROM STUDENT;"
         
     },
     {
         "input": "What is the highest compensation offered to students?",
         "query": "SELECT MAX(COMPENSATION_OFFERED) FROM STUDENT;"
     },
     {
         "input": "What is the lowest compensation offered to students?",
         "query": "SELECT MIN(COMPENSATION_OFFERED) FROM STUDENT;"
     },
     {
         "input":"Name the students who secured the highest package?",
         "query":"SELECT ROLL_NUMBER,STUDENT_NAME,COMPANY_PLACED FROM STUDENT WHERE COMPENSATION_OFFERED = (SELECT MAX(COMPENSATION_OFFERED) FROM STUDENT);"
     },
     {
         "input": "Name the students who secured the lowest package?",
         "query": "SELECT ROLL_NUMBER,STUDENT_NAME, COMPANY_PLACED FROM STUDENT WHERE COMPENSATION_OFFERED = (SELECT MIN(COMPENSATION_OFFERED) FROM STUDENT);"
     },
     {
         "input":"Tell me which company took the highest number of students?",
         "query":"SELECT COMPANY_PLACED, COUNT(*) FROM STUDENT GROUP BY COMPANY_PLACED ORDER BY COUNT(*) DESC LIMIT 1 ;"
     },
     {
         "input":"What is the difference in CTC of Nisha Singh and Kanishka?",
         "query":"""WITH C1 AS (SELECT COMPENSATION_OFFERED FROM STUDENT WHERE STUDENT_NAME = 'Nisha Singh')
                    WITH C2 AS (SELECT COMPENSATION_OFFERED FROM STUDENT WHERE STUDENT_NAME = 'Kanishka')
                    SELECT C1 - C2 ;
         """
     },{
         "input":"What universities are students going to for Higher Studies?",
         "query":"""SELECT COMPANY_PLACED FROM STUDENT WHERE COMPANY_PLACED LIKE '%Higher_Studies%';
"""
     },{
         "input":"How many students are there?",
         "query":"SELECT COUNT(*) FROM STUDENT;"
     },{
         "input":"How many students are going for Higher Studies?",
         "query":"SELECT COUNT(*) FROM STUDENT WHERE COMPANY_PLACED LIKE '%Higher_Studies%' OR COMPANY_PLACED LIKE '%University%'"
     },{
         "input":"What was the compensation offered by Microsoft?",
         "query":"SELECT AVG(*) FROM STUDENT WHERE COMPANY_PLACED='Microsoft';"
     },{
         "input":"Did Netflix visit the campus?",
         "query":" SELECT COUNT(*) FROM STUDENT WHERE COMPANY_PLACED = 'Netflix';"
     },{
         "input":"Tell me the Companies who offered maximum compensation and to whom?",
         "query":"SELECT STUDENT_NAME, COMPANY_PLACED FROM STUDENT WHERE COMPENSATION_OFFERED=(SELECT MAX(COMPENSATION_OFFERED) FROM STUDENT);"

     },{
         "input":"What was the stipend offered by Google?",
         "query":"SELECT STIPEND_OFFERED FROM INTERNSHIP_OFFERS WHERE COMPANY='Google';"
     },{
         "input":"How many internship offers from Intuit?",
         "query":"SELECT STUDENTS_COUNT FROM INTERNSHIP_OFFERS WHERE COMPANY='Intuit';"
     },{
         "input":"How many full time offers and intern offers made by Microsoft?",
         "query":"SELECT COUNT(*),INTERNSHIP_OFFERS.STUDENTS_COUNT FROM STUDENT,INTERNSHIP_OFFERS WHERE STUDENT.COMPANY_PLACED= INTERNSHIP_OFFERS.COMPANY AND  STUDENT.COMPANY_PLACED='Microsoft';"
     },{
         "input":"How many full time offers and intern offers made by Google?",
         "query":"SELECT COUNT(*),INTERNSHIP_OFFERS.STUDENTS_COUNT FROM STUDENT,INTERNSHIP_OFFERS WHERE STUDENT.COMPANY_PLACED= INTERNSHIP_OFFERS.COMPANY AND  STUDENT.COMPANY_PLACED='Google';"
     },{
         "input":"Which company hired max interns?",
         "query":"SELECT COMPANY, STUDENTS_COUNT FROM INTERNSHIP_OFFERS ORDER BY STUDENTS_COUNT DESC LIMIT 1;"
     },
        {
        "input": "Name the students with compensation greater than 30 LPA.",
        "query": "SELECT ROLL_NUMBER,STUDENT_NAME FROM STUDENT WHERE COMPENSATION_OFFERED>30;"
    },
    {
        "input": "Which company offered the second highest compensation?",
        "query": "SELECT COMPANY_PLACED, MAX(COMPENSATION_OFFERED) FROM STUDENT WHERE COMPENSATION_OFFERED < (SELECT MAX(COMPENSATION_OFFERED) FROM STUDENT);"
    },
    {
        "input": "Which companies offered more than 5 internship offers?",
        "query": "SELECT COMPANY FROM INTERNSHIP_OFFERS WHERE STUDENTS_COUNT > 5;"
    },
    {
        "input": "Which company offered the least number of internship offers?",
        "query": "SELECT COMPANY FROM INTERNSHIP_OFFERS ORDER BY STUDENTS_COUNT ASC LIMIT 1;"
    },
    {
        "input": "What is the average stipend offered by companies for internships?",
        "query": "SELECT AVG(STIPEND_OFFERED) FROM INTERNSHIP_OFFERS;"
    },
    {
        "input": "Show the names of students with the same compensation.",
        "query": "SELECT STUDENT_NAME FROM STUDENT GROUP BY COMPENSATION_OFFERED HAVING COUNT(*) > 1;"
    },
    {
        "input": "Which student received the highest stipend during an internship?",
        "query": "SELECT STUDENT_NAME, STIPEND_OFFERED FROM INTERNSHIP_OFFERS WHERE STIPEND_OFFERED = (SELECT MAX(STIPEND_OFFERED) FROM INTERNSHIP_OFFERS);"
    },
    {
        "input": "How many students were placed in the top 3 hiring companies?",
        "query": "SELECT SUM(PLACED_COUNT) FROM (SELECT COMPANY_PLACED, COUNT(*) AS PLACED_COUNT FROM STUDENT GROUP BY COMPANY_PLACED ORDER BY COUNT(*) DESC LIMIT 3);"
    },
    {
        "input": "What percentage of internships were offered by FAANG companies?",
        "query": "SELECT SUM(STUDENTS_COUNT) * 100.0 / (SELECT SUM(STUDENTS_COUNT) FROM INTERNSHIP_OFFERS) FROM INTERNSHIP_OFFERS WHERE COMPANY IN ('Facebook', 'Amazon', 'Apple', 'Netflix', 'Google');"
    },
    {
        "input": "What is the total number of internships and full-time offers?",
        "query": "SELECT (SELECT COUNT(*) FROM STUDENT WHERE COMPANY_PLACED NOT LIKE '%Higher_Studies%') + (SELECT SUM(STUDENTS_COUNT) FROM INTERNSHIP_OFFERS);"
    }
]
