test_cases=[
    {
        "input": "How many students got into MAANG?",
        "query": "SELECT COUNT(*) FROM STUDENT WHERE COMPANY_PLACED IN ('Google','Facebook','Amazon','Amazon Dublin','Netflix','Apple');"
    },
    {
        "input": "Name the students with compensation greater than 30 LPA.",
        "query": "SELECT ROLL_NUMBER,STUDENT_NAME FROM STUDENT WHERE COMPENSATION_OFFERED>30;"
    },
    {
        "input": "List the names of students who were placed in Google.",
        "query": "SELECT ROLL_NUMBER,STUDENT_NAME FROM STUDENT WHERE COMPANY_PLACED = 'Google';"
    },
    {
        "input": "Which company offered the second highest compensation?",
        "query": "SELECT COMPANY_PLACED, MAX(COMPENSATION_OFFERED) FROM STUDENT WHERE COMPENSATION_OFFERED < (SELECT MAX(COMPENSATION_OFFERED) FROM STUDENT);"
    },
    {
        "input": "Show the number of students placed in each company.",
        "query": "SELECT COMPANY_PLACED, COUNT(*) FROM STUDENT GROUP BY COMPANY_PLACED;"
    },
    {
        "input": "What is the minimum stipend offered in internships?",
        "query": "SELECT MIN(STIPEND_OFFERED) FROM INTERNSHIP_OFFERS;"
    },
    {
        "input": "Which companies offered more than 5 internship offers?",
        "query": "SELECT COMPANY FROM INTERNSHIP_OFFERS WHERE STUDENTS_COUNT > 5;"
    },
    {
        "input": "What is the total number of internships and full-time offers?",
        "query": "SELECT (SELECT COUNT(*) FROM STUDENT WHERE COMPANY_PLACED NOT LIKE '%Higher_Studies%') + (SELECT SUM(STUDENTS_COUNT) FROM INTERNSHIP_OFFERS);"
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
        "input": "What is the ratio of internships to full-time offers?",
        "query": "SELECT (SELECT SUM(STUDENTS_COUNT) FROM INTERNSHIP_OFFERS) * 1.0 / (SELECT COUNT(COMPANY_PLACED) FROM STUDENT WHERE COMPANY_PLACED != 'Higher Studies');"
    },
    {
        "input": "What percentage of internships were offered by FAANG companies?",
        "query": "SELECT SUM(STUDENTS_COUNT) * 100.0 / (SELECT SUM(STUDENTS_COUNT) FROM INTERNSHIP_OFFERS) FROM INTERNSHIP_OFFERS WHERE COMPANY IN ('Facebook', 'Amazon', 'Apple', 'Netflix', 'Google');"
    },{
        "input":"Show me the count of students",
        "query":"SELECT COUNT(*) FROM STUDENT;"
    },{
        "input": "Name the companies that offered packages greater than 20 LPA.",
        "query": "SELECT DISTINCT COMPANY_PLACED FROM STUDENT WHERE COMPENSATION_OFFERED > 20;"
    
    }, {
        "input": "Which companies offered packages below 10 LPA?",
        "query": "SELECT DISTINCT COMPANY_PLACED FROM STUDENT WHERE COMPENSATION_OFFERED < 10;"
    },{
        "input":"Show me the list of students who are going for Higher Studies",
        "query":"SELECT STUDENT_NAME FROM STUDENT WHERE COMPANY_PLACED LIKE '%Higher_Studies%'"
    },
    {
        "input": "How many companies offered packages between 15 and 25 LPA?",
        "query": "SELECT COUNT(DISTINCT COMPANY_PLACED) FROM STUDENT WHERE COMPENSATION_OFFERED BETWEEN 15 AND 25;"
    }
]