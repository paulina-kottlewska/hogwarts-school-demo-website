# CS50 Final Project - Hogwarts School Demo Website

My project is a website dedicated to Hogwarts School, the fictional institution from the Harry Potter series. I created it as my final project for the CS50: Introduction to Computer Science course. My objective was to design a digital representation of the renowned school, with a primary focus on digitalizing the enrollment process for first-year students.

Technologies used:
* Python
* Flask
* JavaScript
* SQLite3
* Bootstrap
* AJAX and JSON to communicate between Javascript and Python

## Features
1. Modal inspired by the Hogwarts Acceptance Letter, which is displayed immediately after the user completes the registration form. The user's name is extracted from the form and displayed in the greeting section of the letter.
2. Dynamic Sorting Hat Quiz. The quiz aims to sort the student into one of the Hogwarts houses. It consists of 8 questions. Each question has four options to choose from. An additional question might appear in case there is a tie between houses. After completing the quiz, a modal with the crest, house name, and house colors is displayed.
3. Student panel - for exploring and enrolling in various subjects for the academic year. The user has to be logged in to access the student panel. Once enrolled, the user can review the curriculum for each subject, which is sourced from an integrated database. Additionally, there's a modal designed to resemble the List of Required Books and Equipment from the books, providing users with a familiar and engaging experience.

## Possible Improvements
My webpage focuses mostly on first-year students. It would be necessary to create more academic content like courses, exams, and laboratories to improve the overall experience. Possible improvements:

* Teacher panel where a teacher can post materials and grades
* Expand the webpage to enable students to progress to the next academic year