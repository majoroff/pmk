# coding: utf-8

import datetime
from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from .models import Product, Order
from .forms import OrderForm


def index(request):
	if request.method == "POST":
		order = Order()
		items = dict(request.POST)
		items.pop('csrfmiddlewaretoken')
		ordered_items = { int(k): int(v[0]) for k, v in items.items() if v[0] }
		order.generate_order_text(ordered_items)
		order.save()

		return HttpResponseRedirect(reverse('order-view', kwargs={'order_id': order.id}))	
	else:
		products_raw = Product.objects.filter(available=True).order_by('-category')
		products = defaultdict(list)

		for p in products_raw:
			products[p.get_category_display()].append(p)
		return render(request, 'index.html', {'products': dict(products)})


def order(request, order_id=0):
	order = get_object_or_404(Order, pk=order_id)
	if not order.completed:
		order_form = OrderForm(request.POST or None, instance=order)
		if order_form.is_valid():
			order_form.save()
			order.completed = True
			order.save()
			messages.success(request, 'Ваш заказ успешно оформлен')
			return HttpResponseRedirect('/')				


		return render(request, 'order.html', {"order_form": order_form })
	else:
		raise Http404
	

def error_404(request):
	return render(request, '404.html')
