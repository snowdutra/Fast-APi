from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

app = FastAPI()

# Altere conforme sua configuração do PostgreSQL
engine = create_engine('postgresql://postgres:root@localhost:900/postgres')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

# MODELS
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    region = Column(String(255))
    employees = relationship("Employee", back_populates="department", cascade="all, delete-orphan")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete='CASCADE'))
    name = Column(String(255))
    birthday = Column(DateTime)
    salary = Column(Float)
    job = Column(String(255))
    department = relationship("Department", back_populates="employees")
    job_history = relationship("JobHistory", back_populates="employee", cascade="all, delete-orphan")

class JobHistory(Base):
    __tablename__ = "job_history"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete='CASCADE'))
    title = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    salary = Column(Float)
    job = Column(String(255))
    employee = relationship("Employee", back_populates="job_history")

Base.metadata.create_all(bind=engine)

# DEPARTMENTS
@app.post("/departments", tags=["Departamentos"])
def create_department(name: str, region: str):
    try:
        dept = Department(name=name, region=region)
        session.add(dept)
        session.commit()
        return JSONResponse(content={'id': dept.id, 'name': dept.name, 'region': dept.region}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/departments", tags=["Departamentos"])
def list_departments():
    departments = session.query(Department).all()
    result = []
    for d in departments:
        employees = [{
            'id': e.id,
            'name': e.name,
            'birthday': str(e.birthday),
            'salary': e.salary,
            'job': e.job,
            'job_history': [{
                'id': h.id,
                'title': h.title,
                'start_date': str(h.start_date),
                'end_date': str(h.end_date),
                'salary': h.salary,
                'job': h.job
            } for h in e.job_history]
        } for e in d.employees]
        result.append({'id': d.id, 'name': d.name, 'region': d.region, 'employees': employees})
    return JSONResponse(content=result, status_code=200)

@app.get("/departments/{department_id}", tags=["Departamentos"])
def get_department(department_id: int):
    dept = session.query(Department).filter_by(id=department_id).first()
    if not dept:
        return JSONResponse(content={'error': 'Department not found'}, status_code=404)
    employees = [{
        'id': e.id,
        'name': e.name,
        'birthday': str(e.birthday),
        'salary': e.salary,
        'job': e.job,
        'job_history': [{
            'id': h.id,
            'title': h.title,
            'start_date': str(h.start_date),
            'end_date': str(h.end_date),
            'salary': h.salary,
            'job': h.job
        } for h in e.job_history]
    } for e in dept.employees]
    return JSONResponse(content={'id': dept.id, 'name': dept.name, 'region': dept.region, 'employees': employees}, status_code=200)

@app.put("/departments/{department_id}", tags=["Departamentos"])
def update_department(department_id: int, name: str, region: str):
    dept = session.query(Department).filter_by(id=department_id).first()
    if not dept:
        return JSONResponse(content={'error': 'Department not found'}, status_code=404)
    dept.name = name
    dept.region = region
    session.commit()
    return JSONResponse(content={'message': 'Department updated successfully'}, status_code=200)

@app.delete("/departments/{department_id}", tags=["Departamentos"])
def delete_department(department_id: int):
    dept = session.query(Department).filter_by(id=department_id).first()
    if not dept:
        return JSONResponse(content={'error': 'Department not found'}, status_code=404)
    session.delete(dept)
    session.commit()
    return JSONResponse(content={'message': 'Department deleted successfully'}, status_code=200)

# EMPLOYEES
@app.post("/employees", tags=["Funcionários"])
def create_employee(name: str, department_id: int, birthday: datetime, salary: float, job: str):
    try:
        emp = Employee(name=name, department_id=department_id, birthday=birthday, salary=salary, job=job)
        session.add(emp)
        session.commit()
        return JSONResponse(content={'id': emp.id}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/employees", tags=["Funcionários"])
def list_employees():
    employees = session.query(Employee).all()
    result = []
    for e in employees:
        history = [{
            'id': h.id,
            'title': h.title,
            'start_date': str(h.start_date),
            'end_date': str(h.end_date),
            'salary': h.salary,
            'job': h.job
        } for h in e.job_history]
        result.append({
            'id': e.id,
            'name': e.name,
            'department_id': e.department_id,
            'department': e.department.name if e.department else None,
            'birthday': str(e.birthday),
            'salary': e.salary,
            'job': e.job,
            'job_history': history
        })
    return JSONResponse(content=result, status_code=200)

@app.get("/employees/{employee_id}", tags=["Funcionários"])
def get_employee(employee_id: int):
    emp = session.query(Employee).filter_by(id=employee_id).first()
    if not emp:
        return JSONResponse(content={'error': 'Employee not found'}, status_code=404)
    history = [{
        'id': h.id,
        'title': h.title,
        'start_date': str(h.start_date),
        'end_date': str(h.end_date),
        'salary': h.salary,
        'job': h.job
    } for h in emp.job_history]
    return JSONResponse(content={
        'id': emp.id,
        'name': emp.name,
        'department_id': emp.department_id,
        'department': emp.department.name if emp.department else None,
        'birthday': str(emp.birthday),
        'salary': emp.salary,
        'job': emp.job,
        'job_history': history
    }, status_code=200)

@app.put("/employees/{employee_id}", tags=["Funcionários"])
def update_employee(employee_id: int, name: str, department_id: int, birthday: datetime, salary: float, job: str):
    emp = session.query(Employee).filter_by(id=employee_id).first()
    if not emp:
        return JSONResponse(content={'error': 'Employee not found'}, status_code=404)
    emp.name = name
    emp.department_id = department_id
    emp.birthday = birthday
    emp.salary = salary
    emp.job = job
    session.commit()
    return JSONResponse(content={'message': 'Employee updated successfully'}, status_code=200)

@app.delete("/employees/{employee_id}", tags=["Funcionários"])
def delete_employee(employee_id: int):
    emp = session.query(Employee).filter_by(id=employee_id).first()
    if not emp:
        return JSONResponse(content={'error': 'Employee not found'}, status_code=404)
    session.delete(emp)
    session.commit()
    return JSONResponse(content={'message': 'Employee deleted successfully'}, status_code=200)

# JOB HISTORY
@app.post("/employees/{employee_id}/history", tags=["Histórico de Cargos"])
def add_job_history(employee_id: int, title: str, start_date: datetime, end_date: datetime, salary: float, job: str):
    emp = session.query(Employee).filter_by(id=employee_id).first()
    if not emp:
        return JSONResponse(content={'error': 'Employee not found'}, status_code=404)
    history = JobHistory(employee_id=employee_id, title=title, start_date=start_date, end_date=end_date, salary=salary, job=job)
    session.add(history)
    session.commit()
    return JSONResponse(content={'id': history.id}, status_code=201)

@app.get("/jobhistory", tags=["Histórico de Cargos"])
def list_job_history():
    histories = session.query(JobHistory).all()
    return JSONResponse(content=[{
        'id': h.id, 'employee_id': h.employee_id, 'title': h.title,
        'start_date': str(h.start_date), 'end_date': str(h.end_date),
        'salary': h.salary, 'job': h.job
    } for h in histories], status_code=200)

@app.get("/jobhistory/{history_id}", tags=["Histórico de Cargos"])
def get_job_history(history_id: int):
    h = session.query(JobHistory).filter_by(id=history_id).first()
    if not h:
        return JSONResponse(content={'error': 'Job history not found'}, status_code=404)
    return JSONResponse(content={
        'id': h.id, 'employee_id': h.employee_id, 'title': h.title,
        'start_date': str(h.start_date), 'end_date': str(h.end_date),
        'salary': h.salary, 'job': h.job
    }, status_code=200)

@app.put("/jobhistory/{history_id}", tags=["Histórico de Cargos"])
def update_job_history(history_id: int, title: str, start_date: datetime, end_date: datetime, salary: float, job: str):
    h = session.query(JobHistory).filter_by(id=history_id).first()
    if not h:
        return JSONResponse(content={'error': 'Job history not found'}, status_code=404)
    h.title = title
    h.start_date = start_date
    h.end_date = end_date
    h.salary = salary
    h.job = job
    session.commit()
    return JSONResponse(content={'message': 'Job history updated successfully'}, status_code=200)

@app.delete("/jobhistory/{history_id}", tags=["Histórico de Cargos"])
def delete_job_history(history_id: int):
    h = session.query(JobHistory).filter_by(id=history_id).first()
    if not h:
        return JSONResponse(content={'error': 'Job history not found'}, status_code=404)
    session.delete(h)
    session.commit()
    return JSONResponse(content={'message': 'Job history deleted successfully'}, status_code=200)

# VISUALIZAÇÃO HTML
@app.get("/home", response_class=HTMLResponse, tags=["Visualização"])
def home():
    departments = session.query(Department).all()
    employees = session.query(Employee).all()
    histories = session.query(JobHistory).all()

    html = """
    <html><head><title>Empresa FastAPI</title><style>
    body { font-family: Arial; margin: 40px; } h1 { color: #2c3e50; } ul { margin-bottom: 30px; }
    </style></head><body>
    <h1>Departamentos</h1><ul>"""
    for d in departments:
        html += f"<li>{d.name} ({d.region})</li>"
    html += "</ul><h1>Funcionários</h1><ul>"
    for e in employees:
        html += f"<li>{e.name} - {e.job} - {e.salary}</li>"
    html += "</ul><h1>Histórico de Cargos</h1><ul>"
    for h in histories:
        html += f"<li>{h.title} ({h.start_date.date()} - {h.end_date.date()})</li>"
    html += "</ul></body></html>"

    return HTMLResponse(content=html)
