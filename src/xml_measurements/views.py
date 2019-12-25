from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DeleteView
from xml_measurements.forms import ConfigurationForm, RuleFormset
from xml_measurements.models import Configuration, Rule


def create_update_configuration(request, pk=None):
    if request.method == 'POST':
        configuration_form = ConfigurationForm(request.POST)
        val_err = ValidationError("")
        try:
            with transaction.atomic():
                if configuration_form.is_valid():
                    configuration = configuration_form.save(commit=False)
                    configuration.pk = pk
                    configuration.save()
                    rule_formset = RuleFormset(request.POST, instance=configuration)
                    if rule_formset.is_valid():
                        rule_formset.save()
                        return redirect('xml_measurements:index')
                    else:
                        raise val_err
        except ValidationError:
            pass
    else:
        initial_conf, initial_rules = None, []
        instance = None
        if pk:
            initial_conf = get_object_or_404(Configuration, pk=pk)
            initial_rules = [model_to_dict(rule) for rule in initial_conf.rule_set.all()]
            instance = initial_conf
            initial_conf = model_to_dict(initial_conf)

        configuration_form = ConfigurationForm(initial=initial_conf)
        rule_formset = RuleFormset(initial=initial_rules, instance=instance)

    context = {
        'configuration_form': configuration_form,
        'rule_formset': rule_formset
    }
    return render(request, 'xml_measurements/index.html', context)


class ConfigurationListView(ListView):
    model = Configuration
    template_name = 'xml_measurements/configuration_list.html'


class ConfigurationDeleteView(DeleteView):
    model = Configuration
    template_name = 'xml_measurements/configuration_delete.html'

    def get_success_url(self):
        return reverse('xml_measurements:index')


def duplicate_configuration(request, pk):
    conf = get_object_or_404(Configuration, pk=pk)
    rules = conf.rule_set.all()
    conf.pk = None
    conf.save()

    def set_conf(rule):
        rule.pk = None
        rule.configuration = conf
        return rule

    Rule.objects.bulk_create([set_conf(rule) for rule in rules])
    return redirect('xml_measurements:index')


def inspect_file_view(request):
    pass