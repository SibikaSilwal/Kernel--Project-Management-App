import re
from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import null
from werkzeug.utils import secure_filename
from .models import Discovery, Employee, Project, TaskLists, User, Task, TaskComments, Files
from . import db
import json
import base64
# this file is a blueprint of the website
# it has all the routes and urls for the site

views = Blueprint('views', __name__)

# to define a view/route in flask
#syntax @blueprintName.routes('url to get to the page')
# when the route / is accessed home() is called


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # if request.method == 'GET' or request.method == 'POST':
    this_employee = db.session.query(Employee).filter(
        Employee.employeeId == current_user.id).first()
    user_projects = this_employee.employee_Projects
    db.session.commit()

    if request.method == 'POST':
        projectName = request.form.get('newProject')
        projectDescription = request.form.get('description')
        checkProjectName = db.session.query(Project).filter(
            Project.projectName == projectName).first()
        #print("existing project: ", checkProjectName.projectName)

        if checkProjectName != None:
            flash('Project name already exists. Please choose a unique project name',
                  category='error')
        elif len(projectName) < 1:
            flash('Project name has to be atleast one character long',
                  category='error')
        else:
            new_project = Project(projectName=projectName,
                                  projectDescription=projectDescription)
            db.session.add(new_project)
            db.session.flush()
            this_employee.employee_Projects.append(new_project)
            db.session.commit()
            flash('New project created.', category='success')

    return render_template('home.html', user=current_user, user_projects=user_projects)


@views.route('/project/<project_id>', methods=['POST', 'GET'])
@login_required
def OpenProject(project_id):
    if request.method == 'POST':
        project = json.loads(request.data)
        projectID = project['projectID']
        current_Project = Project.query.get(projectID)
        project_Employees = current_Project.projectEmployees
        print("employees: ", project_Employees)
        db.session.commit()
        if current_Project:
            print("project id: ", projectID)
            return render_template('project.html', user=current_user, current_Project=current_Project, project_Employees=project_Employees)
        else:
            return "Project does not exist"

    if request.method == 'GET':
        current_Project = Project.query.get(project_id)
        project_Employees = current_Project.projectEmployees
        print("employees: ", project_Employees)
        db.session.commit()
        if current_Project:
            print("project id: ", project_id)
            return render_template('project.html', user=current_user, current_Project=current_Project, project_Employees=project_Employees)
        else:
            return "Project does not exist"


@views.route('/add-member', methods=['POST'])
@login_required
def AddMember():
    memberEmail = request.form.get("newMember")
    currentProjectId = request.form.get("projectid")
    memberID = db.session.query(User).filter(User.email == memberEmail).first()
    employee = Employee.query.get(memberID.id)  # employee object
    currentProject = Project.query.get(currentProjectId)  # project object
    print("emploee: ", employee, " project id: ", currentProjectId)

    for project in employee.employee_Projects:
        if(project.projectName == currentProject.projectName):
            flash("Given team member is already in this project.", category='error')
            db.session.commit()
            return redirect(url_for('views.OpenProject', project_id=currentProjectId))

    if employee and currentProject:
        employee.employee_Projects.append(currentProject)

    db.session.commit()

    return redirect(url_for('views.OpenProject', project_id=currentProjectId))


@views.route('/todos/<project_id>', methods=['GET', 'POST'])
@login_required
def todos(project_id):
    if request.method == 'GET':
        current_Project = Project.query.get(project_id)
        taskLists = current_Project.projectTaskLists
        return render_template('todo.html', user=current_user, current_Project=current_Project, taskLists=taskLists)
    return 1


@views.route('/create-list', methods=['POST'])
@login_required
def CreateList():
    listName = request.form.get('newList')
    currentProjectId = request.form.get("projectid")
    newList = TaskLists(listName=listName, projectId=currentProjectId)
    db.session.add(newList)
    db.session.commit()
    return redirect(url_for('views.todos', project_id=currentProjectId))


@views.route('/create-task', methods=['POST'])
@login_required
def CreateTask():
    taskName = request.form.get('newTask')
    currentProjectId = Project.query.get(
        request.form.get("projectid"))  # project object
    taskListId = request.form.get("taskListId")
    assignedToEmail = request.form.get("assignedto")
    assignedtoUserId = db.session.query(User).filter(
        User.email == assignedToEmail).first()
    if not assignedtoUserId:
        flash("Email does not exist!", category="error")
        return redirect(url_for('views.todos', project_id=request.form.get("projectid")))

    assignedtoEmployee = Employee.query.get(assignedtoUserId.id)  # emp obj
    duedate = request.form.get("duedate")
    assignedby = Employee.query.get(current_user.id)
    note = request.form.get("note")
    newTask = Task(taskName=taskName, theProject=currentProjectId,
                   assignedByEmployee=assignedby, dueOnDate=duedate, note=note, tasklistId=taskListId)
    db.session.add(newTask)
    db.session.flush()
    assignedtoEmployee.employee_Tasks.append(newTask)
    db.session.commit()
    return redirect(url_for('views.todos', project_id=request.form.get("projectid")))


@views.route('/todos/<project_id>/task/<task_id>', methods=['GET'])
@login_required
def task(project_id, task_id):
    current_Project = Project.query.get(project_id)
    current_task = Task.query.get(task_id)
    return render_template('task.html', user=current_user, current_Project=current_Project, current_task=current_task)


@views.route('/add-comment', methods=['POST'])
@login_required
def AddComment():
    taskid = request.form.get('task_Id')
    comment = request.form.get('ckeditor')
    commentBy = Employee.query.get(current_user.id)
    taskObject = Task.query.get(taskid)
    print("comment: ", comment)
    new_comment = TaskComments(
        taskComments=taskObject, comment=comment, empComments=commentBy)
    db.session.add(new_comment)
    db.session.flush()
    db.session.commit()
    return redirect(url_for('views.task', project_id=request.form.get("projectid"), task_id=taskid))


@views.route('/files/<project_id>', methods=['GET', 'POST'])
@login_required
def files(project_id):
    if request.method == 'GET':
        current_Project = Project.query.get(project_id)
        projectFiles = current_Project.projectFiles
        return render_template('projectFile.html', user=current_user, current_Project=current_Project, projectFiles=projectFiles)
    return 1


@views.route('/uploadfile', methods=['POST'])
@login_required
def uploadfile():
    file = request.files['projectFile']
    project_id = request.form.get('projectid')
    if not file:
        return 'File not uploaded', 400

    filename = secure_filename(file.filename)
    mimetype = file.mimetype
    new_file = Files(file=file.read(), fileName=filename,
                     mimetype=mimetype, projectId=project_id)
    db.session.add(new_file)
    db.session.flush()
    db.session.commit()
    print("newfile: ", new_file)
    flash("File uploaded sucessfully!", category="success")
    return redirect(url_for('views.files', project_id=project_id))


@views.route('/markTaskDone', methods=['POST'])
@login_required
def markTaskDone():
    taskStatus = request.form.get("done")
    taskId = request.form.get("taskId")
    print("task status: ", taskStatus)
    if taskStatus == '1':
        task = Task.query.filter_by(taskId=taskId).first()
        task.completed = True
        db.session.commit()
        print("task was completed: ", taskId)
    else:
        task = Task.query.filter_by(taskId=taskId).first()
        task.completed = False
        db.session.commit()
        print("task was not completed", taskId)

    return jsonify(status="success")


@views.route('/userTasks', methods=['GET'])
@login_required
def userTasks():
    this_employee = db.session.query(Employee).filter(
        Employee.employeeId == current_user.id).first()
    db.session.commit()
    return render_template('userTasks.html', user=current_user, employee=this_employee)


@views.route('/<project_id>/discovery', methods=['GET'])
@login_required
def discovery(project_id):
    current_Project = Project.query.get(project_id)
    discoveries = current_Project.projectDiscovery
    db.session.commit()
    return render_template('discovery.html', user=current_user, current_Project=current_Project, discoveries=discoveries)


@views.route('/<project_id>/discovery/new_note', methods=['GET', 'POST'])
@login_required
def new_discovery(project_id):
    if request.method == 'GET':
        current_Project = Project.query.get(project_id)
        return render_template('newDiscovery.html', user=current_user, current_Project=current_Project)
    if request.method == 'POST':
        note = request.form.get('ckeditor')
        current_Project = Project.query.get(project_id)
        discoveryTitle = request.form.get('discovery-name')
        new_discovery = Discovery(discoveryName=discoveryTitle,
                                  projectId=project_id, discoveryNote=note, addedBy=current_user.id)
        db.session.add(new_discovery)
        db.session.flush()
        db.session.commit()
        return redirect(url_for('views.discovery', project_id=project_id))


@views.route('/<project_id>/discovery/<discovery_id>', methods=['GET'])
@login_required
def current_discovery(project_id, discovery_id):
    current_Project = Project.query.get(project_id)
    current_discovery = Discovery.query.get(discovery_id)
    addedby_employee = Employee.query.get(current_discovery.addedBy)
    db.session.commit()
    return render_template('discoveryNote.html', user=current_user, current_Project=current_Project, discovery=current_discovery, addedBy=addedby_employee)
