from django.shortcuts import render
from .models import HPCLStudent,HPCLAnswerKey,HPCLExam,HPCLExpectedCutOff
import random
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import render,redirect
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags



#ugc net rank predictor views
def extract_table_data(table):
    table_data = {}
    rows = table.find_all('tr')

    for row in rows:
        columns = row.find_all(['td', 'th'])
        if len(columns) == 2:
            key = columns[0].text.strip().replace(':', '')
            value = columns[1].text.strip()
            table_data[key] = value

    # Additional check for 'Chosen Option' in case it's in a different structure
    chosen_option_column = table.find('td', string='Chosen Option :')
    if chosen_option_column:
        table_data['Chosen Option'] = chosen_option_column.find_next('td', class_='bold').text.strip()

    return table_data


def HPCLexamrank(request):
    if request.session.get('rank_predictor_email'):
        try:
            ugcnetstudent = HPCLStudent.objects.get(email = request.session.get('rank_predictor_email'))
            url = ugcnetstudent.url

            try:
                # Make a request to the specified URL
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'lxml')

                response_tables = soup.find_all('table', {'class': 'menu-tbl'})
            except Exception as e:
                print("the problem is ",e)

            AttemptedQuestionPaper1 = 0
            AttemptedQuestionPaper2 = 0
            CorrectQuestionPaper1 = 0
            CorrectQuestionPaper2 = 0
            PositiveMarksinPaper1 = 0
            PositiveMarksinPaper2 = 0
            NegativeMarksinPaper1 = 0
            NegativeMarksinPaper2 = 0

            print("hello hello")

            for response_table in response_tables:
                # Extract data from the table
                table_data = extract_table_data(response_table)

                # Skip saving if the data is empty
                if not any(table_data.values()):
                    continue

                # Print the extracted data for debugging
                #print("Extracted Data:", table_data)

                #get the data of current question
                ugcnetanswerkey = HPCLAnswerKey.objects.get(question_id=str(table_data.get('Question ID ', '')),ugcnetexam = ugcnetstudent.ugcnetexam)

                CurrentQuesAnswer = ugcnetanswerkey.answer.split(" or ")

                #check if question is attempted or not
                if table_data.get('Status ','') == 'Answered':
                    if ugcnetanswerkey.paper == 1:
                        AttemptedQuestionPaper1 += 1

                        if str(table_data.get('Chosen Option', '')) in CurrentQuesAnswer or str(ugcnetanswerkey.answer) == 'MTA':
                            CorrectQuestionPaper1 += 1
                            PositiveMarksinPaper1 += ugcnetanswerkey.positive_marks
                        else:
                            NegativeMarksinPaper1 += ugcnetanswerkey.negative_marks

                    if ugcnetanswerkey.paper == 2:
                        AttemptedQuestionPaper2 = AttemptedQuestionPaper2 + 1

                        if str(table_data.get('Chosen Option', '')) in CurrentQuesAnswer or str(ugcnetanswerkey.answer) == 'MTA':
                            CorrectQuestionPaper2 += 1
                            PositiveMarksinPaper2 += ugcnetanswerkey.positive_marks
                        else:
                            NegativeMarksinPaper2 += ugcnetanswerkey.negative_marks
                else:
                    if str(ugcnetanswerkey.answer) == 'MTA':
                        if ugcnetanswerkey.paper == 1:
                            CorrectQuestionPaper1 += 1
                            PositiveMarksinPaper1 += ugcnetanswerkey.positive_marks
                        
                        if ugcnetanswerkey.paper == 2:   
                            CorrectQuestionPaper2 += 1
                            PositiveMarksinPaper2 += ugcnetanswerkey.positive_marks

                td_element = soup.find('td',text=str(table_data.get('Question ID ', '')))
                
                # Check if the td element is found and navigate up to its parent table
                if td_element:
                    table_to_modify = td_element.find_parent('table', class_='menu-tbl')
                    
                    # Check if the table is found
                    if table_to_modify:
                        #print("Question ID = ",str(table_data.get('Question ID ', '')),"   Choice Option = ",str(table_data.get('Chosen Option', '')),"     Correct Answer = ",ugcnetanswerkey.answer)
                        if ugcnetanswerkey.answer == str(table_data.get('Chosen Option', '')) or str(ugcnetanswerkey.answer) == 'MTA':
                            # Change the border color of the table
                            table_to_modify['style'] = 'border: 2px solid green;'

                            # Create a new tr element with the desired content
                            new_tr = soup.new_tag('tr')


                            # Create new td element with text content, align="right" attribute, and style attributes
                            td_marks = soup.new_tag('td', align='right', style='font-size: 16px;font-weight:bold; color: green;')
                            td_marks.append('Your Marks:')
                            
                            # Create new td element with text content, class="bold" attribute, and style attributes
                            td_plus_two = soup.new_tag('td', class_='bold', style='font-size: 16px; font-weight:bold; color: green;')

                            td_plus_two.append('+'+str(ugcnetanswerkey.positive_marks))
                        else:
                            # Change the border color of the table
                            table_to_modify['style'] = 'border: 2px solid red;'

                            # Create a new tr element with the desired content
                            new_tr = soup.new_tag('tr')

                        
                            # Create new td element with text content, align="right" attribute, and style attributes
                            td_marks = soup.new_tag('td', align='right', style='font-size: 16px;font-weight:bold; color: red;')
                            td_marks.append('Your Marks:')
                            
                            # Create new td element with text content, class="bold" attribute, and style attributes
                            td_plus_two = soup.new_tag('td', class_='bold', style='font-size: 16px; font-weight:bold; color: red;')

                            td_plus_two.append('-'+str(ugcnetanswerkey.negative_marks))


                        # Append the new td elements to the new tr element
                        new_tr.append(td_marks)
                        new_tr.append(td_plus_two)

                        # Find the parent tr of the td element
                        td_element = soup.find('td',class_="bold",text=str(table_data.get('Question ID ', '')))
                        parent_tr = td_element.find_parent('tr')

                        # Check if the parent tr is found
                        if parent_tr:
                            # Insert the new tr element after the parent tr
                            parent_tr.insert_after(new_tr)


            # Update image URLs to absolute URLs
            for img_tag in soup.find_all('img'):
                img_src = img_tag.get('src')
                if img_src and not img_src.startswith(('http://', 'https://')):
                    img_tag['src'] = urljoin(url, img_src)
            
            Attempted = AttemptedQuestionPaper1 + AttemptedQuestionPaper2
            TotalMarks = (PositiveMarksinPaper1 + PositiveMarksinPaper2) - (NegativeMarksinPaper1 + NegativeMarksinPaper2)
            TotalCorrect = CorrectQuestionPaper1 + CorrectQuestionPaper2

            #if same data then not save other change 
            if ugcnetstudent.total_marks != TotalMarks or ugcnetstudent.question_attempted != Attempted or ugcnetstudent.correct_question != TotalCorrect:
                ugcnetstudent.total_marks = TotalMarks
                ugcnetstudent.question_attempted = Attempted
                ugcnetstudent.correct_question = TotalCorrect
                ugcnetstudent.save()

            
            RankInStudentCategory = HPCLStudent.objects.filter(category=ugcnetstudent.category, total_marks__gt=TotalMarks).values('roll_no').distinct().count()
            Rank = HPCLStudent.objects.filter(total_marks__gt=TotalMarks).values('roll_no').distinct().count()

            TotalStudent = HPCLStudent.objects.filter(ugcnetexam = ugcnetstudent.ugcnetexam).values('roll_no').distinct().count()
            TotalStudentCategory = HPCLStudent.objects.filter(category=ugcnetstudent.category,ugcnetexam = ugcnetstudent.ugcnetexam).values('roll_no').distinct().count()
            
            if ugcnetstudent.category == 'UNRESERVED' or ugcnetstudent.category == 'EWS' or ugcnetstudent.category == 'OBC(NCL)' or ugcnetstudent.category == 'SC':
                ExpectedCutoff = HPCLExpectedCutOff.objects.filter(Q(category='UNRESERVED') | Q(category='OBC(NCL)') | Q(category='EWS') | Q(category='SC') ,ugcnetexam=ugcnetstudent.ugcnetexam)
            else:
                ExpectedCutoff = HPCLExpectedCutOff.objects.filter(Q(category='UNRESERVED') | Q(category='OBC(NCL)') | Q(category='EWS') | Q(category=str(ugcnetstudent.category)) ,ugcnetexam=ugcnetstudent.ugcnetexam)
            
            #count total question in paper 1 
            TotalQuestionInPaper1 = HPCLAnswerKey.objects.filter(ugcnetexam=ugcnetstudent.ugcnetexam,paper = 1).count()

            #count total question in paper 2
            TotalQuestionInPaper2 = HPCLAnswerKey.objects.filter(ugcnetexam=ugcnetstudent.ugcnetexam, paper = 2).count()

            #user category expected cutoff for JRF
            StudentCategoryCutoff = HPCLExpectedCutOff.objects.get(category=str(ugcnetstudent.category),ugcnetexam=ugcnetstudent.ugcnetexam)

            data = {
                    'AttemptedQuestionPaper1': AttemptedQuestionPaper1,
                    'AttemptedQuestionPaper2' : AttemptedQuestionPaper2,
                    'TotalQuestionAttempted' : Attempted,
                    'CorrectQuestionPaper1' : CorrectQuestionPaper1,
                    'CorrectQuestionPaper2' : CorrectQuestionPaper2,
                    'TotalCorrectQuestion': TotalCorrect,
                    'IncorrectQuestionPaper1' : AttemptedQuestionPaper1 - CorrectQuestionPaper1,
                    'IncorrectQuestionPaper2' : AttemptedQuestionPaper2 - CorrectQuestionPaper2,
                    'TotalMarksPaper1' : PositiveMarksinPaper1 - NegativeMarksinPaper1,
                    'TotalMarksPaper2':PositiveMarksinPaper2 - NegativeMarksinPaper2,
                    'PositiveMarksinPaper1' :PositiveMarksinPaper1,
                    'PositiveMarksinPaper2':PositiveMarksinPaper2,
                    'NegativeMarksinPaper1':NegativeMarksinPaper1,
                    'NegativeMarksinPaper2':NegativeMarksinPaper2,
                    'TotalPositiveMarks':PositiveMarksinPaper1 + PositiveMarksinPaper2,
                    'TotalNegativeMarks':NegativeMarksinPaper1 + NegativeMarksinPaper2,
                    'TotalQuestionInPaper1':TotalQuestionInPaper1,
                    'TotalQuestionInPaper2':TotalQuestionInPaper2,
                    'TotalQuestionInPaper' : TotalQuestionInPaper1 + TotalQuestionInPaper2,
                    'TotalMarks' : TotalMarks,
                    'ExpectedCutoff':ExpectedCutoff,
                    'RankInStudentCategory':RankInStudentCategory + 1,
                    'Rank':Rank + 1,
                    'TotalStudent':TotalStudent,
                    'TotalStudentCategory' : TotalStudentCategory,
                    'StudentCategory':ugcnetstudent.category,
                    'ExpectedNetCutOff': StudentCategoryCutoff.assistant_professor,
                    'ExpectedJrfCutoff' : StudentCategoryCutoff.jrf,
            }


            # Render the modified HTML content
            modified_html = str(soup)
            print("success now")
            return render(request, 'hpcl-response.html', {'data':data,'modified_html': modified_html,})
        except requests.RequestException as e:
            print("ugc net response error = ",e)
            return render(request, 'hpcl_rank_predictor.html', {'error_message': ""})

        except Exception as e:
            return render(request, 'hpcl_rank_predictor.html', {'error_message': f"Error: {str(e)}"})
    else:
        return render(request,'hpcl_rank_predictor.html',{'context':''})


def HPCLrankpredictor(request):
    #index page of ugc net rank predictor
    '''for i in range(87827024938,87827025091):
        currentexam = UgcNetExam.objects.get(name='UGC NET December 2023')
        answer = ['1','2','3','4']
        cupaper = 0
        if i <= 87827024988:
            cupaper = 1
        else:
            cupaper = 2
        ugcnetanswerkey = UgcNetAnswerKey(ugcnetexam = currentexam,question_id = i,answer = random.choice(answer),paper = cupaper,positive_marks = 2,negative_marks = 0)
        ugcnetanswerkey.save()'''
    return render(request,'hpcl_rank_predictor.html',{'context':''})


def HPCLStudentData(request):
    try:
        request.session.flush()
        if request.method == 'POST':
            # Extract data from the POST request
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            category = request.POST.get('category')
            url = request.POST.get('url')
            examname = request.POST.get('examname')
            subject = request.POST.get('subject')
            shift = request.POST.get('shift')

            # Perform additional backend validations if needed

            # Send email verification OTP
            otp = generate_otp()
            #send_otp_email(email, otp)
            
            try:
                HPCLExam.objects.get(name=examname, subject=subject, shift=shift)
                
                #get the data from url
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()


                    # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract data for UgcNetStudent
                student_table = soup.find('table', {'border': '1', 'cellpadding': '1', 'cellspacing': '1', 'style': 'width:500px'})
                rows = student_table.find_all('tr')

                ugc_net_student_data = {}


                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) == 2:
                        key = columns[0].text.strip()
                        value = columns[1].text.strip()
                        ugc_net_student_data[key] = value
                    
                    
                #getexam id 
                currentexam = HPCLExam.objects.get(name=examname, subject=subject, shift=shift)

                #check if student already registered
                try:
                    ugcnetstudentregisted = HPCLStudent.objects.get(email = email)
                    ugcnetstudentregisted.url = url
                    ugcnetstudentregisted.save()
                    #return JsonResponse({'status':'success','email_already_verified':'0'})
                except:
                    #store data in database if user check rank first time
                    # Create UgcNetStudent instance and save to the database
                    ugc_net_student = HPCLStudent.objects.create(
                        ugcnetexam = currentexam,
                        email = email,
                        mobile = mobile,
                        category = category,
                        url = url,
                        otp = otp,
                        email_verify = 0,
                        application_no=ugc_net_student_data.get('Application No', ''),
                        candidate_name=ugc_net_student_data.get('Candidate Name', ''),
                        roll_no=ugc_net_student_data.get('Roll No', ''),
                        test_date=ugc_net_student_data.get('Test Date', ''),
                        test_time=ugc_net_student_data.get('Test Time', ''),
                        total_marks = 0,
                        question_attempted = 0,
                        correct_question = 0
                        )
            except Exception as e:
                print("error occured",e)
                return JsonResponse({'status': 'error'})


            #store email in session for student response view
            request.session['rank_predictor_email'] = email

            #store email in session for student response view
            request.session['rank_predictor_url'] = url

            # Store the OTP in session for verification
            request.session['email_verification_otp'] = otp

            #print("ugc net rank predictor otp is = ",otp)

            send_email('Email Verification for Turing Code UGC NET/JRF Rank Predictor',email,otp,'HPCL')

            # Return success response
            return JsonResponse({'status': 'success'})
        else:
            print("error")
            return JsonResponse({'status': 'error'})
    except Exception as e:
        print("ugc net form submit error is ",e)

def generate_otp():
    return str(random.randint(100000, 999999))


def verify_email_otp(request):
    if request.method == 'POST':
        user_entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('email_verification_otp')
        print("user_entered_otp = ",user_entered_otp)
        print('stored_otp',stored_otp)
        if user_entered_otp == stored_otp:
            ugcnetstudentregisted = HPCLStudent.objects.get(email = request.session.get('rank_predictor_email'))
            ugcnetstudentregisted.email_verify = 1
            ugcnetstudentregisted.save()
            # Email verification successful, redirect to another page
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'error': 'Invalid OTP'})
    else:
        return JsonResponse({'status': 'error', 'error': 'Something went wrong please try again.'})
    


def send_email(Subject,StudentEmail,Otp,EmailType):
    
    try:
        if EmailType == 'HPCL':
            Student = HPCLStudent.objects.get(email = StudentEmail)
            # Assuming you have a user or username to personalize the email
            StudentName = Student.candidate_name

            html_message = render_to_string('email.html', {'StudentName': StudentName,'otp':Otp,'email_type':EmailType})
        
        # Create a plain text version of the HTML content
        plain_message = strip_tags(html_message)
        from_email = 'Turing Code'

        # Create the EmailMultiAlternatives object
        email = EmailMultiAlternatives(
            subject=str(Subject),  # Email subject
            body=plain_message,  # Plain text message
            from_email=from_email,  # Sender's email address with friendly name
            to=[StudentEmail],  # List of recipient email addresses
        )

        # Attach the HTML version of the email
        email.attach_alternative(html_message, 'text/html')

        # Send the email
        try:
            email.send()
            #if email send successfully then return true other return false
            print("email send success")
            return True
        except Exception as e:
            return False
    except Exception as e:
        print("email not send because ",e)
        return False