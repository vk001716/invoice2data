"""
This module abstracts templates for invoice providers.

Templates are initially read from .yml files and then kept as class.
"""
import re
import dateparser
from unidecode import unidecode
import logging
from collections import OrderedDict
from .plugins import lines, tables
from ..config import *
from collections import defaultdict
logger = logging.getLogger(__name__)

OPTIONS_DEFAULT = {
    'remove_whitespace': False,
    'remove_accents': False,
    'lowercase': False,
    'currency': 'EUR',
    'date_formats': [],
    'languages': [],
    'decimal_separator': '.',
    'replace': [],  # example: see templates/fr/fr.free.mobile.yml
}

PLUGIN_MAPPING = {'lines': lines, 'tables': tables}


class InvoiceTemplate(OrderedDict):
    """
    Represents single template files that live as .yml files on the disk.

    Methods
    -------
    prepare_input(extracted_str)
        Input raw string and do transformations, as set in template file.
    matches_input(optimized_str)
        See if string matches keywords set in template file
    parse_number(value)
        Parse number, remove decimal separator and add other options
    parse_date(value)
        Parses date and returns date after parsing
    coerce_type(value, target_type)
        change type of values
    extract(optimized_str)
        Given a template file and a string, extract matching data fields.
    """

    def __init__(self, *args, **kwargs):
        super(InvoiceTemplate, self).__init__(*args, **kwargs)

        # Merge template-specific options with defaults
        self.options = OPTIONS_DEFAULT.copy()

        for lang in self.options['languages']:
            assert len(lang) == 2, 'lang code must have 2 letters'

        if 'options' in self:
            self.options.update(self['options'])

        # Set issuer, if it doesn't exist.
        if 'issuer' not in self.keys():
            self['issuer'] = self['keywords'][0]

    def prepare_input(self, extracted_str):
        """
        Input raw string and do transformations, as set in template file.
        """

        # Remove withspace
        if self.options['remove_whitespace']:
            optimized_str = re.sub(' +', '', extracted_str)
        else:
            optimized_str = extracted_str

        # Remove accents
        if self.options['remove_accents']:
            optimized_str = unidecode(optimized_str)

        # convert to lower case
        if self.options['lowercase']:
            optimized_str = optimized_str.lower()

        # specific replace
        for replace in self.options['replace']:
            assert len(replace) == 2, 'A replace should be a list of 2 items'
            optimized_str = optimized_str.replace(replace[0], replace[1])

        return optimized_str

    def matches_input(self, optimized_str):
        """See if string matches keywords set in template file"""

        if all([keyword in optimized_str for keyword in self['keywords']]):
            logger.debug('Matched template %s', self['template_name'])
        # @vk001716
        return True

    def parse_number(self, value):
        assert (
            value.count(self.options['decimal_separator']) < 2
        ), 'Decimal separator cannot be present several times'
        # replace decimal separator by a |
        amount_pipe = value.replace(self.options['decimal_separator'], '|')
        # remove all possible thousands separators
        amount_pipe_no_thousand_sep = re.sub(r'[.,\s]', '', amount_pipe)
        # put dot as decimal sep
        return float(amount_pipe_no_thousand_sep.replace('|', '.'))

    def parse_date(self, value):
        """Parses date and returns date after parsing"""
        res = dateparser.parse(
            value, date_formats=self.options['date_formats'], languages=self.options['languages']
        )
        logger.debug("result of date parsing=%s", res)
        return res

    def coerce_type(self, value, target_type):
        if target_type == 'int':
            if not value.strip():
                return 0
            return int(self.parse_number(value))
        elif target_type == 'float':
            if not value.strip():
                return 0.0
            return float(self.parse_number(value))
        elif target_type == 'date':
            return self.parse_date(value)
        assert False, 'Unknown type'

    def extract(self, optimized_str):
        """
        Given a template file and a string, extract matching data fields.
        """

        logger.debug('START optimized_str ========================')
        logger.debug(optimized_str)
        logger.debug('END optimized_str ==========================')
        logger.debug(
            'Date parsing: languages=%s date_formats=%s',
            self.options['languages'],
            self.options['date_formats'],
        )
        logger.debug('Float parsing: decimal separator=%s',
                     self.options['decimal_separator'])
        logger.debug("keywords=%s", self['keywords'])
        logger.debug(self.options)
        print("optimized_str={}".format(optimized_str))
        # Try to find data for each field.
        # @vk001716
        output = defaultdict()
        output['issuer'] = self['issuer']

        for k, v in self['fields'].items():
            if k.startswith('static_'):
                logger.debug("field=%s | static value=%s", k, v)
                output[k.replace('static_', '')] = v
            else:
                logger.debug("field=%s | regexp=%s", k, v)

                sum_field = False
                if k.startswith('sum_amount') and type(v) is list and False:
                    k = k[4:]  # remove 'sum_' prefix
                    sum_field = True
                # Fields can have multiple expressions
                if type(v) is list:
                    print("type of {} is list".format(str(v)))
                    res_find = []
                    for v_option in v:
                        res_val = re.findall(v_option, optimized_str)
                        if res_val:
                            if sum_field:
                                res_find += res_val
                            else:
                                res_find.extend(res_val)
                else:
                    res_find = re.finditer(v, optimized_str)
                    res_find = [ i.group() for i in res_find ]
                    res_find = res_find if len(res_find) > 0 else None 
                if res_find:
                    logger.debug("res_find=%s", res_find)
                    if (k.startswith('date') or k.endswith('date')) and False:
                        output[k] = self.parse_date(res_find[0])
                        if not output[k]:
                            logger.error(
                                "Date parsing failed on date '%s'", res_find[0])
                            return None
                    elif (k.startswith('amount')) and False:
                        if sum_field:
                            output[k] = 0
                            for amount_to_parse in res_find:
                                output[k] += self.parse_number(amount_to_parse)
                        else:
                            output[k] = self.parse_number(res_find[0])
                    else:
                        # Only this part is executing
                        print(k,v,str(res_find))
                        output[k] = []
                        res_find = list(set(res_find))
                        for value in  res_find:
                            trimmed_value = value.replace(k,"").strip()
                            print(k,value,trimmed_value)
                            if len(trimmed_value) > 2:
                                if trimmed_value[0] in remove_initial_character:
                                    if len(trimmed_value) > 2:
                                        trimmed_value = trimmed_value[1:]
                                        trimmed_value = trimmed_value.strip()
                                        output[k].append(trimmed_value)
                                else:
                                    output[k].append(trimmed_value)
                        if len(output[k]) == 0:
                            del output[k]
                else:
                    logger.warning("regexp for field %s didn't match", k)

        # Run plugins:
        for plugin_keyword, plugin_func in PLUGIN_MAPPING.items():
            if plugin_keyword in self.keys():
                plugin_func.extract(self, optimized_str, output)
        # @vk001716
        out = defaultdict()
        for m in re.finditer(regex, optimized_str):
            match = optimized_str[int(m.start()): int(m.end())]
            print(match)
            if len(str(match.split(':')[1].strip())) > 0:
                out[str(match.split(':')[0].strip())] = str(
                    match.split(':')[1].strip())
        for key in list(out.keys()):
            if key in garbage_data or out[key] in garbage_value:
                del out[key]
        output['From base model'] = dict(out)
        return dict(output)
