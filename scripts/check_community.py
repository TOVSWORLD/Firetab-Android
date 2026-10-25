#!/usr/bin/env python3
"""Validate tracked community docs, issue forms, taxonomy and release metadata offline."""
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from ci import ROOT, git, require
from check_release import VERSION, validate_manifest

REQUIRED = ['CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', 'SECURITY.md', 'SUPPORT.md', 'GOVERNANCE.md', 'LICENSING.md', 'THIRD_PARTY_NOTICES.md', 'CHANGELOG.md', 'docs/README.md', '.github/CODEOWNERS', '.github/pull_request_template.md']


def validate_links(text, parent, root, tracked):
    for value in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        value = value.strip().strip('<>')
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = (parent / unquote(parsed.path)).resolve()
        require(target.is_relative_to(root.resolve()), f'Link outside repository: {value}')
        relative = target.relative_to(root.resolve()).as_posix()
        require(relative in tracked or any(x.startswith(relative.rstrip('/') + '/') for x in tracked), f'Untracked/missing documentation target: {value}')


def validate_form(form, labels):
    require(form['name'] and form['description'], 'Form name and description required')
    require(set(form['labels']) <= labels, 'Issue form refers to unknown labels')
    ids = [x['id'] for x in form['body'] if x['type'] != 'markdown']
    require(ids and len(ids) == len(set(ids)), 'Missing or duplicate form IDs')
    for item in form['body']:
        require(item['type'] in {'markdown','input','textarea','dropdown','checkboxes'}, 'Unsupported form field')
        if item['type'] == 'dropdown':
            require(item['attributes']['options'], 'Empty dropdown options')
        if item['type'] != 'markdown':
            require(item['attributes']['label'], 'Unlabelled form field')
            require(type(item['validations']['required']) is bool, 'Explicit required-field flag needed')


def main():
    tracked = set(filter(None, git('ls-files', '-z').decode().split('\0')))
    for name in REQUIRED:
        require(name in tracked and (ROOT/name).stat().st_size > 0, f'Missing community document: {name}')
    for name in sorted(tracked):
        if name.endswith('.md') and not name.startswith('evidence/'):
            validate_links((ROOT/name).read_text(), (ROOT/name).parent, ROOT, tracked)
    taxonomy = json.loads((ROOT/'projects/github-taxonomy.json').read_text())
    names = [x['name'] for x in taxonomy['labels']]
    require(len(names) == len(set(names)), 'Duplicate taxonomy labels')
    for label in taxonomy['labels']:
        require(re.fullmatch('[0-9a-f]{6}', label['color']) and label['description'], 'Invalid label metadata')
    templates = list((ROOT/'.github/ISSUE_TEMPLATE').glob('*.yml'))
    require(len(templates) == 8, 'Expected seven issue forms and config')
    for path in templates:
        # These files intentionally use JSON, a YAML-compatible syntax GitHub accepts.
        form = json.loads(path.read_text())
        if path.name != 'config.yml':
            validate_form(form, set(names))
    policy = json.loads((ROOT/'releases/policy.json').read_text())
    require(set(policy['streams']) == {'workspace','firetabs-android','crestron-panel'}, 'Release streams changed unexpectedly')
    prefixes = [x['tag_prefix'] for x in policy['streams'].values()]
    require(len(set(prefixes)) == 3, 'Overlapping release prefixes')
    require(all(VERSION.fullmatch(x['next_version']) for x in policy['streams'].values()), 'Invalid next-version proposal')
    for path in sorted((ROOT/'releases/manifests').glob('*.json')):
        manifest = json.loads(path.read_text())
        require(path.stem == manifest['tag'], 'Manifest filename must match tag')
        validate_manifest(manifest)
    print('PASS: community documents, local link targets, issue forms, taxonomy and release records')
    print('No network checks, runtime tests or release publication performed.')


if __name__ == '__main__':
    main()
