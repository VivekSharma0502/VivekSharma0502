"""Fill the neofetch card with live GitHub numbers. Runs daily from Actions."""
import json, os, urllib.request
from datetime import datetime

USER = os.environ['USERNAME']
q = """query($login:String!){ user(login:$login){
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:1, orderBy:{field:PUSHED_AT, direction:DESC}){
    totalCount nodes{ name pushedAt } }
  contributionsCollection{ contributionCalendar{ totalContributions } } } }"""
req = urllib.request.Request('https://api.github.com/graphql',
    data=json.dumps({'query': q, 'variables': {'login': USER}}).encode(),
    headers={'Authorization': f"bearer {os.environ['GITHUB_TOKEN']}", 'Content-Type': 'application/json'})
u = json.load(urllib.request.urlopen(req))['data']['user']
repos = u['repositories']
last = repos['nodes'][0] if repos['nodes'] else None
lastpush = (datetime.fromisoformat(last['pushedAt'].replace('Z', '+00:00')).strftime('%d %b %Y') + ' · ' + last['name']) if last else '-'
svg = open('.github/neofetch.template.svg').read()
svg = (svg.replace('{{REPOS}}', str(repos['totalCount']))
          .replace('{{CONTRIB}}', f"{u['contributionsCollection']['contributionCalendar']['totalContributions']:,}")
          .replace('{{LASTPUSH}}', lastpush))
os.makedirs('profile-3d-contrib', exist_ok=True)
open('profile-3d-contrib/neofetch.svg', 'w').write(svg)
print('neofetch:', repos['totalCount'], lastpush)
