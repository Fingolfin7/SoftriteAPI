from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.urls import reverse
from .forms import *
from .scrapers.rbz_rate import download_rbz_pdf_binary, get_rbz_rate
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import logging

logger = logging.getLogger(__name__)
sndLogger = logging.getLogger('apscheduler')


def update_rbz_rate():
    sndLogger.info("Called update_rbz_rate")
    # if the rate for today is not in the database, then download the pdf and get the rate,
    # else get the rate from the database
    if not InterbankUSDRate.objects.filter(date=datetime.today()).exists():
        logger.info("Getting latest RBZ pdf file...")
        try:
            latest_pdf_binary = download_rbz_pdf_binary()
            if latest_pdf_binary:
                logger.info("Getting RBZ ZWL-USD rate...")
                try:
                    mid_rate = get_rbz_rate(latest_pdf_binary)
                    if mid_rate:
                        logger.info("RBZ ZWL-USD rate: {} on {}".format(mid_rate['rate'], mid_rate['date']))
                        # check if the rate for this date is already in the database
                        date = datetime.strptime(mid_rate['date'], '%m-%d-%Y')
                        if not InterbankUSDRate.objects.filter(date=date).exists():
                            InterbankUSDRate.objects.create(date=date, rate=mid_rate['rate'])
                        else:
                            logger.info("Rate for {} date already exists".format(date))
                except Exception as e:
                    logger.error("Error getting rate. Error: {}".format(e))
        except Exception as e:
            logger.error("Download error. Error: {}".format(e))


# api endpoint to get the most recent rate.
# We can use an external cron scheduler to call this endpoint at least once every day
def get_latest_rate(request):
    update_rbz_rate()
    rate_obj = InterbankUSDRate.objects.order_by('-date').first()

    return JsonResponse(
        {
            'rate': rate_obj.rate,
            'date': rate_obj.date.strftime('%m-%d-%Y')
        }
    )


def get_rate_on(request, **kwargs):
    try:
        date = datetime.strptime(str(kwargs['date']), '%m-%d-%Y')
        rate_obj = InterbankUSDRate.objects.filter(date=date).get()

        return JsonResponse(
            {
                'rate': rate_obj.rate,
                'date': rate_obj.date.strftime('%m-%d-%Y')
            }
        )
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No rate found for this date")


# api endpoint to get all the rates so far
def get_all_rates(request):
    rates = InterbankUSDRate.objects.all().order_by('-date')
    rates_list = []

    for rate in rates:
        rates_list.append({
            'rate': rate.rate,
            'date': rate.date.strftime('%m-%d-%Y')
        })

    if not rates_list:
        # return a 404 if no rates are found
        return HttpResponseNotFound("No rates found")

    return JsonResponse(rates_list, safe=False)


# api endpoint to get all the necs and their ids
def get_necs(request):
    necs = NEC.objects.all()
    necs_list = []

    for nec in necs:
        necs_list.append({
            'id': nec.pk,
            'name': nec.name
        })

    if not necs_list:
        # return a 404 if no necs are found
        return HttpResponseNotFound("No NECs found")

    return JsonResponse(necs_list, safe=False)


# api endpoint to get the most recent rate for a given nec
def get_latest_nec_rate(request, **kwargs):
    try:
        nec = NEC.objects.filter(pk=kwargs['pk']).get()
        rate_obj = nec.rates_set.order_by('-date').first()  # ordered by date descending (latest first)

        if not rate_obj:
            # return a 404 if no rate is found
            return HttpResponse(status=404, reason="No rate found for this NEC")

        if not nec:
            # return a 404 if no nec is found
            return HttpResponse(status=404, reason="No NEC found")

        return JsonResponse(
            {
                'nec': nec.name,
                'rate': rate_obj.rate,
                'date': rate_obj.date.strftime('%m-%d-%Y')
            }
        )
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No NEC found")


def get_all_nec_rates(request, **kwargs):
    try:
        nec = NEC.objects.filter(pk=kwargs['pk']).get()
        rates = nec.rates_set.all().order_by('-date')
        rates_list = []

        for rate in rates:
            rates_list.append({
                'nec': nec.name,
                'rate': rate.rate,
                'date': rate.date.strftime('%m-%d-%Y')
            })

        if not rates_list:
            # return a 404 if no rates are found
            return HttpResponseNotFound("No rates found")

        return JsonResponse(rates_list, safe=False)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No NEC found")


def get_nec_rate_on(request, **kwargs):
    try:
        nec = NEC.objects.filter(pk=kwargs['pk']).get()
        date = datetime.strptime(str(kwargs['date']), '%m-%d-%Y')
        rate_obj = nec.rates_set.filter(date=date).get()

        return JsonResponse(
            {
                'nec': nec.name,
                'rate': rate_obj.rate,
                'date': rate_obj.date.strftime('%m-%d-%Y')
            }
        )
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No rate found for this date")


def get_all_nec_grades(request, **kwargs):
    try:
        nec = NEC.objects.filter(pk=kwargs['pk']).get()
        grades = nec.grades_set.all()
        grades_list = []

        for grade in grades:
            grades_list.append({
                'nec': nec.name,
                'grade': grade.grade,
                'usd_min': grade.usd_minimum,
            })

        if not grades_list:
            # return a 404 if no grades are found
            return HttpResponseNotFound("No grades found")

        return JsonResponse(grades_list, safe=False)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No NEC found")


def get_nec_grade(request, **kwargs):
    try:
        nec = NEC.objects.filter(pk=kwargs['pk']).get()
        grade = nec.grades_set.filter(grade=kwargs['grade']).get()

        return JsonResponse(
            {
                'nec': nec.name,
                'grade': grade.grade,
                'usd_min': grade.usd_minimum,
            }
        )
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No grade found")


@login_required
def home(request):
    # update_rbz_rate()
    necs = NEC.objects.all()
    interbank_instance = InterbankUSDRate.objects.order_by('-date').first()  # ordered by date descending (latest first)

    context = {
        'title': 'Admin',
        'necs': necs,
        'interbank_rate': interbank_instance,
    }
    return render(request, 'payroll_info/admin.html', context)


# list view for all the interbank rates
class InterbankListView(LoginRequiredMixin, ListView):
    model = InterbankUSDRate
    template_name = 'payroll_info/interbank_list.html'
    context_object_name = 'inter_rates'
    ordering = ['-date']  # ordered by date descending (latest first)
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Interbank Rates'
        context['search_form'] = InterbankSearchForm(
            initial={
                'start_date': self.request.GET.get('start_date'),
                'end_date': self.request.GET.get('end_date')
            }
        )
        # context['search_results'] = True \
        #     if self.request.GET.get('start_date') or self.request.GET.get('end_date') \
        #     else False

        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date and end_date and start_date <= end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])  # filter by date range.
        # __range is a django filter
        elif start_date and not end_date:
            queryset = queryset.filter(date__gte=start_date)  # gte is greater than or equal to
        elif end_date and not start_date:
            queryset = queryset.filter(date__lte=end_date)  # lte is less than or equal to
        else:
            queryset = queryset.all()  # return all the queryset if no date is specified

        return queryset


class InterbankCreateView(LoginRequiredMixin, CreateView):
    model = InterbankUSDRate
    template_name = 'payroll_info/interbank_page.html'
    form_class = InterbankUSDRateForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New Interbank Rate'
        return context


class InterbankUpdateView(LoginRequiredMixin, UpdateView):
    model = InterbankUSDRate
    template_name = 'payroll_info/interbank_page.html'
    form_class = InterbankUSDRateForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Interbank Rate'
        return context


class InterbankDeleteView(LoginRequiredMixin, DeleteView):
    model = InterbankUSDRate
    template_name = 'payroll_info/interbank_delete.html'
    context_object_name = 'rate'
    success_url = '/'

    def get_object(self, queryset=None):
        obj = super().get_object()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Interbank Rate'
        return context


class NecCreateView(LoginRequiredMixin, CreateView):
    model = NEC
    template_name = 'payroll_info/nec_page.html'
    form_class = NecForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New NEC'
        return context


class NecUpdateView(LoginRequiredMixin, UpdateView):
    model = NEC
    template_name = 'payroll_info/nec_page.html'
    form_class = NecForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update NEC'
        return context


class NecDeleteView(LoginRequiredMixin, DeleteView):
    model = NEC
    template_name = 'payroll_info/nec_delete.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete NEC'
        context['nec'] = NEC.objects.get(id=self.kwargs['pk'])
        return context


class NecRatesListView(LoginRequiredMixin, ListView):
    model = Rates
    template_name = 'payroll_info/nec_rates_list.html'
    context_object_name = 'rates'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        return NEC.objects.get(id=self.kwargs['pk']).rates_set.order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'NEC Rates'
        context['nec'] = NEC.objects.get(id=self.kwargs['pk'])
        return context


class NecRatesCreateView(LoginRequiredMixin, CreateView):
    model = Rates
    form_class = NecRatesForm
    template_name = 'payroll_info/nec_rate_create.html'

    # post method to set the parent to the nec passed in the url
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        nec = get_object_or_404(NEC, pk=kwargs['pk'])
        print("nec id: ", nec.id)
        if form.is_valid():
            form.instance.nec = nec
            form.save()
            return redirect('nec-rates', pk=nec.pk)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Rate'
        return context


class NecRatesUpdateView(LoginRequiredMixin, UpdateView):
    model = Rates
    form_class = NecRatesForm
    template_name = 'payroll_info/nec_rate_update.html'

    # post method to set the parent to the nec passed in the url
    def post(self, request, *args, **kwargs):
        nec = get_object_or_404(NEC, pk=kwargs['pk'])
        rate = nec.rates_set.get(id=self.kwargs['rate_pk'])
        form = self.form_class(request.POST, instance=rate)
        if form.is_valid():
            form.save()
            return redirect('nec-rates', pk=nec.pk)
        else:
            return self.form_invalid(form)

    def get_object(self, queryset=None):
        nec = get_object_or_404(NEC, pk=self.kwargs['pk'])
        return nec.rates_set.get(id=self.kwargs['rate_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Rate'
        context['nec'] = NEC.objects.get(id=self.kwargs['pk'])
        return context


class NecRatesDeleteView(LoginRequiredMixin, DeleteView):
    model = Rates
    context_object_name = 'rate'
    template_name = 'payroll_info/nec_rate_delete.html'

    # using get_object to get the rate to be deleted
    def get_object(self, queryset=None):
        nec = get_object_or_404(NEC, pk=self.kwargs['pk'])
        return nec.rates_set.get(id=self.kwargs['rate_pk'])

    def get_success_url(self):
        nec = get_object_or_404(NEC, pk=self.kwargs['pk'])
        return reverse('nec-rates', kwargs={'pk': nec.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Rate'
        context['nec'] = NEC.objects.get(id=self.kwargs['pk'])
        return context


class NecGradesListView(LoginRequiredMixin, ListView):
    model = Grades
    template_name = 'payroll_info/nec_grades_list.html'
    context_object_name = 'grades'
    ordering = ['grade']
    paginate_by = 10

    def get_queryset(self):
        return NEC.objects.get(id=self.kwargs['pk']).grades_set.order_by("grade")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'NEC Grades'
        context['nec'] = NEC.objects.get(id=self.kwargs['pk'])
        return context


class NecGradesCreateView(LoginRequiredMixin, CreateView):
    model = Grades
    form_class = NECGradesForm
    template_name = 'payroll_info/nec_grade_create_update.html'

    # post method to set the parent to the nec passed in the url
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        nec = get_object_or_404(NEC, pk=kwargs['pk'])
        if form.is_valid():
            form.instance.nec = nec
            form.save()
            return redirect('nec-grades', pk=nec.pk)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New Grade'
        context['nec'] = NEC.objects.get(id=self.kwargs['pk'])
        return context


class NecGradesUpdateView(LoginRequiredMixin, UpdateView):
    model = Grades
    form_class = NECGradesForm
    template_name = 'payroll_info/nec_grade_create_update.html'

    # # post method to set the parent to the nec passed in the url
    # def post(self, request, *args, **kwargs):
    #     nec = get_object_or_404(NEC, pk=kwargs['pk'])
    #     grade = nec.grades_set.get(id=self.kwargs['grade_pk'])
    #     form = self.form_class(request.POST, instance=grade)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('nec-grades', pk=nec.pk)
    #     else:
    #         return self.form_invalid(form)

    def get_success_url(self):
        nec = get_object_or_404(NEC, pk=self.kwargs['pk'])
        return reverse('nec-grades', kwargs={'pk': nec.pk})

    def get_object(self, queryset=None):
        nec = get_object_or_404(NEC, pk=self.kwargs['pk'])
        return nec.grades_set.get(id=self.kwargs['grade_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Grade'
        context['nec'] = NEC.objects.get(id=self.kwargs['pk'])
        return context


class NecGradesDeleteView(LoginRequiredMixin, DeleteView):
    model = Grades
    context_object_name = 'grade'
    template_name = 'payroll_info/nec_grade_delete.html'

    def get_success_url(self):
        nec = get_object_or_404(NEC, pk=self.kwargs['pk'])
        return reverse('nec-grades', kwargs={'pk': nec.pk})

    def get_object(self, queryset=None):
        nec = get_object_or_404(NEC, pk=self.kwargs['pk'])
        return nec.grades_set.get(id=self.kwargs['grade_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Grade'
        return context
