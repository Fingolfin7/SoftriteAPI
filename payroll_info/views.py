from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.urls import reverse
from .forms import *
from .scrapers.rbz_rate import download_rbz_pdf_binary, get_rbz_rate
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import InterbankUSDRateSerializer, NECSerializer, GradesSerializer

import logging

logger = logging.getLogger(__name__)


class StaffRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(StaffRequiredMixin, cls).as_view(**kwargs)
        return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view)


def update_rbz_rate():
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
@api_view(['GET'])
def get_latest_rate(request):
    update_rbz_rate()
    rate_obj = InterbankUSDRate.objects.order_by('-date').first()
    serializer = InterbankUSDRateSerializer(rate_obj)
    return Response(serializer.data)


@api_view(['GET'])
def get_rate_on(request, date):
    try:
        date = datetime.strptime(date, '%m-%d-%Y')
        rate_obj = InterbankUSDRate.objects.filter(date=date).get()
        serializer = InterbankUSDRateSerializer(rate_obj)
        return Response(serializer.data)
    except InterbankUSDRate.DoesNotExist:
        return HttpResponseNotFound("No rate found for this date")


@api_view(['GET'])
def get_rates_between(request, start_date, end_date):
    try:
        start_date = datetime.strptime(start_date, '%m-%d-%Y')
        end_date = datetime.strptime(end_date, '%m-%d-%Y')
        rates = InterbankUSDRate.objects.filter(date__range=[start_date, end_date]).order_by('date')
        serializer = InterbankUSDRateSerializer(rates, many=True)
        if not rates:
            return HttpResponseNotFound("No rates found")
        return Response(serializer.data)
    except ValueError:
        return HttpResponseNotFound("Invalid date format")
    except InterbankUSDRate.DoesNotExist:
        return HttpResponseNotFound("No rates found")


@api_view(['GET'])
def get_all_rates(request):
    rates = InterbankUSDRate.objects.all().order_by('-date')
    serializer = InterbankUSDRateSerializer(rates, many=True)
    if not rates:
        return HttpResponseNotFound("No rates found")
    return Response(serializer.data)


@api_view(['GET'])
def get_necs(request):
    necs = NEC.objects.all()
    serializer = NECSerializer(necs, many=True)
    if not necs:
        return HttpResponseNotFound("No NECs found")
    return Response(serializer.data)


@api_view(['GET'])
def get_latest_nec_rate(request, pk):
    try:
        nec = NEC.objects.get(pk=pk)
        rate_obj = nec.rates_set.order_by('-date').first()
        if not rate_obj:
            return HttpResponseNotFound("No rate found for this NEC")
        serializer = InterbankUSDRateSerializer(rate_obj)
        return Response({
            'nec': nec.name,
            **serializer.data
        })
    except NEC.DoesNotExist:
        return HttpResponseNotFound("No NEC found")


@api_view(['GET'])
def get_all_nec_rates(request, pk):
    try:
        nec = NEC.objects.get(pk=pk)
        rates = nec.rates_set.all().order_by('-date')
        serializer = InterbankUSDRateSerializer(rates, many=True)
        if not rates:
            return HttpResponseNotFound("No rates found")
        return Response([
            {'nec': nec.name, **rate}
            for rate in serializer.data
        ])
    except NEC.DoesNotExist:
        return HttpResponseNotFound("No NEC found")


@api_view(['GET'])
def get_nec_rate_on(request, pk, date):
    try:
        nec = NEC.objects.get(pk=pk)
        date = datetime.strptime(date, '%m-%d-%Y')
        rate_obj = nec.rates_set.filter(date=date).get()
        serializer = InterbankUSDRateSerializer(rate_obj)
        return Response({
            'nec': nec.name,
            **serializer.data
        })
    except (NEC.DoesNotExist, InterbankUSDRate.DoesNotExist):
        return HttpResponseNotFound("No rate found for this date")


@api_view(['GET'])
def get_all_nec_grades(request, pk):
    try:
        nec = NEC.objects.get(pk=pk)
        grades = nec.grades_set.all()
        serializer = GradesSerializer(grades, many=True)
        if not grades:
            return HttpResponseNotFound("No grades found")
        return Response([
            {'nec': nec.name, **grade}
            for grade in serializer.data
        ])
    except NEC.DoesNotExist:
        return HttpResponseNotFound("No NEC found")


@api_view(['GET'])
def get_nec_grade(request, pk, grade):
    try:
        nec = NEC.objects.get(pk=pk)
        grade_obj = nec.grades_set.filter(grade=grade).get()
        serializer = GradesSerializer(grade_obj)
        return Response({
            'nec': nec.name,
            **serializer.data
        })
    except (NEC.DoesNotExist, Grades.DoesNotExist):
        return HttpResponseNotFound("No grade found")


@user_passes_test(lambda u: u.is_staff or u.is_superuser)  # check if user is staff or superuser
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
class InterbankListView(StaffRequiredMixin, ListView):
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


class InterbankCreateView(StaffRequiredMixin, CreateView):
    model = InterbankUSDRate
    template_name = 'payroll_info/interbank_page.html'
    form_class = InterbankUSDRateForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New Interbank Rate'
        return context


class InterbankUpdateView(StaffRequiredMixin, UpdateView):
    model = InterbankUSDRate
    template_name = 'payroll_info/interbank_page.html'
    form_class = InterbankUSDRateForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Interbank Rate'
        return context


class InterbankDeleteView(StaffRequiredMixin, DeleteView):
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


class NecCreateView(StaffRequiredMixin, CreateView):
    model = NEC
    template_name = 'payroll_info/nec_page.html'
    form_class = NecForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New NEC'
        return context


class NecUpdateView(StaffRequiredMixin, UpdateView):
    model = NEC
    template_name = 'payroll_info/nec_page.html'
    form_class = NecForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update NEC'
        return context


class NecDeleteView(StaffRequiredMixin, DeleteView):
    model = NEC
    template_name = 'payroll_info/nec_delete.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete NEC'
        context['nec'] = NEC.objects.get(id=self.kwargs['pk'])
        return context


class NecRatesListView(StaffRequiredMixin, ListView):
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


class NecRatesCreateView(StaffRequiredMixin, CreateView):
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


class NecRatesUpdateView(StaffRequiredMixin, UpdateView):
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


class NecRatesDeleteView(StaffRequiredMixin, DeleteView):
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


class NecGradesListView(StaffRequiredMixin, ListView):
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


class NecGradesCreateView(StaffRequiredMixin, CreateView):
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


class NecGradesUpdateView(StaffRequiredMixin, UpdateView):
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


class NecGradesDeleteView(StaffRequiredMixin, DeleteView):
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
