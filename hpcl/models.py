from django.db import models

ExamShift = (
    ('Morning','Morning'),
    ('Afternoon','Afternoon'),
)

ExamSession = (
    ('June','June'),
    ('December','December'),
)

ExamPaper = (
    (1,1),
    (2,2),
)

QuestionType = (
    ('MCQ','MCQ'),
    ('MSQ','MSQ'),
    ('NAT','NAT')
)

Subject = (
    ('Chemical Engineering','Chemical Engineering'),
    ('Mechanical Engineering','Mechanical Engineering'),
    ('Civil Engineering','Civil Engineering'),
    ('Electrical Engineering','Electrical Engineering'),
    ('Instrumentation Engineering','Instrumentation Engineering'),
)

TotalShift = (
    (1,1),
    (2,2)
)

Marks = (
    (1,1),
    (2,2)
)

NegativeMarks = (
    (0,0),
    (0.33,0.33),
    (0.33,0.33)
)

Category = (
    ('GENERAL','GENERAL'),
    ('OBC(NCL)','OBC(NCL)'),
    ('EWS','EWS'),
    ('SC','SC'),
    ('ST','ST'),
    ('PWD','PWD'),
)

class HPCLExam(models.Model):
    name = models.CharField(null=False,max_length=60)
    subject = models.CharField(null=False,max_length=60)
    shift = models.CharField(choices=ExamShift,null=False,max_length=50)
    session = models.CharField(choices=ExamSession,null=False,max_length=50)
    year = models.IntegerField(null=False)



class HPCLAnswerKey(models.Model):
    HPCLexam = models.ForeignKey(HPCLExam,on_delete=models.CASCADE,null=False)
    question_id = models.CharField(null=False,max_length=30)
    answer = models.CharField(max_length=10,null=False)
    paper = models.IntegerField(null=False,choices=ExamPaper)
    positive_marks = models.IntegerField(null=False,default=0)
    negative_marks = models.IntegerField(null=False,default=0)

class HPCLStudent(models.Model):
    HPCLexam = models.ForeignKey(HPCLExam,on_delete=models.CASCADE,null=False)
    email = models.EmailField(null=False,default="admin@margdarshanprep.com")
    mobile = models.IntegerField(null=False)
    otp = models.IntegerField(null=False)
    email_verify = models.BooleanField(default=0)
    application_no = models.CharField(max_length=50)
    candidate_name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=50)
    test_date = models.CharField(max_length=50)
    test_time = models.CharField(max_length=50)
    url = models.TextField()
    total_marks = models.IntegerField(default=0)
    question_attempted = models.IntegerField(default=0)
    correct_question = models.IntegerField(default=0)
    category = models.CharField(max_length=20,null=False)

class HPCLExpectedCutOff(models.Model):
    HPCLexam = models.ForeignKey(HPCLExam,on_delete=models.CASCADE,null=False)
    category = models.CharField(null=False,max_length=50)
    jrf = models.CharField(null=False,max_length=15)
    assistant_professor = models.CharField(null=False,max_length=15)

