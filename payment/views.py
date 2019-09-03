from django.shortcuts import render,HttpResponse
from first import settings
import braintree
from login.models import infor
from datetime import date,timedelta
from django.contrib.auth.decorators import login_required

@login_required
def checkout_page(request):
    template = 'checkout.html'
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY,
    )
 
    try:
        braintree_client_token = braintree.ClientToken.generate({ "customer_id": user.id })
    except:
        braintree_client_token = braintree.ClientToken.generate({})

    context = {'braintree_client_token': braintree_client_token}
    print ('a')
    return render(request, template, context)

@login_required
def payment(request):
    print ('a')
    nonce_from_the_client = request.POST['paymentMethodNonce']
    customer_kwargs = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email
    }
    customer_create = braintree.Customer.create(customer_kwargs)
    customer_id = customer_create.customer.id
    result = braintree.Transaction.sale({
        "amount": get_price(request),
        "payment_method_nonce": nonce_from_the_client,
        "options": {
            "submit_for_settlement": True
        }
    })
    objs = infor.objects.all()
    for i in objs:
        if str(i.price) == get_price(request):
            i.started = True
            i.start = date.today()
            if i.price == 29.99:
                b = timedelta(days = 30)
                i.end = i.start + b
                i.save()
            if i.price == 299.99:
                b = timedelta(days = 365)
                i.end = i.start + b
                i.save()
    return HttpResponse("Done")

def get_price(request):
    objs = infor.objects.all()
    for i in objs:
        if i.user == request.user:
            return (str(i.price))