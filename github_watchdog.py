#!/usr/bin/env python
# poll github for new contributors

import shelve
import configparser
import logging
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

    def log(self,message):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename='github_watchdog.log',
                            filemode='a')
        logging.info(message)

    def count_contribs(self):
        contrib_arr=[]
        count=0
        g=Github()
        r=g.get_repo(self.repo)
        contrib_list=r.get_contributors()
        for each in contrib_list:
            count+=1
            print each.login
            contrib_arr.append(each.login)
        new_contrib=contrib_arr[-1]
        return count,new_contrib

    def check_contribs(self):
        current,new_contrib=self.count_contribs()
        d = shelve.open('/github_watchdog/gw_persist.db')
        flag = 'contrib_count' in d
        if flag:
            if (d['contrib_count']) == current:
                #self.slack_alert()
                self.log('no change in contributors')
                print('no change in number of contribs')
            else:
                #self.slack_alert()
                self.log('new contributor: '+new_contrib)
                d['contrib_count']=current
                print('ermagerd, more contribs!!!')
        else:
            print('initializing state')
            self.log('initializing state')
            d['contrib_count']=current
        d.close()

c=Contrib()
c.check_contribs()



