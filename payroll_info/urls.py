from django.urls import path
from . import views

urlpatterns = [
    # page paths
    path('', views.home, name='payroll-home'),

    path('interbank/', views.InterbankListView.as_view(), name='interbank-rates'),
    path('interbank/add/', views.InterbankCreateView.as_view(), name='interbank-add'),
    path('interbank/<int:pk>/update/', views.InterbankUpdateView.as_view(), name='interbank-update'),
    path('interbank/<int:pk>/delete/', views.InterbankDeleteView.as_view(), name='interbank-delete'),

    path('nec/add/', views.NecCreateView.as_view(), name='nec-add'),
    path('nec/<int:pk>/update/', views.NecUpdateView.as_view(), name='nec-update'),
    path('nec/<int:pk>/delete/', views.NecDeleteView.as_view(), name='nec-delete'),

    path('nec/<int:pk>/rates/', views.NecRatesListView.as_view(), name='nec-rates'),
    path('nec/<int:pk>/rates/add/', views.NecRatesCreateView.as_view(), name='nec-rate-add'),
    path('nec/<int:pk>/rates/<int:rate_pk>/update/', views.NecRatesUpdateView.as_view(), name='nec-rate-update'),
    path('nec/<int:pk>/rates/<int:rate_pk>/delete/', views.NecRatesDeleteView.as_view(), name='nec-rate-delete'),

    path('nec/<int:pk>/grades/', views.NecGradesListView.as_view(), name='nec-grades'),
    path('nec/<int:pk>/grades/add/', views.NecGradesCreateView.as_view(), name='nec-grade-add'),
    path('nec/<int:pk>/grades/<int:grade_pk>/update/', views.NecGradesUpdateView.as_view(), name='nec-grade-update'),
    path('nec/<int:pk>/grades/<int:grade_pk>/delete/', views.NecGradesDeleteView.as_view(), name='nec-grade-delete'),


    # api paths
    path('interbank/get_latest_rate/', views.get_latest_rate, name='get_latest_rate'),
    path('interbank/get_rate_on/<str:date>/', views.get_rate_on, name='get_rates_on'),
    path('interbank/get_all_rates/', views.get_all_rates, name='get_all_rates'),
    path('nec/get_necs/', views.get_necs, name='nec_get_necs'),
    path('nec/<int:pk>/get_latest_rate/', views.get_latest_nec_rate, name='nec_get_latest_rate'),
    path('nec/<int:pk>/get_all_rates/', views.get_all_nec_rates, name='nec_get_all_rates'),
    path('nec/<int:pk>/get_rate_on/<str:date>/', views.get_nec_rate_on, name='nec_get_rate_on'),
    path('nec/<int:pk>/get_all_grades/', views.get_all_nec_grades, name='nec_get_all_grades'),
    path('nec/<int:pk>/get_grade/<str:grade>/', views.get_nec_grade, name='nec_get_grade'),
]
