from django.contrib.auth import authenticate, login

from django.contrib.auth.views import LoginView

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from reportlab.lib.colors import HexColor

from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Quiz,Question,Result

from datetime import date

from django.core.paginator import Paginator

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():

         user = form.save()

        login(request, user)

        return redirect('dashboard')

    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})



class CustomLoginView(LoginView):

    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)

@login_required
def dashboard(request):

    query = request.GET.get('q')

    quizzes = Quiz.objects.all()

    if query:
      quizzes = quizzes.filter(
        title__icontains=query
    )

    total_quizzes = quizzes.count()

    results = Result.objects.filter(student=request.user).order_by('-submitted_at')

    for result in results:
       result.percentage = round(
         (result.score / result.total_questions) * 100
    )

    completed = results.count()

    if completed > 0:

        total_percentage = 0

        for result in results:
            percentage = (result.score / result.total_questions) * 100
            total_percentage += percentage

        average = total_percentage / completed

    else:
        average = 0

    # 👇 Ye hamesha if/else ke bahar rahega
    highest_score = 0
    latest_quiz = "No Quiz Attempted"

    if results.exists():
        highest_score = max(result.score for result in results)
        latest_quiz = results.first().quiz.title

    context = {
        'total_quizzes': total_quizzes,
        'completed': completed,
        'average': f"{round(average,1)}%",
        'highest_score': highest_score,
        'latest_quiz': latest_quiz,
        'quizzes': quizzes,
        'results': results,
    }

    return render(request, 'dashboard.html', context)

@login_required
def quiz_list(request):

    query = request.GET.get('q')

    quizzes = Quiz.objects.all()

    if query:
        quizzes = quizzes.filter(
            title__icontains=query
        )

    context = {
    'quizzes': quizzes,
    'query': query,
    'quiz_count': quizzes.count(),
}

    return render(request, 'quiz_list.html', context)

@login_required
def start_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)

    if request.method == "POST":

        score = 0

        for question in questions:

            selected_option = request.POST.get(f"q{question.id}")

            if selected_option:

                if int(selected_option) == question.correct_option:
                    score += question.marks

        Result.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            total_questions=questions.count()
        )

        percentage = (score / questions.count()) * 100

        if percentage >= 80:
            message = "🏆 Excellent Performance!"
            alert_class = "success"

        elif percentage >= 60:
            message = "👍 Good Performance!"
            alert_class = "info"

        else:
            message = "📚 Needs Improvement"
            alert_class = "warning"

        return render(request, 'result.html', {
            'quiz': quiz,
            'score': score,
            'total': questions.count(),
            'percentage': round(percentage),
            'message': message,
            'alert_class': alert_class,
        })

    return render(request, 'start_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })



@login_required
def results(request):

    results = Result.objects.filter(
        student=request.user
    ).order_by('-submitted_at')

    all_results = results

    paginator = Paginator(results, 10)

    page_number = request.GET.get('page')

    results = paginator.get_page(page_number)

    for result in results:
     
     if result.total_questions > 0:
        result.percentage = round(
            (result.score / result.total_questions) * 100
        )
    else:
        result.percentage = 0

    total_attempts = paginator.count

    highest_score = 0
    average_percentage = 0

    if total_attempts > 0:

        if total_attempts > 0:

         percentages = [
        (r.score / r.total_questions) * 100
        for r in all_results
        if r.total_questions > 0
    ]

    if percentages:
        highest_score = max(percentages)
        average_percentage = sum(percentages) / len(percentages)

        context = {
        'results': results,
        'total_attempts': total_attempts,
        'highest_score': round(highest_score),
        'average_percentage': round(average_percentage)
    }

    return render(request, 'results.html', context)




@login_required
def delete_result(request, id):

    result = Result.objects.get(
        id=id,
        student=request.user
    )

    result.delete()

    return redirect('results')



@login_required
def result_detail(request, id):

    result = Result.objects.get(
        id=id,
        student=request.user
    )

    percentage = round(
        (result.score / result.total_questions) * 100
        
    )

    correct_answers = result.score
    wrong_answers = result.total_questions - result.score

    context = {
        'result': result,
        'percentage': percentage,
        'correct_answers': correct_answers,
        'wrong_answers': wrong_answers,
    }

    return render(
        request,
        'result_detail.html',
        context
    )


@login_required
def download_certificate(request):

    latest_result = Result.objects.filter(
        student=request.user
    ).order_by('-submitted_at').first()

    if not latest_result:
        return HttpResponse("No quiz attempted yet.")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'

    p = canvas.Canvas(response, pagesize=(11*inch, 8.5*inch))

    # Background Border
    p.setStrokeColor(HexColor("#2563eb"))
    p.setLineWidth(4)
    p.rect(25, 25, 742, 560)

    # Inner Border
    p.setStrokeColor(HexColor("#93c5fd"))
    p.setLineWidth(1.5)
    p.rect(40, 40, 712, 530)

    # Smart Quiz Title
    p.setFont("Helvetica-Bold", 18)
    p.setFillColor(HexColor("#2563eb"))
    p.drawCentredString(396, 545, "SMART QUIZ SYSTEM")

    # Certificate Heading
    p.setFillColor(HexColor("#111827"))
    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(396, 500, "CERTIFICATE OF ACHIEVEMENT")

        # Subtitle
    p.setFont("Helvetica", 16)
    p.setFillColor(HexColor("#6b7280"))
    p.drawCentredString(
        396,
        440,
        "This certificate is proudly presented to"
    )

    # Student Name
    p.setFont("Helvetica-Bold", 34)
    p.setFillColor(HexColor("#2563eb"))
    p.drawCentredString(
        396,
        395,
        request.user.username.title()
    )

    # Certificate Text
    p.setFont("Helvetica", 16)
    p.setFillColor(HexColor("#374151"))
    p.drawCentredString(
        396,
        355,
        "for successfully completing the online assessment"
    )

    # Quiz Name
    p.setFont("Helvetica-Bold", 18)
    p.setFillColor(HexColor("#111827"))
    p.drawCentredString(
        396,
        305,
        f"Quiz Name : {latest_result.quiz.title}"
    )

    percentage = (
        latest_result.score /
        latest_result.total_questions
    ) * 100

    # Score
    p.drawCentredString(
        396,
        275,
        f"Score : {latest_result.score}/{latest_result.total_questions}"
    )

    # Percentage
    p.drawCentredString(
        396,
        245,
        f"Percentage : {round(percentage)}%"
    )


    # Date
    p.setFont("Helvetica", 13)
    p.setFillColor(HexColor("#374151"))
    p.drawString(80, 90, f"Date: {date.today().strftime('%d-%m-%Y')}")

    # Signature Line
    p.line(520, 90, 720, 90)

    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(630, 70, "Authorized Signature")

    # Footer
    p.setFont("Helvetica", 11)
    p.setFillColor(HexColor("#6b7280"))
    p.drawCentredString(
    396,
    55,
    "Smart Quiz System | Certificate of Achievement"
)

    p.save()

    return response


@login_required
def profile(request):

    results = Result.objects.filter(student=request.user)

    total_attempts = results.count()

    highest_score = 0
    average_percentage = 0

    if total_attempts > 0:

        highest_score = round(
            max(
                (r.score / r.total_questions) * 100
                for r in results
            )
        )

        average_percentage = round(
            sum(
                (r.score / r.total_questions) * 100
                for r in results
            ) / total_attempts
        )

    context = {
        'total_attempts': total_attempts,
        'highest_score': highest_score,
        'average_percentage': average_percentage,
        'certificates': total_attempts,
    }

    return render(request, 'profile.html', context)