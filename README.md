<h1 align="center">Welcome to Achilles-Engage-21 👋</h1>

> All in one cloud-based learning management system (LMS) gives you all the tools you need to create, deliver, track and analyze the Test/Quizzes, includes easy to use Annoucement maker along with attachments.

### 🏠 [Homepage](https://achilles.cloudns.asia)

## Why is Achilles different?
- **Extensible** - All features from creating classes and Tests, to evaluating online OMR is built from scratch and with minimal dependencies. Additionally, it's inherits in-built database models of Django. This makes the application highly extensible, i.e features can easily be integrated without worrying about interdependency between components, customization limits.
- **Adaptable** - The code is compartmentalized, i.e it is broken into components. Changing any feature is an efficient process with an assurance that no other component will be impacted directly.
- **Easy Integrations** - Achilles, as a platform, can be integrated into any organization's architecture as a microservice. Credits to the agile way of development.
- **Painless UI** - The UI is built with Bootstrap components, keeping the static files to minimal which greatly increases site loading time, execution time, memory consumption.
- **Hosted** - Hosted on Azure Virtual Machines, Using NGINX (High-performance Web Server). Also uses Git tools for enforcing Agile Methodology. 


## Online Test maker with Auto-grader in each class 
- Built with Django backend, OpenCV library, and Bootstrap front-end.
- Create unlimited Classes.

#### Features
- Invite multiple students using email-ids or share the unique class code.
- Platform to create unlimited Test/Quizzes for your students using our optimised Auto-grader.
- Reduces Manual work of Teachers, create Test/Quizzes, and get result in Excel.
- Option to make Responses visible after assessment.
- Never miss a Test Deadline using automatic emails to each student.  
- Compiles Test result, with all metrics for further analysis, includes solution reference file too.
- First in class online OMR filler, practice filling OMR for your Board exams.
- Delete Classes or Tests after session or evaluations.
- Easy to operate, High accuracy.
- No compromise on security, uses client and server side credentials hashing of all data. 


## Online Annoucement maker 
- Built using Django models.
- Create unlimited Annoucements.

#### Features
- Notify each student automatically after creating an annoucement.
- Attach any media file upto 10 MB.
- Data of file is available for lifetime.
- Share Meet links in Annoucement for upcoming classes.
- Delete annoucement if required after deadline.
- Easy to maintain Notices/Annoucement, sorted by recent posted date.


## Guide to Use Achilles
#### Install

```
git clone https://github.com/Tewatia5355/Achilles-Engage-21.git
```

#### Secret variables

Before running the application you need to fill 3 variables in ```eng\info.py``` 
```
EMAIL_HOST =  ## enter email host, i.e. 'smtp.gmail.com'
EMAIL_HOST_USER = ## enter email address
EMAIL_HOST_PASSWORD = ## enter passwrod of email address
```

#### Usage

```
cd Achilles-Engage-21 
pip install -r requirements.txt 
python manage.py makemigrations 
python manage.py migrate
python manage.py runserver
```

## Author

👤 **Yash Kumar**

* Resume: [Link](https://bit.ly/ResumeYashKumar)
* Github: [@Tewatia5355](https://github.com/Tewatia5355)
* LinkedIn: [@yash--kumar](https://linkedin.com/in/yash--kumar)

## Show your support

Give a ⭐️ if this project helped you!

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
