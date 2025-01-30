from django.shortcuts import render
from .models import Order, PART_STATUS

def index(request):
    order = None
    error = False
    try:
        number = request.GET.get('number')
        if number:
            order = Order.objects.get(number=number)
    except Order.DoesNotExist:
        error = True
    context = {
        'order': order,
        'error': error,
        'status': dict(PART_STATUS)[order.part.status] if order else None,
    }
    print(context)
    return render(request, "orders/index.html", context)