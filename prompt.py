prompt="""
 You are a MySQL expert. Task: Generate a syntactically SQL statement to query a MySQL database.
 Here is the relevant table information:
 Table Name: 'STUDENT'
 Table Description: Table contains Indira Gandhi Delhi Techincal University for Women's Placements Data for CSE Btech Batch 2018.
 Table Columns are as follows:
    COLUMN :ROLL_NUMBER, DATA TYPE: INT, DESCRIPTION: Enrollment Number of Student.
    COLUMN :STUDENT_NAME, DATA TYPE: VARCHAR, DESCRIPTION: Full name of Student
    COLUMN: COMPANY_PLACED, DATA_TYPE: VARCHAR , DESCRIPTION: Company name where the student was placed. If the Student went for Higher Studies i.e. did not get placed it contains 'Higher Studies' and University Name.
    COLUMN: COMPENSATION_OFFERED,DATA_TYPE:FLOAT, DESCRIPTION: Compensation offered to the student in LPA (Lakhs per Annum).
 
 Use the only the above column names and refer to the descriptions for generating SQL Query.
 Please ensure that all the following points are met:
 1. No introductory explanation or user input is needed in the response. Ensure that the response generated only contains SQL query, nothing else.
 2. No special charcters or tokens at the start or end of SQL query.
 3. The output should only contain syntactically correct SQL query that can be directly sent to SQL server with no introductory line.
 4. No explanation is needed, just simple SQL query in response. 
 5. Do not include 'AI:', 'Query:','SQL Query: etc in your response.
 Note: Do not start the query with 'AI:','SQL:','SQL Query:' etc. Start directly with resultant query.
 Use these examples for reference. Here are the Examples:
   
"""
prompt2="""
Question: {question}
You are a MySQL expert. Given a question in English, create a syntactically correct MySQL query to execute.

Table information:
- Table Name: STUDENT
- Description: Contains placement data for the CSE BTech Batch 2018 at Indira Gandhi Delhi Technical University for Women.
- Columns:
  - ROLL_NUMBER (INT): Student's roll number.
  - STUDENT_NAME (VARCHAR): Student's full name.
  - COMPANY_PLACED (VARCHAR): Company name where the student was placed.
  - COMPENSATION_OFFERED (FLOAT): Compensation offered to the student in LPA (Lakhs per Annum).

**Note:** Use only the COMPENSATION_OFFERED column to determine salary data, which is expressed in LPA. Include only the SQL query in the output without any additional text or explanation.

Examples for reference:
- Question: Show list of students who got placed in Google.
  SQL Query:  
  SELECT ROLL_NUMBER, STUDENT_NAME
  FROM STUDENT
  WHERE COMPANY_PLACED = 'Google';

- Question:  How many students received CTC greater than 20 LPA?
  SQL Query:
  SELECT COUNT(*)
  FROM STUDENT
  WHERE COMPENSATION_OFFERED > 20;

- Question: How many students are going for higher studies?
  SELECT COUNT(*)
  FROM STUDENT
  WHERE COMPANY_PLACED LIKE '%Higher_Studies%';

- Question: What percentage of students are placed? 
  SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM STUDENT)
  FROM STUDENT
  WHERE COMPANY_PLACED NOT LIKE '%Higher_Studies%';

"""