from django.contrib import admin
from .models import HPCLStudent,HPCLAnswerKey,HPCLExam,HPCLExpectedCutOff

#ugc exam rank predictor

class HPCLExamAdmin(admin.ModelAdmin):
    list_display = ('id','name','subject','shift','session','year')

admin.site.register(HPCLExam,HPCLExamAdmin)

class HPCLAnswerKeyAdmin(admin.ModelAdmin):
    list_display = ('id','HPCLexam','question_id','answer','paper','positive_marks','negative_marks')

admin.site.register(HPCLAnswerKey,HPCLAnswerKeyAdmin)

class HPCLStudentAdmin(admin.ModelAdmin):
    list_display = ('id','HPCLexam','email','mobile','otp','email_verify','application_no','candidate_name','roll_no','test_date','test_time','url','total_marks','question_attempted','correct_question','category')

admin.site.register(HPCLStudent,HPCLStudentAdmin)

class HPCLExpectedCutOffAdmin(admin.ModelAdmin):
    list_display = ('id','HPCLexam','category','jrf','assistant_professor')

admin.site.register(HPCLExpectedCutOff,HPCLExpectedCutOffAdmin)

