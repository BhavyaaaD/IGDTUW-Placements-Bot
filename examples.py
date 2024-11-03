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
         "query":"""SELECT COMPANY_PLACED FROM STUDENT WHERE COMPANY_PLACED LIKE '$HIGHER_STUDIES&';
"""
     }
]
