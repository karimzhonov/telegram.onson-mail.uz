from rest_framework.generics import RetrieveAPIView
from .models import Order
from .serializers import OrderSerializer


class OrderByNumberView(RetrieveAPIView):
    lookup_field = 'number'
    lookup_url_kwarg = 'number'
    serializer_class = OrderSerializer
    queryset = Order.objects.all()