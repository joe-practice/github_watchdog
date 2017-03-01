#!/usr/bin/env python
# poll github for new contributors

import shelve
import configparser
from slacker import Slacker
from github import Github

conf = 'github_watchdog.conf'
print('polling github...')

class Contrib():
    poll=60
    #github's api rate limits might require authentication for >100 contribs
    #repo='stack72/ops-books'
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(conf)
        self.repo=config['default']['repo']
        self.slack_token=config['default']['slack_token']
        self.slack_channel=config['default']['slack_channel']

    def slack_alert(self):
        slack=Slacker(self.slack_token)
        slack.chat.post_message(self.slack_channel,'alert: new contributor detected')

    def count_contribs(self):
        count=0
        g=Github()
        r=g.get_repo(self.repo)
        contrib_list=r.get_contributors()
        for each in contrib_list:
            count+=1
            print each.login
        return count

    def check_contribs(self):
        d = shelve.open('github_watchdog')
        flag = 'contrib_count' in d
        if flag:
            if (d['contrib_count']) == self.count_contribs():
                self.slack_alert()
                print('no change in number of contribs')
            else:
                self.slack_alert()
                print('ermagerd, more contribs!!!')
        else:
            print('initializing state')
            d['contrib_count']=self.count_contribs()
        d.close()

c=Contrib()
c.check_contribs()



