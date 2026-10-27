#!/usr/bin/env python3
"""Require explicit PR-to-issue traceability; never modifies GitHub state."""
import json
import os
import re
import urllib.request


def references(body):
    # Examples/comments in the template do not count as submitted links.
    body = re.sub(r'<!--.*?-->', '', body or '', flags=re.S)
    body = re.sub(r'```.*?```', '', body, flags=re.S)
    return sorted({int(n) for n in re.findall(
        r'(?im)^\s*(?:[-*]\s*)?(?:updates?|refs?|closes?|fix(?:es)?|resolves?)\s+#([1-9][0-9]*)\b', body)})


def validate(body, fetch):
    numbers = references(body)
    if not numbers:
        raise ValueError('PR body needs a line such as Updates #123 or Closes #123')
    for number in numbers:
        record = fetch(number)
        if record.get('number') != number or 'pull_request' in record:
            raise ValueError('Reference must identify a real repository issue, not a PR')
    return numbers


def main():
    with open(os.environ['GITHUB_EVENT_PATH']) as stream:
        event = json.load(stream)
    repository = os.environ['GITHUB_REPOSITORY']
    api = os.environ.get('GITHUB_API_URL', 'https://api.github.com')

    def fetch(number):
        request = urllib.request.Request(
            f'{api}/repos/{repository}/issues/{number}',
            headers={'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
                     'Accept': 'application/vnd.github+json'})
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)

    numbers = validate(event['pull_request'].get('body'), fetch)
    print('PASS: issue traceability ' + ', '.join('#' + str(n) for n in numbers))


if __name__ == '__main__':
    main()
