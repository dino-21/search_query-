from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponseNotAllowed, JsonResponse
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
import requests  # 외부 요청을 위한 라이브러리


def index(request):
    question_list = Question.objects.order_by('-create_date')
    context = {'question_list': question_list}
    return render(request, 'pybo2/question_list.html', context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'pybo2/question_detail.html', context)


def answer_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect('pybo2:detail', question_id=question.id)
    else:
        return HttpResponseNotAllowed('Only POST is possible.')
    context = {'question': question, 'form': form}
    return render(request, 'pybo2/question_detail.html', context)


def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.create_date = timezone.now()
            question.save()
            return redirect('pybo2:index')
    else:
        form = QuestionForm()
    context = {'form': form}
    return render(request, 'pybo2/question_form.html', {'form': form})


def question_modify(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.modify_date = timezone.now()  # 수정일시 저장
            question.save()
            return redirect('pybo2:detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)
    context = {'form': form}
    return render(request, 'pybo2/question_form.html', context)


def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.delete()
    return redirect('pybo2:index')


def answer_modify(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.modify_date = timezone.now()
            answer.save()
            return redirect('pybo2:detail', question_id=answer.question.id)
    else:
        form = AnswerForm(instance=answer)
    context = {'answer': answer, 'form': form}
    return render(request, 'pybo2/answer_form.html', context)



def answer_delete(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    answer.delete()
    return redirect('pybo2:detail', question_id=answer.question.id)



def get_json_data(request):
    query = request.GET.get("search", "").strip()  # 검색어를 "search"로 받음

    # 외부 URL에서 JSON 데이터를 가져옴
    url = "https://dino-21.github.io/2025_0107/json/melon-20230906.json"
    try:
        # 외부 URL에서 JSON 데이터를 가져옴
        response = requests.get(url)
        response.raise_for_status()  # 실패하면 예외 발생

        # JSON 데이터를 딕셔너리 형태로 변환
        data = response.json()

        # 검색어가 있을 경우 필터링
        if query:
            data = [
                song for song in data
                if query.lower() in song['곡명'].lower() or query.lower() in song['가수'].lower()
            ]

        # 데이터를 템플릿에 전달
        return render(request, "pybo2/json.html", {"song_list": data, "query": query})

    except requests.exceptions.RequestException:
        # 요청이 실패했을 때 에러 메시지 표시
        error_message = "데이터를 가져오는 데 실패했습니다. 나중에 다시 시도해주세요."
        return render(request, "pybo2/json.html", {"error": error_message})
