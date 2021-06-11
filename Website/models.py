from enum import unique

from sqlalchemy.orm import backref
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

projectEmployee = db.Table('projectEmployee',
                           db.Column('employeeId', db.Integer,
                                     db.ForeignKey('employee.employeeId')),
                           db.Column('projectId', db.Integer,
                                     db.ForeignKey('project.id'))
                           )

taskEmployee = db.Table('taskEmployee',
                        db.Column('taskId', db.Integer,
                                  db.ForeignKey('task.taskId')),
                        db.Column('assignedTo', db.Integer,
                                  db.ForeignKey('employee.employeeId'))
                        )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projectName = db.Column(db.String(250), unique=True)
    projectDescription = db.Column(db.String(1000))
    tasks = db.relationship('Task', backref='theProject')
    projectFiles = db.relationship('Files', backref='fileProject')
    # if we want all the tasks for a project, we can write Project.tasks
    # If we want to know the project for a task, we can write Task.theProject.projectName
    projectEmployees = db.relationship(
        'Employee', secondary=projectEmployee, backref=db.backref('employee_Projects', lazy='dynamic'))
    projectDiscovery = db.relationship('Discovery', backref='theProject')
    projectTaskLists = db.relationship('TaskLists', backref='theProject')
    # to get the discovery notes in a project: projectObject.projectDiscovery
    # to get the task lists: projectObject.projectTaskLists


class Employee(db.Model):
    employeeId = db.Column(db.Integer, primary_key=True)
    employeeName = db.Column(db.String(150))
    employeeDepartment = db.Column(db.String(150))
    tasksAssigned = db.relationship('Task', backref='assignedByEmployee')
    employeeComments = db.relationship('TaskComments', backref='empComments')
    # get assigned tasks list by the employee: Employee_object.tasksAssigned
    # loop through it: get notes: Employee_object.tasksAssigned.note
    # get who assigned a task: Task.assignedByEmployee.employeeName

    # add employee to a project and vice-versa:
    # Employee_object.employee_Projects.append(Project_object)

    # to get employee's tasks:
    # loop through: Employee_object.employee_Tasks
    # for project in Employee_object.employee_Tasks:
    #   print Employee_object.employee_Tasks.taskName

    # to get employee's projects:
    # loop through: Employee_object.employee_Projects
    # for project in Employee_object.employee_Projects:
    #   print Employee_object.employee_Projects.projectName

# class ProjectEmployeeReln(db.Model):
    #projectId = db.Column(db.Integer, primary_key=True)
    #employeeid = db.Column(db.Integer, primary_key=True)


class TaskLists(db.Model):
    listId = db.Column(db.Integer, primary_key=True)
    listName = db.Column(db.String(300))
    projectId = db.Column(db.Integer, db.ForeignKey('project.id'))
    tasksInList = db.relationship('Task', backref='theList')
    # to get the tasks in a list: listObject.tasksInList
    # to get the task's list: TaskObject.theList


class Task(db.Model):
    taskId = db.Column(db.Integer, primary_key=True)
    taskName = db.Column(db.String(300))
    projectId = db.Column(db.Integer, db.ForeignKey('project.id'))
    assingedBy = db.Column(db.Integer, db.ForeignKey('employee.employeeId'))
    assignedOnDate = db.Column(db.Date, default=func.now())
    dueOnDate = db.Column(db.Date)
    note = db.Column(db.String)
    completed = db.Column(db.Boolean, default=False)
    tasklistId = db.Column(db.Integer, db.ForeignKey('task_lists.listId'))
    comments = db.relationship('TaskComments', backref='taskComments')
    taskEmployees = db.relationship(
        'Employee', secondary=taskEmployee, backref=db.backref('employee_Tasks', lazy='dynamic'))
    # new_task = Task(taskid, theProject = project_object, assignedByEmployee = employee_object,....)

# class TaskEmployeeReln(db.Model):
    #taskId = db.Column(db.Integer, primary_key=True)
    #assignedTo = db.Column(db.Integer, primary_key=True)


class TaskComments(db.Model):
    commentId = db.Column(db.Integer, primary_key=True)
    taskId = db.Column(db.Integer, db.ForeignKey('task.taskId'))
    comment = db.Column(db.String)
    commentBy = db.Column(db.Integer, db.ForeignKey('employee.employeeId'))


class Files(db.Model):
    fileId = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.LargeBinary, nullable=False)
    fileName = db.Column(db.String(50))
    mimetype = db.Column(db.String, nullable=False)
    projectId = db.Column(db.Integer, db.ForeignKey('project.id'))


class Discovery(db.Model):
    discoveryId = db.Column(db.Integer, primary_key=True)
    discoveryName = db.Column(db.String(500))
    projectId = db.Column(db.Integer, db.ForeignKey('project.id'))
    discoveryNote = db.Column(db.String)
    addedBy = db.Column(db.Integer, db.ForeignKey('employee.employeeId'))
