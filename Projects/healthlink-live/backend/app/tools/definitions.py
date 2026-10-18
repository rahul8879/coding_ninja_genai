TOOLS = [{'type': 'function',
  'name': 'list_specialties',
  'description': 'List the exact specialty names in our doctor directory.',
  'parameters': {'type': 'object',
                 'properties': {},
                 'required': [],
                 'additionalProperties': False},
  'strict': True},
 {'type': 'function',
  'name': 'search_doctors',
  'description': 'Search by exact specialty. Returns up to 10 doctors ordered by rating. '
                 'Availability is schedule text, not confirmed slots.',
  'parameters': {'type': 'object',
                 'properties': {'specialty': {'type': 'string',
                                              'description': 'An exact name from '
                                                             'list_specialties.'}},
                 'required': ['specialty'],
                 'additionalProperties': False},
  'strict': True},
 {'type': 'function',
  'name': 'get_available_slots',
  'description': 'Get actual available slots for a doctor and clinic date. Does not book. Use '
                 'a doctor ID returned by search_doctors.',
  'parameters': {'type': 'object',
                 'properties': {'doctor_id': {'type': 'integer'},
                                'on_date': {'type': 'string',
                                            'description': 'Clinic date YYYY-MM-DD, '
                                                           'Asia/Kolkata.'}},
                 'required': ['doctor_id', 'on_date'],
                 'additionalProperties': False},
  'strict': True},
 {'type': 'function',
  'name': 'prepare_booking',
  'description': 'Prepare a confirmation card only after the user explicitly selects an '
                 'unambiguous doctor/date/time for booking. Rechecks availability. Does not '
                 'book or reserve. Copy the exact doctor_id and starts_at from tool results.',
  'parameters': {'type': 'object',
                 'properties': {'doctor_id': {'type': 'integer'},
                                'starts_at': {'type': 'string',
                                              'description': 'Exact slot ISO timestamp with '
                                                             'timezone.'}},
                 'required': ['doctor_id', 'starts_at'],
                 'additionalProperties': False},
  'strict': True}]
