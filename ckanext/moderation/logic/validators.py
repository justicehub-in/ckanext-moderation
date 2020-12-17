import six
from ckan.plugins.toolkit import Invalid
from ckanext.scheming.validation import scheming_validator
from ckan.plugins.toolkit import _, missing


def starts_with_b(value):
    if not value.startswith('b'):
        raise Invalid("Doesn't start with b")
    return value



@scheming_validator
def scheming_multiple_choice_with_other(field, schema):
    """
    Accept zero or more values from a list of choices and convert
    to a json list for storage:
    1. a list of strings, eg.:
       ["choice-a", "choice-b"]
    2. a single string for single item selection in form submissions:
       "choice-a"
    """
    static_choice_values = None
    if 'choices' in field:
        static_choice_order = [c['value'] for c in field['choices']]
        static_choice_values = set(static_choice_order)

    def validator(key, data, errors, context):
        # if there was an error before calling our validator
        # don't bother with our validation
        if errors[key]:
            return

        value = data[key]
        if value is not missing:
            if isinstance(value, six.string_types):
                value = [value]
            elif not isinstance(value, list):
                errors[key].append(_('expecting list of strings'))
                return
        else:
            value = []

        choice_values = static_choice_values
        if not choice_values:
            choice_order = [c['value'] for c in sh.scheming_field_choices(field)]
            choice_values = set(choice_order)

        selected = set()
        for element in value:
            selected.add(element)

            if element and element not in static_choice_order:
                static_choice_order.append(element)
            continue

        if not errors[key]:
            data[key] = ','.join([v for v in
                (static_choice_order if static_choice_values else choice_order)
                if v in selected])

            if field.get('required') and not selected:
                errors[key].append(_('Select at least one'))

    return validator