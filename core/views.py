from django.shortcuts import render
import random

tips = [
    "Не інвестуй емоційно — завжди май план.",
    "Диверсифікація — ключ до стабільності портфеля.",
    "FOMO веде до збитків. Краще пропустити, ніж втратити.",
    # ... добавим позже
]

def index(request):
    tip = random.choice(tips)
    return render(request, "index.html", {"tip": tip})

def academy(request):
    return render(request, "academy.html")
