#!/usr/bin/env python3
"""Idempotently apply this repo's labels, milestones and bounded issue seed via gh."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = 'TOVSWORLD/Firetab-Android'


def gh(*args, payload=None):
    command = ['gh', *args]
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'GitHub command failed: {args[0]}: {result.stderr.strip()}')
    return json.loads(result.stdout) if result.stdout.strip() else None


def api(path, payload=None, method=None):
    args = ['api', f'repos/{REPO}/{path}']
    if payload is not None:
        args += ['--method', method or 'POST', '--input', '-']
    elif method:
        args += ['--method', method]
    return gh(*args, payload=payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Explicitly mutate the configured GitHub repository')
    args = parser.parse_args()
    taxonomy = json.loads((ROOT/'projects/github-taxonomy.json').read_text())
    seed = json.loads((ROOT/'projects/issue-seed.json').read_text())
    if not args.apply:
        print(f'Would reconcile {len(taxonomy["labels"])} labels, {len(taxonomy["milestones"])} milestones and {len(seed)} bounded issues in {REPO}. No network calls or changes.')
        return
    # --paginate --slurp produces a single JSON array of result pages.
    label_pages = gh('api', f'repos/{REPO}/labels?per_page=100', '--paginate', '--slurp')
    existing_labels = {x['name']: x for page in label_pages for x in page}
    for label in taxonomy['labels']:
        old = existing_labels.get(label['name'])
        if old is None:
            api('labels', label)
        elif any(old[field] != label[field] for field in ['color','description']):
            from urllib.parse import quote
            api('labels/'+quote(label['name'],safe=''), label, 'PATCH')
    milestone_pages = gh('api', f'repos/{REPO}/milestones?state=all&per_page=100', '--paginate', '--slurp')
    milestones = {x['title']: x for page in milestone_pages for x in page}
    for item in taxonomy['milestones']:
        if item['title'] not in milestones:
            milestones[item['title']] = api('milestones', item)
    issue_pages = gh('api', f'repos/{REPO}/issues?state=all&per_page=100', '--paginate', '--slurp')
    existing = [x for page in issue_pages for x in page if 'pull_request' not in x]
    mapped = {}
    for item in seed:
        marker = '<!-- firetabs-seed:'+item['key']+' -->'
        matches = [x for x in existing if marker in (x['body'] or '')]
        if len(matches) > 1:
            raise ValueError('Duplicate seed markers; resolve before continuing: '+item['key'])
        if matches:
            issue = matches[0]
        else:
            payload = dict(title=item['title'], body=marker+'\n\n'+item['body'], labels=item['labels'])
            if item['milestone']:
                payload['milestone'] = milestones[item['milestone']]['number']
            issue = api('issues', payload)
            existing.append(issue)
        mapped[item['key']] = issue
        if item['parent']:
            parent = mapped[item['parent']]
            children = api(f'issues/{parent["number"]}/sub_issues?per_page=100')
            if issue['id'] not in {x['id'] for x in children}:
                api(f'issues/{parent["number"]}/sub_issues', dict(sub_issue_id=issue['id']))
        print(f'{item["key"]}: {issue["html_url"]}')
    state = {'repository':REPO,'issues':{key:dict(number=value['number'],url=value['html_url']) for key,value in mapped.items()},'milestones':{key:dict(number=value['number'],url=value['html_url']) for key,value in milestones.items()}}
    (ROOT/'projects/github-setup.json').write_text(json.dumps(state,indent=2)+'\n')
    print('Applied metadata; recorded server identities in projects/github-setup.json. No existing issue bodies/statuses were overwritten.')


if __name__ == '__main__':
    main()
