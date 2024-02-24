"""Views for orders."""

from rest_framework import (
    permissions,
    viewsets,
    status,
    views,
    generics,
    mixins
)
from rest_framework.response import Response
from rest_framework.decorators import action

from order.serializers import PaymentSerializer, OrderSerializer

from order.models import Payment, Order, OrderDetail
from user.models import CartItem

from . import payment_utils


class PaymentView(views.APIView):
    """View for payment setup."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # get the total amount of cart
        total_amount = request.data.get('total_amount', 0)

        # process the payment gateway
        payment_status, payment_id, approval_url = payment_utils.make_paypal_payment(
            total_amount)

        # Successful create payment page
        if payment_status:
            payment_data = {
                'transaction_id': payment_id,
                'customer': request.user.id,
                'order_amount': total_amount,
                'payment_method': 'paypal'
            }
            serializer = PaymentSerializer(data=payment_data)
            
            if serializer.is_valid():
                serializer.save()
            else:
                print("serializer errors: ", serializer.errors)
            return Response({'payment_id': payment_id,
                             'approval url': approval_url},
                            status=status.HTTP_200_OK)
        else:
            return Response({'payment_id': payment_id,
                             'error': 'Failed to create PayPal payment.',
                             'approval url': approval_url},
                            status=status.HTTP_400_BAD_REQUEST)


class PaymentReturnView(views.APIView):
    """View after sucess/ failure in payment for creation of order."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # payment_id = request.query_params.get('payment_id', None)
        payment_id = request.data.get('payment_id', None)

        print("payment_id from view: ", payment_id)
        try:
            # Verify payment in paypal
            payment_status = payment_utils.verify_paypal_payment(payment_id)

            print("payment_status: ", payment_status)
            if payment_status:
                # Add to payment
                payment_instance = Payment.objects.filter(
                    customer=request.user,
                    transaction_id=str(payment_id)).first()
                payment_instance.is_successful = True
                payment_instance.save()
                
                # create order and order details and update CartItems
                order_instance = Order.objects.create(
                    customer=request.user,
                    amount=payment_instance.order_amount,
                    transaction_id=payment_id
                )

                cart_items = CartItem.objects.filter(user=request.user)

                for item in cart_items:
                    OrderDetail.objects.create(
                        order=order_instance,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    item.delete()

                serializer = OrderSerializer(order_instance)

                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Error on payment. Try again'},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Error processing payment: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class OrderView(mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                generics.GenericAPIView):
    """View for list and retrieve order."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_id'

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user)
    
    def get(self, request, *args, **kwargs):
        if 'order_id' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)
