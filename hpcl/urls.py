from django.urls import path
from . import views

urlpatterns = [
    path('hpcl-rank-predictor/',views.HPCLrankpredictor,name="hpclrankpredictor"),
    path('hpcl-student-save/',views.HPCLStudentData,name="hpclstudentsave"),
    path('verify-email-otp/',views.verify_email_otp,name="verify_email_otp"),
    path('hpcl-response/', views.HPCLexamrank, name='hpcl_response'),
]