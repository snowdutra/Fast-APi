from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

app = FastAPI()

engine = create_engine('postgresql://postgres:root@localhost:900/postgres')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

class Vaccine(Base):
    __tablename__ = 'vacine'
    id = Column(Integer, primary_key=True)
    Patient_id = Column(Integer, ForeignKey('patient.id', ondelete='CASCADE'))
    name = Column(String(255))
    dosedate = Column(DateTime)
    dosenumber = Column(Integer)
    vaccinetype = Column(String(255))

class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    lastname = Column(String(255))

class Dose(Base):
    __tablename__ = 'dose'
    id = Column(Integer, primary_key=True)
    Vaccine_id = Column(Integer, ForeignKey('vacine.id', ondelete='CASCADE'))
    typedose = Column(String(255))
    dosedate = Column(DateTime)
    dosenumber = Column(Integer)
    applicationtype = Column(String(255))

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# CRUD Patient
@app.post("/patients", tags=["Pacientes"])
def create_patient(name: str, lastname: str):
    if not name or not lastname:
        return JSONResponse(content={'error': 'Name and Lastname are required'}, status_code=400)
    try:
        patient = Patient(name=name, lastname=lastname)
        session.add(patient)
        session.commit()
        return JSONResponse(content={'id': patient.id, 'name': patient.name, 'lastname': patient.lastname}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.put("/patients", tags=["Pacientes"])
def update_patient(id: int, name: str, lastname: str):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    if not name or not lastname:
        return JSONResponse(content={'error': 'Name and Lastname are required'}, status_code=400)
    try:
        patient = session.query(Patient).filter_by(id=id).first()
        if not patient:
            return JSONResponse(content={'error': 'Patient not found'}, status_code=404)
        patient.name = name
        patient.lastname = lastname
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content={'id': patient.id, 'name': patient.name, 'lastname': patient.lastname}, status_code=200)

@app.delete("/patients", tags=["Pacientes"])
def delete_patient(id: int):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        patient = session.query(Patient).filter_by(id=id).first()
        if not patient:
            return JSONResponse(content={'error': 'Patient not found'}, status_code=404)
        session.delete(patient)
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content={'message': 'Patient deleted successfully'}, status_code=200)

@app.get("/patients", tags=["Pacientes"])
def get_patients():
    try:
        patients = session.query(Patient).all()
        if not patients:
            return JSONResponse(content={'error': 'No patients found'}, status_code=404)
        patient_list = []
        for p in patients:
            vaccines = session.query(Vaccine).filter_by(Patient_id=p.id).all()
            vaccine_list = []
            for v in vaccines:
                doses = session.query(Dose).filter_by(Vaccine_id=v.id).all()
                dose_list = [{
                    'id': d.id,
                    'vaccine_id': d.Vaccine_id,
                    'typedose': d.typedose,
                    'dosedate': str(d.dosedate),
                    'dosenumber': d.dosenumber,
                    'applicationtype': d.applicationtype
                } for d in doses]
                vaccine_list.append({
                    'id': v.id,
                    'name': v.name,
                    'dosedate': str(v.dosedate),
                    'dosenumber': v.dosenumber,
                    'vaccinetype': v.vaccinetype,
                    'doses': dose_list
                })
            patient_list.append({
                'id': p.id,
                'name': p.name,
                'lastname': p.lastname,
                'vaccines': vaccine_list
            })
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content=patient_list, status_code=200)

@app.get("/patients/{patient_id}/", tags=["Pacientes"])
def get_patient(patient_id: int):   
    if not patient_id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        patient = session.query(Patient).filter_by(id=patient_id).first()
        if not patient:
            return JSONResponse(content={'error': 'Patient not found'}, status_code=404)
        vaccines = session.query(Vaccine).filter_by(Patient_id=patient_id).all()
        vaccine_list = []
        for v in vaccines:
            doses = session.query(Dose).filter_by(Vaccine_id=v.id).all()
            dose_list = [{
                'id': d.id,
                'vaccine_id': d.Vaccine_id,
                'typedose': d.typedose,
                'dosedate': str(d.dosedate),
                'dosenumber': d.dosenumber,
                'applicationtype': d.applicationtype
            } for d in doses]
            vaccine_list.append({
                'id': v.id,
                'name': v.name,
                'dosedate': str(v.dosedate),
                'dosenumber': v.dosenumber,
                'vaccinetype': v.vaccinetype,
                'doses': dose_list
            })
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(
        content={
            'id': patient.id,
            'name': patient.name,
            'lastname': patient.lastname,
            'vaccines': vaccine_list
        },
        status_code=200
    )

# CRUD Vaccine
@app.post("/vaccines", tags=["Vacinas"])
def create_vaccine(patient_id: int, name: str, dosedate: datetime, dosenumber: int, vaccinetype: str):
    if not patient_id or not name or not dosedate or not dosenumber or not vaccinetype:
        return JSONResponse(content={'error': 'All fields are required'}, status_code=400)
    try:
        patient = session.query(Patient).filter_by(id=patient_id).first()
        if not patient:
            return JSONResponse(content={'error': 'Patient not found'}, status_code=404)
        vaccine = Vaccine(Patient_id=patient_id, name=name, dosedate=dosedate, dosenumber=dosenumber, vaccinetype=vaccinetype)
        session.add(vaccine)
        session.commit()
        return JSONResponse(content={
            'id': vaccine.id, 'patient_id': vaccine.Patient_id, 'name': vaccine.name,
            'dosedate': str(vaccine.dosedate), 'dosenumber': vaccine.dosenumber, 'vaccinetype': vaccine.vaccinetype
        }, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
@app.put("/vaccines", tags=["Vacinas"])
def update_vaccine(id: int, patient_id: int, name: str, dosedate: datetime, dosenumber: int, vaccinetype: str):
    if not id or not patient_id or not name or not dosedate or not dosenumber or not vaccinetype:
        return JSONResponse(content={'error': 'All fields are required'}, status_code=400)
    try:
        vaccine = session.query(Vaccine).filter_by(id=id).first()
        if not vaccine:
            return JSONResponse(content={'error': 'Vaccine not found'}, status_code=404)
        patient = session.query(Patient).filter_by(id=patient_id).first()
        if not patient:
            return JSONResponse(content={'error': 'Patient not found'}, status_code=404)
        vaccine.Patient_id = patient_id
        vaccine.name = name
        vaccine.dosedate = dosedate
        vaccine.dosenumber = dosenumber
        vaccine.vaccinetype = vaccinetype
        session.commit()
        return JSONResponse(content={
            'id': vaccine.id, 'patient_id': vaccine.Patient_id, 'name': vaccine.name,
            'dosedate': str(vaccine.dosedate), 'dosenumber': vaccine.dosenumber, 'vaccinetype': vaccine.vaccinetype
        }, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
@app.get("/vaccines", tags=["Vacinas"])
def list_vaccines():
    try:
        vaccines = session.query(Vaccine).all()
        if not vaccines:
            return JSONResponse(content={'error': 'No vaccines found'}, status_code=404)
        vaccine_list = []
        for v in vaccines:
            doses = session.query(Dose).filter_by(Vaccine_id=v.id).all()
            dose_list = [{
                'id': d.id,
                'vaccine_id': d.Vaccine_id,
                'typedose': d.typedose,
                'dosedate': str(d.dosedate),
                'dosenumber': d.dosenumber,
                'applicationtype': d.applicationtype
            } for d in doses]
            vaccine_list.append({
                'id': v.id,
                'patient_id': v.Patient_id,
                'name': v.name,
                'dosedate': str(v.dosedate),
                'dosenumber': v.dosenumber,
                'vaccinetype': v.vaccinetype,
                'doses': dose_list
            })
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content=vaccine_list, status_code=200)

@app.get("/vaccines/{vaccine_id}", tags=["Vacinas"])
def get_vaccine(vaccine_id: int):
    if not vaccine_id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        vaccine = session.query(Vaccine).filter_by(id=vaccine_id).first()
        if not vaccine:
            return JSONResponse(content={'error': 'Vaccine not found'}, status_code=404)
        doses = session.query(Dose).filter_by(Vaccine_id=vaccine_id).all()
        dose_list = [{
            'id': d.id,
            'vaccine_id': d.Vaccine_id,
            'typedose': d.typedose,
            'dosedate': str(d.dosedate),
            'dosenumber': d.dosenumber,
            'applicationtype': d.applicationtype
        } for d in doses]
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content={
        'id': vaccine.id,
        'patient_id': vaccine.Patient_id,
        'name': vaccine.name,
        'dosedate': str(vaccine.dosedate),
        'dosenumber': vaccine.dosenumber,
        'vaccinetype': vaccine.vaccinetype,
        'doses': dose_list
    }, status_code=200)

@app.delete("/vaccines", tags=["Vacinas"])
def delete_vaccine(id: int):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        vaccine = session.query(Vaccine).filter_by(id=id).first()
        if not vaccine:
            return JSONResponse(content={'error': 'Vaccine not found'}, status_code=404)
        session.delete(vaccine)
        session.commit()
        return JSONResponse(content={'message': 'Vaccine deleted successfully'}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# CRUD Dose
@app.post("/doses", tags=["Doses"])
def create_dose(vaccine_id: int, typedose: str, dosedate: datetime, dosenumber: int, applicationtype: str):
    if not vaccine_id or not typedose or not dosedate or not dosenumber or not applicationtype:
        return JSONResponse(content={'error': 'All fields are required'}, status_code=400)
    try:
        vaccine = session.query(Vaccine).filter_by(id=vaccine_id).first()
        if not vaccine:
            return JSONResponse(content={'error': 'Vaccine not found'}, status_code=404)
        dose = Dose(Vaccine_id=vaccine_id, typedose=typedose, dosedate=dosedate, dosenumber=dosenumber, applicationtype=applicationtype)
        session.add(dose)
        session.commit()
        return JSONResponse(content={
            'id': dose.id, 'vaccine_id': dose.Vaccine_id, 'typedose': dose.typedose,
            'dosedate': str(dose.dosedate), 'dosenumber': dose.dosenumber, 'applicationtype': dose.applicationtype
        }, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
@app.put("/doses", tags=["Doses"])
def update_dose(id: int, vaccine_id: int, typedose: str, dosedate: datetime, dosenumber: int, applicationtype: str):
    if not id or not vaccine_id or not typedose or not dosedate or not dosenumber or not applicationtype:
        return JSONResponse(content={'error': 'All fields are required'}, status_code=400)
    try:
        dose = session.query(Dose).filter_by(id=id).first()
        if not dose:
            return JSONResponse(content={'error': 'Dose not found'}, status_code=404)
        vaccine = session.query(Vaccine).filter_by(id=vaccine_id).first()
        if not vaccine:
            return JSONResponse(content={'error': 'Vaccine not found'}, status_code=404)
        dose.Vaccine_id = vaccine_id
        dose.typedose = typedose
        dose.dosedate = dosedate
        dose.dosenumber = dosenumber
        dose.applicationtype = applicationtype
        session.commit()
        return JSONResponse(content={
            'id': dose.id, 'vaccine_id': dose.Vaccine_id, 'typedose': dose.typedose,
            'dosedate': str(dose.dosedate), 'dosenumber': dose.dosenumber, 'applicationtype': dose.applicationtype
        }, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
@app.get("/doses", tags=["Doses"])
def list_doses():
    try:
        doses = session.query(Dose).all()
        if not doses:
            return JSONResponse(content={'error': 'No doses found'}, status_code=404)
        dose_list = [{
            'id': d.id, 'vaccine_id': d.Vaccine_id, 'typedose': d.typedose,
            'dosedate': str(d.dosedate), 'dosenumber': d.dosenumber, 'applicationtype': d.applicationtype
        } for d in doses]
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content=dose_list, status_code=200)

@app.get("/doses/{dose_id}", tags=["Doses"])
def get_dose(dose_id: int):
    if not dose_id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        dose = session.query(Dose).filter_by(id=dose_id).first()
        if not dose:
            return JSONResponse(content={'error': 'Dose not found'}, status_code=404)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content={
        'id': dose.id, 'vaccine_id': dose.Vaccine_id, 'typedose': dose.typedose,
        'dosedate': str(dose.dosedate), 'dosenumber': dose.dosenumber, 'applicationtype': dose.applicationtype
    }, status_code=200)

@app.delete("/doses", tags=["Doses"])
def delete_dose(id: int):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        dose = session.query(Dose).filter_by(id=id).first()
        if not dose:
            return JSONResponse(content={'error': 'Dose not found'}, status_code=404)
        session.delete(dose)
        session.commit()
        return JSONResponse(content={'message': 'Dose deleted successfully'}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# Endpoint HTML com títulos de seção (não sobrescfrom fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

app = FastAPI()

# Database setup
engine = create_engine('postgresql://postgres:root@localhost:900/postgres')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
Base = declarative_base()

# Models
class Department(Base):
    __tablename__ = 'department'
    DepartmentID = Column(Integer, primary_key=True)
    Name = Column(String(255))
    Region = Column(String(255))
    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = 'employee'
    EmployeeID = Column(Integer, primary_key=True)
    DepartmentID = Column(Integer, ForeignKey('department.DepartmentID', ondelete='CASCADE'))
    Name = Column(String(255))
    Birthday = Column(DateTime)
    Salary = Column(Float(10, 2))
    Job = Column(String(255))
    department = relationship("Department", back_populates="employees")
    job_history = relationship("JobHistory", back_populates="employee")

class JobHistory(Base):
    __tablename__ = 'jobhistory'
    JobHistoryID = Column(Integer, primary_key=True)
    EmployeeID = Column(Integer, ForeignKey('employee.EmployeeID', ondelete='CASCADE'))
    Title = Column(String(255))
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)
    Salary = Column(Float(10, 2))
    Job = Column(String(255))
    employee = relationship("Employee", back_populates="job_history")

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# CRUD Endpoints for Department
@app.post("/departments", tags=["Departments"])
def create_department(Name: str, Region: str):
    try:
        department = Department(Name=Name, Region=Region)
        session.add(department)
        session.commit()
        return JSONResponse(content={'DepartmentID': department.DepartmentID, 'Name': department.Name, 'Region': department.Region}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/departments", tags=["Departments"])
def list_departments():
    try:
        departments = session.query(Department).all()
        if not departments:
            return JSONResponse(content={'error': 'No departments found'}, status_code=404)
        department_list = [{'DepartmentID': d.DepartmentID, 'Name': d.Name, 'Region': d.Region} for d in departments]
        return JSONResponse(content=department_list, status_code=200)
    except Exception as e:
        return JSONResponse(content={'error': str(e)}, status_code=500)

# CRUD Endpoints for Employee
@app.post("/employees", tags=["Employees"])
def create_employee(DepartmentID: int, Name: str, Birthday: DateTime, Salary: float, Job: str):
    try:
        employee = Employee(DepartmentID=DepartmentID, Name=Name, Birthday=Birthday, Salary=Salary, Job=Job)
        session.add(employee)
        session.commit()
        return JSONResponse(content={'EmployeeID': employee.EmployeeID, 'Name': employee.Name, 'Salary': employee.Salary, 'Job': employee.Job}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/employees", tags=["Employees"])
def list_employees():
    try:
        employees = session.query(Employee).all()
        if not employees:
            return JSONResponse(content={'error': 'No employees found'}, status_code=404)
        employee_list = [{'EmployeeID': e.EmployeeID, 'Name': e.Name, 'Salary': e.Salary, 'Job': e.Job} for e in employees]
        return JSONResponse(content=employee_list, status_code=200)
    except Exception as e:
        return JSONResponse(content={'error': str(e)}, status_code=500)

# CRUD Endpoints for JobHistory
@app.post("/jobhistory", tags=["JobHistory"])
def create_job_history(EmployeeID: int, Title: str, StartDate: DateTime, EndDate: DateTime, Salary: float, Job: str):
    try:
        job_history = JobHistory(EmployeeID=EmployeeID, Title=Title, StartDate=StartDate, EndDate=EndDate, Salary=Salary, Job=Job)
        session.add(job_history)
        session.commit()
        return JSONResponse(content={'JobHistoryID': job_history.JobHistoryID, 'Title': job_history.Title, 'Salary': job_history.Salary}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/jobhistory", tags=["JobHistory"])
def list_job_history():
    try:
        job_histories = session.query(JobHistory).all()
        if not job_histories:
            return JSONResponse(content={'error': 'No job histories found'}, status_code=404)
        job_history_list = [{'JobHistoryID': j.JobHistoryID, 'Title': j.Title, 'Salary': j.Salary} for j in job_histories]
        return JSONResponse(content=job_history_list, status_code=200)
    except Exception as e:
        return JSONResponse(content={'error': str(e)}, status_code=500)reve a documentação Swagger)
@app.get("/home", response_class=HTMLResponse, tags=["Visualização"])
def home():
    pacientes = session.query(Patient).all()
    vacinas = session.query(Vaccine).all()
    doses = session.query(Dose).all()

    html = """
    <html>
    <head>
        <title>Blog FastAPI</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #2c3e50; }
            ul { margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <h1>Autores</h1>
        <ul>
    """
    for autor in pacientes:
        html += f"<li>{autor.name} (idade: {autor.age if autor.age is not None else 'N/A'})</li>"
    html += """
        </ul>
        <h1>Categorias</h1>
        <ul>
    """
    for categoria in vacinas:
        html += f"<li>{categoria.name}</li>"
    html += """
        </ul>
        <h1>Posts</h1>
        <ul>
    """
    for post in doses:
        html += f"<li>{post.title} - {post.subtitle or ''}</li>"
    html += """
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
