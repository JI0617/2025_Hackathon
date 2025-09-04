from django.shortcuts import render

# Create your views here.
# Future calculator-specific views can be added here 

def calculator_view(request):
    """계산기 뷰"""
    return render(request, 'calculator/calculator.html') 