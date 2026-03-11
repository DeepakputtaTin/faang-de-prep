from collections import defaultdict


def grouo_by(employees):
    avg_by_dept = {}
    ddict = defaultdict(list)
    for emp in employees:
        ddict[emp["dept"]].append(emp)
    print(ddict)
    for dept, emps in ddict.items():
        salaries  = [emp['salary'] for emp in emps]
        avg = sum(salaries)/len(salaries)
        avg_by_dept[dept] =  sum(salaries)/len(salaries)


        top  = max(emps, key = lambda e:e['salary'] )
        print(f'salries = {salaries}')
        print(f' average{avg}')
        print(f'top salary {top}')
    print(avg_by_dept)
    best_dept = max(avg_by_dept, key=avg_by_dept.get)
    print(f'Highest paying dept: {best_dept} → {avg_by_dept[best_dept]}')

employees = [
    {"name": "Alice", "dept": "Eng", "salary": 90000},
    {"name": "Bob",   "dept": "Eng", "salary": 85000},
    {"name": "Carol", "dept": "HR",  "salary": 70000},
    {"name": "Dave",  "dept": "HR",  "salary": 75000},
    {"name": "Eve",   "dept": "Eng", "salary": 95000}
]
grouo_by(employees)