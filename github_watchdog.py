#!/usr/bin/env python
# poll github for new contributors

import shelve, configparser, logging, time
from slacker import Slacker
from github import Github

class Contrib():
    """github's api rate limits might require authentication for >100 contribs"""
    def __init__(self):
        """initialize a contrib object"""
        config = configparser.ConfigParser()
        config.read('github_watchdog.conf')
        self.repo = config['default']['repo']
        self.slack_token = config['default']['slack_token']
        self.slack_channel = config['default']['slack_channel']
        global poll_int
        poll_int = float(config['default']['poll_int'])

    def slack_alert(self, alert_message):
        """send an alert to slack"""
        slack = Slacker(self.slack_token)
        slack.chat.post_message(self.slack_channel, alert_message)

    def log(self, message):
        """write to a local log"""
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename='github_watchdog.log',
                            filemode='a')
        logging.info(message)

    def count_contribs(self):
        """count contributors to a repo"""
        contrib_arr = []
        count = 0
        g = Github()
        r = g.get_repo(self.repo)
        contrib_list = r.get_contributors()
        for each in contrib_list:
            count += 1
            print each.login
            contrib_arr.append(each.login)
        new_contrib = contrib_arr[-1]
        return count, new_contrib

    def check_contribs(self):
        """see if number of contributors changes"""
        current, new_contrib = self.count_contribs()
        d = shelve.open('/github_watchdog/persist/gw_shelve')
        flag = 'contrib_count' in d
        if flag:
            if (d['contrib_count']) == current:
                self.slack_alert('no change in contributors')
                self.log('no change in contributors')
                print 'no change in number of contribs'
            else:
                self.slack_alert('alert: new contributor detected')
                self.log('new contributor: ' + new_contrib)
                d['contrib_count'] = current
                print 'new contributor detected!!!'
        else:
            print 'initializing state'
            d['contrib_count'] = current
        d.close()

con = Contrib()
while True:
    con.check_contribs()
    time.sleep(poll_int)
