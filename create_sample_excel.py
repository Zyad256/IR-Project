"""Script to generate sample Excel file for testing."""
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Employees"

headers = ["Name", "Department", "Role", "Skills", "Experience_Years"]
ws.append(headers)

data = [
    ["Ahmed Hassan", "Engineering", "Software Engineer", "Python, Java, Elasticsearch, Machine Learning", 5],
    ["Sara Mohamed", "Data Science", "Data Analyst", "Python, SQL, Pandas, Tableau, Statistics", 3],
    ["Omar Ali", "Engineering", "DevOps Engineer", "Docker, Kubernetes, AWS, Linux, CI/CD", 7],
    ["Fatima Nour", "Research", "NLP Researcher", "Natural Language Processing, Deep Learning, PyTorch", 4],
    ["Youssef Ibrahim", "Engineering", "Backend Developer", "FastAPI, Django, PostgreSQL, Redis", 6],
    ["Mona Khaled", "Data Science", "ML Engineer", "TensorFlow, Scikit-learn, Feature Engineering", 5],
    ["Kareem Saad", "IT", "System Administrator", "Networking, Security, Linux Server, Cloud Computing", 8],
    ["Nadia Fawzy", "Research", "Information Retrieval Specialist", "Search Engines, Indexing, Lucene, Elasticsearch", 6],
]

for row in data:
    ws.append(row)

wb.save("sample_data/employees.xlsx")
print("Created employees.xlsx")
