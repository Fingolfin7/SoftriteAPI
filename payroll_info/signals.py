from .models import *
from django.dispatch import receiver
from django.db.models.signals import post_save


# @receiver(post_save, sender=AgriNecRates)
# def create_agri_nec_table(sender, instance, created, **kwargs):
#     if created:
#         AgriNecTable.objects.create(nec=instance)
#
#
# @receiver(post_save, sender=AgriNecRates)
# def save_agri_rates(sender, instance, **kwargs):
#     instance.agrinectable.save()
