import pandas as pd
scores = []  
grades = [] 
weight = []   
codes = []
units = []
i = 1
print("Welcome to Eminent-thinker cgpa calculator". upper())
num_course = eval(input("Enter the number of courses: "))
while i <= num_course:
    code = input("Enter the course code: ")
    codes.append(code.upper())
    score = eval(input("Enter your score: "))
    credit = eval(input("Enter the number of credit: "))
    units.append(credit)
    i = i+1
    if score>=70 and score<=100:
       scores.append(score)
       grades.append('A')
       weight.append(5*credit)
    elif score>=60 and score<70:
       scores.append(score)
       grades.append('B')
       weight.append(4*credit)
    elif score>=50 and score<60:
       scores.append(score)
       grades.append('C')
       weight.append(3*credit)
    elif score>=45 and score<50:
       scores.append(score)
       grades.append('D')
       weight.append(2*credit)
    elif score >=40 and score <45:
       scores.append(score)
       grades.append('E')
       weight.append(1*credit)
    elif score<40 and score>= 0:
       scores.append(score)
       grades.append('F')
       weight.append(0*credit)
    else:
       scores.append('Invalid')
       grades.append('Invalid')
       weight.append('Invalid')  
d = pd.DataFrame({'course': codes, 'credit' : units, 'score' : scores, 'grade': grades, 'weight' : weight}, index = [str(x) for x in range(1,num_course +1)])
print('\n\n',d)
cgpa = sum(weight)/sum(units)

print('\n\nYour CGPA is {:.2f}'.format(cgpa))