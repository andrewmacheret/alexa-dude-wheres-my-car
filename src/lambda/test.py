import main
import sys

find_device_tests = [
  {
    'expected': 'Your car is located at ',
    'slots': {
      'DEVICE': { 'value': 'car' }
    }
  }
]

failure = False


for test in find_device_tests:
  expected = test['expected']
  intent = {'slots': test['slots']}
  actual = main.get_find_device_response(intent)['response']['outputSpeech']['text']
  success = (actual.startswith(expected))
  print(success, 'expected:', expected, 'actual:', actual)
  if not success:
    failure = True


if failure:
  sys.exit(1)
